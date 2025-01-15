# Define structure of Radix tree node and its elements
class RadixNode:
  def __init__(self,el:str="",children:dict={},is_leaf:bool=False):
    el: str = el
    children: dict[str, RadixNode] = children
    is_leaf: bool = is_leaf

# Define structure for tree insert, delete and lookup
class RadixTree:
  def __init__(self):
    self.ROOT = RadixNode(is_leaf=True)

  def __binary_search(self, node:RadixNode, el:str) -> tuple[bool, int, RadixNode]:
    keys = list(node.children.keys())
    left = 0
    right = len(keys)-1
    mid = -1
    while(left <= right):
      mid = (left+right)//2
      if keys[mid] == el:
        return (True, mid, node.children[keys[mid]])
      elif keys[mid] < el:
        left = mid+1
      else:
        right = mid-1
    return (False, mid, node.children[keys[mid]])
    
  def insert(self, words:str):
    if type(words) is str:
      word_ls = [words]
    else:
      word_ls = words
    for word in word_ls:
      curr_node = self.ROOT
      #To track position of word to insert
      cur_pos = 0                 
      word_len = len(word)
      while not curr_node.is_leaf:
        comp_str = curr_node.el
        while comp_str:
          if comp_str[0] != word[cur_pos]:
            break
          comp_str = comp_str[1:]
          cur_pos+=1
        if cur_pos != word_len-1 and comp_str == "":
          found, pos, curr_node = self.__binary_search(curr_node, word[cur_pos:])
          if not found:
            pass
