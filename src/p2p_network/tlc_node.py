"""
Check the tutorial
https://benediktkr.github.io/dev/2016/02/04/p2p-with-twisted.html
"""

from twisted.internet import reactor
from src.p2p_network.tlc_network import TLCNode

# create and start my node
myNode = TLCNode(reactor, 'localhost', 8010, 1)
myNode.startNode()

# one more node
secondNode = TLCNode(reactor, 'localhost', 8011, 1)
secondNode.startNode()

# connect to the node
myNode.connectTo(secondNode)

delay = 3


# run the reactor
reactor.run()
