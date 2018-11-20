from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from src.p2p_network.simple_p2p_network import TLCClientFactory, TLCProtocol


def gotProtocol(p):
    """
    function for trying to talk to the protocol
    :param p:
    :return:
    """
    print('gotProtocol called')
    p.sendHello()


# d = reactor.connectTCP('localhost', 8007, TLCClientFactory())
# reactor.run()

point = TCP4ClientEndpoint(reactor, "localhost", 8007)
d = point.connect(TLCClientFactory())
d.addCallback(gotProtocol)
reactor.run()

