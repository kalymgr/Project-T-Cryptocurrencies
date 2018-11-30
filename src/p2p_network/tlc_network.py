import json
from time import time
from uuid import uuid4
import socket
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall

from src.block_chain.transactions import Blockchain
from src.p2p_network.parameters import Parameters, NodeTypes
from src.p2p_network.tlc_message import TLCMessage, TLCVersionMessage, TLCVerAckMessage, TLCGetAddrMessage, \
    TLCRejectMessage, TLCAddrMessage, TLCPingMessage, TLCPongMessage, TLCGetBlocksMessage, TLCInvMessage, \
    TLCGetDataMessage, TLCBlockMessage
from src.utilities.tlc_exceptions import TLCNetworkException

generateNodeId = lambda: str(uuid4())  # function that generates the node id

# DEFAULT PARAMETERS
MAINNET_MAX_NBITS = 0x1d00ffff  # big endian order. Sent in little endian order


class TLCNode:
    """
    class for managing the node data and operations.
    According to online info, a full node should:
    - maintain a wallet
    - make transactions
    - enforce bitcoin rules and protocols
    - store all data
    - relay transaction information from users to miners
    - download and verify blocks and transactions
    """

    def __init__(self, reactor: reactor, address: str = '127.0.0.1', port: int = Parameters.NODE_DEFAULT_PORT_MAINNET,
                 protocolVersion = Parameters.PROTOCOL_VERSION, nodeType:int = NodeTypes.FULL_NODE):
        """
        :param address: the ip address of the node - default is localhost
        :param port: the tcp port of the node - default is the mainnet default port set in the application parameters
        :param reactor: the reactor object
        :param protocolVersion: the version of the protocol for this node
        :param nodeType: the type of the node (eg full node, seed node etc.)
        """
        self.__reactor = reactor
        self.__address = address
        self.__port = port
        self.protocolVersion = protocolVersion
        self.__serverEndPoint = self.__createServerEndPoint()  # create the server endpoint
        self.__tlcFactory = TLCFactory(port, self.protocolVersion, nodeType)  # the TLC Factory for the node
        self.lastUsedProtocol = None  # variable that holds the last used protocol

        # initialize the node blockchain
        self.__tlcFactory.blockchain = Blockchain()
        self.blockchain = self.__tlcFactory.blockchain

    def addNodePeersList(self, nodePeersList: list):
        """
        Method for adding to a node a list of node peers. If a node already exists, it is not added. To avoid duplicate
        records, we will use sets.
        :param nodePeersList:
        :return:
        """
        # create sets from the lists
        initialListSet = set(self.__tlcFactory.peers)
        addedListSet = set(nodePeersList)
        # get only the new elements
        elementsInAddedButNotInitial = addedListSet - initialListSet
        # create the final list and set it as the peer list
        self.__tlcFactory.peers = self.__tlcFactory.peers + list(elementsInAddedButNotInitial)

    def getTLCFactory(self):
        """
        returns the TLC Factory of the node
        :return:
        """
        return self.__tlcFactory

    def getPeers(self) -> list:
        """
        method that returns a list with the peers
        :return: list of peers
        """
        return self.__tlcFactory.peers

    def isPortAvailable(self, host: str, port: int) -> bool:
        """
        Checks if a port is available on our pc

        :param host: the host (string)
        :param port: the port (int)
        :return: True if available, else False
        """
        # create a socket to the specific host and port and get the result
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex((host, port))
        # close the socket
        sock.close()
        if res != 0:  # if the res is not equal to zero (socket available - no one listening there)
            return True
        else:
            return False

    def printPeers(self):
        """
        method that prints a list of peers of the node
        :return:
        """
        print(f'Peers for node <<{self.__address}_{self.__port}>>: {self.getPeers()}')

    def getNodeId(self) -> str:
        """
        method that returns the node id
        :return:
        """
        return self.__tlcFactory.nodeId

    def __createServerEndPoint(self):
        """
        method that creates and returns the server endpoint for the node
        :return:
        """
        return TCP4ServerEndpoint(self.__reactor, self.__port)

    def __createClientEndPoint(self):
        """
        method that creates and returns the client endpoint
        :return:
        """
        return TCP4ClientEndpoint(reactor, self.__address, int(self.__port))

    def startNode(self):
        """
        starts the node. If there is a problem with the port (not available), then it raises a TLCNetworkException.
        :return:
        """
        if self.isPortAvailable(self.__address, self.__port):
            self.__serverEndPoint.listen(self.__tlcFactory)
        else:
            raise TLCNetworkException(f"Port {self.__port} not available")

    def initConnection(self, p):
        """
        initialize the connection
        :return:
        """
        p.sendVersion()
        return p

    def getConnectionState(self, p):
        return p.state

    def connectTo(self, node):
        """
        used to connect to another peer node
        :param node: an other TLC Node
        :return:
        """
        # create a client endpoint to connect to the target address:port
        d = self.makeConnection(node.__address, node.__port)
        d.addCallback(self.initConnection)
        d.addCallback(self.setLastUsedProtocol)

    def setLastUsedProtocol(self, p: Protocol):
        """
        Method that sets the lastUsedProtocolVariable. Called via callback.
        :param p:
        :return:
        """
        self.lastUsedProtocol = p

    def getLastUsedProtocol(self) -> Protocol:
        """
        Method that returns the last used protocol
        :return:
        """
        return self.lastUsedProtocol

    def makeConnection(self, nodeAddress: str, nodePort: int) -> Deferred:
        """
        method for making a connection to a node
        :param nodeAddress: the peer node address
        :param nodePort: the port of the peer node
        :return: the twisted Deferred object of the connection
        """
        # create a client endpoint to connect to the target address:port
        point = TCP4ClientEndpoint(reactor, nodeAddress, nodePort)
        # make the connection
        d = connectProtocol(point, TLCProtocol(self.getTLCFactory()))

        def raiseExc(p: Protocol):
            """
            Method used to raise an exception in case of connection error
            :param p: the protocol
            :return:
            """
            errorMsg = f'Could not connect to peer node {nodeAddress}_{nodePort}'
            print(errorMsg)
            # TODO: exception not properly raised
            raise TLCNetworkException(errorMsg)

        d.addErrback(raiseExc)  # add error callback in case of error
        return d

    def getNodePeers(self, node):
        """
        Asks a node to give him his peers (nodes on his network)
        :param node: the node(TLCNode objects), whose peers we want
        :return:
        """
        d = self.makeConnection(node.__address, node.__port)
        # the parameter of the following callback defines the type of request
        d.addCallback(self.initSendRequest, TLCMessage.CTRLMSGTYPE_GETADDR)
        d.addCallback(self.setLastUsedProtocol)

    def initSendRequest(self, p: Protocol, typeOfRequest: int):
        """
        method for starting a request from another node, depending on the type of the request.
        This method will be used from other methods in this class
        :param p: the Protocol object. Automatically added by the callback
        :param typeOfRequest: the type of message as defined in the TLCMessage class
        :return: the Protocol object, in case it is needed for another callback
        """
        p.sendRequest(typeOfRequest)
        return p

    def setConnectionExtraData(self, p: Protocol, dataKey: str, dataValue):
        """
        Method that sets extra data in the connection, depending on what is needed
        :param dataKey: the key of the data (string)
        :param dataValue: the value of the data, for the specific key
        :return: the TLCProtocol
        """
        p.addExtraData(dataKey, dataValue)
        return p

    def initialBlockDownload(self, peerNode):
        """
        Method that executes an initial block download, to sync the blockchain of the node. It can be called
        either after the node starts or when the node needs to be synced, according to some circumstances.
        :param peerNode: the TLC node used for syncing (TLCNode object)
        :return:
        """
        # get the last block header
        lastBlock = self.blockchain.getChain()[len(self.blockchain.getChain())-1]
        lastBlockHeader = lastBlock.blockHeader

        # if the last block header time is more than 24 hours in the past
        # OR the local best block chain is more than 144 blocks lower than it's local best header chain,
        # start syncing
        if (time() - lastBlockHeader.timeStartHashing > 24 * 60 * 60) or \
            (len(self.blockchain.getHeaderChain()) - len(self.blockchain.getChain()) > 144):
            # make a connection
            d = self.makeConnection(peerNode.__address, peerNode.__port)

            # initialize a request for a getBlocks message
            d.addCallback(self.setConnectionExtraData, 'headerHashes', lastBlock.getBlockHeaderHash())
            d.addCallback(self.initSendRequest, TLCMessage.DATAMSGTYPE_GETBLOCKS)
            d.addCallback(self.setLastUsedProtocol)


