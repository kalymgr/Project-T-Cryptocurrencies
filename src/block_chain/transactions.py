# Updated version of my classes (9-11-2018)
# Maybe I can make a Blockchain class method that waits for 5 minutes and then tries to execute a transaction.
# It will be called in the constructor method. Or a transaction can be executed each time one wishes to transfer money
import binascii
from collections import OrderedDict
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from time import time
import hashlib, json
from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.smart_contracts import SmartContractTransactionTypes, SmartContractScripts, SmartContractLanguage
from src.p2p_network.parameters import Parameters
from src.utilities.utilities import TLCUtilities


class CoinTransfer:
    """
    simple class that holds data related to coin transfers
    """
    def __init__(self, recipient: CryptoAccount, value: int):
        """
        Constructor method
        :param recipient: the recipient address (CryptoAccount object)
        :param value: the value of the transfer (int)
        """
        self.__recipient = recipient
        self.__value = value

    def getRecipient(self):
        """
        get the coin transfer recipient
        :return: the recipient address (CryptoAccount)
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
        self.__script = None  # the script of the transaction input

    def setScript(self, script: str):
        """
        sets the script of the tx input (__script property)
        :param script:
        :return:
        """
        self.__script = script

    def getScript(self) -> str:
        """
        returns the script of the tx input (__script property)
        :return:
        """
        return self.__script

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
        self.__script = None  # the script of the tx output

    def setScript(self, script: str):
        """
        sets the script of the tx output (__script property)
        :param script: the script string
        :return:
        """
        self.__script = script

    def getScript(self) -> str:
        """
        returns the script of the tx output (__script property)
        :return: script string
        """
        return self.__script

    def getOrderedDict(self) -> OrderedDict:
        """
        Method that returns the tx output object as an ordered dict
        :return: the TransactionOutput object as OrderedDictionary
        """
        return OrderedDict(
            {
                'value': self.__value,
                'sender': self.__sender,
                'recipient': self.__recipient,
                'script': self.__script
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
        transactionHash = TLCUtilities.getDoubleHash256AsString(transactionString)

        if senderPrivateKey is None:  # empty private key
            return False
        else:

            signedTransactionHash = TLCUtilities.getHashSignature(transactionHash, senderPrivateKey)

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


class BlockHeader:
    """
    Class for managing block headers
    """
    def __init__(self, version: int, targetThreshold: int, prevBlockHeaderHash: str, nonce: int,
                 merkleRoot: str = None, timeStartHashing: int = None):
        """
        :param version: the version of the block. Defines validation rules.
        :param prevBlockHeaderHash: the hash of the previous block header
        :param merkleRoot: the merkle root of the block transactions
        :param timeStartHashing: the time the miner started mining the header
        :param targetThreshold: the target threshold for the PoW algorithm
        :param nonce: the nonce that is used by the proof of work algorithm
        """

        self.version = version
        self.prevBlockHeaderHash = prevBlockHeaderHash
        self.merkleRoot = merkleRoot
        self.timeStartHashing = timeStartHashing
        self.targetThreshold = targetThreshold
        self.nonce = nonce  # the nonce that is used by the proof of work algorithm


class Block:
    """
    Class for implementing the transaction Blocks
    """

    BLOCK_VERSION = 1  # the version of the blocks

    def __init__(self, chain: list, nonce: int = None, targetThreshold: int = Parameters.TARGET_THRESHOLD,
                 previousBlockHash: str = None, version: int = Parameters.BLOCK_VERSION):
        """
        Constructor method for the block. Sets the block content
        :param chain: the chain that contains the blocks
        :param nonce: the nonce
        that will be included in the block
        :param targetThreshold: the target threshold for the PoW mining algorithm
        :param previousBlockHash: the hash of the previous block
        :param version: the block version
        """

        if chain is not None:  # if the constructor has data to initialize the object
            timeOfStartMining = time()  # time the mining has started
            # set the block header
            self.blockHeader = BlockHeader(prevBlockHeaderHash=previousBlockHash,
                                           version=version, timeStartHashing=timeOfStartMining,
                                           targetThreshold=targetThreshold, nonce=nonce)
            self.__blockNumber = len(chain)
            # self.__transactions = transactions
            self.__transactions = list()

    def setTransactionList(self, transactionList: list):
        """
        Method that sets the transaction list of the block and calculates the merkle root
        :param transactionList: list of Transaction Objects
        :return:
        """
        self.__transactions = transactionList
        self.blockHeader.merkleRoot = self.getMerkleRoot()  # set the merkle root of the block

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
        self.blockHeader.merkleRoot = self.getMerkleRoot()

    def getBlockNumber(self) -> int:
        """
        Method that returns the block number
        :return: block number (int)
        """
        return self.__blockNumber

    def getOrderedDictionary(self) -> OrderedDict:
        """
        returns the block header as a dictionary. It will be used for hashing and proof of work.

        :return: the block header as dictionary
        """
        return OrderedDict({
            'block_number': self.__blockNumber,
            'timestamp': self.blockHeader.timeStartHashing,
            'previous_hash': self.blockHeader.prevBlockHeaderHash,
            'merkle_root': self.blockHeader.merkleRoot,
            'version': self.blockHeader.version
        })

    def getBlockHeaderHash(self) -> str:
        """
        returns the SHA-256 hash of the block header. It will be used for the proof of work.
        :return: the hash of the block header as string
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(self.getOrderedDictionary(), sort_keys=True).encode()

        return SHA256.new(block_string).hexdigest()

    def getPreviousBlockHeaderHash(self) -> str:
        """
        returns the block hash of the previous block
        :return: __previousHash property (string)
        """
        return self.blockHeader.prevBlockHeaderHash

    def setPreviousBlockHeaderHash(self, prevBlockHash: str):
        """
        Method that sets the previous block hash property of the block
        :param prevBlockHash: the hash of the previous block
        :return:
        """
        self.blockHeader.prevBlockHeaderHash = prevBlockHash

    def setNonce(self, nonce: int):
        """
        method that sets the nonce of the block
        :param nonce:
        :return:
        """
        self.blockHeader.nonce = nonce

    def getNonce(self) -> int:
        """
        returns the nonce of the block
        :return: __nonce object property
        """
        return self.blockHeader.nonce

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
                            getDoubleHash256AsString(
                            finalDoubleHashes[iterNo - 1][i] + finalDoubleHashes[iterNo - 1][i + 1]
                        )
                    )
                l = int(l / 2)  # divide to 2, to get the number of elements of the tree level above

            return finalDoubleHashes[iterNo][0]

        else:  # no transactions in the block
            return None


