"""
This file contains the code for running the local full node.

Check the tutorial
https://benediktkr.github.io/dev/2016/02/04/p2p-with-twisted.html
"""

from twisted.internet import reactor

from src.p2p_network.parameters import NodeTypes
from src.p2p_network.tlc_network import TLCNode


def startLocalNode() -> TLCNode:
    """
    Function that starts the local full node, and connects the local node to the seeds, to get their lists of
    addresses.
    :return: myNode (TLCNode object)
    """
    localNode = TLCNode(reactor, 'localhost', 8010, 1)
    localNode.startNode()

    # create the TLCNode objects for the two seeds
    seedNode1 = TLCNode(reactor, nodeType=NodeTypes.SEED_NODE, port=8018)
    seedNode2 = TLCNode(reactor, nodeType=NodeTypes.SEED_NODE, port=8019)

    # get the list of nodes from the two seeds
    localNode.getNodePeers(seedNode1)
    localNode.getNodePeers(seedNode2)

    return localNode


# start my full node
localNode = startLocalNode()

# make an IBD (Initial Block Download)
localNode.initialBlockDownload()

# start a second node
secondNode = TLCNode(reactor, 'localhost', 8011, 1)
secondNode.startNode()

# connect to the node
localNode.connectTo(secondNode)

delay = 3

# print the peers of my node
reactor.callLater(delay, localNode.printPeers)
# run the reactor
reactor.run()
