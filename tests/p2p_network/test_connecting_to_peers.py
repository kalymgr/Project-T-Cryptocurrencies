"""
Includes various tests for the "1.1.1 connecting to peers" feature
"""

import unittest
from twisted.internet import reactor
from src.p2p_network.tlc_network import TLCNode


class TestConnectingToPeers(unittest.TestCase):
    def test_start_node(self):
        """
        Testing the creation of a new node
        :return:
        """

        # case of creation of node using default port and localhost host
        node = TLCNode(reactor)
        node.startNode()
        # case of creation using a free port and localhost host
        node = TLCNode(reactor, port=50000)
        node.startNode()
        # case of creation using a not-free port and localhost host
        node3 = TLCNode(reactor, port=6942)
        self.assertRaises(Exception, node3.startNode)
        # node.startNode()
        # case of creation using a free port and the loopback ip address
        # case of creation using a free port and the wrong ip address
        # case of creation using a not-free port and wrong ip address

        reactor.callLater(2, reactor.stop)  # after two seconds, stop the reactor
        reactor.run()  # run the reactor

