# First attempt to put my hands on developing a blockchain
# No network, no multi-threading
# Super super mega extra incredibly impressive simplified Proof of Stake algorithm,
# blocks in the blockchain (which is going to be saved in the RAM), fraud attempt and fraud check
# Don't study from this repo, it's fucked up and it's just for personal usage
# It was a good afternoon and I could have done something better but I don't have a girlfriend and I did this


from datetime import datetime
import time
from hashlib import sha256
import json, requests
from random import randint
from copy import copy
from oracle import Oracle

DATE = datetime.now()

GENESIS_BLOCK = {
  "Index": 0,
  "Timestamp": str(DATE),
  "Transactions": "",
  "PrevHash": "",
  "Validator": "" # address to receive the reward
}


alreadyDone = False;

# All nodes are validators
class Node(object):

  def __init__(self, account, oracle):
    genesis_block = copy(GENESIS_BLOCK);

    self.__blockChain = []
    self.__transaction_pool = set()
    self.__currBlock = {}
    self.__next_validator = self
    self.nodes = set() # instances of Node class
    self.nodes.add(self);
    self.__oracle = oracle;

    self.myAccount = {
      'Address': '',
      'Age': 0,
      'Weight': 0
    }

    self.myAccount['Address'] = account['Address']
    self.myAccount['Weight'] = account['Weight']
    
    self.__blockChain.append(genesis_block);
  
  def get_blockchain(self):
    return self.__blockChain;

  def add_node_to_set(self, node):
    if node and type(node) == type(self):
      self.nodes.add(node);

  def get_next_validator(self):
    return self.__next_validator;

  def print_nodes(self):
    print("I'm " + str(self.myAccount) + ", the connected nodes are: ");
    for node in self.nodes:
      print(node.myAccount);


  def create_transaction(self, sender, receiver, amount):
    if not sender and not receiver and amount <= 0:
      print("Error, create_transaction: null value(s)");
      return None;
    
    trx = {
      'Sender': sender,
      'Receiver': receiver,
      'Amount': amount
    }
    return trx;

  # Check if transaction is valid. If valid: add transaction to pool
  def receive_transaction(self, transaction):
    valid_or_not = randint(1,20);
    if valid_or_not != 20:
      self.__transaction_pool.add(str(transaction));


  def compute_next_validator(self):
    self.__next_validator = self.__oracle.get_next_validator();

  def get_prevHash(self):
    last_block = copy(self.__blockChain[-1]);
    block_string = json.dumps(last_block, sort_keys=True).encode();
    return sha256(block_string).hexdigest();

  def compose_and_send_block(self):
    # compose block
    index = int(self.__blockChain[-1]['Index']) + 1;
    timestamp = str(datetime.now());
    validator = self.myAccount['Address'];
    prevHash = self.get_prevHash();
    transactions = [];
    
    for i in range(20):
      trx = self.__transaction_pool.pop();
      trx_string = json.dumps(trx, sort_keys=True);
      transactions.append(trx);
    
    global alreadyDone;
    if index == 5 and not alreadyDone:
      validator = 'FRAUD';
      alreadyDone = True;

    new_block = {
      "Index": index,
      "Timestamp": timestamp,
      "Transactions": transactions,
      "PrevHash": prevHash,
      "Validator": validator
    }

    self.__blockChain.append(new_block);

    for node in self.nodes:
      if node != self:
        node.receive_block_from_node(self, new_block);


  def is_block_valid(self, block):
    if block['Validator'] == 'FRAUD':
      return False;
    return True;

  def receive_block_from_node(self, node_sender, new_block):
    # Check if block is valid
      # Add block to blockchain
    # If not, remove Validator from Validators set
    if node_sender == self:
      return;

    if node_sender != self.__next_validator:
      return;

    if node_sender not in self.nodes:
      return;
    
    if self.is_block_valid(new_block):
      self.__blockChain.append(new_block);
      self.remove_transactions_from_pool(new_block['Transactions']);
    else:
      print("Block not valid, removing node " + node_sender.myAccount['Address']);
      self.__oracle.request_remove(self, node_sender);
      self.nodes.remove(node_sender);
      # REMOVE STAKE
    
    self.__oracle.oracle_next_validator(self.__blockChain);
    self.__next_validator = self.__oracle.get_next_validator();

  def remove_transactions_from_pool(self, array_transactions):
    for trx in array_transactions:
      if trx in self.__transaction_pool:
        self.__transaction_pool.remove(trx);


def add_nodes_to_each_other(nodes):
  for node in nodes:
    for node_diff in nodes:
      if node != node_diff:
        node.add_node_to_set(node_diff);


def test_adding_nodes(nodes):
  for node in nodes:
    node.print_nodes();

def test_check_validators(nodes):
  for node in nodes:
    validator = node.get_next_validator();
    print(validator.myAccount);


def randomize_receiver(nodes, node):
  while True:
    receiver = nodes[randint(0, len(nodes) - 1)];
    if receiver != node:
      return receiver;

def generate_and_broadcast_transactions(nodes):
  for node in nodes:
    n_trx_per_node = randint(50,200)

    for i in range(n_trx_per_node):
      receiver = randomize_receiver(nodes, node)
      transaction = node.create_transaction(node.myAccount['Address'], receiver.myAccount['Address'], randint(0,100));
      
      node.receive_transaction(transaction);
      for other_node in nodes:
        if other_node != node:
          other_node.receive_transaction(transaction);

def update_next_validator_in_oracle(node, oracle):
  blockchain = node.get_blockchain();
  oracle.oracle_next_validator(blockchain);

def set_validator_in_all_nodes(nodes):
  for node in nodes:
    node.compute_next_validator();


def confront_blockchains(nodes):
  for node in nodes:
    for other_node in nodes:
      if node != other_node:
        blockchain1 = node.get_blockchain();
        blockchain2 = other_node.get_blockchain();
        
        if blockchain1 != blockchain2:
          print("blockchains not equal, accounts: " + node.myAccount['Address'] + ", " + other_node.myAccount['Address']);


def run_Proof_of_Stake(node, oracle, nodes):
  for i in range(10):
    update_next_validator_in_oracle(node, oracle);
    set_validator_in_all_nodes(nodes);

    node_validator = oracle.get_next_validator();
    node_validator.compose_and_send_block();

def test_and_print_blockchains(node, nodes):
  confront_blockchains(nodes);
  blockchain = node.get_blockchain();
  for block in blockchain:
    print(block);


def main():
  account1 = {'Address': 'account1', 'Weight': 50}
  account2 = {'Address': 'account2', 'Weight': 55}
  account3 = {'Address': 'account3', 'Weight': 43}
  account4 = {'Address': 'account4', 'Weight': 67}
  account5 = {'Address': 'account5', 'Weight': 25}

  oracle = Oracle();

  node1 = Node(account1, oracle)
  node2 = Node(account2, oracle)
  node3 = Node(account3, oracle)
  node4 = Node(account4, oracle)
  node5 = Node(account5, oracle)

  nodes = [node1, node2, node3, node4, node5];

  oracle.set_nodes(nodes);

  add_nodes_to_each_other(nodes);
  generate_and_broadcast_transactions(nodes);

  
  
  # ==========================================
  # ============= Proof of Stake =============
  # ==========================================

  run_Proof_of_Stake(node1, oracle, nodes);

  test_and_print_blockchains(node1, nodes);

  # ==========================================
  # ============= Proof of Stake =============
  # ==========================================



if __name__ == '__main__':
    main()