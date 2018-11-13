from Crypto.Hash import SHA256


class TLCUtilities:
    """
    class with various utilities
    """

    @staticmethod
    def getDoubleHash256(text: str) -> str:
        """
        static method that double hashes a text with SHA 256
        :param text: the text that will be double hashed
        :return: the double hash string
        """
        hash = SHA256.new(str.encode('utf8'))
        doubleHash = SHA256.new(hash.hexdigest().encode('utf8'))
        return doubleHash.hexdigest()
