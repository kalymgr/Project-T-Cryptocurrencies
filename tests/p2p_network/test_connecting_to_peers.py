"""
Includes various tests for the "1.1.1 connecting to peers" feature
"""

import unittest
from twisted.internet import reactor
from src.p2p_network.tlc_network import TLCNode
from src.utilities.tlc_exceptions import TLCNetworkException


class TestConnectingToPeers(unittest.TestCase):
    def test_start_node(self):
        """
        Testing the creation of a new node. Scenarios:
        a) free port - localhost
        b) not free port - localhost. Should raise an exception
        c) free port - loopback address
        :return:
        """

        # case of creation of node using default port and localhost host
        node = TLCNode(reactor)
        node.startNode()
        # case of creation using a free port and localhost host
        node = TLCNode(reactor, port=50000)
        node.startNode()

        # case of creation using a not-free port and localhost host - it should raise an error
        node3 = TLCNode(reactor, port=6942)
        self.assertRaises(TLCNetworkException, node3.startNode)  # it should raise an error

        # case of creation using a free port and the loopback ip address
        node4 = TLCNode(reactor, '127.0.0.1', 50001)
        node4.startNode()

        reactor.callLater(2, reactor.stop)  # after two seconds, stop the reactor
        reactor.run()  # run the reactor

    def test_connectTo(self):
        """
        testing the connection between two nodes. Scenarios:
        a) The connection can be made
        b) The connection cannot be made because the second node hasn't started
        c) The connection cannot be completed because of a problem with the version of the two nodes
        :return:
        """

        # a) The connection can be made
        node1 = TLCNode(reactor)
        node1.startNode()
        node2 = TLCNode(reactor, port=8011)
        node2.startNode()
        node1.connectTo(node2)  # make the connection

        node3 = TLCNode(reactor, port=8012)
        node3.startNode()
        node1.connectTo(node3)

        reactor.callLater(2, reactor.stop)  # after two seconds, stop the reactor
        reactor.run()  # run the reactor

        print(1)

