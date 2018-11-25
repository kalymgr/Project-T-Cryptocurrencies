"""
Includes various tests for the "connecting to peers" feature
"""

import unittest

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, defer


class TestConnectingToPeers(unittest.TestCase):
    pass