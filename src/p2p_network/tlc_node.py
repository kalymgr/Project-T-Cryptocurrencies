"""
Check the tutorial
https://benediktkr.github.io/dev/2016/02/04/p2p-with-twisted.html
"""

from uuid import uuid4
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from src.p2p_network.tlc_network import TLCFactory, TLCProtocol


def gotProtocol(p):
    # function for trying to talk to the protocol
    # print('gotProtocol called')
    p.sendHello()


class TLCNode:
    """
    class for managing the node data and operations
    """
    DEFAULT_PORT = 8010  # the default port for running tlc nodes on a computer

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


myNode = TLCNode('localhost', reactor)
myNode.startNode()

secondNode = TLCNode('localhost', reactor, 8011)
secondNode.startNode()


# myNode.connectTo(secondNode)

"""
# setup the list of node data (ip addresses and ports)
# Let's assume the first is our node
nodeAddresses = [
    {'nodeAddress': 'localhost', 'port': 8010},
    {'nodeAddress': 'localhost', 'port': 8011},
    # {'nodeAddress': 'localhost', 'port': 8012},
    # {'nodeAddress': 'localhost', 'port': 8013}
]


# initialize & start the nodes & put them in a list
nodeList = list()
for nodeAddress in nodeAddresses:
    node = TLCNode(nodeAddress['nodeAddress'], nodeAddress['port'], reactor)
    node.startNode()
    nodeList.append(node)

# connect the first node to all the other nodes
for i in range(1, len(nodeList)):
    nodeList[0].connectTo(nodeList[i])
    
"""


# run the reactor
reactor.run()
