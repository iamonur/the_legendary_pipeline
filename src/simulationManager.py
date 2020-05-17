#Huge thing. TODO: Think about small chunks.

import cellularAutomata #my module
import caPolisher       #my module
import spritePlanner    #my module
import player           #my module
import spinner          #my module
import spinParser       #my module
import random           #used in the example feeder
import time
import dbWrapper

def pipelineError(Exception):
    pass

def list_sort(list): #The lists are not that big, bubblesort will do.
    for iter_num in range(len(list) - 1, 0, -1):
        for idx in range(iter_num):
            if list[idx][2] > list[idx + 1][2]:
                temp = list[idx]
                list[idx] = list[idx + 1]
                list[idx + 1] = temp

def isOKBasic(dict):
    #This is an example difficulty asseser. Implement your own and put it on the pipeline.
    width = len(dict['map'][0])
    length = len(dict['map'])
    playable = 0
    for ln, line in enumerate(dict['map']):
        for cn, ch in enumerate(line):
            if ch == '1': #wall
                continue
            elif ch == '0': #floor
                playable += 1
            elif ch == 'A': #Avatar+floor
                playable += 1
                av_loc = (ln,cn)
            elif ch == 'G': #Portal
                p_loc = (ln,cn)
            elif ch == 'E': #Opponent+floor
                op_loc = (ln,cn)
                playable += 1
    playable   = playable/(width*length)
    dist_to_p  = abs(av_loc[0]-p_loc[0])+abs(av_loc[1]-p_loc[1])
    dist_to_p  = dist_to_p/(width*length)
    dist_to_op = abs(av_loc[0]-op_loc[0])+abs(av_loc[1]-op_loc[1])
    dist_to_op = dist_to_op/(width*length)
    dist_to_op = 1 - dist_to_op
    level_size = (width/24)*(length/24)
    op_skips = 0
    for move in dict['opponent']:
        if move == -1:
            op_skips += 1
    op_skips = 1 - op_skips/len(dict['opponent'])
    
    #Get counter-intuitive moves, not sure how, TODO: fix this implementation:
    av_counter_in = 0
    for move in dict['avatar']:
        if move == -1:
            av_counter_in += 1
    av_counter_in = av_counter_in/len(dict['avatar'])

    d_a   = av_counter_in
    d_op  = op_skips
    d_map = 0.25*playable + 0.25*dist_to_p + 0.25*dist_to_op + 0.25*level_size
    difficulty = 0.33*d_a + 0.33*d_op + 0.34*d_map

    

    if difficulty<0.3 or difficulty>0.8:
        return False

    return True

    #With avatar:(0.33)
        #Check percentage of counter-intuitive moves(percentage * 1.0)
    #With map:(0.34)
        #Check playable tile percentage(percentage * 0.25)
        #Check distance to goal(0.25 * distance/(width+height))
        #Check distance to opponent(0.25 * (1 - (distance/(width+height))))
        #Check level size(0.25 * (width/max_width*height/max_height)) #Max is 24 by now.
    #With opponent:(0.33)
        #Check percentage of moves that are not 'Skip' of opponent, means the guy is chasing.((1.0 - (Num of skips/Num of moves))*1.0) 


class FeederException(Exception):
    pass

class startFeeder(): #You can build rules, purely random or just serve a list. This basic guy just returns 10 different randoms, than raises. Remember to raise on yours. 
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,24):
            ret.append(str(random.randint(0,1)))
        self.count += 1
        return "".join(ret)



class SimManager():
    #@classmethod
    #def createSimManager(mapgenclass, polisherclass, plannerclass, spinnerclass=SpinClass, parserclass=spinParser, playerclass=GameClass, startFeed)
        
    def __init__(self, isOK, mapGenerator, mapPolisher, sprPlanner, spin=spinner.SpinClass, parser=spinParser.spinParser, player=player.GameClass, feed=startFeeder, json_args=None):#Gets class definitions as parameters, which is kinda cool.
        self.mapgen = mapGenerator
        self.mappolish = mapPolisher
        self.spriter = sprPlanner
        self.spinner = spin
        self.parser = parser
        self.game = player
        self.rng = startFeeder
        self.isOK = isOK
        self.db = dbWrapper.DBWrapper()
        #if json_args != None:
            #To be implemented. Just wanna see if the pipeline works well.
    


    def pipeline(self):

        rng = self.rng()
        totalExceptions = 0
        while(True):
            rngtime = time.time()
            try:
                line = rng.serve()
            except FeederException: # No more to serve, imagine recovering from that. For me, this is the point we fail to build.
                totalExceptions += 1
                return None
            rngtime = time.time() - rngtime


            mapgentime = time.time()
            try:
                map_ = self.mappolish(ca = self.mapgen(start = line)).perform()
            except caPolisher.polisherException:
                #this map cannot be polished. Let's get a new one.
                totalExceptions += 1
                continue
            mind = self.spriter(map_)
            mind.perform()
            map_ = mind.getMap() #Throws, but if you get an exception at this point, there is something you need to fix. Thus I let it propagate.
            mapgentime = time.time() - mapgentime

            modeltime = time.time()
            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform() #Your output is at your filesystem now.
            except spinner.spinCompileException:
                totalExceptions += 1
                continue # I let it flow by now, but this shouldn't happen if your PROMELA code was correct.

            get_moves = self.parser()
            try:
                avatar, opponent = get_moves.perform()
            except spinParser.cannotWinException:
                totalExceptions += 1
                continue # You created an unplayable level. Move on with a new one.
            modeltime = time.time() - modeltime
            ret = {"map": map_, 'avatar': avatar, 'opponent': opponent, 'timings': {"rng": rngtime, "map_gen": mapgentime, "modelling": modeltime}, "exceptions": totalExceptions}

            if self.isOK(ret) is False:
                continue

            game = self.game(action_list = avatar, level_desc = map_)
            if game.play() == 1:
                #def insertQ(self, line, linetime, ca, cap, sp, maptime, modeltime, game, seq, func_id, isOK):
                self.db.insertQ(line,rngtime,self.mapgen.__name__,self.mappolish.__name__,self.spriter.__name__,mapgentime,modeltime,"1",avatar,"1","1")
                return ret
                
                

            else: #We couldn't win while we think we will, best to fix this. Raise with all info.
                raise NameError("Nuncked up")
                #raise ("Map: " + map_ + " avatar_moves: " + "".join(avatar) + " opponent_moves: " + "".join(opponent) + " failed.") #This can be reconstructed.

if __name__ == "__main__":
    s = SimManager(isOKBasic, cellularAutomata.block_ones_majority_srca, caPolisher.polisher, spritePlanner.spritePlanner)
    while (True):
        s.pipeline()