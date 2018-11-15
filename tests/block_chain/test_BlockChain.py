import unittest
import random
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
        # list of coin transfers used for testing
        self.testCoinTransferList1 = list()
        self.testCoinTransferList2 = list()

        self.testCoinTransferList1 = [
            CoinTransfer(self.testAccount1.getAddress(), 10),
            CoinTransfer(self.testAccount2.getAddress(), 20)
        ]

        self.testCoinTransferList2 = [
            CoinTransfer(self.testAccount2.getAddress(), 30)
        ]

        self.testCoinTransferList3 = [
            CoinTransfer(self.testAccount1.getAddress(), Blockchain.BLOCKCHAIN_INITIAL_AMOUNT*2),
            CoinTransfer(self.testAccount2.getAddress(), Blockchain.BLOCKCHAIN_INITIAL_AMOUNT*2)
        ]

        self.testCoinTransferList4 = [
            CoinTransfer(self.testAccount2.getAddress(), Blockchain.BLOCKCHAIN_INITIAL_AMOUNT*2)
        ]

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

    def test___verifySignature(self):
        """
        testing the __verifySignature method
        :return:
        """
        # sign the transaction
        self.testTransaction.sign(self.blockchain.getBlockchainAccount().getPrivateKey())
        # test that the transaction has been signed
        assert self.testTransaction.getSignature() is not None

        # test that the signature is ok, by using the signer public key
        assert self.blockchain._Blockchain__verifySignature(self.testTransaction)

    def test_executeFeasibleTransactions(self):
        """
        test the executeTransactions method, for some feasible transactions.
        In this case, all the transactions of the block must be inserted in the chain.
        :return:
        """

        # add some transactions to the list of pending transactions
        self.blockchain.submitTransaction(
            self.blockchain.getBlockchainAccount(), self.testCoinTransferList1
        )
        self.blockchain.submitTransaction(
            self.blockchain.getBlockchainAccount(), self.testCoinTransferList2
        )

        # check that the two transactions have been added to the pending transactions list
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 2

        # create a new block
        currentBlock = Block(self.blockchain.getChain(), None, None)

        # execute the transactions
        self.blockchain.executeTransactions(currentBlock)

        # check that the pending transactions list is empty
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 0

        # check that the block has been added to the blockchain
        assert len(self.blockchain.getChain()) == 2

        # check the block variables
        validBlock = self.blockchain.getChain()[1]
        # block number
        assert validBlock._Block__blockNumber == 2
        # hash of the previous block
        assert \
            validBlock._Block__previousBlockHash == self.blockchain.getChain()[0].getBlockHash()
        # merkle root
        assert validBlock._Block__merkleRoot == validBlock.getMerkleRoot()

        # check that in the confirmed transaction list of the blockchain, all the transactions
        # of the specific block have been inserted

        noOfBlockConfirmedTransactions = 0  # number of confirmed transactions of the block in the confirmed list

        for confirmedTransaction in self.blockchain.getConfirmedTransactionList():
            if confirmedTransaction.getBlockNumber() == validBlock.getBlockNumber():
                noOfBlockConfirmedTransactions += 1

        assert noOfBlockConfirmedTransactions == 2
        print(self.blockchain.printAccountTotals())


    def test_executeInfeasibleTransactions(self):
        """
        testing the scenario where none of the transactions can take place because there are not enough money.
        In this case no block will be added to the chain and no transactions to the confirmed transaction list
        :return:
        """
        # submit the infeasible transactions
        self.blockchain.submitTransaction(
            self.blockchain.getBlockchainAccount(), self.testCoinTransferList3
        )

        self.blockchain.submitTransaction(
            self.blockchain.getBlockchainAccount(), self.testCoinTransferList4
        )

        # check that the two transactions have been inserted in the pending transaction list
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 2

        # try to execute the transactions
        currentBlock = Block(self.blockchain.getChain(), None, None)
        self.blockchain.executeTransactions(currentBlock)

        # check that the block hasn't been added. Only the genesis block exists
        assert len(self.blockchain.getChain()) == 1

        # check that the pending transaction list is empty. The transactions have been rejected
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 0

    def test_executeSomeFeasibleTransactions(self):
        """
        test the case where only some feasible transactions exist. Then, the block must be added
        to the chain, so do the feasible transactions
        :return:
        """

        # two feasible and two infeasible coin transfers

        coinTransferList1 = [  # feasible coin transfer
            CoinTransfer(self.testAccount1.getAddress(), 10),
            CoinTransfer(self.testAccount2.getAddress(), 30),
        ]

        coinTransferList2 = [  # infeasible coin transfer
            CoinTransfer(self.testAccount1.getAddress(), 10),
            CoinTransfer(self.testAccount2.getAddress(), 3*Blockchain.BLOCKCHAIN_INITIAL_AMOUNT),
        ]

        coinTransferList3 = [  # infeasible coin transfer
            CoinTransfer(self.testAccount1.getAddress(), 2*Blockchain.BLOCKCHAIN_INITIAL_AMOUNT),
            CoinTransfer(self.testAccount2.getAddress(), 3*Blockchain.BLOCKCHAIN_INITIAL_AMOUNT),
        ]

        coinTransferList4 = [  # feasible coin transfer
            CoinTransfer(self.testAccount1.getAddress(), 20),
            CoinTransfer(self.testAccount2.getAddress(), 20),
        ]

        # submit the transactions
        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList1)
        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList2)
        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList3)
        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList4)

        # check that all transactions have been added to the pending transaction list
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 4

        # try to execute all the transactions
        currentBlock = Block(self.blockchain.getChain(), None, None)
        self.blockchain.executeTransactions(currentBlock)

        # check that the pending transaction list is empty
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 0

        # check that the block has been added to the chain
        assert len(self.blockchain.getChain()) == 2

        # check than only two transactions exist in this block
        validBlock = self.blockchain.getChain()[1]
        assert len(validBlock.getTransactionList()) == 2

        # check that only two transactions have been added to the confirmed transaction list
        assert len(self.blockchain._Blockchain__confirmedTransactionList) == 3

        # check the account totals/balances
        assert self.blockchain.getAccountTotal(
            self.blockchain.getBlockchainAccount().getAddress()
        ) == 20
        assert self.blockchain.getAccountTotal(
            self.testAccount1.getAddress()
        ) == 30
        assert self.blockchain.getAccountTotal(
            self.testAccount2.getAddress()
        ) == 50

    def test_executeTransactionsMultipleSenders(self):
        """
        Block No 2
        The blockchain sends to account1 30 and to account2 20.
        Account1 sends to account2 20.
        Account3 (doesn't have any money) tries to send 50 to account 2.
        Account totals: blockchain: 50, account1: 10, account2: 40, account3: 0
        Block mined
        Block No 3
        Account2 tries to send  50 to account1
        account1 sends 10 to account3
        Account totals: blockchain: 50, account1: 0, account2: 40, account3: 10
        Block mined.

        :return:
        """
        coinTransferList1 = [
            CoinTransfer(self.testAccount1.getAddress(), 30),
            CoinTransfer(self.testAccount2.getAddress(), 20)
        ]
        coinTransferList2 = [
            CoinTransfer(self.testAccount2.getAddress(), 20)
        ]
        coinTransferList3 = [
            CoinTransfer(self.testAccount2.getAddress(), 50)
        ]

        self.blockchain.submitTransaction(self.blockchain.getBlockchainAccount(), coinTransferList1)
        self.blockchain.submitTransaction(self.testAccount1, coinTransferList2)
        testAccount3 = CryptoAccount()  # account with no money
        self.blockchain.submitTransaction(self.testAccount2, coinTransferList3)
        currentBlock = Block(self.blockchain.getChain())
        self.blockchain.executeTransactions(currentBlock)
        assert self.blockchain.getAccountTotal(
            self.blockchain.getBlockchainAccount().getAddress()
        ) == 50
        assert self.blockchain.getAccountTotal(self.testAccount1.getAddress()) == 10
        assert self.blockchain.getAccountTotal(self.testAccount2.getAddress()) == 40
        assert self.blockchain.getAccountTotal(testAccount3.getAddress()) == 0

        # Second block was mined

        coinTransferList4 = [
            CoinTransfer(self.testAccount1.getAddress(), 50),
        ]
        coinTransferList5 = [
            CoinTransfer(testAccount3.getAddress(), 10)
        ]
        self.blockchain.submitTransaction(self.testAccount2, coinTransferList4)
        self.blockchain.submitTransaction(self.testAccount1, coinTransferList5)

        newCurrentBlock = Block(self.blockchain.getChain())
        self.blockchain.executeTransactions(newCurrentBlock)

        assert self.blockchain.getAccountTotal(
            self.blockchain.getBlockchainAccount().getAddress()
        ) == 50
        assert self.blockchain.getAccountTotal(self.testAccount1.getAddress()) == 0
        assert self.blockchain.getAccountTotal(self.testAccount2.getAddress()) == 40
        assert self.blockchain.getAccountTotal(testAccount3.getAddress()) == 10

        # check that total blocks are 3
        assert len(self.blockchain.getChain()) == 3
        # check that total confirmed transactions are 4
        assert len(self.blockchain._Blockchain__confirmedTransactionList) == 4
        # check that the pending transaction list is empty
        assert len(self.blockchain._Blockchain__pendingTransactionList) == 0
        # check that the numbers and the previous hashes of the blocks are ok
        i = 1
        for block in self.blockchain.getChain():
            assert block.getBlockNumber() == i
            if i > i:  # check the previous hashes except from the genesis block
                assert self.blockchain.getChain()[i-2].getBlockHash() == block._Blockchain__previousBlockHash
            i += 1





    def test_executeTransactionToOneSelf(self):
        """
        Testing the case where one tries to send coins to oneself
        blockchain sends 50 to testAccount 1.
        Test account 1 sends 30 to himself.
        Totals: blockchain: 50, testAccount1: 50
        :return:
        """

        coinTransferList1 = [
            CoinTransfer(self.testAccount1.getAddress(), 50)
        ]







