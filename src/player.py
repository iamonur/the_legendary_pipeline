import random #For random game names
import copy #For deep and shallow copies
import os #For openning, saving etc. files and system commands
from vgdl.core import Action #To use actions
from vgdl.util.humanplay.human import RecordedController #Controller to be fed with a sequence of actions
import vgdl.interfaces.gym as cim #Gym interface is used for auto-plays
import gym #Gym is for to be used by the gym interface
import vgdl.ai
import time
from math import sqrt, log
from numpy import inf
skeleton_game_4 = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN
        floor2> Immovable color=BLUE
        players > MazeAvatar
            avatar > alternate_keys=True color=WHITE
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
    InteractionSet
        avatar EOS > stepBack
        avatar wall > stepBack scoreChange=-1000
        avatar floor2> NullEffect scoreChange=-1000
        floor avatar > transformTo stype=floor2 scoreChange=-1
        goalportal avatar > killSprite scoreChange=9
    LevelMapping
        1 > wall
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_4_modifiable = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN
        players > MazeAvatar
            avatar > alternate_keys=True
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
    InteractionSet
        avatar EOS > stepBack
        avatar wall > stepBack scoreChange={WallReward}
        floor avatar > NullEffect scoreChange={FloorReward}
        goalportal avatar > killSprite scoreChange={PortalReward}
    LevelMapping
        1 > wall
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_4_backup = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN
        players > MazeAvatar
            avatar > alternate_keys=True
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
    InteractionSet
        avatar EOS > stepBack
        avatar wall > stepBack scoreChange=-100
        floor avatar > NullEffect scoreChange=-1
        goalportal avatar > killSprite scoreChange=1000009
    LevelMapping
        1 > wall
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_1 = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponent}
        players > MovingAvatar
            avatar > alternate_keys=True{free_mover_opponent}
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
        SpriteCounter stype=opponent limit=0 win=False
    InteractionSet
        avatar EOS > stepBack
        opponent goalportal > stepBack
        avatar wall > stepBack
        opponent wall > stepBack
        goalportal avatar > killSprite scoreChange=1
        opponent avatar > killSprite scoreChange=-1
    LevelMapping
        1 > wall
        E > opponent floor
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_1_smart = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponent}
        players > MovingAvatar
            avatar > alternate_keys=True{free_mover_opponent}
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
        SpriteCounter stype=opponent limit=0 win=False
    InteractionSet
        avatar EOS > stepBack
        opponent goalportal > stepBack
        avatar wall > stepBack
        opponent wall > stepBack
        goalportal avatar > killSprite scoreChange=1
        opponent avatar > killSprite scoreChange=-1
    LevelMapping
        1 > wall
        E > opponent floor
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_3 = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponent}
        players > MovingAvatar
            avatar > alternate_keys=True{free_mover_opponent}
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
        SpriteCounter stype=opponent limit=0 win=False
    InteractionSet
        avatar EOS > stepBack    
        goalportal opponent > killSprite scoreChange=-1
        avatar wall > stepBack
        opponent wall > stepBack
        goalportal avatar > killSprite scoreChange=1
        opponent avatar > stepBack
        avatar opponent > stepBack
    LevelMapping
        1 > wall
        E > opponent floor
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_3_smart = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponent}
        players > MovingAvatar
            avatar > alternate_keys=True{free_mover_opponent}
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
        SpriteCounter stype=opponent limit=0 win=False
    InteractionSet
        avatar EOS > stepBack
        goalportal opponent > killSprite scoreChange=-100000
        avatar wall > stepBack scoreChange=-1000
        floor avatar > NullEffect scoreChange=-1
        opponent wall > stepBack
        goalportal avatar > killSprite scoreChange=1000000
        opponent avatar > stepBack
        avatar opponent > stepBack
    LevelMapping
        1 > wall
        E > opponent floor
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_2 = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponent}
        players > MovingAvatar
            avatar > alternate_keys=True{free_mover_opponent}
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=False
        SpriteCounter stype=opponent limit=0 win=True
    InteractionSet
        avatar EOS > stepBack
        goalportal opponent > killSprite scoreChange=-1
        avatar wall > stepBack
        opponent wall > stepBack
        opponent avatar > killSprite scoreChange=1
        avatar goalportal > stepBack
    LevelMapping
        1 > wall
        E > opponent floor
        G > goalportal
        A > avatar floor
        0 > floor
