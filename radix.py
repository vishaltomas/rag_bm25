# Define structure of Radix tree node and its elements
class RadixNode:
  def __init__(self,el:str="",children:list=[],is_leaf:bool=False, word_end_pos:list=[]):
    self.el: str = el
    self.children: list[RadixNode] = children
    self.is_leaf: bool = is_leaf
    self.word_end_pos: list = word_end_pos if word_end_pos else [0] * len(el)

# Define structure for tree insert, delete and lookup
class RadixTree:
  def __init__(self):
    self.ROOT = RadixNode(is_leaf=True)
    self.is_posit_calc = False

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
    # When el is inserted in "between" two neighbours we have to check which has more match with el
    # For example if el = "b", nodes children are "abc", "bm" then without the below algorithm the
    # function will return "abc" as the candidate but bm has more match with el than abc therefore
    # bm should return
    # BELOW ALGORITHM NEEDS TO BE REIMPLEMENTED
    left_sib = node.children[right].el
    if right < len(node.children) - 1: 
      right_sib = node.children[right+1].el
    else:
      right_sib = left_sib
    new_node = el
    left_sib_match = right_sib_match = 0
    # loop goes until new_node is completed or both left_sib and right_sib is completed
    while (left_sib or right_sib) and new_node:
      if left_sib and left_sib[0] == new_node[0]:
        left_sib_match += 1
      else:
        left_sib = ""
      if right_sib and right_sib[0] == new_node[0]:
        right_sib_match += 1
      else:
        right_sib = ""
      left_sib = left_sib[1:]
      right_sib = right_sib[1:]
      new_node = new_node[1:]
    if left_sib_match >= right_sib_match:
      return (False, right, keys[right])
    return (False, right+1, keys[right+1])
  
  def __binary_insert(self, parent_node:RadixNode, child_node:RadixNode):
    if child_node.is_leaf:
      child_node.word_end_pos[-1] = 1
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
        word_end_pos = curr_node.word_end_pos
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
            curr_word_end_pos = curr_node.word_end_pos
            curr_node.word_end_pos = curr_word_end_pos[:cur_pos-start_pos]
            self.__binary_insert(curr_node, RadixNode(el=word[cur_pos:],is_leaf=True, children=[]))
            self.__binary_insert(curr_node, RadixNode(el=right_part, children=prev_children, is_leaf=False, word_end_pos = curr_word_end_pos[cur_pos-start_pos:]))
          
        else:
          
          word_end_pos[cur_pos-start_pos-1] = 1
        cur_pos = word_len
  
  def search(self, word:str)-> tuple[bool, int]:
    if not self.is_posit_calc:
        print("Positions are not calculated, please execute get_pos()", )
        return (False, -1)
        
    curr_node = self.ROOT
    cur_pos = 0
    word_pos = -1
    word_len = len(word)
    comp_str = ""
    while cur_pos < word_len:
      comp_str = curr_node.el
      while comp_str and cur_pos < word_len:
        if comp_str[0] != word[cur_pos]:
          break
        cur_pos += 1
        comp_str = comp_str[1:]
      if cur_pos != word_len:
        if comp_str or curr_node.is_leaf:
          return (False,-1)
      # check the children of the node
        _, _, curr_node = self.__binary_search(curr_node, word[cur_pos:])
    word_pos = len(curr_node.el) - len(comp_str) - 1
    if curr_node.word_end_pos[word_pos]:
        return (True, curr_node.word_end_pos[word_pos])
    return (False, -1)

  def get_pos(self):
    # Here we will update word_end_pos
    child_stack = [self.ROOT]
    curr_pos = 0
    while child_stack:
        curr_node = child_stack.pop()
        # print("curr node: ",curr_node.el)
        for index in range(len(curr_node.word_end_pos)):
            if curr_node.word_end_pos[index]:
                curr_pos += (curr_node.word_end_pos[index])
                # print("pos: ", index ,"\nbefore: ",curr_node.word_end_pos[index])
                curr_node.word_end_pos[index] = curr_pos
                # print("after: ",curr_pos)
        if curr_node.children:
            # print("Adding to stack")
            for child in reversed(curr_node.children):
                child_stack.append(child)
                # print(child.el)
            # print("len of stack: ", len(child_stack))
            # print("stack: ", [c.el for c in child_stack])
    # print("Last pos : ",curr_pos)
    self.is_posit_calc = True

#  testing functions #
def test_radix():
  with open("./sample_words.txt", "r", encoding="utf-8") as file:
    words = file.read().split("\n")
  words = words[:]
  print("total words: ", len(words))
  rt = RadixTree()
  rt.insert(words)
  rt.get_pos()
  # print([node.el for node in rt.ROOT.children])
  # print([node.word_end_pos for node in rt.ROOT.children])
  print(rt.search("unas"))
  print(rt.search("thao"))

# test_radix()
