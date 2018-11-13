import unittest

from src.block_chain.crypto_account import CryptoAccount


class TestCryptoAccount(unittest.TestCase):
    """
    class for testing the crypto account
    """
    def test_printAccountInfo(self):
        """
        Just printing the info of an account
        :return:
        """
        account = CryptoAccount()
        print('ACCOUNT ADDRESS\n')
        print(account.getAddress())