"""
skeleton_game_2_smart = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponent}
        players > MovingAvatar
            avatar > alternate_keys=True{free_mover_opponent}
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=False
        SpriteCounter stype=opponent limit=0 win=True
    InteractionSet
        avatar EOS > stepBack
        goalportal opponent > killSprite scoreChange=-1
        avatar wall > stepBack
        opponent wall > stepBack
        opponent avatar > killSprite scoreChange=1
        avatar goalportal > stepBack
    LevelMapping
        1 > wall
        E > opponent floor
        G > goalportal
        A > avatar floor
        0 > floor
"""
dummy_maze = """11111111\n1A000001\n10000001\n11110001\n10000001\n10000001\n100000G1\n11111111\n"""


def stringify_list_level(level):
    ret = ""
    width = len(level[0])+2
    for _ in range(width):
        ret += "w"
    ret+="\n"
    for line in level:
        ret += ("w"+"".join(line)+"w")
        ret += "\n"
    for _ in range(width):
        ret += "w"
    ret+="\n"
    return ret



dummy_actions = ['D', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip']

immovable_opponent_str ="\n        opponent > Immovable color=BLUE"
smart_racer_opponent_str = "\n        opponent > LookupChaser stype=goalportal color=RED"
smart_chaser_opponent_str = "\n        opponent > SmartChaser stype=goalportal color=RED"
chaser_opponent_str="\n        opponent > Chaser stype=avatar color=RED"
racer_str="\n        opponent > Chaser stype=goalportal color=RED"
astar_chaser_str="\n        opponent > AStarChaser stype=avatar color=RED"
free_mover_str="\n            opponent > color=DARKBLUE"

gamefile = "tempgame.txt"
levelfile = "tempgame_levl0.txt"

def combinations(space):
    if isinstance(space, gym.spaces.Discrete):
        return range(space.n)
    elif isinstance(space, gym.spaces.Tuple):
        return itertools.product(*[combinations(s) for s in space.spaces])
    else:
        raise NotImplementedError

class MCTS_Node:
    def __init__(self, position_1=0, position_2=0, parent=None, action=None):
        #print("New node")
        self.first = position_1
        self.second = position_2
        self.parent = parent
        self.action = action
        self.children = []
        self.explored_children = 0
        self.visits = 0
        self.value = 0

def ucb(node):
    return node.value / node.visits + sqrt(log(node.parent.visits)/node.visits)

def moving_average(v, n):
    n = min(len(v), n)
    ret = [.0] * (len(v) - n + 1)
    ret[0] = float(sum(v[:n])) / n
    for i in range(len(v) - n):
        ret[i + 1] = ret[i] + float(v[n + i] - v[i]) / n
    return ret

class MCTS_Runner_Reward:
    def __init__(self, max_d=500, reward_goal=-2000, game_desc=skeleton_game_4, level_desc=dummy_maze, observer=None, render=False):
        self.max_depth = max_d
        self.aim = reward_goal
        self.game = game_desc
        self.level = level_desc
        self.render = render
        self._save_game_files()

    def _save_game_files(self):
        game_fh = open(gamefile,'w')
        game_fh.write(self.game)
        game_fh.close()

        level_fh = open(levelfile,'w')
        level_fh.write(self.level)
        level_fh.close()

    def run(self):
        toret = []
        best_rewards = []
        env = cim.VGDLEnv(game_file = gamefile, level_file = levelfile, obs_type='features', block_size=24)#gym.make(self.env_name)
        print("My goal is " + str(self.aim))
        #for loop in range(self.loops):
        while True:
            env.reset()
            root = MCTS_Node()
            best_actions = []
            best_reward = float(-inf)

            #for num_playout in range(self.playouts):
            while best_reward < self.aim:
                state = copy.deepcopy(env)
                state.observer.game = env.observer.game
                state.reset()
                sum_reward = 0
                node = root
                terminal = False
                actions = []

                # Selection
                while node.children:

                    if node.explored_children < len(node.children):

                        child = node.children[node.explored_children]
                        node.explored_children += 1
                        node = child

                    else:

                        node = max(node.children, key=ucb)
                    _, reward, terminal, _ = state.step(node.action)
                    sum_reward += reward
                    actions.append(node.action)

                # Expansion
                if not terminal:

                    node.children = [MCTS_Node(node, a) for a in combinations(state.action_space)]
                    random.shuffle(node.children)
                
                # Playout

                while not terminal:

                    action = state.action_space.sample()

                    if self.render:

                        state.render()

                    _, reward, terminal, _ = state.step(action)
                    sum_reward += reward
                    actions.append(action)

                    if len(actions) > self.max_depth:

                        sum_reward -= 100
                        break

                # Remember the best
                
                if best_reward < sum_reward:

                    best_reward = sum_reward
                    best_actions = actions

                    print(best_reward)

                # Back-propagate

                while node:

                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent
            

            sum_reward = 0
            
            for action in best_actions:

                if self.render:

                    env.render()
    
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward

                if terminal:

                    break
            env.monitor.close()
            toret.append([best_actions,sum_reward])
            best_rewards.append(sum_reward)
            score = max(moving_average(best_rewards, 100))
            return toret

class MCTS_Runner_Timed:
    def __init__(self, max_d=500, seconds=60, game_desc=skeleton_game_4, level_desc=dummy_maze, observer=None, render=True):
        self.max_depth = max_d
        self.seconds = seconds
        self.game = game_desc
        self.level = level_desc
        self.render = render
        self._save_game_files()
        self.discount_factor = 0.9
        self.nodes = {}

    def _save_game_files(self):

        game_fh = open(gamefile,'w')
        game_fh.write(self.game)
        game_fh.close()

        level_fh = open(levelfile,'w')
        level_fh.write(self.level)
        level_fh.close()

    def _new_MCTS_Node(self, node, a):

        return MCTS_Node(node, a)

    def run(self):
        finish_at = time.time() + self.seconds
        toret = []
        best_rewards = []
        env = cim.VGDLEnv(game_file = gamefile, level_file = levelfile, obs_type = 'features', block_size=24)

        while True:

            env.reset()
            root = MCTS_Node()
            best_actions = []
            best_reward = float(-inf)

            while True:
                if time.time() > finish_at:
            
                    break

                state = copy.deepcopy(env)
                state.observer.game = env.observer.game
                #state.reset()
                sum_reward = 0
                node = root
                terminal = False
                actions = []

                # Selection

                while node.children:

                    if node.explored_children < len(node.children):

                        child = node.children[node.explored_children]
                        node.explored_children += 1
                        node = child

                    else:
                        node = max(node.children, key = ucb)

                    _, reward, terminal, _ = state.step(node.action)
                    sum_reward += reward
                    actions.append(node.action)

                # Expansion

                if not terminal:

                    node.children = [self._new_MCTS_Node(node, a) for a in combinations(state.action_space)]
                    random.shuffle(node.children)

                # Playout

                while not terminal:

                    action = state.action_space.sample()

                    if self.render:

                        state.render()

                    _, reward, terminal, _ = state.step(action)
                    sum_reward += reward
                    actions.append(action)

                    if len(actions) > self.max_depth:
                        sum_reward -= 1000
                        break

                # Remember the best
                
                if best_reward < sum_reward and terminal:
                    print(sum_reward)
                    print("asd")
                    best_reward = sum_reward
                    best_actions = actions

                # Back-propagate

                while node:

                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent
                    sum_reward = sum_reward*self.discount_factor

                del state

            sum_reward = 0
            
            for action in best_actions:

                if self.render:

                    env.render()
    
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward

                if terminal:

                    break
            del env
            toret.append([best_actions,sum_reward])
            best_rewards.append(sum_reward)
            #score = max(moving_average(best_rewards, 100))
            return toret

class MCTS_Runner_Reward_Timeout:
    def __init__(self, max_d=500, seconds=60, reward_goal=-2000, game_desc=skeleton_game_4, level_desc=dummy_maze, observer=None, render=True):
        self.max_depth = max_d
        self.seconds = seconds
        self.game = game_desc
        self.level = level_desc
        self.render = render
        self.aim = reward_goal
        self._save_game_files()
        print("Got to finish in: " + str(self.seconds) + " seconds and need to get: " + str(self.aim) + " points.")

    def _save_game_files(self):

        game_fh = open(gamefile,'w')
        game_fh.write(self.game)
        game_fh.close()

        level_fh = open(levelfile,'w')
        level_fh.write(self.level)
        level_fh.close()


    def run(self):
        finish_at = time.time() + self.seconds
        toret = []
        best_rewards = []
        env = cim.VGDLEnv(game_file = gamefile, level_file = levelfile, obs_type = 'features', block_size=24)

        while True:

            env.reset()
            root = MCTS_Node()
            best_actions = []
            best_reward = float(-inf)

            while True:

                

                if time.time() > finish_at:
            
                    break

                if best_reward > self.aim:

                    break

                state = copy.deepcopy(env)
                state.observer.game = env.observer.game
                sum_reward = 0
                node = root
                terminal = False
                actions = []

                # Selection

                while node.children:

                    if node.explored_children < len(node.children):

                        child = node.children[node.explored_children]
                        node.explored_children += 1
                        node = child

                    else:

                        node = max(node.children, key = ucb)

                    _, reward, terminal, _ = state.step(node.action)
                    sum_reward += reward
                    actions.append(node.action)

                # Expansion

                if not terminal:

                    node.children = [MCTS_Node(node, a) for a in combinations(state.action_space)]
                    random.shuffle(node.children)

                # Playout

                while not terminal:

                    action = state.action_space.sample()

                    if self.render:

                        state.render()

                    _, reward, terminal, _ = state.step(action)
                    sum_reward += reward
                    actions.append(action)

                    if len(actions) > self.max_depth:

                        #sum_reward -= 100
                        break

                # Remember the best
                
                if best_reward < sum_reward:

                    best_reward = sum_reward
                    best_actions = actions
                    print(best_reward)

                # Back-propagate

                while node:

                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent

                del(state._monitor)

            sum_reward = 0
            
            for action in best_actions:

                if self.render:

                    env.render()
    
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward

                if terminal:

                    break

            toret.append([best_actions,sum_reward])
            best_rewards.append(sum_reward)
            score = max(moving_average(best_rewards, 100))
            return toret

class MCTS_Runner_Regular_Old:
    def __init__(self,nloops=1,max_d=40,n_playouts=1024, game_desc=skeleton_game_4_backup, level_desc=dummy_maze, observer=None, render=True):
        self.loops = nloops
        self.max_depth = max_d
        self.playouts = n_playouts
        self.render = render
        
        #from gym.envs.registration import register, registry
        
        self.game =game_desc
        self.level =level_desc
        self._save_game_files()
        #level_name = '.'.join(os.path.basename(levelfile).split('.')[:-1])
        #self.env_name = 'vgdl_{}-{}-v0'.format(random.random(),level_name)
        #register(id = self.env_name, entry_point = 'vgdl.interfaces.gym:VGDLEnv', kwargs = {'game_file':gamefile, 'level_file':levelfile, 'block_size':24, 'obs_type':'features',},nondeterministic=True)
    def _save_game_files(self):
        game_fh = open(gamefile,'w')
        game_fh.write(self.game)
        game_fh.close()
        level_fh = open(levelfile,'w')
        level_fh.write(self.level)
        level_fh.close()
    def run(self):
        toret = []
        best_rewards = []
        env = cim.VGDLEnv(game_file = gamefile, level_file = levelfile, obs_type='features', block_size=24)#gym.make(self.env_name)
        for loop in range(self.loops):
            env.reset()
            root = MCTS_Node()
            best_actions = []
            best_reward = float(-inf)
            for num_playout in range(self.playouts):
                state = copy.deepcopy(env)
                state.observer.game = env.observer.game
                sum_reward = 0
                node = root
                terminal = False
                actions = []
                # Selection
                while node.children:
                    if node.explored_children < len(node.children):
                        child = node.children[node.explored_children]
                        node.explored_children += 1
                        node = child
                    else:
                        node = max(node.children, key=ucb)
                    _, reward, terminal, _ = state.step(node.action)
                    sum_reward += reward
                    actions.append(node.action)
                # Expansion
                if not terminal:
                    node.children = [MCTS_Node(parent=node, action=a) for a in combinations(state.action_space)]
                    random.shuffle(node.children)
                
                # Playout
                while not terminal:
                    action = state.action_space.sample()
                    if self.render:
                        state.render()
                    _, reward, terminal, _ = state.step(action)
                    sum_reward += reward
                    actions.append(action)
                    if len(actions) > self.max_depth:
                        sum_reward -= 100
                        break
                # Remember the best
                
                if best_reward < sum_reward:
                    best_reward = sum_reward
                    best_actions = actions
                # Back-propagate
                while node:
                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent
            sum_reward = 0
            
            for action in best_actions:
                if self.render:
                    env.render()
    
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward
                if terminal:
                    break
            toret.append([best_actions,sum_reward])
        return toret

class MCTS_Runner_Regular:
    def __init__(self,nloops=1,max_d=20,n_playouts=500, rollout_depth=50, game_desc=skeleton_game_4_backup, level_desc=dummy_maze, observer=None, render=True, discount_factor=0.95):
        self.loops = nloops
        self.max_depth = max_d
        self.rollout_depth = rollout_depth
        self.playouts = n_playouts
        self.render = render        
        self.game =game_desc
        self.level =level_desc
        self._save_game_files()
        self.df = discount_factor
        self.width = 26
        self.height = 26

    def init_my_second_level(self):
        self.second_level = []
        
        for i in range(0,self.height):

            temp = []

            for i in range(0, self.width):

                temp.append(0)

            self.second_level.append(copy.deepcopy(temp))


    def _save_game_files(self):

        game_fh = open(gamefile,'w')
        game_fh.write(self.game)
        game_fh.close()

        level_fh = open(levelfile,'w')
        level_fh.write(self.level)
        level_fh.close()


    def run_(self):
        terminal = False
        to_ret = []
        env = cim.VGDLEnv(game_file=gamefile, level_file=levelfile, obs_type='features', block_size=24)

        for loop in range(self.loops):

            moves_to_play = []
            sum_reward = 0
            while not terminal or len(moves_to_play) != self.rollout_depth:

                env.reset()
                #Get your second level started.

                for move in moves_to_play:
                    env.step(move.action)


                move = self.search() #search function to be filled.


    def search(self, env):
        best_action = None
        best_reward = float(-inf)
        root = MCTS_Node()#Find your avatar's position on game map?
        for num_playout in range(self.playouts):
            state = copy.deepcopy(env)
            state.observer.game = env.observer.game
            sum_reward = 0
            sum_reward2= 0

    def run(self):

        toret = []
        best_rewards = []
        env = cim.VGDLEnv(game_file = gamefile, level_file = levelfile, obs_type='features', block_size=24)#gym.make(self.env_name)

        for loop in range(self.loops):
            env.reset()
            temp = self.level.split('\n')
            
            self.init_my_second_level()
            for a in range(0,self.height):
                temp[a] = list(temp[a])
                
            for a in range(self.height):
                for b in range(self.width):

                    if temp[a][b] == 'A':

                        p1 = a
                        p2 = b
                        self.second_level[a][b] += 1


            root = MCTS_Node(p1, p2)
            best_actions = []
            best_reward = float(-inf)

            for num_playout in range(self.playouts):
                #print(self.second_level)
                state = copy.deepcopy(env)
                state.observer.game = env.observer.game
                sum_reward = 0
                sum_reward2= 0
                node = root
                terminal = False
                actions = []
                # Selection

                while node.children:

                    if node.explored_children < len(node.children):
                        child = node.children[node.explored_children]
                        node.explored_children += 1
                        node = child

                    else:

                        node = max(node.children, key=ucb)
                        
                    _, reward, terminal, _ = state.step(node.action) #This is where
                    self.second_level[node.first][node.second] += 1
                    sum_reward += reward * self.second_level[node.first][node.second]
                    sum_reward2+= reward
                    actions.append(node.action)

                # Expansion
                if not terminal:
                    
                    node.children = []
                    if node.first != 0 and temp[node.first-1][node.second] == '1':
                        node.children.append(MCTS_Node(node.first,node.second,node,0))#UP
                    else:
                        node.children.append(MCTS_Node(node.first-1,node.second,node,0))#UP

                    if node.first != (self.width-1) and temp[node.first+1][node.second] == '1':
                        node.children.append(MCTS_Node(node.first,node.second,node,2))#DOWN
                    else:
                        node.children.append(MCTS_Node(node.first+1,node.second,node,2))#DOWN
                    
                    if node.second != 0 and temp[node.first][node.second-1] == '1':
                        node.children.append(MCTS_Node(node.first,node.second,node,1))#LEFT
                    else:
                        node.children.append(MCTS_Node(node.first,node.second-1,node,1))#LEFT
                    
                    
                    
                    if node.first != (self.width-1) and temp[node.first][node.second+1] == '1':
                        node.children.append(MCTS_Node(node.first,node.second,node,3))#RIGHT
                    else:
                        node.children.append(MCTS_Node(node.first,node.second+1,node,3))#RIGHT

                    random.shuffle(node.children)
                
                # Playout

                while not terminal:

                    action = state.action_space.sample()

                    if self.render:

                        state.render()

                    _, reward, terminal, _ = state.step(action) #And where
                    sum_reward += reward
                    sum_reward2+= reward
                    actions.append(action)

                    if len(actions) > self.rollout_depth:
                        break


                # Remember the best
                
                if best_reward < sum_reward: #XXX: Remember next action only, not all actions.
                    best_reward = sum_reward
                    best_actions = actions


                # Back-propagate

                while node:

                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent
                    sum_reward = sum_reward * self.df

            sum_reward = 0
            del state
            
            for action in best_actions: #XXX: Should play and return single moves.

                if self.render:

                    env.render()
    
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward
                #sum_reward2+= reward
                if terminal:

                    break

            toret.append([best_actions,sum_reward])
        return toret

def run_mcts():
    if not os.path.exists('mcts_new'):
        os.makedirs('mcts_new')
        next_dir = 0
    else:
        next_dir = max([int(f) for f in os.listdir('mcts_new') + ["0"] if f.isdigit()]) + 1
    rec_dir = 'mcts_new/' + str(next_dir)
    os.makedirs(rec_dir)
    return(MCTS_Runner_Regular(render=False).run()[0])

def run_timed_mcts():
    print(MCTS_Runner_Timed(seconds=1,render=False).run())

class GameClass:
    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_1.format(immovable_opponent="",free_mover_opponent="",chaser_opponent=chaser_opponent_str), level_desc=dummy_maze):
        
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc

        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

    def _register_environment(self, domain_file, level_file, observer=None, blocksize=32):
        
        from gym.envs.registration import register, registry
        level_name = '.'.join(os.path.basename(level_file).split('.')[:-1])
        self.env_name = 'vgdl_{}-{}-v0'.format(random.random(), level_name)

        register(
            id = self.env_name,
            entry_point = 'vgdl.interfaces.gym:VGDLEnv',
            kwargs={
                'game_file': domain_file,
                'level_file': level_file,
                'block_size': blocksize,
                'obs_type': observer or 'features',
            },
            nondeterministic=True
        )

    def _format_actions(self):
        
        for i, action in enumerate(self.actions):
            if action == 'A':
                self.actions[i] = 0
            elif action == 'S':
                self.actions[i] = 3
            elif action == 'D':
                self.actions[i] = 1
            elif action == 'W':
                self.actions[i] = 2
            elif action == 'Skip':
                self.actions[i] = -1

       # print(self.actions)

    def _create_controller(self):
        
        self.controller = RecordedController(self.env_name, self.actions, fps=60)

    def _save_game_files(self):

        game_f = open(gamefile, 'w')
        game_f.write(self.game)
        game_f.close()

        level_f = open(levelfile, 'w')
        if self.level == dummy_maze:
            level_f.write(self.level)
        else:
            level_f.write(stringify_list_level(self.level))
        level_f.close()

    def play(self):

        self.controller.play()
        return self.controller.cummulative_reward, self.controller.terminal

