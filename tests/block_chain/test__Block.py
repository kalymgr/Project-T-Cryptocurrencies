import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.transactions import Transaction, TransactionInput, TransactionOutput, Block


class TestBlock(unittest.TestCase):
    """
    Class for testing the Block class
    """
    def setUp(self):
        # create some accounts - two senders and three recipients
        self.sender1Account = CryptoAccount()
        self.sender2Account = CryptoAccount()
        self.recipient1Account = CryptoAccount()
        self.recipient2Account = CryptoAccount()
        self.recipient3Account = CryptoAccount()

        # create some transactions
        self.testTransaction1 = Transaction(
            self.sender1Account.getAddress(),
            [TransactionInput(2, self.recipient1Account.getAddress(),'-')],
            [TransactionOutput(2, self.sender1Account.getAddress(),self.recipient1Account.getAddress())]
        )
        self.testTransaction2 = Transaction(
            self.sender2Account.getAddress(),
            [TransactionInput(2, self.recipient1Account.getAddress(), '-')],
            [TransactionOutput(2, self.sender2Account.getAddress(), self.recipient1Account.getAddress())]
        )
        self.testTransaction3 = Transaction(
            self.sender1Account.getAddress(),
            [TransactionInput(2, self.recipient2Account.getAddress(), '-')],
            [TransactionOutput(2, self.sender1Account.getAddress(), self.recipient2Account.getAddress())]
        )

        # create a test block
        chain = list()
        self.testBlock = Block(chain, None, '##')
        self.testBlock.setTransactionList([self.testTransaction1, self.testTransaction2, self.testTransaction3])

    def test_changeTransactionList(self):
        """
        testing methods that alter the transaction list
        :return:
        """
        # create a new list with two transactions
        t1 = Transaction(
            self.sender1Account.getAddress(),
            [TransactionInput(2, self.recipient1Account.getAddress(), '-')],
            [TransactionOutput(2, self.sender1Account.getAddress(), self.recipient1Account.getAddress())]
        )
        t2 = Transaction(
            self.sender2Account.getAddress(),
            [TransactionInput(2, self.recipient1Account.getAddress(), '-')],
            [TransactionOutput(2, self.sender2Account.getAddress(), self.recipient1Account.getAddress())]
        )

        self.testBlock.setTransactionList([t1, t2])
        # check the transaction list has been set
        assert [t1, t2] == self.testBlock.getTransactionList()
        assert t1 == self.testBlock.getTransactionList()[0]

        # add one more transaction
        self.testBlock.addTransaction(t2)
        # check that the transaction list has been altered
        assert len(self.testBlock.getTransactionList()) == 3

    def test_getOrderedDictionary(self):
        """
        testing the creation of ordered dictionary
        :return:
        """
        print(self.testBlock.getOrderedDictionary())

    def test_getBlockHash(self):
        """
        Check the get block hash method
        :return:
        """
        print(self.testBlock.getBlockHash())

    def test_getMerkleRoot(self):
        """
        check the getMerkleRoot method
        :return:
        """

        merkleRoot = self.testBlock.getMerkleRoot()
        assert merkleRoot == self.testBlock._Block__merkleRoot  # check that the object property has been properly set

        # add a transaction
        self.testBlock.addTransaction(self.testTransaction1)

        # recalculate the merkle root
        newMerkleRoot = self.testBlock.getMerkleRoot()

        assert merkleRoot != newMerkleRoot  # two merkle roots must be different
        assert newMerkleRoot == self.testBlock._Block__merkleRoot  # check that the object property has been properly set

