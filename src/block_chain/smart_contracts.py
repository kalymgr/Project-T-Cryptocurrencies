"""
File trying to implement some smart contracts functionality
"""

class SmartContractLanguage:
    """
    Class used for evaluating expressions used in smart contracts.
    It will use reverse polish notation, evaluating expressions from left to right.
    All operands should be written in < >
    """

    def __init__(self):
        self.expressionStack = list()  # stack holding elements

    def evaluateExpression(self, expressionString: str):
        """
        method that evaluates a given expression
        :param expressionString: the expression string
        :return: the result of the expression
        """
        self.expressionStack = list()  # reset the stack before evaluating

        # create a list with all the elements of the expression
        elementsList = expressionString.split()

        # initialize the operations class
        smartContractOperations = SmartContractOperations()

        # for each element in the list
        for element in elementsList:
            if self.elementIsOperand(element):  # if it is an operand, append it after stripping it
                self.expressionStack.append(
                    self.stripOperand(element)
                )
            else:  # case it is an operator
                # get the number of the arguments of the operator
                noOfArguments = smartContractOperations.operations[element].__code__.co_argcount - 1

                if noOfArguments == 1:  # one argument. Pop one operand from the stack
                    item = self.expressionStack.pop()
                    result = smartContractOperations.operations[element](item)
                else:  # two arguments. Pop two operands from the stack
                    item1 = self.expressionStack.pop()
                    item2 = self.expressionStack.pop()
                    result = smartContractOperations.operations[element](item1, item2)

                # add the result to the stack
                self.expressionStack.append(result)

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

    def __init__(self):
        """
        constructor method
        """
        # Setup the operations available
        self.operations = dict()
        self.operations['add'] = self.add
        self.operations['sub'] = self.sub
        self.operations['dou'] = self.dou
        self.operations['mul'] = self.mul
        self.operations['div'] = self.div

    def add(self, a: str, b: str):
        """
        method that calculates the sum of two numbers
        :param a: number as string
        :param b: number as string
        :return: the sum
        """
        return float(a) + float(b)

    def sub(self, a: str, b: str):
        """
        method that subtract b from a  (a - b)
        :param a: number string
        :param b: number string
        :return: a - b
        """
        return float(b) - float(a)

    def mul(self, a: str, b: str):
        """
        method that multiplies a and b
        :param a:
        :param b:
        :return: a * b
        """
        return float(a) * float(b)

    def div(self, a: str, b: str):
        """
        method that divides
        :param a:
        :param b:
        :return:
        """
        return float(b) / float(a)

    def dou(self, a: str):
        """
        returns the double of a number
        :param a:
        :return: the double (float)
        """
        return 2 * float(a)

