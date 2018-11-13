# Updated version of my classes (9-11-2018)
# Maybe I can make a Blockchain class method that waits for 5 minutes and then tries to execute a transaction. It will be called
# in the constructor method. Or a transaction can be executed each time one wishes to transfer money
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
        self.__senderAddress = senderAddress # the address of the sender
        if transactionInputList is None:
            self.__transactionInputList = list()  # new transaction input list
        else:
            self.__transactionInputList = transactionInputList  # set the transaction input list
        if transactionOutputList is None:
            self.__transactionOutputList = list()  # new transaction output list
        else:
            self.__transactionOutputList = transactionOutputList  # set the transaction output list

        self.__versionNo = Transaction.VERSION_NO  # the version number of the transaction. One for now.

        self.__inCounter = 0  # the counter for the number of transaction inputs
        self.__outCounter = 0  # the counter for the number of transaction outputs

        self.__transactionHash = None  # the transactionHash

        self.__transactionSignature = None  # the signed transaction hash - the signature of the transaction

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
        Method that returns the transaction object to an ordered dict, which includes the transaction inputs and
        outputs
        :return: the transaction object as an ordered dictionary
        """

        # first create the string for the transaction inputs
        txInputsString = ''
        for txInput in self.__transactionInputList:
            txInputsString += str(txInput.getOrderedDict())

        # then create the string for the transaction outputs
        txOutputsString = ''
        for txOutput in self.__transactionOutputList:
            txOutputsString += str(txOutput.getOrderedDict())

        # finally create and return the ordered dictionary
        return OrderedDict(
            {
                'sender': self.__senderAddress,
                'txInputList': txInputsString,
                'txOutputList': txOutputsString,
                'versionNo': self.__versionNo,
                'inCounter': self.__inCounter,
                'outCounter': self.__outCounter
            }
        )

    def getSender(self) -> str:
        """
        Method that returns the sender address
        :return: the sender address
        """
        return self.__senderAddress


    def setTransactionHash(self):
        """
        method that calculates and sets the transaction hash of the transaction. It is called when the transaction
        inputs and outputs are ok and the transaction is ready to be executed
        :return:
        """
        transactionString = str(self.getOrderedDict())
        self.__transactionHash = TLCUtilities.getDoubleHash256(transactionString)

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

    def getTransactionInputsTotalValue(self) -> int:
        """
        method that calculates and returns the total value of the transaction inputs
        :return: the total value of the transaction inputs (int)
        """
        totalValue = 0
        for tInput in self.__transactionInputList:
            totalValue = totalValue + tInput.getValue()
        return totalValue

    def getTransactionInputsRecipientValue(self, recipient: str) -> int:
        """
        method that calculates and returns the total value of the transaction inputs
        :param recipient: the recipient address of the transaction input
        :return: the value of the transaction inputs for the specific recipient (int)
        """
        recipientValue = 0
        for tInput in self.__transactionInputList:
            if tInput.recipient == recipient:
                recipientValue = recipientValue + tInput.value
        return recipientValue

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

    def printTransactionInputsRecipientValue(self, recipient: str):
        """
        method that prints the value of the transaction inputs for a specific recipient
        :param recipient: the recipient address
        """
        print('- The total value of the transaction inputs for recipient ' + recipient + ' is ' +
              str(self.getTransactionInputsRecipientValue(recipient)))


class Block:
    """
    Class for implementing the transaction Blocks
    """

    def __init__(self, chain: list = None, transactions: list = None,
                 nonce: int = None, previousHash: str = None):
        """
        Constructor method for the block. Sets the block content
        :param chain: the chain that contains the blocks
        :param nonce: the nonce
        :param transactions: the list of the Transaction Objects
        that will be included in the block
        :param previousHash: the hash of the previous block
        """

        if chain is not None:  # if the constructor has data to initialize the object
            self.blockNumber = len(chain) + 1
            self.timeStamp = time()
            self.transactions = transactions
            self.nonce = nonce
            self.previousHash = previousHash
            self.merkleRoot = self.getMerkleRoot()  # set the merkle root of the block

    def getOrderedDictionary(self) -> OrderedDict:
        """
        returns the block content as a dictionary.
        The transactions are included as ordered dictionaries converted to string. Therefore, for the transactions
        the result is a long string.
        :return: the block content as dictionary
        """

        # setup the transactions dict
        transactionsString = ''
        for transaction in self.transactions:
            transactionsString += str(transaction.getOrderedDict())

        return OrderedDict({
            'block_number': self.blockNumber,
            'timestamp': self.timeStamp,
            'transactions': transactionsString,  # long string-concatenation of the string of the tx ordered dicts
            'nonce': self.nonce,
            'previous_hash': self.previousHash,
            'merkle_root': self.merkleRoot
        })

    def getBlockHash(self) -> str:
        """
        returns the SHA-256 hash of the block content
        :return: the hash of the block content as string
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(self.getOrderedDictionary(), sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def getMerkleRoot(self) -> str:
        """
        method that calculates and returns the merkle root of the block.
        It uses a two dimensional array (finalDoubleHashes) which stores the double hashes
        of each level (the first dimension is the level and the second the items of the level)
        :return: the merkle root string if there are transactions, else None
        """

        if len(self.transactions) > 0:  # if there are transactions
            # collect all the transaction hashes
            transactionDoubleHashes = []
            for transaction in self.transactions:
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
                            getDoubleHash256(finalDoubleHashes[iterNo - 1][i] + finalDoubleHashes[iterNo - 1][i + 1])
                    )
                l = int(l / 2)  # divide to 2, to get the number of elements of the tree level above

            return finalDoubleHashes[iterNo][0]

        else:  # no transactions in the block
            return None


