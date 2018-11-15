# Updated version of my classes (9-11-2018)
# Maybe I can make a Blockchain class method that waits for 5 minutes and then tries to execute a transaction.
# It will be called in the constructor method. Or a transaction can be executed each time one wishes to transfer money
import binascii
from collections import OrderedDict
from Crypto.Hash import SHA256, SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from time import time
import hashlib, json
from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.utilities import TLCUtilities


class CoinTransfer:
    """
    simple class that holds data related to coin transfers
    """
    def __init__(self, recipient: str, value: int):
        """
        Constructor method
        :param recipient: the recipient address string
        :param value: the value of the transfer (int)
        """
        self.__recipient = recipient
        self.__value = value

    def getRecipient(self):
        """
        get the coin transfer recipient
        :return: the recipient address string
        """
        return self.__recipient

    def getValue(self):
        """
        get the value (int) transferred
        :return:
        """
        return self.__value


class TransactionInput:
    """
    class that handles transaction inputs
    """

    def __init__(self, value: int, recipient: str, previousTransactionHash: str, prevTxOutIndex: int=None):
        """
        constructor method
        :param value: the value of the tx input
        :param recipient: the address of the recipient
        :param prevTxOutIndex: the reference number of the relevant output from a previous transaction
        """
        self.__value = value
        self.__recipient = recipient
        self.__prevTxOutIndex = prevTxOutIndex
        self.__previousTransactionHash = previousTransactionHash

    def getOrderedDict(self) -> OrderedDict:
        """
        Method that returns the transaction input as an ordered dictionary
        :return: the TransactionInput object as an OrderedDictionary
        """
        return OrderedDict(
            {
                'value': self.__value,
                'recipient': self.__recipient,
                'referenceNo': self.__prevTxOutIndex,
                'previousTransactionHash': self.__previousTransactionHash
            }
        )

    def getValue(self) -> int:
        """
        method that returns the value of the tx input
        :return: the value of the tx input
        """
        return self.__value

    def setValue(self, value: int):
        """
        method that sets the tx input value
        :param value: the tx input value (int)
        :return:
        """
        self.__value = value

    def getRecipient(self) -> str:
        """
        Method for getting the tx input recipient
        :return: the recipient address
        """
        return self.__recipient

    def setRecipient(self, recipient: str):
        """
        Method that sets the recipient
        :param recipient:  the recipient address
        :return:
        """
        self.__recipient = recipient

    def getPreviousTransactionHash(self) -> str:
        """
        method that returns the hash of the previous (referenced) transaction
        :return: __previousTransactionHash class property
        """
        return self.__previousTransactionHash


class TransactionOutput:
    """
    class that handles transaction outputs
    """

    def __init__(self, value: int, sender: str, recipient: str):
        """
        constructor method
        :param value: the value of the transaction output in taliroshis (int)
        :param sender: the sender (str)
        :param recipient: the recipient (str)
        """
        self.__value = value
        self.__sender = sender
        self.__recipient = recipient

    def getOrderedDict(self) -> OrderedDict:
        """
        Method that returns the tx output object as an ordered dict
        :return: the TransactionOutput object as OrderedDictionary
        """
        return OrderedDict(
            {
                'value': self.__value,
                'sender': self.__sender,
                'recipient': self.__recipient
            }
        )

    def getValue(self) -> int:
        """
        method for getting the value
        :return: the value of the tx output
        """
        return self.__value

    def setValue(self, value: int):
        """
        set the value of the tx output
        :param value:
        :return:
        """
        self.__value = value

    def getSender(self) -> str:
        """
        returns the sender of the tx output
        :return: the sender address
        """
        return self.__sender

    def setSender(self, sender: str):
        """
        sets the sender of the tx output
        :param sender: sender address
        :return:
        """
        self.__sender = sender

    def getRecipient(self)-> str:
        """
        returns the recipient of the tx output
        :return: the recipient address
        """
        return self.__recipient

    def setRecipient(self, recipient: str):
        """
        sets the recipient of the tx output
        :param recipient:
        :return:
        """
        self.__recipient = recipient


