"""
title           : blockchain.py
description     : A blockchain implemenation
author          : Adil Moujahid
date_created    : 20180212
date_modified   : 20180309
version         : 0.5
usage           : python blockchain.py
                  python blockchain.py -p 5000
                  python blockchain.py --port 5000
python_version  : 3.6.1
Comments        : The blockchain implementation is mostly based on [1]. 
                  I made a few modifications to the original code in order to add RSA encryption to the transactions 
                  based on [2], changed the proof of work algorithm, and added some Flask routes to interact with the 
                  blockchain from the dashboards
References      : [1] https://github.com/dvf/blockchain/blob/master/blockchain.py
                  [2] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from src.block_chain.blockchain import Blockchain, Block

# Instantiate the Node
app = Flask(__name__)
CORS(app)

# Instantiate the Blockchain
blockchain = Blockchain()

MINING_SENDER = Blockchain.MINING_SENDER
MINING_REWARD = Blockchain.MINING_REWARD
MINING_DIFFICULTY = Blockchain.MINING_DIFFICULTY


@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/configure')
def configure():
    return render_template('./configure.html')


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form

    # Check that the required fields are in the POST'ed data
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    transaction_result = blockchain.submit_transaction(values['sender_address'], values['recipient_address'], values['amount'], values['signature'])

    if transaction_result == False:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to Block ' + str(transaction_result)}
        return jsonify(response), 201


@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #Get transactions from transactions pool
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = Block()
    last_block.setBlockContentFromDict(blockchain.chain[-1])

    nonce = blockchain.proof_of_work()

    # We must receive a reward for finding the proof.
    blockchain.submit_transaction(sender_address=MINING_SENDER, recipient_address=blockchain.node_id, value=MINING_REWARD, signature="")

    # Forge the new Block by adding it to the chain
    previous_hash = last_block.blockHash()
    block = Block()
    block.setBlockContentFromDict(blockchain.create_block(nonce, previous_hash))

    response = {
        'message': "New Block Forged",
        'block_number': block.to_dict()['block_number'],
        'transactions': block.to_dict()['transactions'],
        'nonce': block.to_dict()['nonce'],
        'previous_hash': block.to_dict()['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    # get the port argument when creating a node from the command line
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # run the app
    app.run(host='127.0.0.1', port=port)








