"""
Includes various tests for the "1.1.1 connecting to peers" feature
"""

import unittest
from twisted.internet import reactor
from src.p2p_network.tlc_network import TLCNode
from src.utilities.tlc_exceptions import TLCNetworkException


class TestConnectingToPeers(unittest.TestCase):

    def setUp(self):
        self.reactorDelay = 1  # the delay used for the reactor

        self.nodeV1Port8010 = TLCNode(reactor, port=8010, protocolVersion=1)
        self.nodeV2Port8012 = TLCNode(reactor, port=8012, protocolVersion=2)
        self.nodeV1Port8013 = TLCNode(reactor, port=8013, protocolVersion=1)
        self.nodeV2Port8011 = TLCNode(reactor, port=8011, protocolVersion=2)

        self.nodeV1Port8010.startNode()
        self.nodeV2Port8012.startNode()
        self.nodeV1Port8013.startNode()
        self.nodeV2Port8011.startNode()


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

    def test_version(self):
        """
        testing the version communication
        :return:
        """
        # First case
        # try to connect to a node with higher version. Reject message should be sent and the nodes should be
        # disconnected. Check that the node hasn't been added to the peers.
        self.nodeV1Port8010.connectTo(self.nodeV2Port8011)

        # assert that neither node has added the other one as a peer
        def firstCaseAssertNotIn():
            assert f'{self.nodeV1Port8010._TLCNode__address}_{self.nodeV1Port8010._TLCNode__port}' \
                   not in self.nodeV2Port8011.getPeers()
            assert f'{self.nodeV2Port8011._TLCNode__address}_{self.nodeV2Port8011._TLCNode__port}' \
                   not in self.nodeV1Port8010.getPeers()

        reactor.callLater(self.reactorDelay * 2, firstCaseAssertNotIn)  # call the assertions when possible

        # Second case
        # Try to connect a higher version to a lower version
        self.nodeV2Port8011.connectTo(self.nodeV1Port8010)
        # assert that neither node has added the other one as a peer

        def secondCaseAssertNotIn():
            firstCaseAssertNotIn()
        reactor.callLater(self.reactorDelay * 2, secondCaseAssertNotIn)  # call the assertions when possible

        # Third case
        # Connect two nodes with same protocol versions. Each one should add the other as a peer.
        self.nodeV1Port8010.connectTo(self.nodeV1Port8013)

        # assert that each one exists in the other's peer nodes
        def thirdCaseAssertNotIn():
            assert f'{self.nodeV1Port8010._TLCNode__address}_{self.nodeV1Port8010._TLCNode__port}' \
                   in self.nodeV1Port8013.getPeers()
            assert f'{self.nodeV1Port8013._TLCNode__address}_{self.nodeV1Port8013._TLCNode__port}' \
                   in self.nodeV1Port8010.getPeers()

        reactor.callLater(self.reactorDelay * 2, thirdCaseAssertNotIn)  # call the assertions when possible


        reactor.callLater(self.reactorDelay * 3, reactor.stop)  # after some time, stop the reactor
        reactor.run()  # run the reactor





