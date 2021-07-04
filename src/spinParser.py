import os
from collections import *
class cannotWinException(Exception):
    pass

class spinParser_Soko:

    def __init__(self, outFile="tempfile.txt", execFile="../spin/temp.out", trailFile="temp.pml.trail", mp=None):
        if mp is None:
            raise cannotWinException("You dont know how to use this.")

        self.mp = []
        for line in mp:
            self.mp.append(list(line))
        self.output_file = outFile
        self.executable_file = execFile
        self.trail_file = trailFile

    def __get_trail_output(self):
        os.system("{} -r -S {} > {}".format(self.executable_file, self.trail_file, self.output_file))

    def __parse_trail_output(self):
        f = open(self.output_file)
        lines = f.readlines()
        f.close()

        returnable = []
        last_moved = ""

        for line in lines:

            splitted = line.split()

            if splitted[0] == "pan:1:" and splitted[1] == "assertion" and splitted[2] == "violated":
                returnable.append(["Avatar", "Skip"])
                to_push = ["WIN", splitted[-1]]
                returnable.append(to_push)
                return returnable

            elif splitted[0] == "Push@":
                fr = [int(splitted[1]), int(splitted[2])]
                if splitted[5] == "0":
                    fr[0] -= 1
                    move = "S"
                elif splitted[5] == "1":
                    fr[1] -= 1
                    move = "D"
                elif splitted[5] == "2":
                    fr[0] += 1
                    move = "W"
                elif splitted[5] == "3":
                    fr[1] += 1
                    move = "A"
            
                returnable.append([fr, move])

            elif splitted[0] == "MSC:":

                continue

            else:

                to_push = ["LOSE", "-1"]
                returnable.append(to_push)
                return returnable

    def __parse_moves(self, moves):
        if moves is None:
            return None
        if len(moves) == 0:
            return None
        if ["LOSE", "-1"] in moves:
            return None
        ret_moves = []

        return moves[:-1]

    def __bfs(self, fr, to):
        
        width = len(self.mp[0])
        height = len(self.mp)
        queue = deque([[fr]])
        seen = set([fr])
        while queue:
            path = queue.popleft()
            ind1, ind2 = path[-1]
            if (ind1,ind2) == to:
                return path
            for (i1, i2) in ((ind1+1,ind2), (ind1-1,ind2), (ind1,ind2+1), (ind1,ind2-1)):
                if (0 <= i1 < width) and (0 <= i2 < height) and (self.mp[i1][i2] == "0") and (i1, i2) not in seen:
                    queue.append(path + [(i1, i2)])
                    seen.add((i1, i2))

    def __standardize(self, moves):
        ret = []
        for ln,line in enumerate(self.mp):
            for cn,ch in enumerate(line):
                if ch == "A":
                    avatar_loc = (ln, cn)
                    self.mp[ln][cn] = "0" 

        for move in moves[:-1]:
            #print(move)
            sub_coordinates = self.__bfs(avatar_loc, (move[0][0], move[0][1]))
            #print(sub_coordinates)
            for sub_move in sub_coordinates:
                #print(ret)
                if (avatar_loc[0] - sub_move[0]) == 1:
                    ret.append("A")
                if (avatar_loc[0] - sub_move[0]) == -1:
                    ret.append("D")
                if (avatar_loc[1] - sub_move[1]) == 1:
                    ret.append("W")
                if (avatar_loc[1] - sub_move[1]) == -1:
                    ret.append("S")
                avatar_loc = sub_move

            if(move[1] == 'S'):
                ret.append('D')
            if(move[1] == 'D'):
                ret.append('S')
            if(move[1] == 'W'):
                ret.append('A')
            if(move[1] == 'A'):
                ret.append('W')
            
            

            if move[1] == 'S':
                avatar_loc = (avatar_loc[0]+1, avatar_loc[1])
            if move[1] == 'W':
                avatar_loc = (avatar_loc[0]-1, avatar_loc[1])
            if move[1] == 'D':
                avatar_loc = (avatar_loc[0], avatar_loc[1]+1)
            if move[1] == 'A':
                avatar_loc = (avatar_loc[0], avatar_loc[1]-1)
            #avatar_loc = (move[0][0], move[0][1])
            
            self.mp[avatar_loc[0]][avatar_loc[1]] = "0"
            if(move[1] == "W"):
                if self.mp[avatar_loc[0]-1][avatar_loc[1]] != "H":
                    self.mp[avatar_loc[0]-1][avatar_loc[1]] = "B"
                else:
                    self.mp[avatar_loc[0]-1][avatar_loc[1]] = "0"
            if(move[1] == "A"):
                if self.mp[avatar_loc[0]][avatar_loc[1]-1] != "H":
                    self.mp[avatar_loc[0]][avatar_loc[1]-1] = "B"
                else:
                    self.mp[avatar_loc[0]][avatar_loc[1]-1] = "0"
            if(move[1] == "S"):
                if self.mp[avatar_loc[0]+1][avatar_loc[1]] != "H":
                    self.mp[avatar_loc[0]+1][avatar_loc[1]] = "B"
                else:
                    self.mp[avatar_loc[0]+1][avatar_loc[1]] = "0"                    
            if(move[1] == "D"):
                if self.mp[avatar_loc[0]][avatar_loc[1]+1] != "H":
                    self.mp[avatar_loc[0]][avatar_loc[1]+1] = "B"
                else:
                    self.mp[avatar_loc[0]][avatar_loc[1]+1] = "0"


        return ret

    def perform(self):
        self.__get_trail_output()
        moves = self.__parse_moves(self.__parse_trail_output())
        if moves is None:
            raise cannotWinException("Sokoban game cannot be won!")

        return self.__standardize(moves)

