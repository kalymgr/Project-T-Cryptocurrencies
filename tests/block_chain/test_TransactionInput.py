import unittest
from src.block_chain.transactions import TransactionInput


class TestTransactionInput(unittest.TestCase):
    """
    Class for testing the TransactionInput class
    """
    def setUp(self):
        pass

    def test_Nones(self):
        """
        creating a transaction input object with none content
        :return:
        """
        txInputNone = TransactionInput(None, None, None, None)
        print(str(txInputNone.getOrderedDict()))
        print(txInputNone.getValue())