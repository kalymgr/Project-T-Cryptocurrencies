"""
This file contains the code for running the seed nodes.
"""

from twisted.internet import reactor

from src.p2p_network.parameters import NodeTypes
from src.p2p_network.tlc_network import TLCNode

# initialize two seed nodes running on ports 8018 and 8019 and ask them for some node addresses
seedNode1 = TLCNode(reactor, nodeType=NodeTypes.SEED_NODE, port=8018)
seedNode1.addNodePeersList(['127.0.0.1_8015', '127.0.0.1_8016'])  # set the list for the first seed
seedNode2 = TLCNode(reactor, nodeType=NodeTypes.SEED_NODE, port=8019)
seedNode2.addNodePeersList(['127.0.0.1_8017', '127.0.0.1_8018'])  # set the list for the second seed
seedNode1.startNode()
seedNode2.startNode()

# run the reactor
reactor.run()
