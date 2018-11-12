import unittest

from src.block_chain.crypto_wallet import CryptoWallet
from src.block_chain.transactions import Blockchain, Transaction, TransactionInput, TransactionOutput, Block


class TestBlock(unittest.TestCase):
    """
    class for testing the Block manipulation
    """
    blockChain = Blockchain()  # class variable used by the methods

    def setUp(self):
        """
        Method that sets up some things needed for testing. It will be called for each test we will be running
        :return:
        """
        # initialize a blockchain object for test purposes
        self.blockChain = Blockchain()
        txInputList1 = [
            TransactionInput(2, 'stefanos', '0', 0),
            TransactionInput(5, 'stefanos', '0', 0),
        ]
        txOutputList1 = [
            TransactionOutput(3, 'stefanos', 'michalis'),
            TransactionOutput(1, 'stefanos', 'evdoxia')
        ]
        t1 = Transaction('sender address', transactionInputList=txInputList1, transactionOutputList=txOutputList1)

        # initialize a block object for test purposes
        self.block = Block(chain=self.blockChain.getChain(), transactions=[t1], nonce=0, previousHash='00')

    def test_BlockCreation(self):
        """
        test method for creating the creation of a new block
        :return:
        """

        b = self.block
        print('end of testing')

    def test_getOrderedDictionary(self):
        """
        testing the getOrderedDictionary
        :return:
        """

        print(self.block.getOrderedDictionary())