class RacerGameClass(GameClass):

    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_3.format(immovable_opponent = "", free_mover_opponent = "", chaser_opponent = racer_str), level_desc=dummy_maze):
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

class MazeGameClass(GameClass):

    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_4, level_desc=dummy_maze):
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

class ChaserGameClass(GameClass):
    
    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_2.format(immovable_opponent = "", free_mover_opponent = "", chaser_opponent = racer_str), level_desc=dummy_maze):
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

class ChaserGameClass_Smart(GameClass):
    
     def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_2_smart.format(immovable_opponent = "", free_mover_opponent = "", chaser_opponent = smart_racer_opponent_str), level_desc=dummy_maze):
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

class RacerGameClass_Smart(GameClass):

    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_3_smart.format(immovable_opponent = "", free_mover_opponent = "", chaser_opponent = smart_racer_opponent_str), level_desc=dummy_maze):
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

class GameClass_Smart(GameClass):
    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_1_smart.format(immovable_opponent = "", free_mover_opponent = "", chaser_opponent = smart_chaser_opponent_str), level_desc=dummy_maze):
        self.actions = action_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment(gamefile, levelfile)
        self._format_actions()
        self._create_controller()

def main_func():
    total_goal_reached = 0
    total_aced = 0
    total_wrong_1 = 0
    total_wrong_2 = 0
    number_of_runs = 50

    for a in range(0,number_of_runs):
        asd = run_mcts()
        res = -asd[1]
        moves = asd[0]
        print(res)
        print(moves)
        wrong_1 = res%1000
        wrong_2 = res//1000
        if(wrong_1 + wrong_2) > 19:
            print("Run number {} failed to achieve the goal".format(a))
        elif (wrong_1+wrong_2) == 0:
            print("MCTS aced run #{}".format(a))
            total_goal_reached += 1
            total_aced += 1
        else:
            print("Run Number: {}   Type-1_Wrongs:{}   Type-2_Wrongs{}".format(a,wrong_1,wrong_2))
            total_goal_reached += 1
            total_wrong_1 += wrong_1
            total_wrong_2 += wrong_2

    print("In {} runs, {} of them achieved to find the goal within 20 mistakes, a total success rate of {}".format(number_of_runs, total_goal_reached, total_goal_reached/number_of_runs))
    print("In {} runs that is succesful, the type-1 mistake average is {}, and the type-2 mistake average is {}".format(total_goal_reached ,total_wrong_1/total_goal_reached, total_wrong_2/total_goal_reached))
    print("{} of the {} runs were an ace, that is {} in one game".format(total_aced, number_of_runs, total_aced/number_of_runs))

