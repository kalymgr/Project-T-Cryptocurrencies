import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class CryptoWallet:
    """
    class for managing the crypto wallet
    """

    RSA_BITS = 1024  # the bits that will be used for creating the private key with the RSA algorithm

    @staticmethod
    def getNewPrivateKey()->Crypto.PublicKey.RSA:
        """
        static method for creating an new private key
        :return: the private key
        """
        # create something random
        randomGen = Crypto.Random.new().read
        # generate the private key with the RSA algorithm - 1024 bits
        privateKey = RSA.generate(CryptoWallet.RSA_BITS, randomGen)

        return privateKey

    @staticmethod
    def getNewPublicKey(privateKey: Crypto.PublicKey.RSA)-> Crypto.PublicKey.RSA:
        """
        static method
        :param privateKey: the private key
        :return: the public key that corresponds to the private key
        """

        return privateKey.publickey()

    @staticmethod
    def getNewWallet()->dict:
        """
        static method for creating and returning a new crypto wallet (set of private and public key)
        :return: the set of public and private key as dictionary
        """
        # get the public and private key
        privateKey = CryptoWallet.getNewPrivateKey()
        publicKey = CryptoWallet.getNewPublicKey(privateKey)

        # create the dictionary containing the public and private key
        walletKeySet = {
            'private_key': binascii.hexlify(privateKey.exportKey(format='DER')).decode('ascii'),
            'public_key': binascii.hexlify(publicKey.exportKey(format='DER')).decode('ascii')
        }
        return walletKeySet

    @staticmethod
    def getPrivateKeyasASCII(privateKey):
        """
        :param privateKey: RSA Object
        :return: the private key as ascii
        """
        return binascii.hexlify(privateKey.exportKey(format='DER')).decode('ascii')

    @staticmethod
    def getPublicKeyAsASCII(publicKey):
        """
        :param publicKey: RSA object
        :return: the public key as ascii
        """
        return binascii.hexlify(publicKey.exportKey(format='DER')).decode('ascii')


