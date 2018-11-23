"""
Check the tutorial
https://benediktkr.github.io/dev/2016/02/04/p2p-with-twisted.html
"""

from twisted.internet import reactor
from src.p2p_network.tlc_network import TLCNode

# create and start my node
myNode = TLCNode('localhost', reactor)
myNode.startNode()

# create and start two more nodes
secondNode = TLCNode('localhost', reactor, 8011)
secondNode.startNode()
# thirdNode = TLCNode('localhost', reactor, 8012)
# thirdNode.startNode()

# connect my node to the other two nodes
myNode.connectTo(secondNode)
# myNode.connectTo(thirdNode)

# run the reactor
reactor.run()
