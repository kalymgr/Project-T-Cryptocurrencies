import unittest
from src.block_chain.blockchain import Block
from src.block_chain.transaction import Transaction
from Crypto.Hash import SHA256


class TestBlock(unittest.TestCase):

    def test_getMerkleRoot(self):

        # test getMerkleRoot with odd number of transactions

        # create some transactions
        t1 = Transaction('me', 'him', 3)
        t2 = Transaction('you', 'someone else', 5)
        # get manually the merkle root
        b = Block('chain', [t1.to_dict(), t2.to_dict()])

        t1DoubleHash = b.doubleHash(str(t1.to_dict()))
        t2DoubleHash = b.doubleHash(str(t2.to_dict()))
        t1t2 = t1DoubleHash + t2DoubleHash
        t1t2DoubleHash = b.doubleHash(t1t2)

        # create the block
        b = Block('chain', [t1, t2])
        mRoot = b.getMerkleRoot()

        assert t1t2DoubleHash == mRoot

        # test getMerkleRoot with even number of transactions
        t4 = Transaction('me', 'him', 3)  # create the transactions
        t5 = Transaction('you', 'someone else', 5)
        t6 = Transaction('him', 'uknown', 5)

        b2 = Block('chain2', [t4, t5, t6])  # create the block

        t4DoubleHash = b2.doubleHash(str(t4.to_dict()))
        t5DoubleHash = b2.doubleHash(str(t5.to_dict()))
        t6DoubleHash = b2.doubleHash(str(t6.to_dict()))
        t4t5 = t4DoubleHash + t5DoubleHash
        t6t6 = t6DoubleHash + t6DoubleHash
        t4t5DoubleHash = b2.doubleHash(t4t5)
        t6t6DoubleHash = b2.doubleHash(t6t6)
        t4t5t6t6 = t4t5DoubleHash + t6t6DoubleHash
        t4t5t6t6DoubleHash = b2.doubleHash(t4t5t6t6)

        assert t4t5t6t6DoubleHash == b2.getMerkleRoot()


    def test_doubleHash256(self):
        """
        testing the doubleHash256 method
        :return:
        """
        # case of hashing a normal text
        text = 'hello'
        hash256 = SHA256.new(text.encode('utf8'))
        doubleHash256 = SHA256.new(hash256.hexdigest().encode('utf8'))

        b = Block()
        assert doubleHash256.hexdigest() == b.doubleHash(text)





