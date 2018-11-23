import json
from time import time
from uuid import uuid4

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall

from src.p2p_network.parameters import Parameters
from src.p2p_network.tlc_message import TLCMessage, TLCVersionMessage

generateNodeId = lambda: str(uuid4())  # function that generates the node id

# DEFAULT PARAMETERS
MAINNET_DEFAULT_PORT = 8010
MAINNET_MAX_NBITS = 0x1d00ffff  # big endian order. Sent in little endian order


def initConnection(p: Protocol):
    """
    Function that initializes the connection for a specific protocol.
    The first thing sent is the version of the node

    :param p:  Protocol instance
    :return:
    """
    p.sendVersion()  # send the version of the node

class TLCNode:
    """
    class for managing the node data and operations
    """
    DEFAULT_PORT = MAINNET_DEFAULT_PORT  # the default port for running tlc nodes on a computer

    def __init__(self, address: str, reactor: reactor, port: int = DEFAULT_PORT):
        """

        :param address: the ip address of the node
        :param port: the tcp port of the node
        :param reactor: the reactor object
        """
        self.__reactor = reactor
        self.__address = address
        self.__port = port
        self.__serverEndPoint = self.__createServerEndPoint()  # create the server endpoint
        # self.__clientEndPoint = self.__createClientEndPoint()  # create the client endpoint
        # self.__clientEndPoint = None
        self.__tlcFactory = TLCFactory()  # the TLC Factory for the node

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
        starts the node
        :return:
        """
        self.__serverEndPoint.listen(self.__tlcFactory)

    def connectTo(self, node):
        """
        used to connect to another peer node
        :param node: an other TLC Node
        :return:
        """
        # create a client endpoint to connect to the target address:port
        point = TCP4ClientEndpoint(reactor, node.__address, node.__port)
        d = connectProtocol(point, TLCProtocol(self.getTLCFactory(), 1))
        d.addCallback(initConnection)


class TLCProtocol(Protocol):

    VERSION = Parameters.PROTOCOL_VERSION  # set the version of the protocol as the version of the message

    def __init__(self, factory, peerType):
        self.factory = factory
        self.state = 'HELLO'
        self.nodeId = self.factory.nodeId  # keep the node id
        self.peerType = peerType
        self.remoteNodeId = None

        self.lcPing = LoopingCall(self.sendPing)  # Calls the sendPing method repeatedly to ping nodes
        self.lastPing = None

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
            msgType = json.loads(line)['msgType']  # get the msg type

            # depending on the message received, do something
            if self.state == 'HELLO' or msgType == TLCMessage.CTRLMSGTYPE_VERSION:  # if the node is in hello mode
                self.handleVersion(line)
                self.state = 'READY'
            elif msgType == 'ping':  # if the node has received a ping message
                self.handlePing()
            elif msgType == 'pong':  # if the node has received a pong message
                self.handlePong()
            elif msgType == 'addr':
                self.handleAddr(line)

    def sendVersion(self):
        """
        Method for sending the hello
        :return:
        """
        # create the version message, in a sendable form
        versionMsg = TLCVersionMessage().getMessageAsSendable()

        self.state = 'READY'  # after I send the HELLO, I declare I'm ready to talk
        self.transport.write(versionMsg)

    def sendPing(self):
        ping = json.dumps({'msgType': 'ping'}) + '\n'
        print(f'Ping sent \t\t {self.nodeId} --> {self.remoteNodeId}')
        self.transport.write(ping.encode('utf8'))

    def sendPong(self):
        pong = json.dumps({'msgType': 'pong'}) + '\n'
        self.transport.write(pong.encode('utf8'))

    def sendAddr(self, mine=False):
        """
        Send the list of addresses of my peers, or my address
        :param mine: if True, I send my address, else I send the addresses of my peers
        :return:
        """
        now = time()  # used to check the peer last ping (if they are still alive)

        if mine:  # case I want to send my address
            peers = [
                [self.hostIp.host, self.hostIp.port, self.nodeId]
            ]
        else:  # case I want to send my peers addresses
            """
            peers = [
                (peer.remoteIp, peer.remoteNodeId)
                for peer in self.factory.peers
                if peer.peerType == 1 and peer.lastPing > now-240
            ]
            """
            # TODO: add functionality so the node can send to the other it's peer node info
            peers = list()
            for peer in self.factory.peers.values():
                remoteHostIp = peer.remoteIp.host
                remoteHostPort = peer.remoteIp.port
                peers.append((remoteHostIp, remoteHostPort, peer.remoteNodeId))

        addr = json.dumps({'msgType': 'addr', 'peers': peers}) + '\n'
        self.transport.write(addr.encode('utf8'))  # send the addr

    def handlePing(self):
        self.sendPong()

    def handlePong(self):
        print(f'Pong received \t {self.nodeId} <-- {self.remoteNodeId}')
        self.lastPing = time()  # keep the timestamp

    def handleAddr(self, addrData):
        # get the address
        addr = json.loads(addrData)
        for peer in addr['peers']:
            if peer[2] not in self.factory.peers:  # if the peer node id doesn't exist in the list
                # add to the list and connect to it
                host = peer[0]
                port = peer[1]
                point = TCP4ClientEndpoint(reactor, host, int(port))
                print ("Connect to protocol...")
                d = connectProtocol(point, TLCProtocol(self.factory, 2))
                # TODO: fix the problem with the loop. It is caused because the gotProtocol is
                #   called and the conversation starts from the beginning iteratively
                # d.addCallback(gotProtocol)

    def printPeerStatus(self):
        """
        Method that prints the peer status for a node
        :return:
        """
        # print('*** Current number of peers for node ' + self.nodeId + ' is ' + str(len(self.factory.peers)))
        print("----------------------------------------------------------")
        print("List of peers for node %s : " % self.nodeId)
        i = 0
        for peer in self.factory.peers:
            print(' - ' + peer)

    def handleVersion(self, versionMsg):
        """
        method that handles the line that is sent to the node (json string)
        :param versionMessage: json string
        :return:
        """
        try:
            versionMessage = json.loads(versionMsg)  # load the json from the string
            self.remoteNodeId = versionMessage.get('nodeId')  # get the remote node id
            if self.remoteNodeId == self.nodeId:  # case node connected to itself
                print('Connected to myself')
                self.transport.loseConnection()  # close the connection
            else:  # add the remote node id to the dictionary of peers
                self.factory.peers[self.remoteNodeId] = self
                self.lcPing.start(10)
                # inform the new peer about us
                self.sendAddr(True)
                # ask for more peers
                # self.sendAddr()
                # print('-> Peer node ' + self.remoteNodeId + ' added to node ' + self.nodeId)
                self.printPeerStatus()
        except:
            print('Communication problem')


# in the example, Factory is used instead of ClientFactory
class TLCFactory(Factory):
    def startFactory(self):
        self.nodeId = generateNodeId()  # generate a node id
        self.peers = dict()  # initialize the dictionary containing the peers
        # print('Start factory for the node ' + self.nodeId)
        print(f' Node <<{self.nodeId}>> online.')

    def buildProtocol(self, addr):
        print('Connected.')
        # return TLCProtocol(self)
        return TLCProtocol(self, 1)