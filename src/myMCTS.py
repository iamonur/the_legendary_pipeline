from abc import ABC, abstractmethod
from collections import defaultdict
import math
from random import choice
from collections import namedtuple

class MCTS_Node(ABC):
    """
    A single board state.
    """
    @abstractmethod
    def find_children(self):
        "All successors"
        return set()
    @abstractmethod
    def find_random_child(self):
        "A random successor"
        return None
    @abstractmethod
    def is_terminal(self):
        "True if this node has no child"
        return True
    @abstractmethod
    def reward(self):
        "Assume this is a terminal node"
        return 0
    @abstractmethod
    def __hash__(self):
        "Hash for comparison"
        return "123456789"
    def __eq__(node1, node2):
        "Comparison by hash"
        if hash(node1) == hash(node2):
            return True
        return False
    
class MCTS:
    "MCTSer. Rollout the tree, choose a move"

    def __init__(self, exploration_weight=0.5):
        self.Q = defaultdict(int) #Rewards of each node
        self.N = defaultdict(int) #Total visit count of each node
        self.children = dict()
        self.exploration_weight = exploration_weight

    def choose(self, node):
        "Choose best successor"
        if node.is_terminal():
            raise RuntimeError("Terminal nodes do not choose! {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf") # Minus infinity to avoid any unseen moves.
            return self.Q[n]/self.N[n] #Avg. reward

        return max(self.children[node], key=score)

    def do_rollout(self, node):
        "Trains for one iteration"
        path = self._select(node)
        leaf = path[-1]
        self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path,reward)

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children()

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        invert_reward = True
        while True:
            if node.is_terminal():
                reward = node.reward()
                return 1 - reward if invert_reward else reward
            node = node.find_random_child()
            invert_reward = not invert_reward

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[node], key=uct)