class mcts_tryout:
    def __init__(self, MCTS_Class, numTry=1, max_reward=1000000, spin_out_len=10, max_state_changes=10000, render_while_running=False, verbose=True, level=dummy_maze):
        self.myMCTS = MCTS_Class
        self.tries = numTry
        self.goal = max_reward
        self.verbose = verbose
        self.render = render_while_running
        self.max_depth = spin_out_len
        self.num_playouts = 10000//self.max_depth
        self.my_rules = self.__getRules(spin_out_len)
        self.level = level
        self.outputs = []
    def __getRules(self, spin_len):
        wallRew = "-1000"
        floorRew = "-1"
        portalRew = str( self.goal -( (spin_len-1) * int(floorRew) ) )
        return skeleton_game_4_modifiable.format(WallReward=wallRew, FloorReward=floorRew, PortalReward=portalRew)
    def run(self):
        output = []
        for q in range(self.tries):
            print(q)
            runtime = time.time()
            moves = self.myMCTS(max_d=self.max_depth, n_playouts=self.num_playouts, game_desc=self.my_rules, level_desc=self.level, render=self.render).run()[0][0]
            runtime = time.time() - runtime
            my_score = MazeGameClass(action_list=moves, game_desc=self.my_rules, level_desc=self.level).play()
            output.append([moves, my_score, self.__analyze_score(my_score),runtime])
        return output
    def __analyze_score(self, score):
        if score > 0:
            win = True
        else:
            win = False

        if win:
            score = -(score - self.goal)
        else:
            score = -score

        walls = score//1000
        displacements = score%1000

        return [win,displacements,walls]

