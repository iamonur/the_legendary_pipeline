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
        players > MazeAvatar
            avatar > alternate_keys=True
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
    InteractionSet
        avatar wall > stepBack scoreChange=-1
        avatar floor > NullEffect scoreChange=-1
        goalportal avatar > killSprite scoreChange=101
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
        avatar wall > stepBack scoreChange=-1000
        floor avatar > NullEffect scoreChange=-1000
        goalportal avatar > killSprite scoreChange=1000000
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
smart_racer_opponent_str = "\n        opponent > SmartChaser stype=goalportal color=RED"
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
    def __init__(self, parent=None, action=None):
        print("New node")
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


class MCTS_Runner_Regular:
    def __init__(self,nloops=1,max_d=512,n_playouts=512, game_desc=skeleton_game_4, level_desc=dummy_maze, observer=None, render=True):
        self.loops = nloops
        self.max_depth = max_d
        self.playouts = n_playouts
        self.render = render        
        self.game =game_desc
        self.level =level_desc
        self._save_game_files()
        self.df = 0.7

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
                print(num_playout)
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
                    if reward > 0:
                        print("Got a positive reward")
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
                    print(sum_reward)
                    best_reward = sum_reward
                    best_actions = actions

                # Back-propagate

                while node:

                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent
                    sum_reward = sum_reward*self.df

            sum_reward = 0
            del state
            
            for action in best_actions:

                if self.render:

                    env.render()
    
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward

                if terminal:

                    break

            toret.append([best_actions,sum_reward])
        
        print(toret)
        print(total)
        return toret


def run_mcts():
    if not os.path.exists('mcts_new'):
        os.makedirs('mcts_new')
        next_dir = 0
    else:
        next_dir = max([int(f) for f in os.listdir('mcts_new') + ["0"] if f.isdigit()]) + 1
    rec_dir = 'mcts_new/' + str(next_dir)
    os.makedirs(rec_dir)
    print(MCTS_Runner_Regular(render=False).run())

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
        return self.controller.cummulative_reward

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


if __name__ == "__main__":
    run_mcts()