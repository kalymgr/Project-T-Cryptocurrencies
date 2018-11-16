"""
testing functionality related to smart contracts
"""
import unittest

from src.block_chain.smart_contracts import SmartContractLanguage


class TestSmartContractsLanguage(unittest.TestCase):
    """
    Some testing on the smart contract language
    """

    def test_basicExpression(self):
        """
        method that tests some basic expression
        :return:
        """
        scLanguage = SmartContractLanguage()  # initialize the smart contract language

        expression1 = "<1> <2> add"
        assert scLanguage.evaluateExpression(expression1) == 3

        expression2 = "<1> <2> add <10> add"
        assert scLanguage.evaluateExpression(expression2) == 13

        expression3 = "<10> <5> sub"
        assert scLanguage.evaluateExpression(expression3) == 5

        expression3 = "<10> <5> sub <6> add"
        assert scLanguage.evaluateExpression(expression3) == 11

        expression3 = "<10> dou"
        assert scLanguage.evaluateExpression(expression3) == 20

        expression3 = "<15> dou <10> add <15> sub"
        assert scLanguage.evaluateExpression(expression3) == 25

        expression4 = "<15> <7> <1> <1> add sub div <3> mul <2> <1> <1> add add sub"
        assert scLanguage.evaluateExpression(expression4) == 5

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

