"""
This file includes class related to network messages
"""
import json
from random import randint
from time import time
from src.p2p_network.parameters import Parameters


class MessageHeader:
    """
    class related to the message header
    """

    MAINNET_START_STRING = "0xf9beb4d9"  # appears at the start of all messages sent on the network

    def __init__(self, commandName: int, payloadSize: int = 0, checkSum: str = '',
                 startString: str = MAINNET_START_STRING):
        """
        Read https://bitcoin.org/en/developer-reference#message-headers
        :param commandName: identifies the type of message
        :param payloadSize: number of bytes in payload
        :param checkSum: First 4 bytes of SHA256(SHA256(payload)) in internal byte order.
        :param startString: always at the start of the message
        """
        self.startString = startString
        self.commandName = commandName
        self.payloadSize = payloadSize
        self.checkSum = checkSum
        self.startString = startString

    def getMessageHeaderAsDict(self) -> dict:
        """
        returns the message header as dictionary
        :return: message header dict
        """
        return {
            'startString': self.startString,
            'commandName': self.commandName,
            'payloadSize': self.payloadSize,
            'checkSum': self.checkSum,
            'startString': self.startString
        }


class Inventory:
    """
    class for managing inventories of messages
    """
    # inventory type identifiers
    TYPEID_MSG_TX = 1  # the hash is a txid
    TYPEID_MSG_BLOCK = 2  # the hash is of a block header
    TYPEID_MSG_FILTERED_BLOCK = 3
    TYPEID_MSG_CMPCT_BLOCK = 4
    TYPEID_MSG_WITNESS_BLOCK = 5
    TYPEID_MSG_WITNESS_TX = 6
    TYPEID_MSG_FILTERED_WITNESS_BLOCK = 7

    def __init__(self):
        # self.messageHeader = TLCNetworkMessage.MessageHeader()
        pass


class TLCMessage:
    """
    Messages sent on the TLC network
    """

    # set the types of the data messages - start from 1
    DATAMSGTYPE_BLOCK = 1
    DATAMSGTYPE_GETBLOCKS = 2
    DATAMSGTYPE_GETDATA = 3
    DATAMSGTYPE_GETHEADERS = 4
    DATAMSGTYPE_HEADERS = 5
    DATAMSGTYPE_INV = 6
    DATAMSGTYPE_MEMPOOL = 7
    DATAMSGTYPE_MERKLEBLOCK = 8
    DATAMSGTYPE_CMPCTBLOCK = 9
    DATAMSGTYPE_SENDCMPCT = 10
    DATAMSGTYPE_GETBLOCKTXN = 11
    DATAMSGTYPE_BLOCKTXN = 12
    DATAMSGTYPE_NOTFOUND = 13
    DATAMSGTYPE_TX = 14

    # set the types of the control messages - start from 50
    CTRLMSGTYPE_ADDR = 50
    CTRLMSGTYPE_GETADDR = 51
    CTRLMSGTYPE_VERSION = 52
    CTRLMSGTYPE_VERACK = 53
    CTRLMSGTYPE_PING = 54
    CTRLMSGTYPE_PONG = 55
    CTRLMSGTYPE_REJECT = 56

    def __init__(self, msgType: int, msgData = None):
        """
        Constructor for a message
        :param msgType: the type of the message
        :param msgData: the data of the message
        """
        # create the message header
        # self.msgHeader = MessageHeader(msgType)
        self.msgHeader = MessageHeader(msgType)
        self.msgData = msgData

    def getMessageAsDict(self):
        """
        returns the message as a dictionary
        :return:
        """
        return {
            'msgHeader': self.msgHeader.getMessageHeaderAsDict(),
            'msgData': self.msgData
        }

    def getMessageAsSendable(self):
        """
        returns the messaqe in a form that is sendable by the tcp protocol
        :return: for now, a json string
        """
        return (json.dumps(self.getMessageAsDict()) + '\n').encode('utf8')


