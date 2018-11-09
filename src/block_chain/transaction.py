"""
contains the Transaction class, responsible for handling transactions
"""

import binascii
from collections import OrderedDict
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Transaction:
    """
    class for managing the transaction.
    The private key is not required
    """
    def __init__(self, sender_address: str, recipient_address: str, value, sender_private_key: str=None):
        self.versionNo = 1  # the version of the transaction format

        self.flag = None  # indicates the presence of witness data
        self.witnesses = []  # list of witnesses, 1 for each input, omitted if flag variable is missing

        self.listOfInputs = []  # the list of inputs
        self.inCounter = len(self.listOfInputs)  # the size of the list of inputs
        self.listOfOutputs = []  # the list of outputs
        self.outCounter = len(self.listOfOutputs)  # the size of the list of outputs

        self.lockTime = None  # TODO:// read the bitcoin transaction documentation

        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address

        self.value = value   # value measured in taliroshi - 1 coin is equal to 100,000,000 taliroshi

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self)->OrderedDict:
        """
        :return: returns the transaction data as an ordered dictionary
        """
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})

    def sign_transaction(self)->binascii:
        """
        Sign the transaction with the private key
        :return: the transaction hash signed with the private key
        """
        if self.sender_private_key is not None:  # if there is a private key
            # create the private key in a form that will make signing possible
            private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
            # create the signer
            signer = PKCS1_v1_5.new(private_key)
            # create the hash of the transaction
            h = SHA.new(str(self.to_dict()).encode('utf8'))
            # sign the hash of the transaction with the private key
            return binascii.hexlify(signer.sign(h)).decode('ascii')
        else:  # not private key for this transaction
            return False

    def verifySignature(self, signature)->bool:
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        :param signature:
        :return:
        """

        public_key = RSA.importKey(binascii.unhexlify(self.sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))

    def createTransactionInputs(self, prevTransactionOutputs: list):
        """
        method for creating the transaction inputs and returning the total value of the inputs
        "param prevTransactionOutputs: list of the previous transaction outputs
        :return: the total value of the previous transaction outputs
        """
        totalTransOutputValue = 0  # the total value of the previous transaction outputs
        for preTransactionOutput in prevTransactionOutputs:  # for each of the previous transaction outputs
            # create the list of transaction inputs and calculate the total value
            totalTransOutputValue = totalTransOutputValue + preTransactionOutput.value



        return totalTransOutputValue

    def generateOutputs(self, prevTransactionOutputs):
        """
        method for generating the outputs
        :return:
        """

        TransactionOutputs = self.createTransactionInputs(prevTransactionOutputs)
        # get the value from all the inputs
        totalValue = 0  # this is the total value of the inputs
        for transactionInput in self.listOfInputs:
            totalValue = totalValue + transactionInput.

class TransactionInput:
    """
    class for handling the transaction inputs
    """
    def __init__(self, prevTransactionHash: str,
                 prevTxoutIndex: int,txInScriptLength: int,
                 txInScript: bytes, sequenceNo: str='ffffffff' ):
        """
        Construction method
        :param prevTransactionHash: doubled SHA256-hashed of a (previous) to-be-used transaction
        :param prevTxoutIndex: non negative integer indexing an output of the to-be-used transaction
        :param txInScriptLength: non negative integer
        :param txInScript: the Script
        :param sequenceNo: normally 0xFFFFFFFF; irrelevant unless transaction's lock_time is > 0
        """
        self.prevTransactionHash = prevTransactionHash
        self.prevTxoutIndex= prevTxoutIndex
        self.txInScriptLength = txInScriptLength
        self.txInScript = txInScript
        self.sequenceNo = sequenceNo


class TransactionOutput:
    """
    class for handling the transaction outputs
    """
    def __init__(self, value: int,txoutScriptLength: int, txOutScript: bytes ):
        """
        constructor method
        :param value: non negative integer giving the number of Taliroshis(TLC/10^8) to be transferred
        :param txoutScriptLength: non negative integer
        :param txOutScript: Script
        """
        self.value = value
        self.txOutScriptLength = txoutScriptLength
        self.txOutScript = txOutScript

