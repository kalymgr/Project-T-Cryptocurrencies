import unittest

from src.block_chain.transaction import Transaction, TransactionInput, TransactionOutput


class TestTransaction(unittest.TestCase):

    """
    class for testing the transaction class
    """

    def test_transactions(self):
        """
        Testing transactions with multiple inputs and output.
        :return:
        """

        transOutput1 = TransactionOutput(10, 2, b'ab')
        transOutput2 = TransactionOutput(6, 2, b'ab')

        # create the first transaction
        firstTransaction = Transaction('my address', 'his address', 16)
        firstTransaction.listOfInputs.append(transOutput1)
        firstTransaction.listOfInputs.append(transOutput2)

        # generate the transaction list of outputs