class TLCVersionMessage(TLCMessage):
    """
    class specifically for the version messages. Extends the TLC Message class
    """
    def __init__(self, nodeType: int, ipAddress: str = None, port: int = None,
                 protocolVersion = Parameters.PROTOCOL_VERSION):
        """
        Constructor method for the version message
        :param nodeType: the type of the node (eg full node, seed etc.)
        :param ipAddress: the ip address of the transmitting node. The default used, if None
        :param port: the port of the transmitting node. The default used, if None
        :param protocolVersion: the version of the protocol. If ommitted, it uses the default from the Params
        """

        # use the default values of ip address and port, if omitted when calling the constructor
        if ipAddress is None:
            ipAddress = Parameters.NODE_IP_ADDRESS
        if port is None:
            port = Parameters.NODE_DEFAULT_PORT_MAINNET

        # call the constructor of the parent class
        super().__init__(TLCMessage.CTRLMSGTYPE_VERSION)

        # set the data for the version control message
        self.msgData = \
            {
                'version': protocolVersion,
                'services': Parameters.NODE_TYPE,
                'timestamp': time(),
                'addrReceivServices': nodeType,  # this is about the receiving node. Suppose it's a full n
                'ipAddress': ipAddress,  # ip of the transmitting node
                'port': port  # port of the transmitting node
            }

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())


class TLCVerAckMessage(TLCMessage):
    """
    Class for the verack message
    """

    def __init__(self):
        """
        constructor method
        """
        # call the constructor of the parent class, stating the verack type of this message
        super().__init__(TLCMessage.CTRLMSGTYPE_VERACK)

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())


class TLCGetAddrMessage(TLCMessage):
    """
    implementing the getAddr message, that asks a peer to send his ip address list
    """
    def __init__(self):
        """
        constructor method
        """
        # call the constructor of the parent class, stating the type of this message
        super().__init__(TLCMessage.CTRLMSGTYPE_GETADDR)

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())


class TLCAddrMessage(TLCMessage):
    """
    Class for the addr messages, that return a list of addresses of nodes
    """

    def __init__(self, addressesList: list):
        """
        constructor method
        :param addressesList: the list of addresses sent
        """
        # call the constructor of the parent class, stating the type of this message
        super().__init__(TLCMessage.CTRLMSGTYPE_ADDR)

        # add data to the message
        self.msgData = {
            'ipAddresses': addressesList,  # the list of addresses
            'ipAddressCount': len(addressesList)  # the number of addresses
        }

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())


class TLCRejectMessage(TLCMessage):
    """
    Implementing the reject message
    """

    REJECT_CODE_DIF_VERSION = 1  # reject code for a different version

    def __init__(self, msgRejectedType: str, rejectCode: str, reason: str = None):
        """
        Constructor that initializes a reject message
        :param msgRejectedType: the type of the message rejected (eg 'version')
        :param rejectCode: the code of the reject
        :param reason: the reason (description) of the rejection
        """

        # call the constructor of the parent class, stating the verack type of this message
        super().__init__(TLCMessage.CTRLMSGTYPE_REJECT)

        # set the data of the message
        self.msgData = {
            'msgRejectedType': msgRejectedType,
            'rejectCode': rejectCode,
            'reason': reason
        }

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())


class TLCPingMessage(TLCMessage):
    """
    Implementing the ping message
    """
    def __init__(self):
        """
        constructor method
        """
        # call the constructor of the parent class, stating the type of this message
        super().__init__(TLCMessage.CTRLMSGTYPE_PING)

        # set the data
        self.msgData = {
            'nonce': randint(1, 1000)  # a random number between 1 and 1000
        }

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())


class TLCPongMessage(TLCMessage):
    """
    Implementing the pong message
    """
    def __init__(self, nonce: int):
        """
        constructor method
        :param nonce: the nonce received from the ping message
        """
        # call the constructor of the parent class, stating the type of this message
        super().__init__(TLCMessage.CTRLMSGTYPE_PONG)

        # set the data
        self.msgData = {
            'nonce': nonce  # the nonce received from the ping message
        }

        # set the payload size
        self.msgHeader.payloadSize = len(self.getMessageAsSendable())