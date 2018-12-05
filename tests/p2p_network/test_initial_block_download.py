"""
Various tests related to the "0.1.3 initial block download" story
"""
import pickle
import unittest
from twisted.internet import reactor

from src.block_chain.transactions import Block, Transaction
from src.p2p_network.parameters import Parameters
from src.p2p_network.tlc_message import TLCBlockMessage
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

    def setUp(self):
        # create and start a test node
        self.testNode = TLCNode(reactor)
        self.testNode.startNode()

    def test_nodeBlockchainInitialization(self):
        """
        testing the initialization of a node blockchain.
        Checks:
        C1) check that the first block of the blockchain has block number 0
        :return:
        """

        node = TLCNode(reactor, port=8013)
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

    def test_initialBlockDownload(self):
        """
        Testing the initial block download
        :return:
        """

        # append a block to the blockchain of the node, that is old
        newBlock = Block(self.testNode.blockchain.getChain(), nonce=1, previousBlockHash='a')
        newBlock.blockHeader.timeStartHashing = 0  # set the age of the block as 1/1/1970
        self.testNode.blockchain.getChain().append(newBlock)

        # create a second node with some fresh blocks
        peerNode = TLCNode(reactor, port=8011)
        peerNode.startNode()

        # initially, use the same genesis block with the other node
        peerChain = list(self.testNode.getTLCFactory().blockchain.getChain())
        peerNode.getTLCFactory().blockchain._Blockchain__chain = peerChain
        noOfBlocks = 1000  # number of blocks to add
        for i in range(1, noOfBlocks + 1):  # add the blocks to the peer node
            prevBlockHash = peerChain[len(peerChain)-1].getBlockHeaderHash()  # previous block hash
            b = Block(chain=peerChain,  # create the block
                      previousBlockHash=prevBlockHash,
                      )
            b.setNonce(peerNode.getTLCFactory().blockchain.getProofOfWork(b))  # set the block nonce
            peerNode.blockchain.getChain().append(b)  # append the block to the chain

        # TODO: the two nodes must share the same genesis block. Find why the hash header cannot
        #   be found in the peer node.
        self.testNode.initialBlockDownload(peerNode)
        self.testNode.connectTo(peerNode)

        def makeAssertions(node: TLCNode, peerNode: TLCNode):
            print(1)

        reactor.callLater(50, makeAssertions, self.testNode, peerNode)
        reactor.callLater(70, reactor.stop)
        reactor.run()

    def testBlockMessageCreation(self):
        """
        testing the creation of a TLCBlockMessage
        :return:
        """
        # create a block and serialize it
        block = Block(chain=list(), previousBlockHash='abc')  # block creation
        serBlock = pickle.dumps(block)  # block serialization
        intSerBlock = list(serBlock)  # conversion to list of ints, so it can be json dumped

        # create the TLCBlockMessage
        blockMessage = TLCBlockMessage(intSerBlock)
