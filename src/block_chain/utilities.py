from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.Hash import RIPEMD, SHA256


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



