import binascii

import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA

from src.utilities.utilities import TLCUtilities


class CryptoAccount:
    """
    class for managing the crypto account (wallet, address etc.)
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

        self.__version = 1  # the version of the bitcoin address
        self.__address = self.__createAddress()

    def __createAddress(self) -> str:
        """
        Method for creating the address which will be used for transferring coins
        :return: the address string
        """
        text = str(self.__version) + self.__publicKey
        # textSHA256Hash = SHA256.new(text.encode('utf8')).hexdigest()
        # return RIPEMD.new(textSHA256Hash).hexdigest()
        return TLCUtilities.getSHA256RIPEMDHash(text)

    def getAddress(self) -> str:
        """
        Method that returns the address of the crypto account
        :return: address string
        """
        return self.__address

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

    def getPublicKeySignature(self) -> str:
        """
        Method that creates and returns the signature of the public key
        :return: public key signature (string)
        """
        return TLCUtilities.getSHA256RIPEMDHash(self.__publicKey)

    def __getNewPrivateKey(self)->Crypto.PublicKey.RSA:
        """
        static method for creating an new private key
        :return: the private key
        """
        # create something random
        randomGen = Crypto.Random.new().read
        # generate the private key with the RSA algorithm - 1024 bits
        privateKey = RSA.generate(CryptoAccount.RSA_BITS, randomGen)

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



