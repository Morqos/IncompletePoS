
class Oracle(object):

  def __init__(self):
    self.__next_validator = None;
    self.__nodes = [];
    self.__removing_requests = {}

  def set_nodes(self, nodes):
    self.__nodes = nodes;

  def oracle_next_validator(self, blockchain):
    last_index = int(blockchain[-1]['Index']);
    index = last_index % len(self.__nodes);
    self.__next_validator = self.__nodes[index];
  

  def get_next_validator(self):
    return self.__next_validator;
  
  def request_remove(self, sender_node, node_to_remove):
    sender_address = sender_node.myAccount['Address'];
    address_to_remove = node_to_remove.myAccount['Address'];

    if address_to_remove not in self.__removing_requests:
      self.__removing_requests[address_to_remove] = [];

    if sender_address not in self.__removing_requests[address_to_remove]:
      self.__removing_requests[address_to_remove].append(sender_address);
    
    if len(self.__removing_requests[address_to_remove]) >= 3:
      for node in self.__nodes:
        if node.myAccount['Address'] == address_to_remove:
          self.__nodes.remove(node);
          break;
      



