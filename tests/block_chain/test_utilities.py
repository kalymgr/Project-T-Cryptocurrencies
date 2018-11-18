"""
testing the functionality in the utilities python file
"""

import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.utilities import TLCUtilities


class TestTLCUtilities(unittest.TestCase):
    def setUp(self):
        self.testAccount = CryptoAccount()  # crypto account for testing

    def test_signing(self):
        """
        testing the signing functionality of the TLCUtilities class
        :return:
        """

        text = 'this is a text to sign'
        # sign the text
        signedText = TLCUtilities.getHashSignature(text, self.testAccount.getPrivateKey())

        # check that the signature is ok
        assert TLCUtilities.verifyHashSignature(text, signedText, self.testAccount.getPublicKey())

        # fake text
        fakeText = 'this is the wrong text for the signature'
        assert not TLCUtilities.verifyHashSignature(fakeText, signedText, self.testAccount.getPublicKey())

        # fake signature - other public key
        fakeAccount = CryptoAccount()
        assert not TLCUtilities.verifyHashSignature(text, signedText, fakeAccount.getPublicKey())