class TLCProtocol(Protocol):

    # some node statuses
    NODE_STATUS_READY_TO_CONNECT = 1  # before sending the version message
    NODE_STATUS_WAITING_VERACK = 2
    NODE_STATUS_CONNECTED = 3  # after receiving the verack message

    def __init__(self, factory):
        """
        constructor method.
        :param factory: the factory that will be creating protocols
        """

        # set some variables
        self.factory = factory
        self.state = TLCProtocol.NODE_STATUS_READY_TO_CONNECT
        self.nodeId = self.factory.nodeId  # keep the node id
        self.remoteNodeId = None
        self.nodeType = self.factory.nodeType

        # some code for handling connection inactivity
        self.timeOfConInactivity = 0  # time of connection inactivity
        # the interval for increasing the time of connection inactivity
        self.timeOfConInactivityInterval = Parameters.TIME_OF_CON_INACTIVITY_INTERVAL
        # call the method that updates the time of inactivity
        self.measureConInactivity = LoopingCall(self.updateTimeOfConInactivity)

        # the interval for checking the time of connection inactivity
        self.checkConInactivityInterval = Parameters.CHECK_CON_INACTIVITY_INTERVAL
        # the time of inactivity after which the connection should be closed
        self.closeConnectionTimeLimit = Parameters.CLOSE_CONNECTION_TIME_LIMIT
        # the time limit after which the node should send a ping to his peer
        self.conInactivityPingLimit = Parameters.CON_INACTIVITY_PING_LIMIT
        # call the method that checks the time of connection inactivity
        self.checkConInactivity = LoopingCall(self.checkInactivityTime)

        # peer is considered dead
        # self.lastPingPong = None  # keeps the time of the last successful pinging (ping-pong)
        # self.lcPing = LoopingCall(self.sendPing)  # Calls the sendPing method repeatedly to ping nodes

        self.typeOfRequest = None  # the type of request.

        self.extraData = dict()  # extra data that may be needed for some operations

    def addExtraData(self, key, value):
        """
        Method that adds key-value pairs to the dictionary of the extraData
        :param key:
        :param value:
        :return:
        """
        self.extraData[key] = value

    def connectionMade(self):
        self.remoteIp = self.transport.getPeer()
        self.hostIp = self.transport.getHost()
        print(f"Connection to {str(self.transport.getPeer().host)}/{str(self.transport.getPeer().port)} made")

        # run the method that updates the variable that measures the time of connection inactivity periodically
        self.measureConInactivity.start(self.timeOfConInactivityInterval)
        # run the method that checks the time of connection inactivity periodically
        self.checkConInactivity.start(self.checkConInactivityInterval)

        # start pinging and checking if a peer is alive
        # self.lcPing.start(self.pingpongInterval)

    def connectionLost(self, reason):
        # remove the node that disconnected from the peer dictionary, if it exists in the peer list
        if self.remoteNodeId in self.factory.peers:
            self.factory.peers.pop(self.remoteNodeId)
            self.lcPing.stop()
        print(self.nodeId + " disconnected")

    def dataReceived(self, data):
        # each time some data is received, the connection inactivity counter is reset to zero
        self.timeOfConInactivity = 0

        # for each line of data
        for line in data.splitlines():
            line = line.strip()
            msgType = json.loads(line)['msgHeader']['commandName']  # get the msg type

            # Handle ping and pong messages. Separate if from other handlers, becauses it runs periodically
            if msgType == TLCMessage.CTRLMSGTYPE_PING:
                self.handlePing(line)
            elif msgType == TLCMessage.CTRLMSGTYPE_PONG:
                self.handlePong()

            if self.state != TLCProtocol.NODE_STATUS_CONNECTED:  # if the connection has not been made
                """
                In this if statement, the first negotiations are made between the nodes (version & verack).
                If everything is ok after the negotiations, then the node will change it's status to
                STATUS_CONNECTED
                """
                # depending on the message received, do something
                if msgType == TLCMessage.CTRLMSGTYPE_VERSION:  # if the nodes are exchanging versions
                    self.handleVersion(line)
                elif msgType == TLCMessage.CTRLMSGTYPE_VERACK:  # verack message
                    self.handleVerAck()
                # elif msgType == TLCMessage.CTRLMSGTYPE_GETADDR:  # getaddr message
                #    self.handleGetAddr()
                elif msgType == TLCMessage.CTRLMSGTYPE_REJECT:  # reject message
                    self.handleReject(line)

            else:
                """
                STATUS_CONNECTED. Ready to handle requests - put the request handling here
                """
                if msgType == TLCMessage.CTRLMSGTYPE_VERACK:
                    """
                    This the first contact after the version and verack negotiations. What will happen depends
                    on the typeOfRequest, which was given as parameter from a TLCNode method.
                    Here we put the first message sent after the end of the negotiations.
                    """
                    if self.typeOfRequest == TLCMessage.CTRLMSGTYPE_GETADDR:  # getaddr request
                        self.sendGetAddr()
                    elif self.typeOfRequest == TLCMessage.DATAMSGTYPE_GETBLOCKS:  # getBlocks request
                        self.sendGetBlocks()
                    """
                    After this point, we put all the message handlers, depending on the operation desired.
                    """
                elif msgType == TLCMessage.CTRLMSGTYPE_GETADDR:
                    self.handleGetAddr()
                elif msgType == TLCMessage.CTRLMSGTYPE_ADDR:
                    self.handleAddr(line)
                elif msgType == TLCMessage.DATAMSGTYPE_GETBLOCKS:
                    self.handleGetBlocks(line)
                elif msgType == TLCMessage.DATAMSGTYPE_INV:
                    self.handleInv(line)
                elif msgType == TLCMessage.DATAMSGTYPE_GETDATA:
                    self.handleGetData(line)

    def updateTimeOfConInactivity(self):
        """
        Method that updates the variable (counter) that measures the time of connection inactivity
        :return:
        """
        self.timeOfConInactivity += self.timeOfConInactivityInterval
        # print(f'Time of connection inactivity: {self.timeOfConInactivity}')

    def checkInactivityTime(self):
        """
        Method that checks the time of inactivity. If this time surpasses a limit, then a ping is sent.
        If the time of inactivity surpasses another limit, then the connection is closed.
        :return:
        """
        pingLimit = self.conInactivityPingLimit  # the limit (sec) for connection inactivity
        if self.timeOfConInactivity > pingLimit:
            print('Inactive for some time. Sending ping')
            self.sendPing()

        closeConLimit = self.closeConnectionTimeLimit  # the time limit for closing the connection
        if self.timeOfConInactivity > closeConLimit:
            print('Inactive for a long time. Time to close the connection')
            self.transport.loseConnection()  # close the connection
            self.measureConInactivity.stop()  # stop the method that measures connection inactivity for this connection
            self.checkConInactivity.stop()  # stop the method that checks connection inactivity for this connection

    def sendVersion(self):
        """
        Method for sending the version control message
        :return:
        """
        # create the version message, in a sendable form
        print('Sending version')
        versionMsg = TLCVersionMessage(self.nodeType, self.hostIp.host, self.factory.serverPort,
                                       self.factory.protocolVersion).getMessageAsSendable()
        self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK
        # print(f'--> Node {self.nodeId}. Sent my VERSION')
        self.transport.write(versionMsg)

    def sendRequest(self, typeOfRequest):
        """
        method that initiates a request, depending on the type of request
        :param typeOfRequest:
        :return:
        """
        self.typeOfRequest = typeOfRequest  # store the type of request

        # Initialize the conversation
        # create the version message, in a sendable form
        versionMsg = TLCVersionMessage(self.nodeType, self.hostIp.host, self.factory.serverPort,
                                       self.factory.protocolVersion).getMessageAsSendable()
        self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK
        # print(f'--> Node {self.nodeId}. Sent my VERSION')
        self.transport.write(versionMsg)

    def sendVerAck(self):
        """
        Method for sending the verack (response to version) message
        :return:
        """
        verAckMsg = TLCVerAckMessage().getMessageAsSendable()
        # print(f'--> Node {self.nodeId}. Sent my VERACK')
        self.state = TLCProtocol.NODE_STATUS_CONNECTED
        self.transport.write(verAckMsg)

    def sendReject(self):
        """
        reject the messages of the peer node if something goes wrong
        :return:
        """
        rejectMsg = TLCRejectMessage('version', TLCRejectMessage.REJECT_CODE_DIF_VERSION)\
            .getMessageAsSendable()
        self.transport.write(rejectMsg)
        print('sendReject called')

    def sendGetAddr(self):
        """
        Sending a getAddr message to get the list of network peers of the node
        :return:
        """
        # print('sendGetAddr called.')
        getAddrMessage = TLCGetAddrMessage().getMessageAsSendable()
        # print(f'--> Node {self.nodeId}. Sent my GETADDR')
        # self.state = TLCProtocol.NODE_STATUS_CONNECTED
        self.transport.write(getAddrMessage)

    def sendAddr(self):
        """
        Creates a new addr message and sends it
        :return:
        """
        addrMsg = TLCAddrMessage(self.factory.peers).getMessageAsSendable()
        self.transport.write(addrMsg)

    def sendPing(self):
        pingMsg = TLCPingMessage().getMessageAsSendable()
        print(f'Ping sent \t\t {self.nodeId} --> {self.remoteNodeId}')
        self.transport.write(pingMsg)

    def sendPong(self, nonce: int):
        """
        :param nonce: the nonce received from the ping message
        :return:
        """
        pongMsg = TLCPongMessage(nonce).getMessageAsSendable()
        self.transport.write(pongMsg)

    def sendGetBlocks(self):
        """
        Method that sends the getBlocks message
        :return:
        """
        getBlocksMsg = TLCGetBlocksMessage(self.extraData['headerHashes']).getMessageAsSendable()
        self.transport.write(getBlocksMsg)

    def handlePing(self, pingData: str):
        """
        handle ping.
        :param pingData: the ping data. Contains the nonce
        :return:
        """
        pingMsg = json.loads(pingData)
        nonce = pingMsg['msgData']['nonce']
        self.sendPong(nonce)

    def handlePong(self):
        print(f'Pong received \t {self.nodeId} <-- {self.remoteNodeId}')
        # self.lastPingPong = time()  # keep the timestamp of the last successful ping-pong communication

    def handleVersion(self, versionMsg):
        """
        method that handles the line that is sent to the node (json string). If the versions
        of the two nodes are different, then a reject message is sent.
        :param versionMessage: json string
        :return:
        """
        # print(f'--> Node {self.nodeId}. Got the VERSION.')

        versionMessage = json.loads(versionMsg)  # load the json version message from the string
        # If the protocol versions of the two nodes are compatible, decide how to answer
        # Else (incompatible), reset the state of the node and send a reject message

        if self.factory.protocolVersion == versionMessage['msgData']['version']:  # compatible protocol versions
            # get the ip and port of the remote node
            remoteNodeIp = versionMessage['msgData']['ipAddress']
            remoteNodePort = versionMessage['msgData']['port']

            # if the node is trying to connect to itself, then drop the connection
            if self.hostIp.host == remoteNodeIp and self.hostIp.port == remoteNodePort:
                print('Connected to myself')
                self.transport.loseConnection()  # close the connection
            else:  # case another node trying to connect to this node
                # add the remote node id to the dictionary of peers, if not already there
                self.addPeer(remoteNodeIp, remoteNodePort)
                # decide how to answer
                if self.state == TLCProtocol.NODE_STATUS_READY_TO_CONNECT:  # hasn't processed the version
                    self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK  # set the state
                    self.sendVersion()  # send back the version
                    # self.lcPing.start(10)
                    # self.printPeerStatus()

                else:  # has already processed the version. Now verack
                    self.sendVerAck()
        else:  # incompatible protocol versions
            self.state = TLCProtocol.NODE_STATUS_READY_TO_CONNECT  # reset the protocol status
            self.sendReject()  # send the reject message

    def handleGetAddr(self):
        """
        method for handling the get addr message.
        :return:
        """
        # call the sendAddr method
        self.sendAddr()

    def handleAddr(self, addrMsg):
        """
        gets the addr message and adds the peers to the list
        :return:
        """
        jsonAddrMsg = json.loads(addrMsg)
        addresses = jsonAddrMsg['msgData']['ipAddresses']
        # add the addresses to the peer list of the node
        for address in addresses:
            if (address not in self.factory.peers) and (address != f'{self.hostIp.host}_{self.factory.serverPort}'):
                # if the address does not already exist and isn't the node's ip address
                self.factory.peers.append(address)

    def handleGetBlocks(self, getBlocksMsg: str):
        """
        Method for handling the getBlocks messages
        :param getBlocksMsg: the getBlocks message (string)
        :return:
        """
        jsonGetBlocksMsg = json.loads(getBlocksMsg)
        headerHash = jsonGetBlocksMsg['msgData']['headerHash']  # the header hash of the block message

        # find the block that matches the header hash
        i = 0  # index of the block in the blockchain
        found = False  # flag showing if a block with a specific header hash has been found
        positionFound = -1
        while i < len(self.factory.blockchain.getChain()) and not found:
            curBlock = self.factory.blockchain.getChain()[i]
            if headerHash == curBlock.getBlockHeaderHash():  # if you find the block header hash in the chain
                found = True
                positionFound = i  # keep the index of the block where you found it
            i += 1  # increase the index by one

        # create the list of inventory entries and send it with an inv message
        inventoryEntries = list()  # the list of block header hashes
        invCounter = 0
        invCounterMax = 500  # max of 500 inventory entries
        i = positionFound + 1  # start creating the inventory right after the position the block was found
        while i < invCounterMax and i < len(self.factory.blockchain.getChain()):
            # while not surpassed the max of inv entries and while not at the end of the list of blocks
            # append the header hashes of the blocks in the inventory
            inventoryEntries.append(
                {
                    'type': TLCInvMessage.INV_TYPE_BLOCK,
                    'identifier': self.factory.blockchain.getChain()[i].getBlockHeaderHash()
                }
            )
            i += 1

        invMsg = TLCInvMessage(inventoryEntries)  # create the message
        self.transport.write(invMsg.getMessageAsSendable())  # send the message

    def handleInv(self, invMessage: str):
        """
        Method that handles inventory messages
        :param invMessage: the inventory message
        :return:
        """
        jsonInvMessage = json.loads(invMessage)
        inventoryEntries = jsonInvMessage['msgData']['inventory']  # the inventory entries
        noOfInventoryEntries = jsonInvMessage['msgData']['count']  # the number of inventory entries

        # request some blocks using a getData message
        noOfBlocksToRequest = 128  # number of items to request

        # set the list of items to request
        if noOfInventoryEntries > noOfBlocksToRequest:
            # case that the inv list has more than the blocks the node wants to request
            blockHeadersToRequest = inventoryEntries[0:noOfBlocksToRequest]
        else:
            # case that the inv list has equal or less than the blocks the node wants to request
            blockHeadersToRequest = inventoryEntries[0:noOfInventoryEntries]

        # send the message
        msgGetData = TLCGetDataMessage(blockHeadersToRequest)
        self.transport.write(msgGetData.getMessageAsSendable())

    def handleGetData(self, getDataMessage: str):
        jsonGetDataMessage = json.loads(getDataMessage)
        dataEntries = jsonGetDataMessage['msgData']['inventory']  # the data entries
        dataEntriesCount = jsonGetDataMessage['msgData']['count']  # the number of data entries

        # for each data entry, send the data
        for i in range(0, dataEntriesCount):
            if dataEntries[i]['type'] == TLCGetDataMessage.INV_TYPE_BLOCK:
                # if the entry is block type, send the block via a block message
                # get the block that corresponds to the block header hash and send it
                b = self.factory.blockchain.getBlockByBlockHeaderHash(dataEntries[i]['identifier'])
                # send it via a block message
                # TODO: complete the method
                blockMsg = TLCBlockMessage(b.get)
                print(1)


        print(1)

    def handleVerAck(self):
        # print(f'--> Node {self.nodeId}. Got the VERACK')

        if self.state == TLCProtocol.NODE_STATUS_WAITING_VERACK:

            self.state = TLCProtocol.NODE_STATUS_CONNECTED
            self.sendVerAck()  # sendback verack
            # self.addPeer(self.remoteIp.host, self.remoteIp.port)
            # self.printPeerStatus()
        else:
            print(f'Nodes Connected')

    def handleReject(self, msg: str):
        """
        Method that handles the reject message
        :param msg: the message (str)
        :return:
        """
        # get the json from the message
        msgJsonData = json.loads(msg)

        # check the reason of rejection
        if msgJsonData['msgData']['rejectCode'] == TLCRejectMessage.REJECT_CODE_DIF_VERSION:
            # if the two nodes have two different protocol versions
            print(f'Node {self.nodeId}. Incompatible protocol versions of the two nodes')
            self.state = TLCProtocol.NODE_STATUS_READY_TO_CONNECT  # reset the status of the node
            self.transport.loseConnection()  # close the connection

        # if the reason is different version then print message and set status as ready to connect

    def addPeer(self, peerIp: str, peerPort: int):
        """
        Method for adding a new peer to the list of peer nodes, if it doesn't exist
        :param peerIp: string peer ip
        :param peerPort: int peer port
        :return:
        """
        remoteNodeCon = f"{peerIp}_{str(peerPort)}"
        if remoteNodeCon not in self.factory.peers:
            self.factory.peers.append(remoteNodeCon)


