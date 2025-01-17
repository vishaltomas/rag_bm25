# Define structure of Radix tree node and its elements
class RadixNode:
  def __init__(self,el:str="",children:list=[],is_leaf:bool=False):
    self.el: str = el
    self.children: list[RadixNode] = children
    self.is_leaf: bool = is_leaf

# Define structure for tree insert, delete and lookup
class RadixTree:
  def __init__(self):
    self.ROOT = RadixNode(is_leaf=True)

  def __binary_search(self, node:RadixNode, el:str) -> tuple[bool, int, RadixNode]:
    keys = node.children
    left = 0
    right = len(keys)-1
    mid = -1
    while(left <= right):
      mid = (left+right)//2
      if keys[mid].el == el:
        return (True, mid, keys[mid])
      elif keys[mid].el < el:
        left = mid+1
      else:
        right = mid-1
    if mid == -1:
      return (False, right, node)
    return (False, right, keys[right])
  
  def __binary_insert(self, parent_node:RadixNode, child_node:RadixNode):
    if parent_node.is_leaf:
      parent_node.is_leaf = False
      parent_node.children.append(child_node)
    else:
      _, pos, _ = self.__binary_search(parent_node, child_node.el)
      parent_node.children.insert(pos+1, child_node)

  def insert(self, words:str):
    if type(words) is str:
      word_ls = [words]
    else:
      word_ls = words
    for word in word_ls:
      curr_node = self.ROOT
      parent_node = curr_node
      #To track position of word to insert
      cur_pos = 0                 
      word_len = len(word)
      while cur_pos < word_len:
        start_pos = cur_pos
        comp_str = curr_node.el
        while comp_str and cur_pos<word_len:
      
          if comp_str[0] != word[cur_pos]:
            break
          comp_str = comp_str[1:]
          cur_pos+=1
        if cur_pos != word_len:
          right_part = curr_node.el[cur_pos-start_pos:]
          left_part = word[start_pos:cur_pos]
          # print(left_part, " : ", right_part)
          if right_part == "":
            if curr_node.children:
              parent_node = curr_node
              _, _, curr_node = self.__binary_search(curr_node, word[cur_pos:])
              continue
            # Below condition occurs when no children is present to the current node
            else:
              self.__binary_insert(curr_node, RadixNode(el=word[cur_pos:],children=[],is_leaf=True))              
          elif left_part == "":
            self.__binary_insert(parent_node, RadixNode(el=word[cur_pos:],is_leaf=True, children=[]))
          else:            
            
            curr_node.el = left_part  
            prev_children = curr_node.children
            curr_node.children = []
            self.__binary_insert(curr_node, RadixNode(el=word[cur_pos:],is_leaf=True, children=[]))
            self.__binary_insert(curr_node, RadixNode(el=right_part, children=prev_children, is_leaf=False))
        cur_pos = word_len
  
  def search(self, word:str)->bool:
    curr_node = self.ROOT
    cur_pos = 0
    word_len = len(word) -1
    while cur_pos < word_len:
      comp_str = curr_node.el
      while comp_str and cur_pos < word_len:
        if comp_str[0] != word[cur_pos]:
          break
        cur_pos += 1
        comp_str = comp_str[1:]
      if cur_pos != word_len -1:
        if comp_str or curr_node.is_leaf:
          return False
        _, _, curr_node = self.__binary_search(curr_node, word[cur_pos:])
    return True
  


#  testing functions #
def test_radix():
  words = ["qwe", "qwert", "sdr", "abc","bnn","tuv", "bnu"]
  rt = RadixTree()
  rt.insert(words)
  print([node.el for node in rt.ROOT.children[1].children])
