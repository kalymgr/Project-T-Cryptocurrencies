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

    def __init__(self):
        """
        constructor method
        """
        wallet = self.__getNewWallet()  # create the wallet
        # store the private and public key
        self.__privateKey = wallet['private_key']
        self.__publicKey = wallet['public_key']

    def getPrivateKey(self):
        """
        Method that returns the private key of the wallet
        :return: the private key as ascii
        """
        return self.__privateKey

    def getPublicKey(self):
        """
        Method that returns the public key of the wallet
        :return: the public key as ascii
        """
        return self.__publicKey

    def __getNewPrivateKey(self)->Crypto.PublicKey.RSA:
        """
        static method for creating an new private key
        :return: the private key
        """
        # create something random
        randomGen = Crypto.Random.new().read
        # generate the private key with the RSA algorithm - 1024 bits
        privateKey = RSA.generate(CryptoWallet.RSA_BITS, randomGen)

        return privateKey

    def __getNewPublicKey(self, privateKey: Crypto.PublicKey.RSA)-> Crypto.PublicKey.RSA:
        """
        static method
        :param privateKey: the private key
        :return: the public key that corresponds to the private key
        """

        return privateKey.publickey()

    def __getNewWallet(self)->dict:
        """
        static method for creating and returning a new crypto wallet (set of private and public key)
        :return: the set of public and private key as dictionary
        """
        # get the public and private key
        privateKey = self.__getNewPrivateKey()
        publicKey = self.__getNewPublicKey(privateKey)

        # create the dictionary containing the public and private key
        walletKeySet = {
            'private_key': binascii.hexlify(privateKey.exportKey(format='DER')).decode('ascii'),
            'public_key': binascii.hexlify(publicKey.exportKey(format='DER')).decode('ascii')
        }
        return walletKeySet