# in the example, Factory is used instead of ClientFactory
class TLCFactory(Factory):
    """
    This is the class that manages connections (protocols). It can be used for persistent configuration storage,
    meaning holding configuration that will be used in various protocols.
    various things
    """
    def __init__(self, serverPort: int, protocolVersion, nodeType: int = NodeTypes.FULL_NODE):
        """
        Constructor method
        :param serverPort: the port of the server when receiving connections (int)
        :param protocolVersion: the version of the protocol for the node
        :param nodeType: the type of the Node. The default is full node
        """
        self.serverPort = serverPort  # keep the port of the application, to sent it to peers
        self.protocolVersion = protocolVersion
        self.nodeType = nodeType
        self.peers = list()  # initialize the list containing the peers

        self.blockchain = None  # the blockchain related to the node that runs the connection factory

    def startFactory(self):
        self.nodeId = generateNodeId()  # generate a node id
        # self.peers = dict()  # initialize the dictionary containing the peers

        # print('Start factory for the node ' + self.nodeId)
        print(f' Node <<{self.nodeId}>> online.')

    def buildProtocol(self, addr):
        # return TLCProtocol(self)
        # protocol = TLCProtocol(self, 1)
        # self.protocols.append(protocol)
        # return protocol
        return TLCProtocol(self)