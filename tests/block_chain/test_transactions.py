import unittest
from src.block_chain.transactions import Blockchain


class TestTransactions(unittest.TestCase):
    """
    methods for testing the new classes
    """

    def test_initialAccountTotals(self):
        """
        Testing that the initial account totals are ok
        :return:
        """
        blockhain = Blockchain()  # initialize the blockchain
        blockhain.printAccountTotals()

        # test that initial account totals are ok
        assert blockhain.getAccountTotal("michalis") == 20
        assert blockhain.getAccountTotal("evdoxia") == 30
        assert blockhain.getAccountTotal("stefanos") == 100
        # kyriakos account does not have account total, because it does not exist in the blockchain
        assert blockhain.getAccountTotal("kyriakos") == 0

    def test_coinTransfer(self):
        """
        Various scenarios for transferring coins
        :return:
        """
        blockchain = Blockchain()  # initialize the blockchain
        blockchain.printAccountTotals()

        blockchain.getAccountTotal('a')
        # first coin transfer
        coinTransfer1 = [
            ['evdoxia', 10], ['michalis', 10], ['michalis', 5]
        ]
        blockchain.transfer('stefanos', coinTransfer1)  # transfer the funds

        blockchain.printAccountTotals()
        assert blockchain.getAccountTotal('evdoxia') == 40
        assert blockchain.getAccountTotal('michalis') == 35
        assert blockchain.getAccountTotal('stefanos') == 75

        # try to transfer coins to a new account
        coinTransfer2 = [
            ['kyriakos', 10]
        ]
        blockchain.transfer('stefanos', coinTransfer2)  # transfer the funds
        blockchain.printAccountTotals()
        assert blockchain.getAccountTotal('stefanos') == 65
        assert blockchain.getAccountTotal('kyriakos') == 10

        # try to transfer coins, where the first transfer will exceed the sender account total
        # in this case, none of the transfers should be made
        coinTransfer3 = [
            ['michalis', 200],
            ['evdoxia', 10]
        ]
        blockchain.transfer('stefanos', coinTransfer3)

        blockchain.printAccountTotals()
        assert blockchain.getAccountTotal('stefanos') == 65
        assert blockchain.getAccountTotal('evdoxia') == 40
        assert blockchain.getAccountTotal('michalis') == 35

        # try to transfer coins. The first transfer is feasible but the second won't be.
        # In this case, only the first transfer will be made
        coinTransfer4 = [
            ['michalis', 10],
            ['evdoxia', 500]
        ]
        blockchain.transfer('stefanos', coinTransfer4)
        assert blockchain.getAccountTotal('stefanos') == 55
        assert blockchain.getAccountTotal('evdoxia') == 40
        assert blockchain.getAccountTotal('michalis') == 45
        print('FINAL')
        blockchain.printAccountTotals()