class MazeBoard(MCTS_Node):
    """
    A single board state.
    """
    def __init(self, map, parent):
        self.leftChild = None
        self.rightChild = None
        self.upChild = None
        self.downChild = None
        self.skipChild = None
        self.map = map
        self.myHash = self.hashMap()
        self.isEnd = False
        self.avatar_nearbySprites = {}
        self.avatar_pos = (-1,-1)
        self.opponent_nearbySprites = {}
        self.opponent_pos = (-1,-1)
        self.portal_pos = (-1,-1)
        self.graspMap_opponent()
        self.respectiveOpponentMove()#Remember that the first to move is the opponent.
        self.graspMap_avatar()

    def graspMap_opponent(self):

        for lineNum, line in enumerate(self.map):

            for charNum, char in enumerate(line):
                if char == 'A':
                    self.avatar_pos = (lineNum, charNum)

                if char == 'E':
                    self.opponent_pos = (lineNum, charNum)
                #NORTH
                    if lineNum == 0:
                        self.opponent_nearbySprites['North'] = 'Wall'
                    elif self.map[lineNum - 1][charNum] == '1':
                        self.opponent_nearbySprites['North'] = 'Wall'
                    elif self.map[lineNum - 1][charNum] == 'A':
                        self.opponent_nearbySprites['North'] = 'Enemy'
                    elif self.map[lineNum - 1][charNum] == 'G':
                        self.opponent_nearbySprites['North'] = 'Portal'
                    elif self.map[lineNum - 1][charNum] == '0':
                        self.opponent_nearbySprites['North'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")
                    #SOUTH
                    if lineNum == len(self.map)-1:
                        self.opponent_nearbySprites['South'] = 'Wall'
                    elif self.map[lineNum + 1][charNum] == '1':
                        self.opponent_nearbySprites['South'] = 'Wall'
                    elif self.map[lineNum + 1][charNum] == 'A':
                        self.opponent_nearbySprites['South'] = 'Enemy'
                    elif self.map[lineNum + 1][charNum] == 'G':
                        self.opponent_nearbySprites['South'] = 'Portal'
                    elif self.map[lineNum + 1][charNum] == '0':
                        self.opponent_nearbySprites['South'] = 'Floor'
                    else:
                        #caPolisher.map_print(self.map)
                        raise MCTS_Exception("Unknown sprite in map!")
                    #WEST
                    if charNum == 0:
                        self.opponent_nearbySprites['West'] = 'Wall'
                    elif self.map[lineNum][charNum - 1] == '1':
                        self.opponent_nearbySprites['West'] = 'Wall'
                    elif self.map[lineNum][charNum - 1] == 'A':
                        self.opponent_nearbySprites['West'] = 'Enemy'
                    elif self.map[lineNum][charNum - 1] == 'G':
                        self.opponent_nearbySprites['West'] = 'Portal'
                    elif self.map[lineNum][charNum - 1] == '0':
                        self.opponent_nearbySprites['West'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")
                    #EAST
                    if charNum == len(self.map[0])-1:
                        self.opponent_nearbySprites['East'] = 'Wall'
                    elif self.map[lineNum][charNum + 1] == '1':
                        self.opponent_nearbySprites['East'] = 'Wall'
                    elif self.map[lineNum][charNum + 1] == 'A':
                        self.opponent_nearbySprites['East'] = 'Enemy'
                    elif self.map[lineNum][charNum + 1] == 'G':
                        self.opponent_nearbySprites['East'] = 'Portal'
                    elif self.map[lineNum][charNum + 1] == '0':
                        self.opponent_nearbySprites['East'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")

    def graspMap_avatar(self):
        for lineNum, line in enumerate(self.map):

            for charNum, char in enumerate(line):
                
                if char == 'A':
                    self.avatar_pos = (lineNum, charNum)
                #NORTH
                    if lineNum == 0:
                        self.avatar_nearbySprites['North'] = 'Wall'
                    elif self.map[lineNum - 1][charNum] == '1':
                        self.avatar_nearbySprites['North'] = 'Wall'
                    elif self.map[lineNum - 1][charNum] == 'E':
                        self.avatar_nearbySprites['North'] = 'Enemy'
                    elif self.map[lineNum - 1][charNum] == 'G':
                        self.avatar_nearbySprites['North'] = 'Portal'
                    elif self.map[lineNum - 1][charNum] == '0':
                        self.avatar_nearbySprites['North'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")
                    #SOUTH
                    if lineNum == len(self.map)-1:
                        self.avatar_nearbySprites['South'] = 'Wall'
                    elif self.map[lineNum + 1][charNum] == '1':
                        self.avatar_nearbySprites['South'] = 'Wall'
                    elif self.map[lineNum + 1][charNum] == 'E':
                        self.avatar_nearbySprites['South'] = 'Enemy'
                    elif self.map[lineNum + 1][charNum] == 'G':
                        self.avatar_nearbySprites['South'] = 'Portal'
                    elif self.map[lineNum + 1][charNum] == '0':
                        self.avatar_nearbySprites['South'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")
                    #WEST
                    if charNum == 0:
                        self.avatar_nearbySprites['West'] = 'Wall'
                    elif self.map[lineNum][charNum - 1] == '1':
                        self.avatar_nearbySprites['West'] = 'Wall'
                    elif self.map[lineNum][charNum - 1] == 'E':
                        self.avatar_nearbySprites['West'] = 'Enemy'
                    elif self.map[lineNum][charNum - 1] == 'G':
                        self.avatar_nearbySprites['West'] = 'Portal'
                    elif self.map[lineNum][charNum - 1] == '0':
                        self.avatar_nearbySprites['West'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")
                    #EAST
                    if charNum == len(self.map[0])-1:
                        self.avatar_nearbySprites['East'] = 'Wall'
                    elif self.map[lineNum][charNum + 1] == '1':
                        self.avatar_nearbySprites['East'] = 'Wall'
                    elif self.map[lineNum][charNum + 1] == 'E':
                        self.avatar_nearbySprites['East'] = 'Enemy'
                    elif self.map[lineNum][charNum + 1] == 'G':
                        self.avatar_nearbySprites['East'] = 'Portal'
                    elif self.map[lineNum][charNum + 1] == '0':
                        self.avatar_nearbySprites['East'] = 'Floor'
                    else:
                        raise MCTS_Exception("Unknown sprite in map!")

                if char == 'G':
                self.portal_pos = (lineNum, charNum)
                self.win = False

        if self.portal_pos == (-1,-1):
            self.isEnd = True
            self.win = True

        elif (self.avatar_pos == (-1,-1)) or (self.opponent_pos == (-1,-1)):
        #
        #caPolisher.map_print(self.map)
            print("Dude")
        #print(self.map)
            self.isEnd = True

    def serializeMap(self):
        ret = ""
        for line in self.map:
            ret += "".join(line)

        return ret


    def pressLeft(self):
    #print("left")
    #Returns true if already won, false if already lost.
    #If cannot move to left, then skip your move.
        if self.isEnd:
      #print("l")
            return self.win
        if self.leftChild is not None: #Already done this.
            return self.leftChild
        if self.avatar_nearbySprites['West'] == 'Wall':
            self.leftChild = self.pressNothing()
            return self.leftChild
    #You need to move to left for sure.
        mapToPass = copy.deepcopy(self.map)
        temp = list(mapToPass[self.avatar_pos[0]])
        temp[self.avatar_pos[1]] = '0'
        mapToPass[self.avatar_pos[0]] = "".join(temp)

        temp = list(mapToPass[self.avatar_pos[0]])
        temp[self.avatar_pos[1] - 1] = 'A'
        mapToPass[self.avatar_pos[0]] = "".join(temp)

            
        self.leftChild = MCTSNode(mapToPass, self)
        return self.leftChild


    def pressRight(self):
    #print("right")
    #Returns true if already won, false if already lost.
    #If cannot move to right, then skip your move.
        if self.isEnd:
      #print("r")
            return self.win
        if self.rightChild is not None: #Already done this.
            return self.rightChild
        if self.avatar_nearbySprites['East'] == 'Wall':
            self.rightChild = self.pressNothing()
            return self.rightChild
    #You need to move to right for sure.
        mapToPass = copy.deepcopy(self.map)

        temp = list(mapToPass[self.avatar_pos[0]])
        temp[self.avatar_pos[1]] = '0'
        mapToPass[self.avatar_pos[0]] = "".join(temp)

        temp = list(mapToPass[self.avatar_pos[0]])
        temp[self.avatar_pos[1] + 1] = 'A'
        mapToPass[self.avatar_pos[0]] = "".join(temp)


        self.rightChild = MCTSNode(mapToPass, self)
        return self.rightChild
  
    def pressDown(self):
        #Returns true if already won, false if already lost.
        #If cannot move to down, then skip your move.
        #print("down")
        
        if self.isEnd:
        #print("d")
            return self.win
        if self.downChild is not None: #Already done this.
            return self.downChild
        if self.avatar_nearbySprites['South'] == 'Wall':
            self.downChild = self.pressNothing()
            return self.downChild
        #You need to move to down for sure.
        mapToPass = copy.deepcopy(self.map)

        temp = list(mapToPass[self.avatar_pos[0]])
        temp[self.avatar_pos[1]] = '0'
        mapToPass[self.avatar_pos[0]] = "".join(temp)

        temp = list(mapToPass[self.avatar_pos[0] + 1])
        temp[self.avatar_pos[1]] = 'A'
        mapToPass[self.avatar_pos[0] + 1] = "".join(temp)

        self.downChild = MCTSNode(mapToPass, self)
        return self.downChild
  
    def pressUp(self):
        #Returns true if already won, false if already lost.
        #If cannot move to down, then skip your move.
        #print("up")
        
        if self.isEnd:
            return self.win
        if self.upChild is not None: #Already done this.
            return self.upChild
        if self.avatar_nearbySprites['North'] == 'Wall':
            self.upChild = self.pressNothing()
            return self.upChild
        #You need to move to up for sure.
        mapToPass = copy.deepcopy(self.map)

        temp = list(mapToPass[self.avatar_pos[0]])
        temp[self.avatar_pos[1]] = '0'
        mapToPass[self.avatar_pos[0]] = "".join(temp)

        temp = list(mapToPass[self.avatar_pos[0] - 1])
        temp[self.avatar_pos[1]] = 'A'
        mapToPass[self.avatar_pos[0] - 1] = "".join(temp)
        
        self.upChild = MCTSNode(mapToPass, self)
        return self.upChild
  
    def pressNothing(self):
    #print("nothing")
        if self.isEnd:
            return self.win
        if self.skipChild is not None: #Already done this.
            return self.skipChild
    
        mapToPass = copy.deepcopy(self.map)
        self.skipChild = MCTSNode(mapToPass, self)
        return self.skipChild
  
    def respectiveOpponentMove(self):
    #Priority is W>A>S>D. But, the thing is broken at some point, thus S>D>W>A.
    #If cannot move to most prior, skips.
    #Cannot move on walls, portal. Can move on floor, avatar.
    #caPolisher.map_print(self.map)
        if self.opponent_pos == (-1,-1):
            raise MCTS_Exception("Enemy is not placed")
        if self.avatar_pos[0] > self.opponent_pos[0]:  #S
      #caPolisher.map_print(self.map)
            if self.opponent_nearbySprites['South'] == 'Enemy' or self.opponent_nearbySprites['South'] == 'Floor':
        
        

                temp = list(self.map[self.opponent_pos[0]])
                temp[self.opponent_pos[1]] = '0'
                self.map[self.opponent_pos[0]] = "".join(temp)
        
                temp = list(self.opponent_pos)
                temp[0] += 1
                self.opponent_pos = tuple(temp)

                if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
                    self.isEnd = True
                    self.win = False

                temp = list(self.map[self.opponent_pos[0]])
                temp[self.opponent_pos[1]] = 'E'
                self.map[self.opponent_pos[0]] = "".join(temp)

            elif self.avatar_pos[1] > self.opponent_pos[1]:#D
      if self.opponent_nearbySprites['East'] == 'Enemy' or self.opponent_nearbySprites['East'] == 'Floor':
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)

        temp = list(self.opponent_pos)
        temp[1] += 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False

        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)
        
    elif self.avatar_pos[0] < self.opponent_pos[0]:#W
      if self.opponent_nearbySprites['North'] == 'Enemy' or self.opponent_nearbySprites['North'] == 'Floor':
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)

        temp = list(self.opponent_pos)
        temp[0] -= 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)
        
    elif self.avatar_pos[1] < self.opponent_pos[1]:#A
      if self.opponent_nearbySprites['West'] == 'Enemy' or self.opponent_nearbySprites['West'] == 'Floor':
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)

        temp = list(self.opponent_pos)
        temp[1] -= 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False

        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)
       
    else: # Cannot happen
        raise MCTS_Exception('Opponent_move, something wrong!')











    def hashMap(self):
        return hash(self.serializeMap())

    @abstractmethod
    def find_children(self):
        "All successors"
        return set(self.getleft)
    @abstractmethod
    def find_random_child(self):
        "A random successor"
        return None
    @abstractmethod
    def is_terminal(self):
        "True if this node has no child"
        return True
    @abstractmethod
    def reward(self):
        "Assume this is a terminal node"
        return 0
    @abstractmethod
    def __hash__(self):
        return self.hashMap()
    def __eq__(node1, node2):
        "Comparison by hash"
        if hash(node1) == hash(node2):
            return True
        return False





  
    

  
    

    

  

  def findChild(self, lookto):