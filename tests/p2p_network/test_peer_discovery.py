"""
Includes various tests for the "0.1.2 peer discovery" feature
"""

import unittest
from twisted.internet import reactor

from src.p2p_network.parameters import Parameters, NodeTypes
from src.p2p_network.tlc_network import TLCNode
from src.utilities.tlc_exceptions import TLCNetworkException


class TestConnectingToPeers(unittest.TestCase):
    def test_nodeTypeProperlySet(self):
        """
        Method that tests that the node type is properly set in various cases. Scenarios:
        a) create a seed node and check that it's type is properly set
        b) create a full node and check that it's property is properly set

        :return:
        """
        # Scenario a
        seedNode = TLCNode(reactor, nodeType=NodeTypes.SEED_NODE)
        assert seedNode.getTLCFactory().nodeType == NodeTypes.SEED_NODE

        # Scenario b
        fullNode = TLCNode(reactor)
        assert fullNode.getTLCFactory().nodeType == NodeTypes.FULL_NODE

    def test_addNodePeersList_method(self):
        """
        Testing the addNodePeersList method. Scenarios:
        a) create a node with an initial peer list. Then add one more list and check that the final list is ok. The
        final list shouldn't have duplicates.
        :return:
        """
        node = TLCNode(reactor)
        # set the initial list of peers
        initialList = ['127.0.0.1_8015', '127.0.0.1_8016']
        node._TLCNode__tlcFactory.peers = initialList
        # add another list of peers
        list2 = ['127.0.0.1_8017', '127.0.0.1_8016']
        node.addNodePeersList(list2)

        assert len(node.getPeers()) == 3