def mcts_exp(n_runs):
    for _ in range(n_runs):
        moves = MCTS_Runner_Regular(render=False).run()[0][0]
        game = MazeGameClass(action_list=moves, game_desc=skeleton_game_4_backup)
        score = game.play()

        print("I got score:" + str(score))

class spin_tryout:
    def __init__(self, SPIN_Class, Parser_Class, numTry=1, verbose=True, level=dummy_maze, goal=1000000):
        self.mySpin = SPIN_Class
        self.myParser = Parser_Class
        self.tries = numTry
        self.verbose = verbose
        self.level = level
        self.formatted_level = self.format_level(level)
        self.my_rules = skeleton_game_4_backup
        self.output = []
        self.goal = goal

    def format_level(self, level):
        ret = level.split("\n")[:-1]
        for a,b in enumerate(ret):
            ret[a] = list(b)
        return ret

    def run(self):
        output = []
        for q in range(self.tries):
            print(q)
            runtime = time.time()
            spinning = self.mySpin(self.formatted_level).perform()
            parser = self.myParser()
            moves, _ = parser.perform()
            runtime = time.time() - runtime
            my_score = MazeGameClass(action_list=moves, game_desc=self.my_rules, level_desc=self.level).play()
            output.append([moves,my_score, self.__analyze_score(my_score),runtime])
        return output
    def __analyze_score(self, score):
        if score > 0:
            win = True
        else:
            win = False

        if win:
            score = -(score - self.goal)
        else:
            score = -score

        walls = score//1000
        displacements = score%1000

        return [win,displacements,walls]

    

