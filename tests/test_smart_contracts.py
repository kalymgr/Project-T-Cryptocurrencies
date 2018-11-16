"""
testing functionality related to smart contracts
"""
import unittest

from src.block_chain.smart_contracts import SmartContractLanguage, SmartContractOperations
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

    def testSomeScripts(self):
        """
        test various scripts
        :return:
        """
        script = '<1> <2> drop'
        self.testScLanguage.evaluateExpression(script)


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
