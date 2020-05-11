import random #For random game names
import copy #For deep and shallow copies
import os #For openning, saving etc. files and system commands
from vgdl.core import Action #To use actions
from vgdl.util.humanplay.human import RecordedController #Controller to be fed with a sequence of actions
import vgdl.interfaces.gym #Gym interface is used for auto-plays
import gym #Gym is for to be used by the gym interface
import vgdl.ai

skeleton_game_1 = """
BasicGame
    SpriteSet
        goalportal > Immovable color=GREEN
        wall > Immovable color=BLACK
        floor > Immovable color=BROWN{immovable_opponent}{chaser_opponnent}
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
        E > opponent floor
        G > goalportal
        A > avatar floor
        . > floor
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
    LevelMapping
        E > opponent floor
        G > goalportal
        A > avatar floor
        . > floor
"""

dummy_maze = """
wwwwwwww
wA.....w
w......w
w...E..w
w......w
w......w
w.....Gw
wwwwwwww
"""

dummy_actions = ['Skip', 'Skip', 'Skip', 'Skip', 'Skip', 'Skip']

immovable_opponent_str ="\n        opponent > Immovable color=BLUE"
chaser_opponent_str="\n        opponent > Chaser stype=avatar color=RED"
racer_str="\n        opponent > Chaser stype=goalportal color=RED"
astar_chaser_str="\n        opponent > AStarChaser stype=avatar color=RED"
free_mover_str="\n            opponent > color=DARKBLUE"

gamefile = "tempgame.txt"
levelfile = "tempgame_levl0.txt"

class GameClass:
    def __init__(self, action_list=dummy_actions, game_desc=skeleton_game_1.format(immovable_opponent="",free_mover_str="",chaser_str=chaser_opponent_str), level_desc=dummy_maze):
        
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

    def _create_controller(self):
        
        self.controller = RecordedController(self.env_name, self.actions, fps=10)

    def _save_game_files(self):

        game_f = open(gamefile, 'w')
        game_f.write(self.game)
        game_f.close()

        level_f = open(levelfile, 'w')
        level_f.write(self.level)
        level_f.close()

    def play(self):

        self.controller.play()
        print(self.controller.cummulative_reward)
        return self.controller.cummulative_reward

class ChaserGameClass(GameClass):

    def __init__(self, actions_list=dummy_actions, game_desc=skeleton_game_3.format(immovable_opponent = "", free_mover_opponent = "", chaser_opponent = racer_str), level_desc=dummy_maze):
        self.actions = actions_list
        self.level = level_desc
        self.game = game_desc
        self._save_game_files()
        self._register_environment()
        self._format_actions()
        self._create_controller()


if __name__ == "__main__":
    print("Testin gameclass")