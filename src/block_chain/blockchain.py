"""
This module contains some classes related to the blockchain
"""
from collections import OrderedDict
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from Crypto.Hash import SHA256

from src.block_chain.transaction import Transaction


class Blockchain:
    """
    class that implements the blockchain
    """

    MINING_SENDER = "THE BLOCKCHAIN"  # the title of sender when mining a coin
    MINING_REWARD = 1  # the value rewarded when mining
    MINING_DIFFICULTY = 2  # the difficulty of mining

    def __init__(self):
        """
        constructor method
        """
        self.transactions = []  # trasanctions that will be added to the block
        self.chain = []  # chain containing the valid blocks
        self.nodes = set()  # blockchain nodes
        # Generate random number to be used as node_id
        self.node_id = str(uuid4()).replace('-', '')
        # Create genesis block
        # self.create_block(0, '00')  # genesis block
        self.createGenesisBlock()

    def createGenesisBlock(self):
        """
        method that creates the genesis block
        :return:
        """

        # create the only transaction of the genesis block
        senderAddress = 'THE CREATOR'
        recipientAddress = "30819f300d06092a864886f70d010101050003818d0030818902818100eeef" \
                           "22fe3af6ef151b89893f8b42a3448ea5fce1706f9546c73a41d4dbb303ca25ee" \
                           "376335b435662b3de429ef892c2b48d4f85b400295c30d81eec4b00b61bfbd4cd" \
                           "885b76460585ec3350247fa050fa2e1de2ceb428ea4a76ef81484ee875c89bedc" \
                           "520238c2b13180f524cdf939a468271a68c57f477e5484be319a475a110203010001"
        value = 100  # 100 coins for the genesis transaction
        genesisTransaction = Transaction(senderAddress, recipientAddress, value)

        # append the genesis transaction to the transaction list that will be included in the genesis block
        self.transactions.append(genesisTransaction.to_dict())

        # create the genesis block with and the following nonce and previousHash
        nonce = 0
        previousHash = '00'
        b = Block(self.chain, self.transactions, nonce, previousHash)

        # clear the transactions list
        self.transactions = []

        self.chain.append(b.to_dict())
        return b.to_dict()

    def register_node(self, node_url: str):
        """
        Add a new node to the list of nodes
        :param node_url: the url of the node
        :return:
        """
        # Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """
        Add a transaction to transactions array if the signature verified
        :param sender_address:
        :param recipient_address:
        :param value:
        :param signature:
        :return:
        """

        # create a new transaction instance
        t = Transaction(sender_address, recipient_address, value)

        # Reward for mining a block. No verification needed
        if sender_address == Blockchain.MINING_SENDER:
            self.transactions.append(t.to_dict())
            return len(self.chain) + 1

        # Manages transactions from wallet to another wallet
        else:
            transaction_verification = t.verifySignature(signature)
            if transaction_verification:
                self.transactions.append(t.to_dict())
                return len(self.chain) + 1
            else:
                return False

    def create_block(self, nonce, previous_hash):
        """
        Add a block of transactions to the blockchain
        :param nonce:
        :param previous_hash:
        :return:
        """

        # create the new block, containing the pending transactions
        b = Block(self.chain, self.transactions, nonce, previous_hash)

        # Reset the current list of transactions
        self.transactions = []

        # append the block to the chain
        self.chain.append(b.to_dict())

        return b.to_dict()

    def proof_of_work(self):
        """
        Proof of work algorithm
        :return: nonce when proof of work successfully completed
        """

        # get the last block from the chain
        lastBlock = Block()
        lastBlock.setBlockContentFromDict(self.chain[-1])
        # get the hash of the last block
        last_hash = lastBlock.blockHash()

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        :param transactions:
        :param last_hash:
        :param nonce:
        :param difficulty:
        :return: True when proof of work is ok
        """

        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    def valid_chain(self, chain):
        """
        check if a blockchain is valid
        :param chain:
        :return:
        """

        # get the last block
        last_block = Block()
        last_block.setBlockContentFromDict(chain[0])

        current_index = 1

        while current_index < len(chain):
            # block = chain[current_index]
            b = Block()
            b.setBlockContentFromDict(chain[current_index])
            # print(last_block)
            # print(block)
            # print("\n-----------\n")
            # Check that the hash of the block is correct
            if b.previousHash != last_block.blockHash():
                return False

            # Check that the Proof of Work is correct
            # Delete the reward transaction
            transactions = b.transactions[:-1]
            # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
            transaction_elements = ['sender_address', 'recipient_address', 'value']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in
                            transactions]

            if not self.valid_proof(transactions, b.previousHash,
                                    b.nonce, Blockchain.MINING_DIFFICULTY):
                return False

            last_block = b
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        :return:
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            print('http://' + node + '/chain')
            response = requests.get('http://' + node + '/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False


class Block:
    """
    This class is for holding block data and some operations
    """

    def __init__(self, chain: list=None, transactions: list=None, nonce=None, previousHash: str=None):
        """
        Constructor method for the block. Sets the block content
        :param chain: the chain that contains the blocks
        :param nonce: the nonce
        :param transactions: the transactions ordered dictionaries(OrderedDict objects)
        that will be included in the block
        :param previousHash: the hash of the previous block
        """

        if chain is not None:  # if the constructor has data to initialize the object
            self.blockNumber = len(chain) + 1
            self.timeStamp = time()
            self.transactions = transactions
            self.nonce = nonce
            self.previousHash = previousHash
            self.merkleRoot = self.getMerkleRoot()  # set the merkle root of the block

    def setBlockContentFromDict(self, blockContentDict: dict):
        """
        Sets the block content from a dictionary
        :param blockContentDict: the block content dictionary
        """
        self.blockNumber = blockContentDict['block_number']
        self.timeStamp = blockContentDict['timestamp']
        self.transactions = blockContentDict['transactions']
        self.nonce = blockContentDict['nonce']
        self.previousHash = blockContentDict['previous_hash']
        self.merkleRoot = blockContentDict['merkle_root']

    def to_dict(self)->dict:
        """
        returns the block content as a dictionary
        :return: the block content as dictionary
        """
        return {
            'block_number': self.blockNumber,
            'timestamp': self.timeStamp,
            'transactions': self.transactions,
            'nonce': self.nonce,
            'previous_hash': self.previousHash,
            'merkle_root': self.merkleRoot
        }

    def blockHash(self)->str:
        """
        returns the SHA-256 hash of the block content
        :return: the hash of the block content as dictionary
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(self.to_dict(), sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def doubleHash(self, transactionString: str):
        """
        method that calculates the double SHA256 hash for a transaction string. Used for merkle tree
        :param transactionString:
        :return: the double hash of the transaction string
        """

        textHash = SHA256.new(transactionString.encode('utf8'))
        textDoubleHash = SHA256.new(textHash.hexdigest().encode('utf8'))

        return textDoubleHash.hexdigest()

    def getMerkleRoot(self)->str:
        """
        method that calculates and returns the merkle root of the block.
        It uses a two dimensional array (finalDoubleHashes) which stores the double hashes
        of each level (the first dimension is the level and the second the items of the level)
        :return: the merkle root if there are transactions, else None
        """

        if len(self.transactions) > 0:  # if there are transactions
            # get the string content of all the transactions and put it in a list
            transactionStrings = []
            for transaction in self.transactions:
                transactionStrings.append(str(transaction))

            # if the number of items is even, add the last one, one more time
            if len(transactionStrings) % 2 == 1:
                transactionStrings.append(transactionStrings[len(transactionStrings)-1])

            # create the double hashes for all the transaction strings
            transactionDoubleHashes = []
            for tString in transactionStrings:
                transactionDoubleHashes.append(
                    self.doubleHash(tString)
                )

            l = len(transactionDoubleHashes)
            iterNo = 0  # no of iteration. Level of the tree
            finalDoubleHashes = list()
            finalDoubleHashes.append(transactionDoubleHashes)
            while l / 2 >= 1:  # till you reach the merkle root

                iterNo = iterNo + 1  # increase the number of the iteration

                # if the number of elements is even, add one more
                if len(finalDoubleHashes[iterNo-1]) % 2 == 1:
                    finalDoubleHashes[iterNo-1].append(finalDoubleHashes[iterNo-1][len(finalDoubleHashes[iterNo-1])-1])

                finalDoubleHashes.append([])  # add a new empty list
                # concatenate the double hashes and then double hash, until you get to the root
                i = 0
                for i in range(0, l, 2):
                    finalDoubleHashes[iterNo].append(
                        self.doubleHash(finalDoubleHashes[iterNo-1][i] + finalDoubleHashes[iterNo-1][i+1])
                    )
                l = int(l/2)  # divide to 2, to get the number of elements of the tree level above

            return finalDoubleHashes[iterNo][0]

        else:  # no transactions in the block
            return None

