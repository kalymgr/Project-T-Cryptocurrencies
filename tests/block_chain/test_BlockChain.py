import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.transactions import Transaction, TransactionInput, TransactionOutput, Block, Blockchain, \
    CoinTransfer


class TestBlockchain(unittest.TestCase):
    """
    Class for testing the BlockChain class
    """

    def setUp(self):
        """
        initialize some stuff
        :return:
        """
        self.blockchain = Blockchain()  # initialize a blockchain
        self.testAccount1 = CryptoAccount()
        self.testAccount2 = CryptoAccount()
        self.testTransactionInput = TransactionInput(2, self.testAccount1.getAddress(), "-", -1)
        self.testTransactionOutput = TransactionOutput(1, self.blockchain.getBlockchainAccount().getAddress(),
                                                       self.testAccount1.getAddress())
        self.testTransaction = Transaction(self.blockchain.getBlockchainAccount().getAddress(),
                                           [self.testTransactionInput],
                                           [self.testTransactionOutput])

    def test_blockchainInitialization(self):
        """
        testing the initialization of the blockchain
        :return:
        """

        # check that the blockchain has acquired a crypto account (wallet)
        assert self.blockchain.getBlockchainAccount() is not None

        # check that the genesis block has been inserted in the blockchain
        assert len(self.blockchain.getChain()) == 1
        # check that the transaction input pool has one record, for the creator
        assert len(self.blockchain.getTransactionInputPool()) == 1

        # check that the total balance in the transaction input pool is the initial blockchain balance
        assert \
            self.blockchain.getAccountTotal(self.blockchain.getBlockchainAccount().getAddress()) == \
            Blockchain.BLOCKCHAIN_INITIAL_AMOUNT

        # check that there is one confirmed transaction in the transaction list
        assert len(self.blockchain.getConfirmedTransactionList()) == 1

        # check that the genesis block is signed
        genesisBlock = self.blockchain.getChain()[0]

    def test_addTransactionInputToPool(self):
        # check that the size of the transaction input pool has increased
        oldPoolLength = len(self.blockchain.getTransactionInputPool())
        self.blockchain._Blockchain__addTransactionInputToPool(self.testTransactionInput)
        newPoolLength = len(self.blockchain.getTransactionInputPool())
        assert newPoolLength == oldPoolLength + 1

        # check that the last record is the one we 've just added
        newTxAccountInputs = self.blockchain.getTransactionInputPool()[self.testTransactionInput.getRecipient()]
        accountTxInputsLength = len(newTxAccountInputs)
        assert self.testTransactionInput == newTxAccountInputs[accountTxInputsLength-1]

    def test_submitTransaction(self):
        """
        testing the submitTransaction method
        :return:
        """
        # submit a transaction to the blockchain. The sender is the blockchain
        self.blockchain.submitTransaction(
            self.blockchain.getBlockchainAccount(),
            [CoinTransfer(self.testAccount1.getAddress(), 3), CoinTransfer(self.testAccount2.getAddress(),2)]
        )
        pendingTransactionList = self.blockchain._Blockchain__pendingTransactionList
        # test that the submitted transaction has been  inserted in the pending transactions list
        assert len(pendingTransactionList) == 1

        # test that the number of output of this transaction is 2
        assert len(pendingTransactionList[0].getTransactionOutputList()) == 2

        # assert that the transaction has been signed
        assert pendingTransactionList[0].getSignature is not None

        # test that the sender account has been added to the accounts dictionary
        assert self.blockchain.getSenderAccount(pendingTransactionList[0].getSender()) is not None

    def test_signTransaction(self):
        """
        testing the signTransaction method
        :return:
        """
        # sign the transaction
        self.blockchain.signTransaction(self.testTransaction, self.blockchain.getBlockchainAccount().getPrivateKey())

        # test that the transaction has been signed
        assert self.testTransaction.getSignature() is not None

        # test that the signature is ok, by using the signer public key
        assert self.blockchain._Blockchain__verifySignature(self.testTransaction)

