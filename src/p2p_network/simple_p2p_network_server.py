"""
simple app to understand how to create the p2p network
one can connect to the tcp server via the cmd prompt, using the command 'telnet 127.0.0.1 8007'
https://benediktkr.github.io/dev/2016/02/04/p2p-with-twisted.html
"""
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

# 8007 is the port you want to run under. Choose something >1024
from src.p2p_network.simple_p2p_network import TLCClientFactory

endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(TLCClientFactory())
reactor.run()