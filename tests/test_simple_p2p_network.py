import unittest

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor

from src.p2p_network.simple_p2p_network import QOTD


class TestSimpleP2PNetwork(unittest.TestCase):
    """
    Class for testing the BlockChain class
    """

    def test_Server(self):
        def gotProtocol(p):
            """The callback to start the protocol exchange. We let connecting
            nodes start the hello handshake"""
            p.send_hello()

        point = TCP4ClientEndpoint(reactor, 'localhost', 8007)
        d = connectProtocol(point, QOTD())
        d.addCallback(gotProtocol)


