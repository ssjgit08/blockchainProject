
# Importing Liabraries 

import datetime    # To get exact time when block is mined
import hashlib     # To use cryptographic hash functions
import json        # To use transactions (which are in json format)
from flask import Flask, jsonify, request    # To create Web App
import requests    # To get nodes in the decentralize blockchain
from uuid import uuid4      # To create and address each node
from urllib.parse import urlparse   # To parse the url


# Architecture of the Blockchain

class Blockchain:
    
    # initialization
    
    def __init__(self):       
        self.chain = []  # list containing different blocks
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0') # genisis block
        self.nodes = set() # list of non duplicate nodes
        
    # building a block
    
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    # joining the blocks
    
    def get_previous_block(self):
        return self.chain[-1]
    
    # problem needs to be solved to mine a block or proof of work
    
    # hard to find easy to verify 
    
    def proof_of_work(self, previous_proof):
     new_proof = 1                              # approach trial and run
     check_proof = False
     while check_proof is False:
         hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
         if hash_operation[:4] == '0000':
             check_proof = True
         else:
             new_proof += 1
     return new_proof
    
    # checking correctness of pow and previous hash
    
    def hash(self, block):
        encoded_block  = json.dumps(block, sort_keys= True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    # checking validity of blockchain
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    # format of a transaction
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    # decentralization 
    
    # 1. Adding nodes 
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    # 2. Replacement with largest chain
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True 
        return False
        

# Mining the Blockchain


# 1. Creating a Web App

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# 2. Creating an address for the node on the port 5001

node_address = str(uuid4()).replace('-', '')

# 3. Creating a Blockchain

blockchain = Blockchain()

# 4. Minining a new block 

@app.route('/mine_block', methods = ['GET'])

def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'miner2', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200   # OK


# 5. Getting the full Blockchain


@app.route('/get_chain', methods = ['GET'])

def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# 6. Checking If Bloackchain is Valid

@app.route('/is_valid', methods = ['GET'])

def is_valid():
    
    blockchain.is_chain_valid(blockchain.chain)   # returns true or false
    
    if is_valid:
        response = {'message' : 'All good, blockchain is valid.' }
    else:
        response = {'message' : 'Yo we have a problem, blockchain is not valid.' }    
    return jsonify(response), 200

# 7. Adding a new transaction to the Blockchain

@app.route('/add_transaction', methods = ['POST'])

def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'incomplete transaction elements', 400 # Bad request
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : f'This transaction will be added to block {index}'}
    return jsonify(response), 201   # request created

# Decentralizing our Cryptocurrency


# 1. Connecting new Nodes 

@app.route('/connect_node', methods = ['POST'])

def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node is there', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected and The SSJ Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# 2. Replacing the chain by the longest chain if needed

@app.route('/replace_chain', methods = ['GET'])

def replace_chain():
    
    is_chain_replaced = blockchain.replace_chain()  # returns true or false
    
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Finally Running the app

app.run(host = '0.0.0.0', port = 5003)




























