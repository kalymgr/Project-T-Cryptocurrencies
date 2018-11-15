import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.transactions import Blockchain, Transaction, TransactionInput, TransactionOutput, Block, \
    CoinTransfer

# TODO: more testing for cases where the account balance is not enough etc.

class TestTransactions(unittest.TestCase):
    """
    methods for testing the new classes
    """

    def setUp(self):
        """
        Setup for testing
        :return:
        """

        # create the blockchain
        self.blockchain = Blockchain()

        # create some wallets
        self.blockchainAccount = self.blockchain.getBlockchainAccount()
        self.stefanosAccount = CryptoAccount()
        self.michalisAccount = CryptoAccount()
        self.evdoxiaAccount = CryptoAccount()
        self.kyriakosAccount = CryptoAccount()

        # create a block to aid with testing
        # test that initial account balance is ok
        blockchainAddress = self.blockchain.getBlockchainAccount().getAddress()

        # make a coin transfer and then check the results
        coinTransferList = [
            CoinTransfer(self.evdoxiaAccount.getAddress(), 20),
            CoinTransfer(self.michalisAccount.getAddress(), 20),
            CoinTransfer(self.stefanosAccount.getAddress(), 10)
        ]

        coinTransferList2 = [
            CoinTransfer(self.evdoxiaAccount.getAddress(), 10),
            CoinTransfer(self.stefanosAccount.getAddress(), 10)
        ]

        # submit the transactions
        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList)
        self.blockchain.submitTransaction(self.michalisAccount, coinTransferList2)

        # verify the pending transactions and add the block of transactions to the blockchain
        currentBlock = Block(self.blockchain.getChain())
        self.blockchain.executeTransactions(currentBlock)

    def test_variousTransactions(self):
        """
        Testing that the initial account totals are ok
        :return:
        """

        # print the existing account balances in the blockchain
        self.blockchain.printAccountTotals()

        self.blockchain.printAccountTotals()

        coinTransferList3 = [
            CoinTransfer(self.stefanosAccount.getAddress(), 10),
            CoinTransfer(self.michalisAccount.getAddress(), 10)

        ]

        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList3)
        b = Block(self.blockchain.getChain())
        assert self.blockchain.executeTransactions(b) == 1  # check that one transaction has been added

        self.blockchain.printAccountTotals()

        """
        # now the balances have changed.
        assert self.blockchain.getAccountTotal(
            self.evdoxiaAccount.getAddress()
        ) == 20
        assert self.blockchain.getAccountTotal(
            self.michalisAccount.getAddress()
        ) == 30
        assert self.blockchain.getAccountTotal(blockchainAddress) == 50

        self.blockchain.printAccountTotals()

        # kyriakos account does not have account total, because it does not exist in the blockchain
        assert self.blockchain.getAccountTotal("kyriakos") == 0
        """

    def test_proofOfWork(self):
        """
        Testing the proof of work related methods
        :return:
        """
        # get the last block of the chain
        lastBlock = self.blockchain.getChain()[len(self.blockchain.getChain())-1]

        # get the blockTransactionsHash
        blockTransactionsHash = lastBlock.getTransactionsHash()

        # get the hash of the previous block
        prevBlockHash = self.blockchain.getChain()[len(self.blockchain.getChain())-2].getBlockHash()

        # try to find a valid nonce
        validNonce = self.blockchain._Blockchain__getProofOfWork(lastBlock)
        print('Valid block nonce :' + str(validNonce))
        assert validNonce > 0



