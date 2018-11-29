"""
File trying to implement some smart contracts functionality
"""
from src.utilities.utilities import TLCUtilities


class SmartContractTransactionTypes:
    """
    class for holding the different type of transactions. This will help in choosing the type of scripts to be used
    """
    TYPE_P2PKH = 'p2pkh'  # standard type. pay to public key hash


class SmartContractLanguage:
    """
    Class used for evaluating expressions used in smart contracts.
    It will use reverse polish notation, evaluating expressions from left to right.
    All operands should be written in < >
    """

    def __init__(self):
        self.expressionStack = list()  # stack holding elements
        self.transactionHash = None

    def evaluateExpression(self, expressionString: str, transactionHash: str):
        """
        method that evaluates a given expression
        :param expressionString: the expression string
        :param transactionHash: needed for evaluation
        :return: the result of the expression
        """

        self.transactionHash = transactionHash  # set the transaction hash

        self.expressionStack = list()  # reset the stack before evaluating

        # create a list with all the elements of the expression
        elementsList = expressionString.split()

        # initialize the operations class
        smartContractOperations = SmartContractOperations(self.transactionHash)

        # for each element in the list
        for element in elementsList:
            if self.elementIsOperand(element):  # if it is an operand, append it after stripping it
                self.expressionStack.append(
                    self.stripOperand(element)
                )
            else:  # case it is an operator
                # execute the operation, giving the operator the expression stack
                result = smartContractOperations.operations[element](
                    self.expressionStack
                )

        return self.expressionStack[0]  # the bottom element of the stack must be the result

    def elementIsOperand(self, element: str) -> bool:
        """
        tests if the element is an operand. To be, it must be surrounded by < >
        :param element: the element string
        :return: True if it is, else False
        """

        if len(element) == 0:  # if empty element
            return False

        # get the first and the last character of the string
        firstCharacter = element[0]
        lastCharacter = element[len(element) - 1]

        if firstCharacter != '<' or lastCharacter != '>':
            # if element does not start with < or does not end with >
            return False
        else:
            return True

    def stripOperand(self, operandString: str) -> str:
        """
        method that strips the operand from < and >
        :param operandString:
        :return: the operand string without < and >
        """
        return operandString[1:len(operandString)-1]


class SmartContractOperations:
    """
    Class for the operations used in the smart contract language
    """

    def __init__(self, transactionHash: str):
        """
        constructor method
        :param transactionHash: the transaction hash string
        """
        # set the transaction hash
        self.transactionHash = transactionHash

        # Setup the operations available
        self.operations = {
            'drop': self.drop,
            'dup': self.dup,
            'hash160': self.hash160,
            'equal': self.equal,
            'equalVerify': self.equalVerify,
            'checkSig': self.checkSig,
            'checkMultiSig': self.checkMultiSig,
            'op_2': self.op_2,
            'op_3': self.op_3
        }

    def drop(self, expressionStack: list):
        """
        method that drops the top item from the stack if it is not empty
        :param expressionStack:
        :return:
        """
        if len(expressionStack) > 0:  # if the expression stack is not empty
            expressionStack.pop()  # pop the top item

    def dup(self, expressionStack: list):
        """
        method that duplicates the top element of the stack
        :param expressionStack:
        :return:
        """
        if len(expressionStack) > 0:  # if the expression stack is not empty
            expressionStack.append(  # append the top key to the stack
                expressionStack[len(expressionStack)-1]
            )

    def hash160(self, expressionStack: list):
        """
        method for hashing the top stack item twice, the first time with SHA256 and the second
        time with RIPEMD

        :param expressionStack:
        :return:
        """
        if len(expressionStack) > 0: # if the stack is not empty
            # get the top item
            topItem = expressionStack.pop()
            # hash it
            topItemHash160 = TLCUtilities.getSHA256RIPEMDHash(topItem)
            # put the hash back on the stack
            expressionStack.append(topItemHash160)

    def equal(self, expressionStack: list):
        """
        checks if the top two items are equal and put the result on the top of the stack
        :param expressionStack:
        :return:
        """
        if len(expressionStack) >= 2:  # at least two items must exist in the stack
            # get two top items
            topItem1 = expressionStack.pop()
            topItem2 = expressionStack.pop()

            # put the result of equality check in the stack
            expressionStack.append(topItem1 == topItem2)

    def equalVerify(self, expressionStack: list):
        """
        checks if the inputs are equal and then marks transaction as invalid
        if top stack value is not true. The top stack value is removed.
        :param expressionStack:
        :return:
        """
        self.equal(expressionStack)  # first run the equal operation
        transactionValid = expressionStack.pop()  # get the top item (result of the equal operation)
        if not transactionValid:  # if the transaction is not valid, mark it as invalid
            pass

    def checkSig(self, expressionStack: list):
        """
        The entire transaction's outputs, inputs, and script
        (from the most recently-executed OP_CODESEPARATOR to the end)
        are hashed. The signature used by OP_CHECKSIG must be a valid signature
        for this hash and public key. If it is, 1 is returned, 0 otherwise
        :param expressionStack:
        :return:
        """
        # get the public key
        publicKey = expressionStack.pop()
        # get the transaction signature
        signature = expressionStack.pop()

        # verify the signature for the specific public key
        verificationResult = TLCUtilities.verifyHashSignature(self.transactionHash, signature, publicKey)

        # put the result on the stack
        expressionStack.append(verificationResult)





    def checkMultiSig(self, expressionStack: list):
        """
        Compares the first signature against each public key until it finds a
        match. Starting with the subsequent public key, it compares the second signature
        against each remaining public key until it finds
        match. The process is repeated until all signatures have been checked or not enough public keys
        remain to produce a successful result. All signatures need to match a public key.
        Because public keys are not checked again if they fail any signature comparison,
        signatures must be placed in the scriptSig using the same order as their corresponding public keys
        were placed in the scriptPubKey or redeemScript. If all signatures are valid,
        1 is returned, 0 otherwise. Due to a bug, one extra unused value is removed from the stack
        :param expressionStack:
        :return:
        """
        pass

    def op_2(self, expressionStack: list):
        """
        pushes number 2 to the stack
        :param expressionStack:
        :return:
        """
        expressionStack.append(2)

    def op_3(self, expressionStack: list):
        """
        pushes number 3 to the stack
        :param expressionStack:
        :return:
        """
        expressionStack.append(3)


class SmartContractScripts:
    """
    class for handling some scripts used by transactions
    """
    @staticmethod
    def getPayToPubKeyHashScript(pubKeyHash: str) -> str:
        """
        creates and returns the pay-to-pubKeyhash script
        :param pubKeyHash:
        :return: string script
        """
        script = "dup hash160 <%s> equalVerify checkSig" % pubKeyHash
        return script

    @staticmethod
    def getScriptSig(sig: str, publicKey: str) -> str:
        """
        creates and returns the standard script that will be added to the input
        :param sig:
        :param publicKey:
        :return: string script
        """
        return "<%s> <%s> " % (sig, publicKey)

    @staticmethod
    def getTxOutputScript(txType: str = SmartContractTransactionTypes.TYPE_P2PKH) -> str:
        """
        returns the tx output script, depending on the transaction type
        :param txType:
        :return:
        """
        pass