class Transaction:
    """
    class that handles transactions
    """

    VERSION_NO = 1  # the version number for the transactions

    def __init__(self, senderAddress: str, transactionInputList: list=None, transactionOutputList: list=None):
        """
        constructor method.
        We assume that each transaction is related to only one sender.
        :param senderAddress: the address of the sender that wishes to make the transaction
        :param transactionInputList: a list with the TransactionInput objects
        :param transactionOutputList: a list with the TransactionOutput objects
        """
        self.__senderAddress = senderAddress  # the address of the sender
        if transactionInputList is None:
            self.__transactionInputList = list()  # new transaction input list
        else:
            self.__transactionInputList = transactionInputList  # set the transaction input list
        if transactionOutputList is None:
            self.__transactionOutputList = list()  # new transaction output list
        else:
            self.__transactionOutputList = transactionOutputList  # set the transaction output list

        self.__versionNo = Transaction.VERSION_NO  # the version number of the transaction. One for now.
        if transactionInputList is None:  # the counter for the number of transaction inputs
            self.__inCounter = 0
        else:
            self.__inCounter = len(transactionInputList)

        if transactionOutputList is None:  # the counter for the number of transaction outputs
            self.__outCounter = 0
        else:
            self.__outCounter = len(transactionOutputList)

        self.__transactionHash = self.__setTransactionHash()  # the transactionHash

        self.__transactionSignature = None  # the signed transaction hash - the signature of the transaction

        self.__blockNumber = None   # the number of the block where the transaction belongs (added after mining)

    def setBlockNumber(self, blockNo: int):
        """
        Method that sets the number of the block
        :param blockNo: the number of the block
        :return:
        """
        self.__blockNumber = blockNo

    def getBlockNumber(self) -> int:
        """
        Method that returns the block number of the transaction
        :return: the number (int) of the transaction if there is one, else None
        """
        return self.__blockNumber

    def sign(self, senderPrivateKey: str) -> bool:
        """
        Method that signs the transaction by using the sender's private key
        :param senderPrivateKey:  sender private key
        :return: True if signing is ok, else False
        """
        # first create the transaction hash
        transactionString = str(self.getOrderedDict())
        transactionHash = TLCUtilities.getDoubleHash256(transactionString)

        if senderPrivateKey is None:  # empty private key
            return False
        else:
            # create the private key in a form that will make signing possible
            privateKey = RSA.importKey(binascii.unhexlify(senderPrivateKey))

            # create the signer
            signer = PKCS1_v1_5.new(privateKey)

            # sign the hash of the transaction with the private key
            signedTransactionHash = binascii.hexlify(signer.sign(transactionHash)).decode('ascii')
            # set the transaction property (signedTransactionHash) and return true
            self.__transactionSignature = signedTransactionHash
            return True

    def setSignature(self, signedTransactionHash: str):
        """
        Method that sets the signed transaction hash (the signature of the transaction)
        :param signedTransactionHash:
        :return:
        """
        self.__transactionSignature = signedTransactionHash

    def getSignature(self) -> str:
        """
        Method that returns the signature of the transaction
        :return: __transactionSignature class property
        """
        return self.__transactionSignature

    def getDoubleHash(self) -> str:
        """
        Method that returns the transaction hash. It should return the same result as __getDoubleHash256, but it gets
        the data from the transaction object property __transactionHash. Therefore, it doesn't need to make the
        calculations again
        :return: the transaction hash string
        """
        return self.__transactionHash

    def getOrderedDict(self) -> OrderedDict:
        """
        Method that returns the transaction object to an ordered dict, which includes
        outputs, except from the change. The change tx output is excluded because it is
        added later, during the transaction verification and it would alter the transaction hash
        and signature (therefore would cause problem at the tx verification)
        :return: the transaction object as an ordered dictionary
        """

        """
        # first create the string for the transaction inputs
        txInputsString = ''
        for txInput in self.__transactionInputList:
            txInputsString += str(txInput.getOrderedDict())
        """

        # create the string for the transaction outputs
        txOutputsString = ''
        for txOutput in self.__transactionOutputList:
            if txOutput.getRecipient() != self.__senderAddress:  # if it is not the change tx output
                txOutputsString += str(txOutput.getOrderedDict())  # add it to the tx output string

        # finally create and return the ordered dictionary
        return OrderedDict(
            {
                'sender': self.__senderAddress,
                'txOutputList': txOutputsString,
                'versionNo': self.__versionNo,
                'outCounter': self.__outCounter
            }
        )

    def getSender(self) -> str:
        """
        Method that returns the sender address
        :return: the sender address
        """
        return self.__senderAddress


    def getTransactionHash(self) -> str:
        """
        Method that returns the transaction hash
        :return: __transactionHash string
        """
        return self.__transactionHash

    def __setTransactionHash(self) -> str:
        """
        method that calculates and sets the transaction hash of the transaction. It is called when the transaction
        inputs and outputs are ok and the transaction is ready to be executed
        :return: the transactionHash string
        """
        transactionString = str(self.getOrderedDict())
        self.__transactionHash = TLCUtilities.getDoubleHash256AsString(transactionString)
        return self.__transactionHash

    def getInCounter(self) -> int:
        """
        returns the number of transaction inputs
        :return: in-counter. Number of transaction inputs
        """
        return self.__inCounter

    def getOutCounter(self) -> int:
        """
        returns the number of transaction outputs
        :return: out-counter. Number of transaction outputs
        """
        return self.__outCounter

    def getTransactionOutputList(self)-> list:
        """
        method that returns the list of transaction output objects
        :return: list of TransactionOutput Objects
        """
        return self.__transactionOutputList

    def getTransactionInputList(self) -> list:
        """
        method for returning the list of transaction inputs
        :return: a list of TransactionInput objects
        """
        return self.__transactionInputList

    def getTransactionInputsTotalValue(self) -> int:
        """
        method that calculates and returns the total value of the transaction inputs
        :return: the total value of the transaction inputs (int)
        """
        totalValue = 0
        for tInput in self.__transactionInputList:
            totalValue = totalValue + tInput.getValue()
        return totalValue

    def getTransactionOutputsTotalValue(self) -> int:
        """
        method for calculating the total value of all transaction outputs
        :return: the total value of all transaction outputs in taliroshis (int)
        """
        transactionOutputsTotalValue = 0
        for tOutput in self.__transactionOutputList:
            transactionOutputsTotalValue = transactionOutputsTotalValue + tOutput.getValue()
        return transactionOutputsTotalValue

    def extendTransactionInputList(self, tInputsNecessary: list):
        """
        Method that extends the tx input list and increases the in-counter
        :param tInputsNecessary: list of transaction input objects
        :return:
        """
        self.__transactionInputList.extend(tInputsNecessary)  # add the list of inputs
        self.__inCounter += len(tInputsNecessary)  # increase the in-counter

    def addTransactionOutput(self, txOutput: TransactionOutput):
        """
        method for adding a tx output to the transaction output list and increasing the out-counter
        :param txOutput: the TransactionOutput object
        :return:
        """
        self.__transactionOutputList.append(txOutput)  # add the output
        self.__outCounter += 1  # increase the out-counter


