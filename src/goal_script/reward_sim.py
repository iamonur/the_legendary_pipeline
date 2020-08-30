import sys
import os
import time
sys.path.insert(1, '../')
from player import MCTS_Runner_Regular as MCTS
from player import MazeGameClass as get_score
from player import skeleton_game_4_modifiable as custom_game

wall_punishments = [-1,-4,-16,-64,-256,-1024,-4096]
floor_punishments = [-1,-4,-16,-64,-256,-1024,-4096]
portal_rewards = [1,25,625,15625,390625]

def set_rules(wall, floor, portal):
    return custom_game.format(WallReward=wall, FloorReward=floor, PortalReward=portal)


class tryout():
    def __init__(self, wall, floor, portal, tryout=50):
        self.tries = tryout
        self.depth = 20
        self.playouts = 500
        self.rules = set_rules(wall, floor, portal)

    def simulate(self):
        output = []
        for _ in range(self.tries):
            runtime = time.time()
            moves = MCTS(max_d=self.depth, n_playouts=self.playouts, game_desc=self.rules, render=False).run()[0][0]
            runtime = time.time() - runtime
            my_score, is_terminal = get_score(action_list=moves, game_desc=self.rules).play()
            output.append([moves, my_score, is_terminal, runtime])
        return output

def simulate_all(repetitions=1):
    folder_name = str(time.time())
    os.mkdir(folder_name)
    os.chdir(folder_name)
    for portal in portal_rewards:
        for floor in floor_punishments:
            for wall in wall_punishments:
                fileName = "w"+str(wall)+"f"+str(floor)+"p"+str(portal)+".csv"
                file = open(fileName, "w+")
                results = tryout(wall,floor,portal,tryout=repetitions).simulate()
                for result in results:
                    for i,move in enumerate(result[0]):
                        result[0][i] = str(move)
                    csv_line = "*".join(result[0]) + "," + str(result[1]) + "," + str(result[2]) + "," + str(result[3])
                    file.writelines([csv_line])
                    file.writelines("\n")
                file.close()

if __name__ == "__main__":
    simulate_all(50)
