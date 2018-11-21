from uuid import uuid4

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from src.p2p_network.simple_p2p_network import TLCFactory, TLCProtocol


def gotProtocol(p):
    # function for trying to talk to the protocol
    # print('gotProtocol called')
    p.sendHello()


class TLCNode:
    """
    class for managing the node data and operations
    """
    def __init__(self, address: str, port: int, reactor: reactor):
        """

        :param address: the ip address of the node
        :param port: the tcp port of the node
        :param reactor: the reactor object
        """
        self.__reactor = reactor
        self.__address = address
        self.__port = port
        self.__serverEndPoint = self.__createServerEndPoint()  # create the server endpoint
        self.__clientEndPoint = self.__createClientEndPoint()  # create the client endpoint
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

    def printPeers(self):
        """
        method that prints the peers of the node on the screen
        :return:
        """
        print('Node id: ' + self.getNodeId() + '\n')
        for peer in self.getPeers():
            print(peer + '\n')

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
        d = connectProtocol(self.__clientEndPoint, TLCProtocol(node.getTLCFactory()))
        d.addCallback(gotProtocol)


firstNode = TLCNode('localhost', 8010, reactor)
secondNode = TLCNode('localhost', 8011, reactor)
thirdNode = TLCNode('localhost', 8012, reactor)

firstNode.startNode()
secondNode.startNode()
thirdNode.startNode()

firstNode.connectTo(secondNode)
secondNode.connectTo(thirdNode)
thirdNode.connectTo(secondNode)

# TODO: fix printPeers method. Doesn't work
firstNode.printPeers()
secondNode.printPeers()
thirdNode.printPeers()

"""
# this is the end point installed on my pc
myEndpoint = TCP4ServerEndpoint(reactor, 8007)
tlcFactory = TLCFactory()
myEndpoint.listen(tlcFactory)

# let's create one more endpoint which would belong to another instance of the p2p application
secondEndpoint = TCP4ServerEndpoint(reactor, 8008)
tlcFactory2 = TLCFactory()
secondEndpoint.listen(tlcFactory2)





bootstrapNodes = [
    'localhost:8007', 'localhost:8008'
]
# let's make a connection between both of the endpoints
for node in bootstrapNodes:

    # get the ip address and port
    host, port = node.split(":")

    # create the client endpoint
    point = TCP4ClientEndpoint(reactor, host, int(port))

    # connect to the first endpoint
    d = connectProtocol(point, TLCProtocol(tlcFactory))
    d.addCallback(gotProtocol)

    # connect to the second endpoint
    d = connectProtocol(point, TLCProtocol(tlcFactory2))
    d.addCallback(gotProtocol)

"""

# run the reactor
reactor.run()