class Block:
    """
    Class for implementing the transaction Blocks
    """

    BLOCK_VERSION = 1  # the version of the blocks

    def __init__(self, chain: list, nonce: int = None, previousBlockHash: str = None):
        """
        Constructor method for the block. Sets the block content
        :param chain: the chain that contains the blocks
        :param nonce: the nonce
        that will be included in the block
        :param previousBlockHash: the hash of the previous block
        """

        if chain is not None:  # if the constructor has data to initialize the object
            self.__version = Block.BLOCK_VERSION
            self.__blockNumber = len(chain) + 1
            self.__timeStamp = time()
            # self.__transactions = transactions
            self.__nonce = nonce
            self.__previousBlockHash = previousBlockHash
            self.__transactions = list()
            self.__merkleRoot = None  # set the merkle root of the block

    def setTransactionList(self, transactionList: list):
        """
        Method that sets the transaction list of the block and calculates the merkle root
        :param transactionList: list of Transaction Objects
        :return:
        """
        self.__transactions = transactionList
        self.__merkleRoot = self.getMerkleRoot()  # set the merkle root of the block

    def getTransactionList(self) -> list:
        """
        get the transaction list of the block
        :return: list of Transaction objects
        """
        return self.__transactions

    def addTransaction(self, transaction: Transaction):
        """
        Method that adds a transaction and recalculates the merkle root
        :param transaction: Transaction object
        :return:
        """
        self.__transactions.append(transaction)
        self.__merkleRoot = self.getMerkleRoot()

    def getBlockNumber(self) -> int:
        """
        Method that returns the block number
        :return: block number (int)
        """
        return self.__blockNumber

    def getOrderedDictionary(self) -> OrderedDict:
        """
        returns the block content as a dictionary.
        The transactions are included as ordered dictionaries converted to string. Therefore, for the transactions
        the result is a long string.
        :return: the block content as dictionary
        """

        # setup the transactions dict
        transactionsString = ''
        for transaction in self.__transactions:
            transactionsString += str(transaction.getOrderedDict())

        return OrderedDict({
            'block_number': self.__blockNumber,
            'timestamp': self.__timeStamp,
            'transactions': transactionsString,  # long string-concatenation of the string of the tx ordered dicts
            'nonce': self.__nonce,
            'previous_hash': self.__previousBlockHash,
            'merkle_root': self.__merkleRoot,
            'version': self.__version
        })

    def getBlockHash(self) -> str:
        """
        returns the SHA-256 hash of the block content
        :return: the hash of the block content as string
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(self.getOrderedDictionary(), sort_keys=True).encode()

        return SHA256.new(block_string).hexdigest()

    def getPreviousBlockHash(self) -> str:
        """
        returns the block hash of the previous block
        :return: __previousHash property (string)
        """
        return self.__previousBlockHash

    def setPreviousBlockHash(self, prevBlockHash: str):
        """
        Method that sets the previous block hash property of the block
        :param prevBlockHash: the hash of the previous block
        :return:
        """
        self.__previousBlockHash = prevBlockHash

    def setNonce(self, nonce: int):
        """
        method that sets the nonce of the block
        :param nonce:
        :return:
        """
        self.__nonce = nonce

    def getMerkleRoot(self) -> str:
        """
        method that calculates and returns the merkle root of the block.
        It uses a two dimensional array (finalDoubleHashes) which stores the double hashes
        of each level (the first dimension is the level and the second the items of the level)
        :return: the merkle root string if there are transactions, else None
        """

        if len(self.__transactions) > 0:  # if there are transactions
            # collect all the transaction hashes
            transactionDoubleHashes = []
            for transaction in self.__transactions:
                transactionDoubleHashes.append(transaction.getDoubleHash())

            # if the number of items is even, add the last one, one more time
            if len(transactionDoubleHashes) % 2 == 1:
                transactionDoubleHashes.append(transactionDoubleHashes[len(transactionDoubleHashes) - 1])

            l = len(transactionDoubleHashes)
            iterNo = 0  # no of iteration. Level of the tree
            finalDoubleHashes = list()
            finalDoubleHashes.append(transactionDoubleHashes)
            while l / 2 >= 1:  # till you reach the merkle root

                iterNo = iterNo + 1  # increase the number of the iteration

                # if the number of elements is even, add one more
                if len(finalDoubleHashes[iterNo - 1]) % 2 == 1:
                    finalDoubleHashes[iterNo - 1].append(
                        finalDoubleHashes[iterNo - 1][len(finalDoubleHashes[iterNo - 1]) - 1])

                finalDoubleHashes.append([])  # add a new empty list
                # concatenate the double hashes and then double hash, until you get to the root
                i = 0
                for i in range(0, l, 2):
                    finalDoubleHashes[iterNo].append(
                        TLCUtilities.
                            getDoubleHash256AsString(finalDoubleHashes[iterNo - 1][i] + finalDoubleHashes[iterNo - 1][i + 1])
                    )
                l = int(l / 2)  # divide to 2, to get the number of elements of the tree level above

            return finalDoubleHashes[iterNo][0]

        else:  # no transactions in the block
            return None

    def getTransactionsHash(self) -> str:
        """
        Method that returns a hash string concatenation of all the transactions included in the hash
        :return: transactions hash string
        """
        hashConcat = ''
        for transaction in self.__transactions:
            hashConcat += transaction.getTransactionHash()
        return hashConcat


class Blockchain:
    """
    class that handles the blockchain
    """

    MINING_DIFFICULTY = 2  # the mining difficulty
    BLOCKCHAIN_INITIAL_AMOUNT = 100

    def __init__(self):
        """
        constructor method
        """
        self.__name = 'TLC Creator'  # the name of the blockchain creator

        # create the dictionary containing all the accounts (wallets) that make transactions (senders)
        # the keys are the addresses and the values are dictionaries
        self.__senderAccounts = dict()

        self.__transactionInputPool = dict()  # pool with available transaction inputs. These are the unspent money
        self.__pendingTransactionList = list()  # the list that contains all the pending transactions
        self.__confirmedTransactionList = list()  # the list of executed (confirmed) transactions
        self.__chain = list()  # the chain of confirmed blocks

        # generate a crypto wallet for the genesis transaction
        self.__cryptoAccount = CryptoAccount()

        self.__executeGenesisTransaction(Blockchain.BLOCKCHAIN_INITIAL_AMOUNT)  # the genesis transaction of the system. 100 taliroshis

    def __addSenderAccount(self, address: str, publicKey: str):
        """
        method that adds to the accounts dictionary a new account, if it doesn't already exist
        :param address:
        :param publicKey:
        :return:
        """
        if self.__senderAccounts.get(address) is None:  # if the account does not exist in the dictionary
            self.__senderAccounts[address] = {
                'publicKey': publicKey
            }

    def getSenderAccount(self, address: str) -> dict:
        """
        method that returns the information about an account based on it's address
        :param address: the address of th account
        :return: the account info (dictionary)
        """
        return self.__senderAccounts.get(address)

    def getBlockchainAccount(self) -> CryptoAccount:
        """
        Method that returns the crypto wallet of the blockchain
        :return: CryptoWallet object
        """
        return self.__cryptoAccount

    def getChain(self) -> list:
        """
        Method that returns the chain of the blocks
        :return: list of Block objects
        """
        return self.__chain

    def getTransactionInputPool(self) -> dict:
        """
        method that returns the transaction input pool of the blockchain
        :return:  __transactionInputPool class property
        """
        return self.__transactionInputPool

    def getConfirmedTransactionList(self) -> list:
        """
        Method that returns the transaction list of the blockchain
        :return: __transactionList class property
        """
        return self.__confirmedTransactionList

    def __executeGenesisTransaction(self, value: int):
        """
        Method that executes the genesis transaction (the first transaction of the blockchain)
        :param value: the value of the genesis transaction
        :return:
        """

        # create the genesis transaction and block and add it to the chain
        genesisBlock = Block(self.__chain, -1, '-')  # genesis block

        genesisTxOutput = TransactionOutput(value, self.__cryptoAccount.getAddress(),
                                            self.__cryptoAccount.getAddress())
        genesisTransaction = Transaction(self.__cryptoAccount.getAddress(), None,
                                         [genesisTxOutput])

        genesisTransaction.setBlockNumber(genesisBlock.getBlockNumber())
        genesisTransaction.sign(self.getBlockchainAccount().getPrivateKey())

        genesisBlock.setTransactionList([genesisTransaction])  # set the genesis block transaction list
        self.__chain.append(genesisBlock)

        # add the transaction to the list of the confirmed transactions
        self.__confirmedTransactionList.append(genesisTransaction)

        # add the blockchain account to the accounts dictionary
        self.__addSenderAccount(self.getBlockchainAccount().getAddress(), self.getBlockchainAccount().getPublicKey())

        # last but not least add a transaction input to the tx input pool, towards the creator
        genesisTxInput = TransactionInput(value, self.__cryptoAccount.getAddress(), '-', -1)
        self.__addTransactionInputToPool(genesisTxInput)  # add genesis tx input to the pool

    def getAccountTotal(self, accountAddress: str) -> int:
        """
        method for getting the total for an account address. It calculates the total from the transaction inputs that exist
        in the transaction input pool
        :return: the account total (int)
        """

        accountAddressInputs = self.__transactionInputPool.get(accountAddress)
        if accountAddressInputs is None:  # case the address does not exist in the transaction input pool
            return 0
        else:
            total = 0
            for tInput in accountAddressInputs:  # for each of the accounts transaction inputs
                total = total + tInput.getValue()
            return total

    def __addTransactionInputToPool(self, tInput: TransactionInput):
        """
        method that adds a transaction input to the transaction input pool. The transaction input pool is a dictionary
        whose keys are the recipient addresses and the values the transaction input objects.
        :param tInput: the transaction input object that will be added to the pool
        """
        if self.__transactionInputPool.get(
                tInput.getRecipient()) is None:  # if the specific recipient does not exist in the dictionary
            self.__transactionInputPool[
                tInput.getRecipient()] = list()  # create a list with the recipient's transaction inputs

        self.__transactionInputPool[tInput.getRecipient()].append(tInput)

    def printAccountTotals(self):
        """
        Method for printing the account totals for the accounts in the blockchain transaction input pool
        :return:
        """

        # get all the keys (account addresses) of the transaction input pool
        accountAddresses = list(self.__transactionInputPool.keys())

        print('\n--- BLOCKCHAIN ACCOUNT TOTALS ---')
        # for each key (account address), print the account total
        for accountAddress in accountAddresses:
            print(
                'The total for the account ' + accountAddress +
                " is " + str(self.getAccountTotal(accountAddress))
            )

    def submitTransaction(self, senderAccount: CryptoAccount, coinTransfers: list):
        """
        Method for creating and submitting the transaction to the pending transaction list.
        Only the outputs are added. The inputs will be added at the mining/confirmation phase.
        It also adds the sender to the accounts list of the blockchain

        :param senderAccount: the sender CryptoAccount object
        :param coinTransfers: the list of coin transfers (CoinTransfer objects)
        :return:
        """
        senderAddress = senderAccount.getAddress()
        senderPrivateKey = senderAccount.getPrivateKey()
        senderPublicKey = senderAccount.getPublicKey()

        # create the transaction
        t = Transaction(senderAddress)  # initiate a new transaction and add the outputs
        for coinTransfer in coinTransfers:
            t.addTransactionOutput(TransactionOutput(
                coinTransfer.getValue(), senderAddress, coinTransfer.getRecipient()))

        # sign the transaction
        t.sign(senderPrivateKey)

        # add the transaction to the pending transaction list
        self.__pendingTransactionList.append(t)

        # add the sender to the accounts dictionary
        self.__addSenderAccount(senderAddress, senderPublicKey)

    def signTransaction(self, transaction: Transaction, privateKeyString: str) -> str:
        """
        Method that signs the transaction and adds the signature to the transaction data that will be appended
        to the blockchain
        :param transaction: the Transaction to be signed
        :param privateKeyString: the private key of the signer
        :return: the transaction signature if everything ok, else None
        """

        # get the transaction hash string
        transactionString = transaction.getDoubleHash()

        if privateKeyString is None:  # empty private key
            return None
        else:
            # create the private key in a form that will make signing possible
            privateKey = RSA.importKey(binascii.unhexlify(privateKeyString))

            # create the signer
            signer = PKCS1_v1_5.new(privateKey)
            # create the hash of the transaction
            h = SHA.new(transactionString.encode('utf8'))
            # sign the hash of the transaction with the private key
            signedTransactionHash = binascii.hexlify(signer.sign(h)).decode('ascii')
            # set the transaction property (signedTransactionHash) and return true
            transaction.setSignature(signedTransactionHash)
            return signedTransactionHash

    def executeTransactions(self, currentBlock: Block) -> int:
        """
        Method that verifies the transactions that are in the pending list, forges a new blocks and adds them
        to the blockchain
        :param currentBlock: the current Block, to which the transactions will be added
        :return: number of transactions added to the blockchain
        """
        # TODO: add some incentives for miners (cryptoeconomics)
        transactionsAdded = 0  # number of transactions added to the blockchain

        # for each transaction in the pending transaction list
        for pendingTransaction in self.__pendingTransactionList:

            # verify the signature of the transaction using the public key of the sender
            verificationResult = self.__verifySignature(pendingTransaction)

            if not verificationResult:
                break  # stop with the current pending transaction. Go to the next one

            # verify that the sender account balance is enough for the transaction to take place
            txOutTotalValue = 0  # total value of transaction outputs
            for txOutput in pendingTransaction.getTransactionOutputList():
                txOutTotalValue += txOutput.getValue()
            accountBalance = self.getAccountTotal(pendingTransaction.getSender())
            if txOutTotalValue > accountBalance:  # if the balance is not enough, stop with this transaction
                break

            # mine the transaction (add it to the block, add block number etc.)

            # add some tx inputs
            senderTxInputPool = self.__transactionInputPool.get(pendingTransaction.getSender())  # sender tx inputs
            txInputTotalValue = 0
            txInputList = list()
            i = 0
            while txInputTotalValue < txOutTotalValue:
                txInputTotalValue += senderTxInputPool[i].getValue()  # increase the tx input total value
                txInputList.append(senderTxInputPool[i])  # create the tx input list
                senderTxInputPool.remove(senderTxInputPool[i])  # remove the tx input from the resources available
                i += 1
            # txInputList.append(senderTxInputPool[i])  # add one final input
            # senderTxInputPool.remove(senderTxInputPool[i])
            pendingTransaction.extendTransactionInputList(txInputList)  # set the tx input list of the transaction

            # if there is any change, create a new tx output
            if txInputTotalValue > txOutTotalValue:
                pendingTransaction.addTransactionOutput(
                    TransactionOutput(txInputTotalValue-txOutTotalValue, pendingTransaction.getSender(),
                                      pendingTransaction.getSender())
                )

            # add the transaction to the block
            pendingTransaction.setBlockNumber(currentBlock.getBlockNumber())  # set the block number
            currentBlock.addTransaction(pendingTransaction)

            # add the transaction to the confirmed transactions list
            self.__confirmedTransactionList.append(pendingTransaction)

            # create some inputs for the input pool
            for txOutput in pendingTransaction.getTransactionOutputList():
                self.__addTransactionInputToPool(
                    TransactionInput(txOutput.getValue(),
                                     txOutput.getRecipient(),
                                     pendingTransaction.getTransactionHash(),
                                     pendingTransaction.getTransactionOutputList().index(txOutput)
                                     )
                )

            # increase the number of transactions added
            transactionsAdded += 1

        # set the __previousBlockHash property of the block
        previousBlock = self.__chain[len(self.__chain)-1]
        currentBlock.setPreviousBlockHash(previousBlock.getBlockHash())

        # mine the block
        nonce = self.__getProofOfWork(currentBlock)
        currentBlock.setNonce(nonce)  # set the nonce of the block

        # add the block to the chain
        self.__chain.append(currentBlock)

        # reset the pending transaction list
        self.__pendingTransactionList = list()

        return transactionsAdded

    def __verifySignature(self, transaction: Transaction) -> bool:
        """
        Verifies the transaction signature of a transaction
        :param transaction: the Transaction object
        :return: True if verified, else false
        """
        senderPublicKey = self.getSenderAccount(transaction.getSender()).get('publicKey')
        publicKey = RSA.importKey(binascii.unhexlify(senderPublicKey))
        verifier = PKCS1_v1_5.new(publicKey)
        txString = str(transaction.getOrderedDict())
        h = TLCUtilities.getDoubleHash256(txString)
        result = verifier.verify(h, binascii.unhexlify(transaction.getSignature()))

        if result:
            return True
        else:
            return False

    def __getProofOfWork(self, block: Block) -> int:
        """
        Proof of work algorithm. Returns the nonce, when successfully completed
        :param block: the block on which the proof of work process will take place
        :return: the nonce (int)
        """
        blockTransactionsHash = block.getTransactionsHash()  # get the block transactions hash
        prevBlockHash = block.getPreviousBlockHash()

        nonce = 0  # nonce - starts from zero
        # search while you find a valid proof
        while not self.__validProof(nonce, blockTransactionsHash, prevBlockHash):
            nonce += 1

        return nonce

    def __validProof(self, nonce: int, blockTransactionsHash: str,
                     prevBlockHash: str, miningDifficulty: int = MINING_DIFFICULTY) -> bool:
        """
        Method that checks the proof for a specific nonce. If ok, returns True, else returns False
        :param nonce: the nonce to be checked
        :param blockTransactionsHash: the hash of the transactions of the block
        :param prevBlockHash: the hash of the previous block
        :param miningDifficulty: the mining difficulty
        :return: True if ok, else False
        """
        guess = (blockTransactionsHash + prevBlockHash + str(nonce)).encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:miningDifficulty] == '0' * miningDifficulty
