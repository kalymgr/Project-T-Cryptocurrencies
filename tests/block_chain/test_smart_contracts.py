"""
testing functionality related to smart contracts
"""
import unittest

from src.block_chain.crypto_account import CryptoAccount
from src.block_chain.smart_contracts import SmartContractLanguage, SmartContractOperations, SmartContractScripts
from src.block_chain.utilities import TLCUtilities


class TestSmartContractsLanguage(unittest.TestCase):
    """
    Some testing on the smart contract language
    """
    def setUp(self):
        self.testa = 5
        self.testScLanguage = SmartContractLanguage()

    def test_elementIsOperand(self):
        """
        check if an element is an operand
        :return:
        """
        scLanguage = SmartContractLanguage()

        # case the element is empty
        assert not scLanguage.elementIsOperand('')

         # case it is an operand
        assert scLanguage.elementIsOperand('<something>')

        # case it is not an operand
        assert not scLanguage.elementIsOperand('something')
        assert not scLanguage.elementIsOperand('<something')
        assert not scLanguage.elementIsOperand('something>')

    def test_stripOperand(self):
        """
        test stripping the operand from < and >
        :return:
        """
        scLanguage = SmartContractLanguage()

        operand = '<1>'
        assert scLanguage.stripOperand(operand) == '1'

        operand2 = '<someotheroperand>'
        assert scLanguage.stripOperand(operand2) == 'someotheroperand'

    def test_evaluateExpression(self):
        """
        testing the evaluation of expressions - scripts
        :return:
        """

        # case a script is successfully evaluated -  should return true

        account = CryptoAccount()  # the test account used
        # create the transaction hash and the signature
        transactionHash = TLCUtilities.getDoubleHash256AsString('transaction content')
        signature = TLCUtilities.getHashSignature(transactionHash, account.getPrivateKey())

        # create the script, combining the txoutput and txinput parts
        txOutputScript = SmartContractScripts.getPayToPubKeyHashScript(  # the script of the tx output
            TLCUtilities.getSHA256RIPEMDHash(account.getPublicKey())
        )
        txInputScipt = SmartContractScripts.getScriptSig(signature, account.getPublicKey())

        script = txInputScipt + txOutputScript  # the script that will be evaluated
        # evaluate the script. Assert it is True
        assert self.testScLanguage.evaluateExpression(script, transactionHash)

        # case a script is unsuccessfully evaluated - change only the tx input script (put different public key)
        # Should return false
        fakeAccount = CryptoAccount()
        txInputScipt = SmartContractScripts.getScriptSig(signature, fakeAccount.getPublicKey())
        script = txInputScipt + txOutputScript
        assert not self.testScLanguage.evaluateExpression(script, transactionHash)


class TestSmartContractOperations:
    """
    testing the SmartContractOperations class
    """
    def setup(self):
        """
        setup some things for the tests
        :return:
        """
        self.testSmartContractOperations = SmartContractOperations()
        self.testExpressionStack = ['1', '4', '8', '2']

    def test_op_drop(self):
        """
        test the operation that drops something from the stack
        :return:
        """
        # case of non empty stack
        expressionStack = [1, 5, 7]

        self.testSmartContractOperations.operations['drop'](expressionStack)
        assert len(expressionStack) == 2

        # case of empty stack
        expressionStack = []
        self.testSmartContractOperations.operations['drop'](expressionStack)
        assert len(expressionStack) == 0

    def test_op_dup(self):
        """
        test the operation dup that duplicates the top item of the stack
        :return:
        """
        # case of non empty stack
        length = len(self.testExpressionStack)
        self.testSmartContractOperations.operations['dup'](self.testExpressionStack)
        # check that the size has grown
        assert len(self.testExpressionStack) == length + 1
        # check that the two top elements are the same
        assert self.testExpressionStack[length] == self.testExpressionStack[length-1]

        # case of empty stack
        emptyStack = []
        self.testSmartContractOperations.operations['dup'](emptyStack)
        assert len(emptyStack) == 0

    def test_hash160(self):
        """
        test the operation hash160 that hashes the top item and puts the hash on the stack
        :return:
        """
        # case of non empty stack
        length = len(self.testExpressionStack)

        # calculate the top item hash, before you process the stack
        topItemHash = TLCUtilities.getSHA256RIPEMDHash(self.testExpressionStack[
                                                           len(self.testExpressionStack)-1])

        self.testSmartContractOperations.operations['hash160'](self.testExpressionStack)
        assert length == len(self.testExpressionStack)  # check that the length is the same
        assert topItemHash == self.testExpressionStack[
            len(self.testExpressionStack)-1
        ]

        # case of empty stack

    def test_equal(self):
        """
        Check the equal operation
        :return:
        """
        # case two top items are equal
        stack = [1, 2, 5, 5]
        self.testSmartContractOperations.operations['equal'](stack)
        assert stack.pop()  # check that the top item is True

        # case two top items are not equal
        stack = [1, 2, 5, 15]
        self.testSmartContractOperations.operations['equal'](stack)
        assert not stack.pop()  # check that the top item is False

    def test_op_2_op_3(self):
        """
        test the op_2 and op_3 operation
        :return:
        """

        self.testSmartContractOperations.operations['op_2'](  # push two onto the stack
            self.testExpressionStack
        )
        assert self.testExpressionStack.pop() == 2  # check that two has been successfully pushed

        self.testSmartContractOperations.operations['op_3'](  # push three onto the stack
            self.testExpressionStack
        )
        assert self.testExpressionStack.pop() == 3  # check that three has been successfully pushed


class TestSmartContractScripts:
    """
    Class for testing smart contract scripts
    """

    def test_getPayToPubKeyHashScript(self):
        """
        testing the generation of a standard PayToPubKeyHash script
        :return:
        """
        pubKeyHash = 'abc'
        desiredScript = "dup hash160 <abc> equalVerify checkSig"
        assert SmartContractScripts.getPayToPubKeyHashScript(pubKeyHash) == desiredScript

    def test_getScriptSig(self):
        """
        teting the generation of a script sig
        :return:
        """
        sig = "abc"
        publicKey = "def"
        assert SmartContractScripts.getScriptSig(sig, publicKey) == "<abc> <def> "
