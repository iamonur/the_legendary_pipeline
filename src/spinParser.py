import os

class cannotWinException(Exception):
    pass

class spinParser:

    def __init__(self, outFile, execFile, trailFile):
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

        if len(moves) == 0:
            print("EMPT")
            return None, None

        if ["LOSE", "-1"] in moves:
            print("LOST")
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
        if av is None:
            raise cannotWinException("Avatar cannot win the game!")
        return av

if __name__ == "__main__":
