"""
This module contains some classes related to the blockchain
"""
from collections import OrderedDict
import binascii
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests

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
        self.create_block(0, '00')  # genesis block

    def register_node(self, node_url):
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

        # create the new block
        b = Block(self.chain, self.transactions, nonce, previous_hash)

        # Reset the current list of transactions
        self.transactions = []

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
    This class is for holding block data
    """

    def __init__(self, chain=None, transactions=None, nonce=None, previousHash=None):
        """
        Constructor method for the block. Sets the block content
        :param chain: the chain that contains the blocks
        :param nonce: the nonce
        :param transactions: the transactions that will be included in the block
        :param previousHash: the hash of the previous block
        """

        if chain is not None:  # if the constructor has data to initialize the object
            self.blockNumber = len(chain) + 1
            self.timeStamp = time()
            self.transactions = transactions
            self.nonce = nonce
            self.previousHash = previousHash

    def setBlockContentFromDict(self, blockContentDict):
        """
        Sets the block content from a dictionary
        :param blockContentDict: the block content dictionary
        """
        self.blockNumber = blockContentDict['block_number']
        self.timeStamp = blockContentDict['timestamp']
        self.transactions = blockContentDict['transactions']
        self.nonce = blockContentDict['nonce']
        self.previousHash = blockContentDict['previous_hash']

    def to_dict(self):
        """
        returns the block content as a dictionary
        :return: the block content as dictionary
        """
        return {
            'block_number': self.blockNumber,
            'timestamp': self.timeStamp,
            'transactions': self.transactions,
            'nonce': self.nonce,
            'previous_hash': self.previousHash
        }

    def blockHash(self):
        """
        returns the SHA-256 hash of the block content
        :return: the hash of the block content as dictionary
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(self.to_dict(), sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()
