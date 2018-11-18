import binascii

from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.Hash import RIPEMD, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class TLCUtilities:
    """
    class with various utilities
    """

    @staticmethod
    def getDoubleHash256AsString(text: str) -> str:
        """
        static method that double hashes a text with SHA 256
        :param text: the text that will be double hashed (string)
        :return: the double hash string
        """
        return TLCUtilities.getDoubleHash256(text).hexdigest()

    @staticmethod
    def getDoubleHash256(text: str)-> SHA256Hash:
        """
        static method that double hashes a text with SHA256
        :param text: the text (string)
        :return: the hash (SHA256Hash object)
        """
        hash = SHA256.new(text.encode('utf8'))
        doubleHash = SHA256.new(hash.hexdigest().encode('utf8'))
        return doubleHash

    @staticmethod
    def getSHA256RIPEMDHash(text: str) -> str:
        """
        static method that is used for creating bitcoin addresses etc.
        First it hashes using SHA256 and then using RIPEMD
        :param text:
        :return:
        """
        textSHA256Hash = SHA256.new(text.encode('utf8')).hexdigest()
        return RIPEMD.new(textSHA256Hash).hexdigest()

    @staticmethod
    def getHashSignature(textToBeSigned: str, privateKeyStr: str) -> str:
        """
        method that signs a text and returns the signature, using a private key
        :param textToBeSigned:
        :param privateKeyStr:
        :return:
        """
        # create the private key in a form that will make signing possible
        privateKey = RSA.importKey(binascii.unhexlify(privateKeyStr))

        # create the signer
        signer = PKCS1_v1_5.new(privateKey)

        hash = SHA256.new(textToBeSigned.encode('utf8'))
        # sign the hash of the text with the private key

        signedText = binascii.hexlify(signer.sign(hash)).decode('ascii')

        return signedText

    @staticmethod
    def verifyHashSignature(text: str, signature: str, publicKeyStr: str) -> bool:
        """
        verifies the signature for a specific public key. If ok returns True, else returns False
        :param text: text to be signed
        :param signature: the signature (string)
        :param publicKeyStr: the public key (string) to verify the signature of the text
        :return: True if verified
        """

        publicKey = RSA.importKey(binascii.unhexlify(publicKeyStr))
        verifier = PKCS1_v1_5.new(publicKey)
        h = SHA256.new(text.encode('utf8'))
        result = verifier.verify(h, binascii.unhexlify(signature))

        if result:
            return True
        else:
            return False