class Blockchain:
    """
    class that handles the blockchain
    """

    def __init__(self):
        """
        constructor method
        """
        self.__name = 'TLC Creator'  # the name of the blockchain creator
        self.__transactionInputPool = dict()  # pool with transaction inputs. These are the unspent money
        self.__transactionList = list()  # the list that contains all the executed transactions

        # generate a crypto wallet for the genesis transaction
        self.__cryptoAccount = CryptoAccount()

        self.__executeGenesisTransaction()  # the genesis transaction of the system

        self.__chain = list()  # the chain of blocks

    def getAccount(self) -> CryptoAccount:
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

    def getTransactionList(self) -> list:
        """
        Method that returns the transaction list of the blockchain
        :return: __transactionList class property
        """
        return self.__transactionList

    def __executeGenesisTransaction(self):
        """
        Method that executes the genesis transaction (the first transaction of the blockchain)
        :return:
        """

        # first add a transaction input, towards the creator
        self.__addInitialTransactionInputs()

    def __transferCoins(self, sender: str, recipient: str, value: int, transaction: Transaction=None):
        """
        Method for transferring coins. First it checks if the transfer can be made. If yes, it removes money from the
        transaction input pool and adds the trasanction inputs needed to a new Transaction. It returns the transaction.
        If there is a problem, it returns false

        :param sender: the sender of the coins
        :param recipient: the recipient of the coins
        :param value: the value of the coins transfered
        :param transaction: the existing transaction, or None if it's a new one
        :return: Transaction object if coins can be transferred, else None
        """

        # create a new transaction, if no Transaction parameter was given
        if transaction is None:
            transaction = Transaction(sender)

        # check if the sender has enough money to make the transaction and if he exists in the pool
        amountInPool = self.getAccountTotal(sender)
        amountInTransactionInputs = transaction.getTransactionInputsTotalValue()
        amountInTransactionOutputs = transaction.getTransactionOutputsTotalValue()

        if (amountInPool + amountInTransactionInputs) < (amountInTransactionOutputs + value) \
                or self.__transactionInputPool.get(sender) is None:
            return None  # the money of the sender are not enough to make the transaction

        # check if the the transaction inputs in the transaction are enough to make the coin transfer
        # if the transaction inputs are not enough, then get more from the pool
        if transaction.getTransactionInputsTotalValue() < transaction.getTransactionOutputsTotalValue() + value:
            i = 0
            senderTransactionInputs = self.__transactionInputPool.get(sender)  # all the transaction inputs of the sender
            tInputsNecessary = list()  # transaction inputs necessary
            tInputsTotal = 0  # the total of the transaction inputs necessary
            while i < len(senderTransactionInputs) and tInputsTotal + senderTransactionInputs[i].getValue() < value:
                tInputsNecessary.append(senderTransactionInputs[i])  # add the tr. input to the list of those necessary
                # remove the t. input from the pool
                self.__transactionInputPool.get(sender).remove(senderTransactionInputs[i])
                tInputsTotal = tInputsTotal + senderTransactionInputs[i]
                i = i + 1
            tInputsNecessary.append(senderTransactionInputs[i])  # append the last transaction needed
            tInputsTotal = tInputsTotal + senderTransactionInputs[i].getValue()  # add the last transaction needed to the total
            # also remove this transaction input from the pool
            self.__transactionInputPool.get(sender).remove(senderTransactionInputs[i])

            # Add the transaction input list to the transaction
            transaction.extendTransactionInputList(tInputsNecessary)

        # add a transaction output to the transaction
        transaction.addTransactionOutput(TransactionOutput(value, sender, recipient))

        return Transaction
        # make the transaction

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

    def __addInitialTransactionInputs(self):
        """
        method for adding initial transaction inputs to the system. Just pouring some money into the system.
        """
        self.__addTransactionInputToPool(TransactionInput(100, self.__cryptoAccount.getAddress(), '-', -1))

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

    def __executeTransaction(self, transaction: Transaction, privateKey: str):
        """
        This method executes the transaction and gives back the change
        :param transaction:
        :param privateKey: the private key of the sender
        :return:
        """

        # calculate the change and make an extra transaction output
        change = transaction.getTransactionInputsTotalValue() - transaction.getTransactionOutputsTotalValue()
        if change > 0:  # if there is change, then make the extra transaction output
            changeTransactionOutput = TransactionOutput(change, transaction.getSender(), transaction.getSender())
            transaction.addTransactionOutput(changeTransactionOutput)  # add change tx output to the list of tx output

        transaction.setTransactionHash()  # set the transaction hash of the transaction

        # for each transaction output, create a transaction input that will be added to the blockchain pool
        for txOutput in transaction.getTransactionOutputList():
            txInput = TransactionInput(txOutput.getValue(), txOutput.getRecipient(),
                                       transaction.getDoubleHash(), transaction.getTransactionOutputList().index(txOutput))
            # if the recipient address is a new recipient, then add it to the blockchain tx input pool
            txInputRecipient = self.__transactionInputPool.get(txInput.getRecipient())  # the recipient of the input
            if txInputRecipient is None:
                self.__transactionInputPool[txInput.getRecipient()] = list()
            self.__transactionInputPool.get(txInput.getRecipient()).append(txInput)

        # sign the transaction and add it to the blockchain, if it is not empty
        if transaction.getInCounter()>0 and transaction.getOutCounter()>0:
            # sign the transaction
            self.signTransaction(transaction, privateKey)
            # add it to the blockchain
            self.__transactionList.append(transaction)

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

    def transfer(self, sender: str, coinTransfers: list, privateKey: str):
        """
        Method for transferring value to lots of recipients. Because of the way that the method __transferCoins
        work, coin transfers will start adding to the transaction output list until a coin transfer is found
        that cannot be made (insufficient recipient)
        :param sender: the sender address
        :param coinTransfers: the list of coin transfers (CoinTransfer objects)
        :param privateKey: the private key of the sender
        :return:
        """
        t = Transaction(sender)  # initiate a transaction for the sender

        for coinTransfer in coinTransfers:
            # make the coin transfer if possible, else stop the coin transfers
            result = self.__transferCoins(sender, coinTransfer.getRecipient(), coinTransfer.getValue(), t)
            if result is None or result is False:
                break
        self.__executeTransaction(t, privateKey)

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