def spin_performance_check(spin_type,parser_type,tryouts):
    results = spin_tryout(spin_type,parser_type,numTry=tryouts).run()
    total_wins = 0
    total_displacements = 0
    total_hits = 0
    total_perfects = 0
    min_time = float(inf)
    max_time = float(-inf)
    total_time = 0
    for result in results:
        
        if result[3] > max_time:
            max_time = result[3]
        
        if result[3] < min_time:
            min_time = result[3]

        total_time += result[3]

        if result[2][0] == False: #Lost
            continue
        else: #Won
            total_wins += 1
            if result[2][1] == 0 and result[2][2] == 0: #Perfect run
                total_perfects += 1
                continue
            total_displacements += result[2][1]
            total_hits += result[2][2]
    result_string = ""
    result_string = "{} win rate, {} displacement rate in wins, {} hit rate in wins.".format((total_wins/tryouts), (total_displacements/total_wins), (total_hits/total_wins))
    result_string +="\nPerfect ratio is {} from all games, and {} from games that are won.".format((total_perfects/tryouts),(total_perfects/total_wins))
    result_string +="\nMinimum time cost is {}, maximum time cost is {}, and average time cost is {}".format(min_time, max_time, total_time/tryouts)

    return result_string


def mcts_performance_check(mcts_type,tryouts):
    results = mcts_tryout(mcts_type, numTry=tryouts).run()
    total_wins = 0
    total_displacements = 0
    total_hits = 0
    total_perfects = 0
    min_time = float(inf)
    max_time = float(-inf)
    total_time = 0
    for result in results:
        
        if result[3] > max_time:
            max_time = result[3]
        
        if result[3] < min_time:
            min_time = result[3]

        total_time += result[3]

        if result[2][0] == False: #Lost
            continue
        else: #Won
            total_wins += 1
            if result[2][1] == 0 and result[2][2] == 0: #Perfect run
                total_perfects += 1
                continue
            total_displacements += result[2][1]
            total_hits += result[2][2]

    result_string = "{} win rate, {} displacement rate in wins, {} hit rate in wins.".format((total_wins/tryouts), (total_displacements/total_wins), (total_hits/total_wins))
    result_string +="\nPerfect ratio is {} from all games, and {} from games that are won.".format((total_perfects/tryouts),(total_perfects/total_wins))
    result_string +="\nMinimum time cost is {}, maximum time cost is {}, and average time cost is {}".format(min_time, max_time, total_time/tryouts)
    result_string +="\nMaximum depth allowed was: 100, so there was 100 playouts per tryout."

    return result_string

if __name__=="__main__":
    import spinner
    import spinParser
    print(spin_performance_check(spinner.SpinClass_Game4_Parameter_Capital_I, spinParser.spinParser, 100))
    """print("New MCTS:")
    print(mcts_performance_check(MCTS_Runner_Regular,100))
    print("Old MCTS:")
    print(mcts_performance_check(MCTS_Runner_Regular_Old,100))"""