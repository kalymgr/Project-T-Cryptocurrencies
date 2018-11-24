import unittest

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, defer


class TestTLCNode(unittest.TestCase):
    """
    class testing the source code related to network nodes
    """
    def setUp(self):
        """
        method for test setup
        :return:
        """
        pass

    def test_deferred_functionality(self):
        """
        testing twisted functionality. This is not a test of our code
        :return:
        """

        """
        This function is a dummy which simulates a delayed result and
        returns a Deferred which will fire with that result. Don't try too
        hard to understand this.
        """

        def power(x):
            return x * x

        def printResult(x):
            print(f"The result is {x}")

            return x

        def printTheEnd(x):
            print("End of program")

        d = defer.Deferred()  # create the deferred object

        # add some callbacks
        d.addCallback(power)
        d.addCallback(printResult)
        d.addCallback(printTheEnd)

        # run the series of callbacks, using 5 as input of the first callback function
        d.callback(5)

    def test_reactor_functionality(self):
        """
        Exploring reactor functionality
        :return:
        """
        reactor.run()