class spinParser:

    def __init__(self, outFile="tempfile.txt", execFile="../spin/temp.out", trailFile="temp.pml.trail"):
        self.output_file = outFile
        self.executable_file = execFile
        self.trail_file = trailFile

    def __get_trail_output(self):
        os.system("{} -r -S {} > {}".format(self.executable_file, self.trail_file, self.output_file))

    def __parse_trail_output(self):
        f = open(self.output_file)
        lines = f.readlines()
        f.close()

        returnable = []
        last_moved = ""

        for line in lines:

            splitted = line.split()

            if splitted[0] == "pan:1:" and splitted[1] == "assertion" and splitted[2] == "violated": #Last meaningful line of the trail file.
                returnable.append(["Avatar", "Skip"])
                to_push = ["WIN", splitted[-1][:-1]]
                returnable.append(to_push)
                return returnable

            elif splitted[1] == "-":

                if splitted[0] == last_moved: #A skip needs to be inserted before.

                    if splitted[0] == "Opponent":

                        to_push = ["Avatar", "Skip"]

                    else:

                        to_push = ["Opponent", "Skip"]

                    returnable.append(to_push)

                to_push = [splitted[0], splitted[-1]]
                last_moved = splitted[0]
                returnable.append(to_push)

            elif splitted[0] == "MSC:":

                continue

            else:

                to_push = ["LOSE", "-1"]
                returnable.append(to_push)
                return returnable

    def __parse_moves(self, moves):
        if moves is None:
            return None, None
        if len(moves) == 0:
            return None, None
        if ["LOSE", "-1"] in moves:
            return None, None

        avatar_moves = []
        opponent_moves = []

        for move in moves:

            if move[0] == "Avatar":

                avatar_moves.append(move[1])

            elif move[0] == "Opponent":

                opponent_moves.append(move[1])

            else:

                return avatar_moves, opponent_moves

        return avatar_moves, opponent_moves

    def perform(self):

        self.__get_trail_output()
        avatar, opponent = self.__parse_moves(self.__parse_trail_output())
        
        if avatar is None:
            raise cannotWinException("Avatar cannot win the game!")
        avatar.append("Skip")
        return avatar, opponent

class mctsParser:
    def __init__(self, mcts_out="asd.txt"):
        self.file = mcts_out

    def __parse_moves(self):
        f = open(self.file)
        lines = f.readlines()
        f.close()
        toRet = []
        for line in lines:
            toRet.append(line[:-1])

        return toRet

    def perform(self):
        ret = self.__parse_moves()
        if ret[-1] == 'LOST':
            raise cannotWinException
        return ret
"""
class spinParser_Generic:
    def __init__(self, outFile = "tempfile.txt", execFile="../spin/temp.out", trailFile="temp.pml.trail", passFunc=None):
        if passFunc == None:
            raise cannotWinException("This is not how you create a generic parser!")

        self.output_file = outFile
        self.executable_file = execFile
        self.trail_file = trailFile

    
    def __get_trail_output(self):
        os.system("{} -r -S {} > {}".format(self.executable_file, self.trail_file, self.output_file))

    def __parse_trail_output(self):
        f = open(self.output_file)
        lines = f.readlines()
        f.close()

        returnable = []
        last_moved = ""

        for line in lines:

            splitted = line.split()

            if splitted[0] == "pan:1:" and splitted[1] == "assertion" and splitted[2] == "violated": #Last meaningful line of the trail file.
                returnable.append(["Avatar", "Skip"])
                to_push = ["WIN", splitted[-1][:-1]]
                returnable.append(to_push)
                return returnable

            elif splitted[1] == "-":

                if splitted[0] == last_moved: #A skip needs to be inserted before.

                    if splitted[0] == "Opponent":

                        to_push = ["Avatar", "Skip"]

                    else:

                        to_push = ["Opponent", "Skip"]

                    returnable.append(to_push)

                to_push = [splitted[0], splitted[-1]]
                last_moved = splitted[0]
                returnable.append(to_push)

            elif splitted[0] == "MSC:":

                continue

            else:

                to_push = ["LOSE", "-1"]
                returnable.append(to_push)
                return returnable

    def __parse_moves(self, moves):
        if moves is None:
            return None, None
        if len(moves) == 0:
            return None, None
        if ["LOSE", "-1"] in moves:
            return None, None

        self.avatar_moves = []
        self.opponent_moves = []

        for move in moves:

            if move[0] == "Avatar":

                self.avatar_moves.append(move[1])

            elif move[0] == "Opponent":

                self.opponent_moves.append(move[1])

            else:

                return self.avatar_moves, self.opponent_moves

        return self.avatar_moves, self.opponent_moves

    def check_params(self):
        self.straight_moves = 0
        self.turn_moves = 0
        self.


    def get_straight_moves(self):
        if self.straight_moves == 0:
            raise cannotWinException("Probably not parsed!")
        return self.straight_moves

    def get_turn_moves(self):
        if self.turn_moves == 0:
            raise cannotWinException("Probably not parsed!")
        return self.turn_moves

    def get_straight_pct(self):
        if self.straight_moves == 0:
            raise cannotWinException("Probably not parsed!")
        return (self.straight_moves*100)/(self.straight_moves + self.turn_moves)

    def get_turn_moves(self):
        if self.turn_moves == 0:
            raise cannotWinException("Probably not parsed!")
        return (self.turn_moves*100)/(self.straight_moves + self.turn_moves)"""