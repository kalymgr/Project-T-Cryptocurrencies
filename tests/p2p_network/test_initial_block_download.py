"""
Various tests related to the "0.1.3 initial block download" story
"""
import unittest
from twisted.internet import reactor

from src.block_chain.transactions import Block, Transaction
from src.p2p_network.parameters import Parameters
from src.p2p_network.tlc_network import TLCNode


class TestBlockChain(unittest.TestCase):
    """
    Because of structural changes, blockchain related operations will have to be tested again.
    """
    def test_BlockOperations(self):
        """
        Testing various block operations
        :return:
        """
        # create the block and check that the properties have been properly initialized
        b = Block(list(), 200, 2, 'abc')
        assert b.blockHeader.version == Parameters.BLOCK_VERSION and \
            b.blockHeader.targetThreshold == 2 and \
            b.blockHeader.nonce == 200

        # set the transaction list of the block and check that merkle root has been properly stored
        tList = [Transaction('abc')]
        b.setTransactionList(tList)
        assert b.blockHeader.merkleRoot == b.getMerkleRoot()

        # check that the operation for getting the transaction list operates properly.
        assert b.getTransactionList() == tList

        # check that the addTransaction operation works properly
        tList2 = list(tList)  # create a copy of the list first

        newTransaction = Transaction('def')
        b.addTransaction(newTransaction)

        tList2.append(newTransaction)
        assert b.getTransactionList() == tList2
        assert b.blockHeader.merkleRoot == b.getMerkleRoot()

        # test printing the block as an ordered dictionary and the block header hash
        print(b.getOrderedDictionary())
        print(b.getBlockHeaderHash())

        # test the getPreviousBlockHash method
        assert b.getPreviousBlockHeaderHash() == 'abc'


class TestInitialBlockDownload(unittest.TestCase):
    """
    Testing class
    """

    def test_nodeBlockchainInitialization(self):
        """
        testing the initialization of a node blockchain.
        Checks:
        C1) check that the first block of the blockchain has block number 0
        :return:
        """

        node = TLCNode(reactor)
        node.startNode()

        def examineNodeStatus(node: TLCNode):
            """
            Just used for debugging
            :return:
            """
            print(1)
            # Check C1
            assert node.blockchain.getChain()[0]._Block__blockNumber == 0

        reactor.callLater(3, reactor.stop)
        reactor.callLater(0.1, examineNodeStatus, node)
        reactor.run()
