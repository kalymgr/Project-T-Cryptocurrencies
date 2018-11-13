import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.transactions import Blockchain, Transaction, TransactionInput, TransactionOutput, Block, \
    CoinTransfer


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

    def test_initialAccountTotals(self):
        """
        Testing that the initial account totals are ok
        :return:
        """

        # print the existing account balances in the blockchain
        self.blockchain.printAccountTotals()

        # test that initial account balance is ok
        blockchainAddress = self.blockchain.getBlockchainAccount().getAddress()
        assert self.blockchain.getAccountTotal(blockchainAddress) == 100

        # make a coin transfer and then check the results
        coinTransferList = [
            CoinTransfer(self.evdoxiaAccount.getAddress(), 20),
            CoinTransfer(self.michalisAccount.getAddress(), 30)
        ]

        # submit the transaction
        self.blockchain.submitTransaction(
            blockchainAddress, coinTransferList, self.blockchain.getBlockchainAccount().getPrivateKey()
        )
        # add the sender to the accounts dictionary
        self.blockchain.addAccount(blockchainAddress, self.blockchain.getBlockchainAccount().getPublicKey())

        # transaction not verified, so the balance is the same
        assert self.blockchain.getAccountTotal(blockchainAddress) == 100

        # verify the pending transactions and add the block of transactions to the blockchain
        self.blockchain.verifyTransactions()

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

    def test_coinTransfer(self):
        """
        Various scenarios for transferring coins
        :return:
        """

        # get stefanos account info
        stefanosPrivateKey = self.stefanosAccount.getPrivateKey()
        stefanosPublicKey = self.stefanosAccount.getPublicKey()
        stefanosAddress = self.stefanosAccount.getAddress()

        # transfer some money to stefanos
        coinTransferList0 = [
            CoinTransfer(stefanosAddress, 50)
        ]
        self.blockchain.transfer(self.blockchain.getBlockchainAccount().getAddress(), coinTransferList0,
                                 self.blockchain.getBlockchainAccount().getPrivateKey())

        assert self.blockchain.getAccountTotal(stefanosAddress) == 50

        # first coin transfer
        coinTransferList1 = [
            CoinTransfer(self.evdoxiaAccount.getAddress(), 10), CoinTransfer(self.michalisAccount.getAddress(), 10),
            CoinTransfer(self.michalisAccount.getAddress(), 5)
        ]

        self.blockchain.transfer(stefanosAddress, coinTransferList1, stefanosPrivateKey)

        assert self.blockchain.getAccountTotal(stefanosAddress) == 25
        assert self.blockchain.getAccountTotal(
            self.michalisAccount.getAddress()
        ) == 15
        assert self.blockchain.getAccountTotal(
            self.evdoxiaAccount.getAddress()
        ) == 10

        # try to transfer coins, where the first transfer will exceed the sender account total
        # in this case, none of the transfers should be made
        coinTransferList2 = [
            CoinTransfer(self.michalisAccount.getAddress(), 200),
            CoinTransfer(self.evdoxiaAccount.getAddress(), 10)
        ]
        self.blockchain.transfer(stefanosAddress, coinTransferList2, stefanosPrivateKey)

        assert self.blockchain.getAccountTotal(stefanosAddress) == 25
        assert self.blockchain.getAccountTotal(
            self.michalisAccount.getAddress()
        ) == 15
        assert self.blockchain.getAccountTotal(
            self.evdoxiaAccount.getAddress()
        ) == 10

        # try to transfer coins. The first transfer is feasible but the second won't be.
        # In this case, only the first transfer will be made
        coinTransferList3 = [
            CoinTransfer(self.michalisAccount.getAddress(), 10),
            CoinTransfer(self.evdoxiaAccount.getAddress(), 500)
        ]
        self.blockchain.transfer(stefanosAddress, coinTransferList3, stefanosPrivateKey)

        assert self.blockchain.getAccountTotal(stefanosAddress) == 15
        assert self.blockchain.getAccountTotal(
            self.michalisAccount.getAddress()
        ) == 25
        assert self.blockchain.getAccountTotal(
            self.evdoxiaAccount.getAddress()
        ) == 10
        assert self.blockchain.getAccountTotal(
            self.blockchain.getBlockchainAccount().getAddress()
        ) == 50

    def test_transactionSignaturesAndHashes(self):
        """
        method to test that the transactions are properly signed and that
        they are properly linked via their transaction hash.
        First I make a simple transaction and then I check the signatures and hashes
        :return:
        """

        # make a transaction
        # transfer some money to stefanos
        coinTransferList0 = [
            CoinTransfer(self.stefanosAccount.getAddress(), 50),
            CoinTransfer(self.michalisAccount.getAddress(), 10),
            CoinTransfer(self.evdoxiaAccount.getAddress(), 5)
        ]
        self.blockchain.transfer(self.blockchain.getBlockchainAccount().getAddress(), coinTransferList0,
                                 self.blockchain.getBlockchainAccount().getPrivateKey())

        # for each of the transaction inputs in the transaction input pool, the prev transaction hash
        # should be the hash of the first transaction of the blockchain
        for txInputList in self.blockchain.getTransactionInputPool().values():
            for txInput in txInputList:
                assert txInput.getPreviousTransactionHash() == self.blockchain.getTransactionList()[0].getDoubleHash()

        # for each transaction in the blockchain, check that the transaction signature is properly stored
        for transaction in self.blockchain.getTransactionList():
            assert transaction.getSignature() == \
                   self.blockchain.signTransaction(transaction,
                                              self.blockchain._Blockchain__cryptoAccount._CryptoAccount__privateKey)



