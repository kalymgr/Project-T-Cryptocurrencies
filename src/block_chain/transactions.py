# Updated version of my classes (9-11-2018)
# Maybe I can make a Blockchain class method that waits for 5 minutes and then tries to execute a transaction. It will be called
# in the constructor method. Or a transaction can be executed each time one wishes to transfer money


class TransactionInput:
    """
    class that handles transaction inputs
    """

    def __init__(self, value: int, recipient: str, previousTransactionHash: str, referenceNo: int):
        """
        constructor method
        :param recipient: the address of the recipient
        :param referenceNo: the reference number of the relevant output from a previous transaction
        """
        self.value = value
        self.recipient = recipient
        self.referenceNo = referenceNo
        self.previousTransactionHash = previousTransactionHash


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
        self.value = value
        self.sender = sender
        self.recipient = recipient


class Transaction:
    """
    class that handles transactions
    """

    def __init__(self, senderAddress: str, transactionInputList: list=None, transactionOutputList: list=None):
        """
        constructor method.
        We assume that each transaction is related to only one sender.
        :param senderAddress: the address of the sender that wishes to make the transaction
        :param transactionInputList: a list with the TransactionInput objects
        :param transactionOutputList: a list with the TransactionOutput objects
        """
        self.senderAddress = senderAddress
        if transactionInputList is None:
            self.transactionInputList = list()  # new transaction input list
        else:
            self.transactionInputList = transactionInputList  # set the transaction input list
        if transactionOutputList is None:
            self.transactionOutputList = list()  # new transaction output list
        else:
            self.transactionOutputList = transactionOutputList  # set the transaction output list

    def getTransactionInputsTotalValue(self) -> int:
        """
        method that calculates and returns the total value of the transaction inputs
        :return the total value of the transaction inputs (int)
        """
        totalValue = 0
        for tInput in self.transactionInputList:
            totalValue = totalValue + tInput.value
        return totalValue

    def getTransactionInputsRecipientValue(self, recipient: str) -> int:
        """
        method that calculates and returns the total value of the transaction inputs
        :param recipient: the recipient address of the transaction input
        :returns the value of the transaction inputs for the specific recipient (int)
        """
        recipientValue = 0
        for tInput in self.transactionInputList:
            if tInput.recipient == recipient:
                recipientValue = recipientValue + tInput.value
        return recipientValue

    def getTransactionOutputsTotalValue(self) -> int:
        """
        method for calculating the total value of all transaction outputs
        :returns the total value of all transaction outputs in taliroshis (int)
        """
        transactionOutputsTotalValue = 0
        for tOutput in self.transactionOutputList:
            transactionOutputsTotalValue = transactionOutputsTotalValue + tOutput.value
        return transactionOutputsTotalValue

    def printTransactionInputsRecipientValue(self, recipient: str):
        """
        method that prints the value of the transaction inputs for a specific recipient
        :param recipient: the recipient address
        """
        print('- The total value of the transaction inputs for recipient ' + recipient + ' is ' +
              str(self.getTransactionInputsRecipientValue(recipient)))

    def execute(self) -> bool:
        """
        method for executing the transaction
        Scenario A: The transaction either executes in total (for all outputs) or fails.
        Scenario B: Some of the transaction outputs are executed and others fails.
        In this implementation we implement only Scenario A
        :returns True if properly executed, else False (eg in case of not sufficient input value)
        """
        # first check that the total value of outputs is ge to the total value of inputs. If not, return false
        if self.getTransactionOutputsTotalValue < self.getTransactionInputsTotalValue:
            return False


