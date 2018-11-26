import json
from time import time
from uuid import uuid4
import socket
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall

from src.p2p_network.parameters import Parameters
from src.p2p_network.tlc_message import TLCMessage, TLCVersionMessage, TLCVerAckMessage, TLCGetAddrMessage
from src.utilities.tlc_exceptions import TLCNetworkException

generateNodeId = lambda: str(uuid4())  # function that generates the node id

# DEFAULT PARAMETERS
MAINNET_DEFAULT_PORT = 8010
MAINNET_MAX_NBITS = 0x1d00ffff  # big endian order. Sent in little endian order

"""
def initConnection(p: Protocol):
    
    # Function that initializes the connection for a specific protocol.
    # The first thing sent is the version of the node

    :param p:  Protocol instance
    :return:
    
    p.sendVersion()  # send the version of the node
"""


class TLCNode:
    """
    class for managing the node data and operations
    """
    DEFAULT_PORT = MAINNET_DEFAULT_PORT  # the default port for running tlc nodes on a computer

    def __init__(self, reactor: reactor, address: str = 'localhost', port: int = DEFAULT_PORT):
        """

        :param address: the ip address of the node - default is localhost
        :param port: the tcp port of the node - default is the default port defined in the application parameters
        :param reactor: the reactor object
        """
        self.__reactor = reactor
        self.__address = address
        self.__port = port
        self.__serverEndPoint = self.__createServerEndPoint()  # create the server endpoint
        # self.__clientEndPoint = self.__createClientEndPoint()  # create the client endpoint
        # self.__clientEndPoint = None
        self.__tlcFactory = TLCFactory(port)  # the TLC Factory for the node
        # self.d = None  # the deferred object

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

    def askPeerForAddresses(self, p):
        """
        ask for the addresses
        :return:
        """
        p.sendGetAddr()
        return p

    def connectTo(self, node):
        """
        used to connect to another peer node
        :param node: an other TLC Node
        :return:
        """
        # create a client endpoint to connect to the target address:port
        point = TCP4ClientEndpoint(reactor, node.__address, node.__port)

        d = connectProtocol(point, TLCProtocol(self.getTLCFactory(), 1))
        d.addCallback(self.initConnection)

    def getNodePeers(self, node):
        """
        Asks a node to give him his peers (nodes on his network)
        :param node: the node(TLCNode objects), whose peers we want
        :return:
        """
        # create a client endpoint to connect to the target address:port
        point = TCP4ClientEndpoint(reactor, node.__address, node.__port)
        # make the connection
        d = connectProtocol(point, TLCProtocol(self.getTLCFactory(), 1))
        # the parameter of the following callback defines the type of request
        d.addCallback(self.initSendRequest, TLCMessage.CTRLMSGTYPE_GETADDR)

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


