from abc import ABC, abstractmethod
import numpy as np
from collections import defaultdict
from copy import deepcopy

class illegalMoveException(Exception):
    pass

class MCT_Node(ABC):

    def __init__(self, state, parent=None):
        """"""
        self.state = state
        self.parent = parent
        self.children = []

    @abstractmethod
    @property
    def untried_actions(self): 
        """
        Returns a list of actions that are not taken yet.
        """
        pass

    @abstractmethod
    @property
    def q(self):
        """
        Returns the average reward beneath this node.
        """
        pass

    @abstractmethod
    @property
    def n(self):
        """
        Returns the number of visits for this node.
        """
        pass
    
    @abstractmethod
    def expand(self):
        """
        If not a terminal node, neeeds its children.
        """
        pass

    @abstractmethod
    def is_terminal_node(self):
        """
        If terminal, needs to backpropagate etc.
        """
        pass

    @abstractmethod
    def rollout(self):
        """
        If not terminal, run a simulated playout from node until result.
        """
        pass

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.4):
        choices_weight = [ (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n)) for c in self.children ]
        return self.children[np.argmax(choices_weight)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))] #Chooses randomly for rolluot.


class my_maze_node(MCT_Node):
    def __init__(self, state, parent=None):
        super().__init__(state, parent)
        self._number_of_visits = 0.
        self._results = defaultdict()
        self._untried_actions = None

    @property
    def untried_actions(self):
        if self._untried_actions is None:
            self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    @property
    def q(self):
        wins = self._results[self.parent.state.game_result]
        loses = self._results[-1 * self.parent.state.game_result]
        return wins - loses

    @property
    def n(self):
        return self._number_of_visits

    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.move(action)
        return current_rollout_state.game_result

    def backpropagate(self, result)
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

class MCTS(object):
    def __init__(self, node):
        self.root = node

    def best_action(self, simulations_number):
        for _ in range(0, simulations_number):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        return self.root.best_child(c_param=0.)

    def _tree_policy(self):
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_terminal_node():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

class two_player_abstract_game_state(ABC):
    @abstractmethod
    def game_result(self):
        """
        1 if Avatar wins
        -1 if Opponent wins
        None for unknown
        """
        pass

    def is_game_over(self):
        return self.game_result() is not None

    @abstractmethod
    def move(self, action):
        """
        Consumes action, creates the new game_state and returns
        """
        pass

    @abstractmethod
    def get_legal_actions(self):
        """
        Returns list of possible to make actions.
        """
        pass

class abstract_game_action(ABC):
    pass

class my_maze_move(abstract_game_action):
    def __init__(self, line, char, mover): #Mover is either 'avatar' or 'enemy'
        self.line = line
        self.char = char
        self.mover = mover

    def __repr__(self):
        #Returns a string to identify move
        return "x:{} y:{} {}".format(self.line, self.char, self.mover)

class my_maze_state(two_player_abstract_game_state):
    def __init__(self, map): #Done-sies
        """
        Parses map to create itself. Probably only root node needs this.
        """
        self.lines = len(map)
        self.chars = len(map[0])
        self.walls = []
        for ln, line in enumerate(map):
            for cn, char in enumerate(line):
                if char == 'A':
                    self.avatar = (ln,cn)
                elif char == 'E':
                    self.enemy = (ln,cn)
                elif char == 'G':
                    self.portal = (ln,cn)
                elif char == '1':
                    self.walls.append((ln,cn))
        self.__append_legal_actions()

    def __init__(self, walls, avatar, enemy, portal, lines, chars): #Done-sies
        """
        Don't need the whole map to state yourself.
        """
        self.lines = lines
        self.chars = chars
        self.walls = walls
        self.avatar = avatar
        self.enemy = enemy
        self.portal = portal
        self.game_result = None
        if self.portal == self.avatar: #Avatar stepped on portal.
            self.game_result = 1 
        elif self.avatar == self.enemy: #Enemy stepped on avatar.
            self.game_result = -1
        self.legal_actions = self.__append_legal_actions()

    def __append_legal_actions(self): #Done-sies
        if self.game_result is None:
            return []
        retlist = []
        #Skipping is always valid.
        retlist.append(my_maze_move(self.avatar[0], self.avatar[1], 'Avatar'))

        #Only walls break you
        if self.avatar[0] > 0: #Cannot go up otherwise
            temp = (self.avatar[0]-1, self.avatar[1])
            if temp not in self.walls:
                retlist.append(my_maze_move(self.avatar[0]-1, self.avatar[1], 'Avatar'))

        if self.avatar[0] < self.lines-1: #Cannot go down otherwise
            temp = (self.avatar[0]+1, self.avatar[1])
            if temp not in self.walls:
                retlist.append(my_maze_move(self.avatar[0]+1, self.avatar[1], 'Avatar'))
        
        if self.avatar[1] < self.chars-1: #Cannot go right otherwise
            temp = (self.avatar[0], self.avatar[1]+1)
            if temp not in self.walls:
                retlist.append(my_maze_move(self.avatar[0], self.avatar[1]+1, 'Avatar'))
        
        if self.avatar[1] > 0: #Cannot go left otherwise
            temp = (self.avatar[0], self.avatar[1]-1)
            if temp not in self.walls:
                retlist.append(my_maze_move(self.avatar[0], self.avatar[1]-1, 'Avatar'))

        return retlist

    def move(self, action): #Done-sies
        """
        Take action and move avatar. Then move opponent respectively.
        """
        if self.game_result is not None:
            #Should not move here, since the game ended.
            raise illegalMoveException("Move arrived after the game is over.")

        if action.mover == 'Avatar':
            #Check legality of move. Can move on portal, opponent, and floor. Cannot move on walls.
            if action not in self.legal_actions:
                raise illegalMoveException("Take your actions from me, dude! Yours was {}".format(action))

            #Create the next state.
            nextState = my_maze_state(self.walls, (action.line, action.char), self.enemy, self.portal, self.lines, self.chars)
            nextState = nextState._move_dummy_enemy()
        elif action.mover == 'Enemy': 
            #Parent shouldn't change here, the real parent was just a phase.
            
            #No illegal action will be there since the action is not from outside. SO I'M NOT CHECKING.

            nextState = my_maze_move(self.walls, self.avatar, (action.line, action.char), self.portal, self.lines, self.chars)

        return nextState

    def get_legal_actions(self): #Done-sies
        """
        Look around of avatar. Return possible moves.
        """
        return self.legal_actions

    def _move_dummy_enemy(self): #LEFT, UP, RIGHT, DOWN
        """
        Moves enemy wrt avatar.
        """
        if self.game_result is not None:
            return self

        if self.avatar[1] < self.enemy[1]:
            return self.move(my_maze_move(,,'Enemy'))

        elif self.avatar[0] < self.enemy[0]:
            return self.move(my_maze_move(,,'Enemy'))

        elif self.avatar[1] > self.enemy[1]:
            return self.move(my_maze_move(,,'Enemy'))

        elif self.avatar[0] > self.enemy[0]:
            return self.move(my_maze_move(,,'Enemy'))
        

    def game_result(self): #Done-sies
        """
        Return result if ended. Else return None.
        """
        return self.game_result
