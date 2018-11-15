import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.transactions import Transaction, TransactionInput, TransactionOutput


class TestTransaction(unittest.TestCase):
    """
    Class for testing the Transaction class
    """
    def setUp(self):
        # setup a crypto senderAccount and a recipientAccount
        self.senderAccount = CryptoAccount()
        self.recipientAccount = CryptoAccount()

        # setup a transaction that will be used for testing
        self.testTransaction = Transaction(
            self.senderAccount.getAddress(),
            [TransactionInput(3, self.recipientAccount.getAddress(), '#', -1)]
        )

    def test_getOrderedDict(self):
        """
        test that ordered dict really works
        :return:
        """
        print(self.testTransaction.getOrderedDict())

    def test_sign(self):
        """
        testing signing of a transaction
        :return:
        """
        self.testTransaction.sign(self.senderAccount.getPrivateKey())

    def test_extendTransactionInputList(self):
        """
        test the extending of a transaction input list
        :return:
        """

        # extend the tx input list
        newTxInputList = [
            TransactionInput(2, self.recipientAccount.getAddress(), '#', -1),
            TransactionInput(5, self.recipientAccount.getAddress(), '#', -1)
        ]
        oldTxInputListSize = len(self.testTransaction.getTransactionInputList())
        self.testTransaction.extendTransactionInputList(newTxInputList)

        newTxInputListSize = len(self.testTransaction.getTransactionInputList())

        # check that the length of the new tx input list is ok
        assert newTxInputListSize == oldTxInputListSize + len(newTxInputList)

        # check that the inCounter is OK
        assert self.testTransaction.getInCounter() == newTxInputListSize

        # add one more transaction input
        self.testTransaction.extendTransactionInputList([
            TransactionInput(5, self.recipientAccount.getAddress(), '#', -1)
        ])

        # check that the length is ok
        newTxInputLength = newTxInputListSize + 1
        assert newTxInputLength == len(self.testTransaction.getTransactionInputList())

        # check that the inCounter is ok
        assert self.testTransaction.getInCounter() == newTxInputLength

    def test_addTransactionOutput(self):
        """
        testing the adding of a transaction output
        :return:
        """
        # initially test that the outCounter is zero
        assert self.testTransaction.getOutCounter() == 0

        # add a transaction output
        self.testTransaction.addTransactionOutput(
            TransactionOutput(5, self.senderAccount.getAddress(),self.recipientAccount.getAddress())
        )

        # check the length of the transaction output list
        assert len(self.testTransaction.getTransactionOutputList()) == 1

        # check the outCounter
        assert self.testTransaction.getOutCounter() == 1