import player           #my module
import spinner          #my module
import spinParser       #my module
import os
import time

def pipelineError(Exception):
    pass

class Recorded_lvl_spin_player:
    def __init__(
        self,
        spin=spinner.SpinClass_Sokoban,
        parser=spinParser.spinParser,
        player=player.SokobanClass):
        self.spinner = spin
        self.parser  = parser
        self.player  = player

    def pipeline(self):
        #Parse level list
        files = os.listdir('sokobanlevels')
        #For every level, do sub-pipeline
        for file in files:
            score, term, mtime, moves = self.sub_pipeline(file)
            record(score, term, mtime, moves)

    def sub_pipeline(self, levelfile):


        f = open('sokobanlevels/' + levelfile)
        map_ = f.readlines()
        f.close()
        map_ = map_[:-1]
        
        for ln, _ in enumerate(map_):
            map_[ln] = map_[ln][:-1]

        print(map_)

        #GET_GOAL_COUNT

        modelling_success = True
        modelling_time = time.time()
        modelChecker = self.spinner(map_,6)

        try:
            modelChecker.perform()
        except spinner.spinCompileException:
            modelling_success = False

        if modelling_success:
            get_moves = self.parser()
            try:
                avatar, _ = get_moves.perform()
            except spinParser.cannotWinException:
                modelling_success = False
            
            if modelling_success:
                modelling_time = time.time() - modelling_time
                game = self.player(action_list=avatar, level_desc=map_)
                spin_score, spin_terminal = game.play()
            print(avatar)
            return spin_score, spin_terminal, modelling_time, "*".join(avatar)
        return None, None, None, None

    def record(self, filename, score, term, mtime, moves):
        line = "Score: {}\nTerm: {}\nTime: {}\nMoves: {}\n".format(
            score, term, mtime, moves
        )

        f = open(filename + "_spin", "a")
        f.write(line)
        f.close()

if __name__ == "__main__":
    Recorded_lvl_spin_player().pipeline()