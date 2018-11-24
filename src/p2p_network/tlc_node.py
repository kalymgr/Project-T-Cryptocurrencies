"""
Check the tutorial
https://benediktkr.github.io/dev/2016/02/04/p2p-with-twisted.html
"""

from twisted.internet import reactor
from src.p2p_network.tlc_network import TLCNode

# create and start my node
myNode = TLCNode('localhost', reactor)
myNode.startNode()

# create and start three more nodes
secondNode = TLCNode('localhost', reactor, 8011)
secondNode.startNode()
thirdNode = TLCNode('localhost', reactor, 8012)
thirdNode.startNode()
# fourthNode = TLCNode('localhost', reactor, 8013)
# fourthNode.startNode()

# connect my node to the other two nodes
# myNode.connectTo(secondNode)
# secondNode.connectTo(thirdNode)
# secondNode.connectTo(fourthNode)

# call some other functions, with a little delay
delay = 3

# get the addresses of the peer node
reactor.callLater(delay, myNode.getAddressesFromNode, secondNode)

# print the peers

reactor.callLater(delay * 2, myNode.printPeers)
reactor.callLater(delay * 2, secondNode.printPeers)


# run the reactor
reactor.run()
