"""
Includes various tests for the "0.1.1 connecting to peers" feature
"""

import unittest
from twisted.internet import reactor

from src.p2p_network.parameters import Parameters
from src.p2p_network.tlc_network import TLCNode
from src.utilities.tlc_exceptions import TLCNetworkException


class TestConnectingToPeers(unittest.TestCase):

    def setUp(self):
        self.reactorDelay = 1  # the delay used for the reactor

        # initialize and start the nodes
        self.nodeV1Port8010 = TLCNode(reactor, port=8010, protocolVersion=1)
        self.nodeV1Port8013 = TLCNode(reactor, port=8013, protocolVersion=1)
        self.nodeV1Port8014 = TLCNode(reactor, port=8014, protocolVersion=1)
        self.nodeV1Port8015 = TLCNode(reactor, port=8015, protocolVersion=1)
        self.nodeV1Port8016 = TLCNode(reactor, port=8016, protocolVersion=1)

        self.nodeV2Port8012 = TLCNode(reactor, port=8012, protocolVersion=2)
        self.nodeV2Port8011 = TLCNode(reactor, port=8011, protocolVersion=2)

        self.nodeV1Port8010.startNode()
        self.nodeV2Port8012.startNode()
        self.nodeV1Port8013.startNode()
        self.nodeV2Port8011.startNode()

        self.nodeV1Port8014.startNode()
        self.nodeV1Port8015.startNode()
        self.nodeV1Port8016.startNode()

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
        Testing the version communication. Scenarios:
        a) low version node tries to connect to high version. Peer lists not updated.
        b) high version node tries to connect to low version. Peer lists not updated.
        c) same versions try to connect. Peer lists updated.
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

    def test_getNodePeers(self):

        """
        test that the node gets the peers of the node it connects to.
        No duplicate entry should exist in the peer list
        :return:
        """
        # the node on 8013 connects to the nodes on 8014 and 8015
        self.nodeV1Port8013.connectTo(self.nodeV1Port8014)
        self.nodeV1Port8013.connectTo(self.nodeV1Port8015)

        # the node on 8010 connects to the node on 8013 and 8016
        self.nodeV1Port8010.connectTo(self.nodeV1Port8013)
        self.nodeV1Port8010.connectTo(self.nodeV1Port8016)

        # the node on 8010 asks for the peers of 8013 (8014)
        self.nodeV1Port8010.getNodePeers(self.nodeV1Port8013)

        # assert that the list of peers of nodeV1 now has 8013, 8014, 8015, 8016
        # also assert that the node itself is not included in the peer list
        def peerAssertion():
            assert f'{self.nodeV1Port8013._TLCNode__address}_{self.nodeV1Port8013._TLCNode__port}' \
                   in self.nodeV1Port8010.getPeers()
            assert f'{self.nodeV1Port8014._TLCNode__address}_{self.nodeV1Port8014._TLCNode__port}' \
                   in self.nodeV1Port8010.getPeers()
            assert f'{self.nodeV1Port8015._TLCNode__address}_{self.nodeV1Port8015._TLCNode__port}' \
                   in self.nodeV1Port8010.getPeers()
            assert f'{self.nodeV1Port8016._TLCNode__address}_{self.nodeV1Port8016._TLCNode__port}' \
                   in self.nodeV1Port8010.getPeers()
            assert f'{self.nodeV1Port8010._TLCNode__address}_{self.nodeV1Port8010._TLCNode__port}' \
                   not in self.nodeV1Port8010.getPeers()

        reactor.callLater(self.reactorDelay * 2, peerAssertion)  # call the assertions when possible

        reactor.callLater(self.reactorDelay * 2, self.nodeV1Port8010.printPeers)

        reactor.callLater(self.reactorDelay * 3, reactor.stop)  # after some time, stop the reactor
        reactor.run()

    def test_checkInactivity(self):
        """
        Method that tests the functionality related to the inactivity between two nodes
        and the closing of the connection. Scenarios:
        a) Connect a node to two more nodes. Check that the connection to the first node is open before the time limit
        and closed after the time limit.
        For now, testing has taken place by observing TCP Connections Status in TCPView Windows Tool.
        In the future, a better implementation of the network code (eg using ClientFactory) will lead to
        improved handling of network operations.
        :return:
        """

        # Scenario (a)
        self.nodeV1Port8010.connectTo(self.nodeV1Port8014)

        self.nodeV1Port8010.connectTo(self.nodeV1Port8013)

        def makeAssertionsOpen():
            p1 = self.nodeV1Port8010.getLastUsedProtocol()
            print(1)  # this connection is still open. Should have a peer.
        # call the assertions before the connection is closed
        reactor.callLater(Parameters.CLOSE_CONNECTION_TIME_LIMIT - 2, makeAssertionsOpen)

        def makeAssertionsClosed():
            p1 = self.nodeV1Port8010.getLastUsedProtocol()
            print(1)  # the peer of this con should be none. Connection closed.
        # call the assertions after the connection is closed
        reactor.callLater(Parameters.CLOSE_CONNECTION_TIME_LIMIT + 20, makeAssertionsClosed)

        # run the reactor and stop after the connection is closed and assertions are completed

        reactor.callLater(Parameters.CLOSE_CONNECTION_TIME_LIMIT + 22, reactor.stop)
        reactor.run()





