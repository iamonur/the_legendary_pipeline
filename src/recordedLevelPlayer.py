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
        spin=spinner.SpinClass_Sokoban_100k,
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
            self.record(file,score, term, mtime, moves)

    def sub_pipeline(self, levelfile):


        f = open('sokobanlevels/' + levelfile)
        map_ = f.readlines()
        f.close()
        
        for ln, _ in enumerate(map_):
            map_[ln] = map_[ln][:-1]

        temp = ""
        for i in range(0, len(map_[0])+2):
            temp += "1"
        map2 = temp + "\n1"+"1\n1".join(map_)+"1\n" + temp

        #GET_GOAL_COUNT

        modelling_success = True
        modelling_time = time.time()
        count = 0
        for a in map2:
            for b in a:
                if b == 'B':
                    count += 1
        modelChecker = self.spinner(map_,count)

        try:
            modelChecker.perform()
        except spinner.spinCompileException:
            modelling_success = False

        if modelling_success:
            get_moves = self.parser()
            try:
                avatar, _ = get_moves.perform()
            except spinParser.cannotWinException:
                print("Cannot win")
                modelling_success = False
            
            modelling_time = time.time() - modelling_time
            if modelling_success:
                game = self.player(action_list=avatar, level_desc=map_)
                spin_score, spin_terminal = game.play()
                avatar = list(map(str, avatar))
                return spin_score, spin_terminal, modelling_time, "*".join(avatar)
            return None, None, modelling_time, None
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