class Blockchain:
    """
    class that handles the blockchain
    """

    MINING_DIFFICULTY = Parameters.TARGET_THRESHOLD  # the mining difficulty
    BLOCKCHAIN_INITIAL_AMOUNT = 100  # taliroshis used for the genesis transaction

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

        self.__headerChain = list()  # a list with block headers

        """
        UTXO SET. 
        It will have Bitcoin 0.15 format. Also, Bitcoin stores UTXO set on the hard disk using LEVELDB database. 
        The file set is called 'chainstate'.
        Each record will be an output (keys-values). The key will contain the transaction hash and the index of the 
        unspent output, preceeded by the 'C' character prefix. The value will include (a) the block height, (b) whether
        the output is coinbase or not  (b) the value (c) the type and output script.
        """
        self.__UTXOSet = dict()  # the list of unspent transaction outputs. It is altered by transactions

        # generate a crypto wallet for the genesis transaction
        self.__cryptoAccount = CryptoAccount()

        # the genesis transaction of the system
        self.__executeGenesisTransaction(Blockchain.BLOCKCHAIN_INITIAL_AMOUNT)

    def getHeaderChain(self) -> list:
        """
        returns the chain of block headers
        :return:
        """
        return self.__headerChain

    def addToHeaderChain(self, blockHeader: BlockHeader):
        """
        Adds a block header to the block header chain
        :param blockHeader: a BlockHeader object
        :return:
        """
        self.__headerChain.append(blockHeader)

    def getUTXOSetTxOutputKey(self, transactionHash: str, txOutputIndex: int) -> str:
        """
        creates and returns the key that will be used when storing the tx output in the utxo set dictionary
        :param transactionHash: the transaction hash string
        :param txOutputIndex: the tx output index
        :return: utxo set tx output key (string)
        """
        return transactionHash + '_' + str(txOutputIndex)

    def getTransactionHashFromUTXOSetKey(self, utxoSetKey: str) -> str:
        """
        given a key of the utxo set, it returns only the transaction hash string
        :param utxoSetKey:
        :return:
        """
        return utxoSetKey[:utxoSetKey.find('_')]  # return the part of the string till the _

    def getTxOutputIndexFromUTXOSetKey(self, utxoSetKey: str) -> str:
        """
        given a key of the utxo set, it returns only the transaction output index in the specific transaction
        :param utxoSetkey: the utxo set key (string)
        :return: the tx output index (str)
        """
        return utxoSetKey[utxoSetKey.find('_')+1:len(utxoSetKey)]

    def addTxOutputToUTXOSet(self, txOutput: TransactionOutput, transactionHash: str, txOutputIndex: int):
        """
        method that add an transaction output to the utxo set

        :param txOutput: the transaction output to be added
        :return:
        """
        self.__UTXOSet[self.getUTXOSetTxOutputKey(transactionHash, txOutputIndex)] = txOutput

    def removeTxOutputFromUTXOSet(self, transactionHash: str, txOutputIndex: int) -> bool:
        """
        removes a tx output from the utxo set, if it exists and if the utxo set is not empty
        :param transactionHash: the transaction hash string of the tx output
        :param txOutputIndex: the tx output index in the transaction
        :return: True if successfully removed, else false
        """
        txOutputUTXOKey = self.getUTXOSetTxOutputKey(transactionHash, txOutputIndex)  # the key in the utxo set

        if (len(self.__UTXOSet) == 0) or self.__UTXOSet.get(txOutputUTXOKey) is None:
            # if the utxo set is empty or the key does not exist in the set
            return False
        else:
            self.__UTXOSet.pop(txOutputUTXOKey)  # remove the tx output
            return True

    def getUTXOSet(self) -> dict:
        """
        method that returns the utxo set of the blockchain
        :return: utxo set (dict)
        """
        return self.__UTXOSet

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

    def getBlockByBlockHeaderHash(self, blockHeaderHash: str) -> Block:
        """
        Method tha searches the block chain and gets a block by it's block header hash.
        If it is not found, it returns None.
        :param blockHeaderHash: the hash of the block header
        :return: the block if found, else None
        """
        # search every block in the chain until you find what you are looking for
        found = False  # flag that show if found or not
        i = 0  # index for the while loop
        b = None  # the block that will be returned
        while i<len(self.__chain) and found == False:
            # while not found and not at the end of the blockchain
            if self.__chain[i].getBlockHeaderHash() == blockHeaderHash:
                # if found
                b = self.__chain[i]
                found = True
            i += 1
        return b

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
        genesisBlock = Block(chain=self.__chain, targetThreshold=-1, previousBlockHash='-')  # genesis block

        genesisTxOutput = TransactionOutput(value, self.__cryptoAccount.getAddress(),
                                            self.__cryptoAccount.getAddress())

        # create and set the tx output script for the genesis tx output
        blockChainPubKeyHash = TLCUtilities.getSHA256RIPEMDHash(
            self.getBlockchainAccount().getPublicKey()
        )
        genesisTxOutputScript = SmartContractScripts.getPayToPubKeyHashScript(blockChainPubKeyHash)  # create script
        genesisTxOutput.setScript(genesisTxOutputScript)
        genesisTransaction = Transaction(self.__cryptoAccount.getAddress(), None,
                                         [genesisTxOutput])

        genesisTransaction.setBlockNumber(genesisBlock.getBlockNumber())
        genesisTransaction.sign(self.getBlockchainAccount().getPrivateKey())

        genesisBlock.setTransactionList([genesisTransaction])  # set the genesis block transaction list
        genesisBlock.setNonce(  # set the nonce
            self.getProofOfWork(genesisBlock)
        )
        self.__chain.append(genesisBlock)

        # add the transaction to the list of the confirmed transactions
        self.__confirmedTransactionList.append(genesisTransaction)

        # add the blockchain account to the accounts dictionary
        self.__addSenderAccount(self.getBlockchainAccount().getAddress(), self.getBlockchainAccount().getPublicKey())

        # add the tx output to the tx set
        self.addTxOutputToUTXOSet(genesisTxOutput, genesisTransaction.getTransactionHash(),
                                  genesisTransaction.getTransactionOutputList().index(genesisTxOutput))

        # last but not least add a transaction input to the tx input pool, towards the creator
        genesisTxInput = TransactionInput(value, self.__cryptoAccount.getAddress(), '-', -1)
        self.__addTransactionInputToPool(genesisTxInput)  # add genesis tx input to the pool

    def getAccountAvailableTotal(self, account: CryptoAccount) -> int:
        """
        Method that calculates the total amount of the money of a specific account address that exists
        in the utxo set and can be spent, according to the smart contract that has been defined.
        :param account: the account (CryptoAccount object)
        :param accountPublicKey: the account public key string
        :return: the account total (int)
        """

        # the account info
        accountAddress = account.getAddress()
        accountPublicKey = account.getPublicKey()
        accountPrivateKey = account.getPrivateKey()

        # get account total from the utxo set, for the specific recipient
        balance = 0
        for utxSetKey, utxoElement in self.__UTXOSet.items():  # for each unspent tx output in the utxo set

            # check if the tx output is spendable
            isSpendable = self.isTxOutputSpendable(utxSetKey, utxoElement, accountPrivateKey, accountPublicKey)

            # if the tx output is related to the specific recipient address and if it can be spent (script result true)
            if utxoElement.getRecipient() == accountAddress and isSpendable:
                balance += utxoElement.getValue()
        return balance

    def isTxOutputSpendable(self, utxSetKey: str, utxoElement: TransactionOutput,
                            accountPrivateKey: str, accountPublicKey: str) -> bool:
        """
        Method that decides whether an txoutput is spendable, based on the smart contract
        :param utxSetKey: the key of the txoutput in the utxo set (string)
        :param utxoElement: the value of the utxo record that corresponds to the utxSetKey. It is the txOutput
        :param accountPrivateKey: the private key of the spender (string)
        :param accountPublicKey: the public key of the spender (string)
        :return: True if it is spendable, else False
        """
        # smart contract language object
        scl = SmartContractLanguage()

        # get the transaction hash, sign it and get the signature
        transactionHash = self.getTransactionHashFromUTXOSetKey(utxSetKey)
        signedTransactionHash = TLCUtilities.getHashSignature(transactionHash, accountPrivateKey)

        # create the script for checking the specific tx output
        script = \
            SmartContractScripts.getScriptSig(signedTransactionHash, accountPublicKey) + utxoElement.getScript()

        # evaluate the script and return the result
        isSpendable = scl.evaluateExpression(script, transactionHash)
        return isSpendable

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

        # get all the addresses from the utxo set
        addresses = set()  # using a set, so as not to have duplicate values
        for utxoElement in self.__UTXOSet.values():
            addresses.add(utxoElement.getRecipient())

        # for each address, print the account total
        print('\n--- BLOCKCHAIN ACCOUNT TOTALS ---')
        for address in addresses:
            print('Acount address: ' + address + ', Total: ' + str(self.getAccountAvailableTotal(address)))

    def submitTransaction(self, senderAccount: CryptoAccount, coinTransfers: list,
                          transactionType: str=SmartContractTransactionTypes.TYPE_P2PKH):
        """
        Method for creating and submitting the transaction to the pending transaction list.
        Only the outputs are added. The inputs will be added at the mining/confirmation phase.
        It also adds the sender to the accounts list of the blockchain

        :param senderAccount: the sender CryptoAccount object
        :param coinTransfers: the list of coin transfers (CoinTransfer objects)
        :param transactionType: type of the transaction. Defines the script that will be attached to the tx outputs
        :return:
        """
        senderAddress = senderAccount.getAddress()
        senderPrivateKey = senderAccount.getPrivateKey()
        senderPublicKey = senderAccount.getPublicKey()
        senderPublicKeySignature = senderAccount.getPublicKeySignature()

        # check that the available account balance of the sender is enough to make the transaction.
        # First calculate the total value of coin tranfers. Then get the amount available from the utxo set,
        # for the sender. Compare them.

        coinTransferTotalValue = 0  # the total value of the coin tranfers
        for cTransfer in coinTransfers:
            coinTransferTotalValue += cTransfer.getValue()

        # the available acc. balance of the senderin the utxo set
        availableAmount = self.getAccountAvailableTotal(senderAccount)

        if availableAmount > coinTransferTotalValue:  # if the acc. balance is greater than the amount needed
            # do all the necessary actions to submit the transaction

            # first add some transaction inputs, from the utxo set. Go through the records of the utxo set
            # and get the unspent outputs you need to to make the transaction. Create the corresponding
            # tx inputs

            txInputList = list()  # the transaction input list
            totalInputValue = 0  # the total value of the tx inputs
            for utxSetKey, utxoElement in self.__UTXOSet.items():  # for each unspent tx output in the utxo set

                # check if the tx output is spendable
                isSpendable = self.isTxOutputSpendable(utxSetKey, utxoElement, senderPrivateKey, senderPublicKey)

                # if the tx output is related to the specific recipient address
                # and if it can be spent (script result true)
                if utxoElement.getRecipient() == senderAddress and isSpendable:
                    # add the value to the total input value
                    totalInputValue += utxoElement.getValue()
                    # create a tx input from the specific output and add it to the tx input list
                    txInput = TransactionInput(utxoElement.getValue(), utxoElement.getRecipient(),
                                               self.getTransactionHashFromUTXOSetKey(utxSetKey),
                                               self.getTxOutputIndexFromUTXOSetKey(utxSetKey))
                    # set the script for the tx input
                    txInput.setScript(SmartContractScripts.getScriptSig(
                        TLCUtilities.getHashSignature(
                            txInput.getPreviousTransactionHash(), senderPrivateKey
                        ), senderPublicKey
                    ))
                    txInputList.append(txInput)

                # when the total input value is enough, stop collecting more tx inputs from the utxo set
                if totalInputValue > coinTransferTotalValue:
                    break

            # create the transaction
            t = Transaction(senderAddress)  # initiate a new transaction

            # add the transaction inputs to the transaction
            t.extendTransactionInputList(txInputList)

            # add the transaction outputs to the transaction
            for coinTransfer in coinTransfers:
                # get the public key hash of the recipient to create the tx output script
                recipientPubKeyHash = TLCUtilities.getSHA256RIPEMDHash(coinTransfer.getRecipient().getAddress())

                # create the script
                script = ''  # empty script, before the type is decided
                if transactionType == SmartContractTransactionTypes.TYPE_P2PKH:  # standard tx output
                    # select script for P2PKH transactions
                    script = SmartContractScripts.getPayToPubKeyHashScript(recipientPubKeyHash)

                # create a new transaction output and add the script to it
                txOutput = TransactionOutput(coinTransfer.getValue(), senderAddress,
                                             coinTransfer.getRecipient().getAddress())
                txOutput.setScript(script)

                # add the output to the transaction
                t.addTransactionOutput(txOutput)

            # sign the transaction
            t.sign(senderPrivateKey)

            # add the transaction to the pending transaction list
            self.__pendingTransactionList.append(t)

            # add the sender to the accounts dictionary
            self.__addSenderAccount(senderAddress, senderPublicKey)

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
                continue  # stop with the current pending transaction. Go to the next one

            # verify that the sender account balance is enough for the transaction to take place
            txOutTotalValue = 0  # total value of transaction outputs
            for txOutput in pendingTransaction.getTransactionOutputList():
                txOutTotalValue += txOutput.getValue()

            accountBalance = self.getAccountAvailableTotal(pendingTransaction.getSender())
            if txOutTotalValue > accountBalance:  # if the balance is not enough, stop with this transaction
                continue

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

            # if there is any change, create a new tx output and set it's script (standard script)
            if txInputTotalValue > txOutTotalValue:
                changeTxOutput = TransactionOutput(txInputTotalValue-txOutTotalValue, pendingTransaction.getSender(),
                                      pendingTransaction.getSender())

                recipientPubKeyHash = TLCUtilities.getSHA256RIPEMDHash(self.getBlockchainAccount().getPublicKey())
                script = SmartContractScripts.getPayToPubKeyHashScript(recipientPubKeyHash)
                changeTxOutput.setScript(script)
                pendingTransaction.addTransactionOutput(changeTxOutput)

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

        if transactionsAdded > 0:  # if at least one transaction is valid
            # set the __previousBlockHash property of the block
            previousBlock = self.__chain[len(self.__chain)-1]
            currentBlock.setPreviousBlockHeaderHash(previousBlock.getBlockHeaderHash())

            # mine the block
            nonce = self.getProofOfWork(currentBlock)
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

    def getProofOfWork(self, block: Block) -> int:
        """
        Proof of work algorithm. Returns the nonce, when successfully completed
        :param block: the block on which the proof of work process will take place
        :return: the nonce (int)
        """
        # blockTransactionsHash = block.getTransactionsHash()  # get the block transactions hash
        blockHash = block.getBlockHeaderHash()  # get the blockHash
        prevBlockHash = block.getPreviousBlockHeaderHash()

        nonce = 0  # nonce - starts from zero
        # search while you find a valid proof
        while not self.validProof(nonce, blockHash, prevBlockHash):
            nonce += 1

        return nonce

    def validProof(self, nonce: int, blockHash: str,
                   prevBlockHash: str, miningDifficulty: int = MINING_DIFFICULTY) -> bool:
        """
        Method that checks the proof for a specific nonce. If ok, returns True, else returns False
        :param nonce: the nonce to be checked
        :param blockHash: the hash of the header of the block
        :param prevBlockHash: the hash of the previous block
        :param miningDifficulty: the mining difficulty
        :return: True if ok, else False
        """
        guess = (blockHash + prevBlockHash + str(nonce)).encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:miningDifficulty] == '0' * miningDifficulty

    def validate(self) -> bool:
        """
        Method that validates the blockchain. To do that, it checks two things: (a) that the hash of the block
        is the same prevBlockHash of the next block  (b) that the nonce stored in the block data is valid
        :return: True if validation is ok, else False
        """
        chainValid = True  # let's assume that the chain is valid
        chainLength = len(self.__chain)  # the length of the chain
        i = 0
        while i < chainLength and chainValid:  # while the chain has not ended and it is valid
            currentBlock = self.__chain[i]
            if i > 0:   # check the block hashes for all blocks except from the first one (i>0)
                previousBlock = self.__chain[i-1]
                if currentBlock.getPreviousBlockHeaderHash() != previousBlock.getBlockHeaderHash():
                    chainValid = False

            if not self.validProof(currentBlock.getNonce(), currentBlock.getBlockHeaderHash(),
                                   currentBlock.getPreviousBlockHeaderHash()):
                chainValid = False

            i += 1  # go to the next block

        return chainValid  # return the result of the validation check