class Blockchain:
    """
    class that handles the blockchain
    """

    def __init__(self):
        """
        constructor method
        """
        self.transactionInputPool = dict()  # pool with transaction inputs. These are the unspent money
        self.transactionList = list()  # the list that contains all the executed transactions
        self.addInitialTransactionInputs()  # add money to the system

    def transferCoins(self, sender: str, recipient: str, value: int, transaction: Transaction=None):
        """
        Method for transferring coins. First it checks if the transfer can be made. If yes, it removes money from the
        transaction input pool and adds the trasanction inputs needed to a new Transaction. It returns the transaction.
        If there is a problem, it returns false

        :param sender: the sender of the coins
        :param recipient: the recipient of the coins
        :param value: the value of the coins transfered
        :param transaction: the existing transaction, or None if it's a new one
        :returns Transaction object if coins can be transferred, else None
        """

        # create a new transaction, if no Transaction parameter was given
        if transaction is None:
            transaction = Transaction(sender)

        # check if the sender has enough money to make the transaction and if he exists in the pool
        amountInPool = self.getAccountTotal(sender)
        amountInTransactionInputs = transaction.getTransactionInputsTotalValue()
        amountInTransactionOutputs = transaction.getTransactionOutputsTotalValue()

        if (amountInPool + amountInTransactionInputs) < (amountInTransactionOutputs + value) \
                and self.transactionInputPool.get(sender) is not None:
            return None  # the money of the sender are not enough to make the transaction

        # check if the the transaction inputs in the transaction are enough to make the coin transfer
        # if the transaction inputs are not enough, then get more from the pool
        if transaction.getTransactionInputsTotalValue() < transaction.getTransactionOutputsTotalValue() + value:
            i = 0
            senderTransactionInputs = self.transactionInputPool.get(sender)  # all the transaction inputs of the sender
            tInputsNecessary = list()  # transaction inputs necessary
            tInputsTotal = 0  # the total of the transaction inputs necessary
            while i < len(senderTransactionInputs) and tInputsTotal + senderTransactionInputs[i].value < value:
                tInputsNecessary.append(senderTransactionInputs[i])  # add the tr. input to the list of those necessary
                # remove the t. input from the pool
                self.transactionInputPool.get(sender).remove(senderTransactionInputs[i])
                tInputsTotal = tInputsTotal + senderTransactionInputs[i]
                i = i + 1
            tInputsNecessary.append(senderTransactionInputs[i])  # append the last transaction needed
            tInputsTotal = tInputsTotal + senderTransactionInputs[i].value  # add the last transaction needed to the total
            # also remove this transaction input from the pool
            self.transactionInputPool.get(sender).remove(senderTransactionInputs[i])

            # Add the transaction input list to the transaction
            transaction.transactionInputList.extend(tInputsNecessary)

        # add a transaction output to the transaction
        transaction.transactionOutputList.append(TransactionOutput(value, sender, recipient))

        return Transaction
        # make the transaction

    def getAccountTotal(self, accountAddress: str) -> int:
        """
        method for getting the total for an account address. It calculates the total from the transaction inputs that exist
        in the transaction input pool
        """
        accountAddressInputs = self.transactionInputPool.get(accountAddress)
        if accountAddressInputs is None:  # case the address does not exist in the transaction input pool
            return 0
        else:
            total = 0
            for tInput in accountAddressInputs:  # for each of the accounts transaction inputs
                total = total + tInput.value
            return total

    def addInitialTransactionInputs(self):
        """
        method for adding initial transaction inputs to the system. Just pouring some money into the system.
        """
        self.addTransactionInputToPool(TransactionInput(20, 'michalis', '-', 0))
        self.addTransactionInputToPool(TransactionInput(30, 'evdoxia', '-', 0))
        self.addTransactionInputToPool(TransactionInput(10, 'stefanos', '-', 0))
        self.addTransactionInputToPool(TransactionInput(20, 'stefanos', '-', 0))
        self.addTransactionInputToPool(TransactionInput(30, 'stefanos', '-', 0))
        self.addTransactionInputToPool(TransactionInput(40, 'stefanos', '-', 0))

    def addTransactionInputToPool(self, tInput: TransactionInput):
        """
        method that adds a transaction input to the transaction input pool. The transaction input pool is a dictionary
        whose keys are the recipient addresses and the values the transaction input objects.
        :param tInput: the transaction input object that will be added to the pool
        """
        if self.transactionInputPool.get(
                tInput.recipient) is None:  # if the specific recipient does not exist in the dictionary
            self.transactionInputPool[
                tInput.recipient] = list()  # create a list with the recipient's transaction inputs

        self.transactionInputPool[tInput.recipient].append(tInput)

    def executeTransaction(self, transaction: Transaction):
        """
        This method executes the transaction and gives back the change
        :param transaction:
        :return:
        """

        # calculate the change and make an extra transaction output
        change = transaction.getTransactionInputsTotalValue() - transaction.getTransactionOutputsTotalValue()
        changeTransactionOutput = TransactionOutput(change, transaction.senderAddress, transaction.senderAddress)
        transaction.transactionOutputList.append(changeTransactionOutput)  # added to the list of tx outputs

        # for each transaction output, create a transaction input that will be added to the blockchain pool
        for txOutput in transaction.transactionOutputList:
            txInput = TransactionInput(txOutput.value, txOutput.recipient, '-', 0)
            # if the recipient address is a new recipient, then add it to the blockchain tx input pool
            txInputRecipient = self.transactionInputPool.get(txInput.recipient)  # the recipient of the input
            if txInputRecipient is None:
                self.transactionInputPool[txInput.recipient] = list()
            self.transactionInputPool.get(txInput.recipient).append(txInput)

        # add the transaction to the transaction list of the blockchain
        self.transactionList.append(transaction)

    def printAccountTotals(self):
        """
        Method for printing the account totals for the accounts in the blockchain transaction input pool
        :return:
        """

        # get all the keys (account addresses) of the transaction input pool
        accountAddresses = list(self.transactionInputPool.keys())

        print('\n--- BLOCKCHAIN ACCOUNT TOTALS ---')
        # for each key (account address), print the account total
        for accountAddress in accountAddresses:
            print(
                'The total for the account ' + accountAddress +
                " is " + str(self.getAccountTotal(accountAddress))
            )

    def transfer(self, sender: str, coinTransfers: list):
        """
        Method for transferring value to lots of recipients
        :param sender: the sender address
        :param coinTransfers: the list of coin transfers
        :return:
        """
        t = Transaction(sender)  # initiate a transaction for the sender

        for coinTransfer in coinTransfers:
            # make the coin transfer if possible, else stop the coin transfers
            result = self.transferCoins(sender, coinTransfer[0], coinTransfer[1], t)
            if result is None or result is False:
                break
        self.executeTransaction(t)
