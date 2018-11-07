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
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

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
