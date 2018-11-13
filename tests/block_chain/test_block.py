import unittest

from src.block_chain.crypto_wallet import CryptoAccount
from src.block_chain.transactions import Blockchain, Transaction, TransactionInput, TransactionOutput, Block


class TestBlock(unittest.TestCase):
    """
    class for testing the Block manipulation
    """

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
        t1.__setTransactionHash()  # set the transaction hash

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

    def test_getBlockHash(self):
        """
        test the getBlockHash method
        :return:
        """
        blockHash = self.block.getBlockHash()
        print(blockHash)
        assert len(blockHash) == 64  # check that the length of the hash is 64 characters

    def test_getMerkleRoot(self):
        """
        method for testing the getMerkleRoot method
        :return:
        """
        print(self.block.getMerkleRoot())
