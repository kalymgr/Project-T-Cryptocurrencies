import unittest

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor

from src.p2p_network.tlc_message import TLCMessage, MessageHeader, TLCVersionMessage


class TestTLCNetworkMessage(unittest.TestCase):
    """
    class for testing the network messages
    """

    def test_init_message(self):
        """
        testing the creation of a new message header
        :return:
        """

        # create a new message header
        messageHeader = MessageHeader('a', 2, 'a')
        print(messageHeader.getMessageHeaderAsDict())

        # create a new message
        message = TLCMessage(TLCMessage.CTRLMSGTYPE_VERSION)
        print(message.getMessageAsDict())

    def test_version_control_message(self):
        msg = TLCVersionMessage()
        print(msg.getMessageAsDict())
