import unittest

from src.block_chain.blockchain import Block
from src.block_chain.transaction import Transaction


class TestBlock(unittest.TestCase):
    def test_getMerkleRoot(self):

        # create some transactions
        t1 = Transaction('me', 'him', 3)
        t2 = Transaction('me', 'him', 5)
        t3 = Transaction('me', 'him', 7)
        t4 = Transaction('me', 'him', 3)
        t5 = Transaction('me', 'him', 5)
        t6 = Transaction('me', 'him', 7)

        # create the block
        b = Block('chain', [t1, t2, t3, t4, t5, t6])

        mRoot = b.getMerkleRoot()
