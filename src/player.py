import random #For random game names
import copy #For deep and shallow copies
import os #For openning, saving etc. files and system commands
from vgdl.core import Action #To use actions
from vgdl.util.humanplay.human import RecordedController #Controller to be fed with a sequence of actions
import vgdl.interfaces.gym #Gym interface is used for auto-plays
import gym #Gym is for to be used by the gym interface
import vgdl.ai
skeleton_game_4 = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN
        players > MovingAvatar
            avatar > alternate_keys=True
    TerminationSet
        SpriteCounter stype=goalportal limit=0 win=True
    InteractionSet
        avatar wall > stepBack
        goalportal avatar > killSprite scoreChange=1
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
dummy_maze = """11111111\n1A000E01\n10000001\n11110001\n10000001\n10000001\n100000G1\n11111111\n"""

def stringify_list_level(level):
    ret = ""
    for line in level:
        ret += "".join(line)
        ret += "\n"

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
    m = GameClass_Smart()
    print(m.play())