class TLCProtocol(Protocol):

    VERSION = Parameters.PROTOCOL_VERSION  # set the version of the protocol as the version of the message

    # some node statuses
    NODE_STATUS_READY_TO_CONNECT = 1  # before sending the version message
    NODE_STATUS_WAITING_VERACK = 2
    NODE_STATUS_CONNECTED = 3  # after receiving the verack message

    def __init__(self, factory, peerType):
        self.factory = factory
        self.state = TLCProtocol.NODE_STATUS_READY_TO_CONNECT
        self.nodeId = self.factory.nodeId  # keep the node id
        self.peerType = peerType
        self.remoteNodeId = None

        self.lcPing = LoopingCall(self.sendPing)  # Calls the sendPing method repeatedly to ping nodes
        self.lastPing = None

        self.typeOfRequest = None  # the type of request.

    def connectionMade(self):
        self.remoteIp = self.transport.getPeer()
        self.hostIp = self.transport.getHost()
        print(f"Connection from ip: {str(self.remoteIp)} to {self.hostIp}")

    def connectionLost(self, reason):
        # remove the node that disconnected from the peer dictionary, if it exists in the peer list
        if self.remoteNodeId in self.factory.peers:
            self.factory.peers.pop(self.remoteNodeId)
            self.lcPing.stop()
        print(self.nodeId + " disconnected")

    def dataReceived(self, data):
        # for each line of data
        for line in data.splitlines():
            line = line.strip()
            msgType = json.loads(line)['msgHeader']['commandName']  # get the msg type

            if self.state != TLCProtocol.NODE_STATUS_CONNECTED:  # if the connection has not been made
                # depending on the message received, do something
                if msgType == TLCMessage.CTRLMSGTYPE_VERSION:  # if the nodes are exchanging versions
                    self.handleVersion(line)
                elif msgType == TLCMessage.CTRLMSGTYPE_VERACK:
                    self.handleVerAck()
                elif msgType == TLCMessage.CTRLMSGTYPE_GETADDR:
                    self.handleGetAddr()
            else:  # ready to handle requests - put the request handling here
                if msgType == TLCMessage.CTRLMSGTYPE_VERACK:
                    print(f"Node {self.nodeId}. Got the VERACK from the node I connected to. Ready to handle requests")
                # self.handleVerAck()  # get the last verack
                print('Ready to make some requests...')


    def sendVersion(self):
        """
        Method for sending the version control message
        :return:
        """
        # create the version message, in a sendable form
        versionMsg = TLCVersionMessage(self.hostIp.host, self.factory.serverPort).getMessageAsSendable()
        self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK
        print(f'--> Node {self.nodeId}. Sent my VERSION')
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
        versionMsg = TLCVersionMessage(self.hostIp.host, self.factory.serverPort).getMessageAsSendable()
        self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK
        print(f'--> Node {self.nodeId}. Sent my VERSION')
        self.transport.write(versionMsg)



    def sendVerAck(self):
        """
        Method for sending the verack (response to version) message
        :return:
        """
        verAckMsg = TLCVerAckMessage().getMessageAsSendable()
        print(f'--> Node {self.nodeId}. Sent my VERACK')
        self.state = TLCProtocol.NODE_STATUS_CONNECTED
        self.transport.write(verAckMsg)

    def sendGetAddr(self):
        """
        Sending a getAddr message to get the list of network peers of the node
        :return:
        """
        print('sendGetAddr called.')
        getAddrMessage = TLCGetAddrMessage().getMessageAsSendable()
        print(f'--> Node {self.nodeId}. Sent my GETADDR')
        # self.state = TLCProtocol.NODE_STATUS_CONNECTED
        self.transport.write(getAddrMessage)

    def sendPing(self):
        ping = json.dumps({'msgType': 'ping'}) + '\n'
        print(f'Ping sent \t\t {self.nodeId} --> {self.remoteNodeId}')
        self.transport.write(ping.encode('utf8'))

    def sendPong(self):
        pong = json.dumps({'msgType': 'pong'}) + '\n'
        self.transport.write(pong.encode('utf8'))

    def handlePing(self):
        self.sendPong()

    def handlePong(self):
        print(f'Pong received \t {self.nodeId} <-- {self.remoteNodeId}')
        self.lastPing = time()  # keep the timestamp

    def handleVersion(self, versionMsg):
        """
        method that handles the line that is sent to the node (json string)
        :param versionMessage: json string
        :return:
        """
        print(f'--> Node {self.nodeId}. Got the VERSION.')

        # create the list of peers for the node
        try:
            versionMessage = json.loads(versionMsg)  # load the json from the string
            # get the ip and port of the remote node
            remoteNodeIp = json.loads(versionMsg)['msgData']['ipAddress']
            remoteNodePort = json.loads(versionMsg)['msgData']['port']
            # self.remoteNodeId = versionMessage.get('nodeId')  # get the remote node id
            if self.hostIp.host == remoteNodeIp and self.hostIp.port == remoteNodePort:
                print('Connected to myself')
                self.transport.loseConnection()  # close the connection
            else:
                # add the remote node id to the dictionary of peers, if not already there
                self.addPeer(remoteNodeIp, remoteNodePort)
        except:
            print('Communication problem')

        # print the list of the peers
        # self.printPeerStatus()

        # decide how to answer
        if self.state == TLCProtocol.NODE_STATUS_READY_TO_CONNECT:
            # send back a verack control message
            # self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK
            self.state = TLCProtocol.NODE_STATUS_WAITING_VERACK
            self.sendVersion()
            # self.lcPing.start(10)
            # self.printPeerStatus()

        else:  # has already processed the version. Now verack
            self.sendVerAck()

    def handleGetAddr(self):
        """
        method for handling the get addr message
        :return:
        """


    def handleVerAck(self):
        print(f'--> Node {self.nodeId}. Got the VERACK')

        if self.state == TLCProtocol.NODE_STATUS_WAITING_VERACK:

            self.state = TLCProtocol.NODE_STATUS_CONNECTED
            self.sendVerAck()  # sendback verack
            # self.addPeer(self.remoteIp.host, self.remoteIp.port)
            # self.printPeerStatus()
        else:
            print(f'Nodes Connected')

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
    def __init__(self, serverPort: int):
        """
        Constructor method
        :param serverPort: the port of the server when receiving connections (int)
        """
        self.serverPort = serverPort  # keep the port of the application, to sent it to peers
        # self.protocols = list()  # list of the protocols-connections

    def startFactory(self):
        self.nodeId = generateNodeId()  # generate a node id
        # self.peers = dict()  # initialize the dictionary containing the peers
        self.peers = list()  # initialize the list containing the peers
        # print('Start factory for the node ' + self.nodeId)
        print(f' Node <<{self.nodeId}>> online.')

    def buildProtocol(self, addr):
        # return TLCProtocol(self)
        # protocol = TLCProtocol(self, 1)
        # self.protocols.append(protocol)
        # return protocol
        return TLCProtocol(self, 1)