from twisted.internet import reactor
from src.p2p_network.simple_p2p_network import TLCClientFactory

reactor.connectTCP('localhost', 8007, TLCClientFactory())
reactor.run()