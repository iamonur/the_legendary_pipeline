#Huge thing. TODO: Think about small chunks.

import cellularAutomata #my module
import caPolisher       #my module
import spritePlanner    #my module
import player           #my module
import spinner          #my module
import spinParser       #my module
import random           #used in the example feeder
import time
#import dbWrapper

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
    
    if len(dict['opponent']) == 0:
        op_skips = 1
    else:
        op_skips = 1 - op_skips/len(dict['opponent'])
    
    #Get counter-intuitive moves, not sure how, TODO: fix this implementation:
    av_counter_in = 0
    for move in dict['avatar']:
        if move == -1:
            av_counter_in += 1

    if len(dict['avatar']) == 0:
        av_counter_in = 0
    else:
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

def isOKDummy(dict):
    return True

class FeederException(Exception):
    pass

class startFeeder: #You can build rules, purely random or just serve a list. This basic guy just returns 10 different randoms, than raises. Remember to raise on yours. 
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

class randomFeeder_Generic:
    def __init__(self, size=24):
        self.count = 0
        self.size = size

    def serve(self):
        if self.count == 10:
            raise FeederException("Your feeder is depleted.")
        ret = []
        for i in range(0,size):
            ret.append(str(random.randint(0,1)))

        self.count += 1
        return "".join(ret)

class startFeederEight:
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,8):
            ret.append(str(random.randint(0,1)))
        self.count += 1
        return "".join(ret)

class startFeederTen:
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,10):
            ret.append(str(random.randint(0,1)))
        self.count += 1
        return "".join(ret)

class startFeederTwelve:
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,12):
            ret.append(str(random.randint(0,1)))
        self.count += 1
        return "".join(ret)

class startFeederFourteen:
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,14):
            ret.append(str(random.randint(0,1)))
        self.count += 1
        return "".join(ret)

class startFeederSixteen:
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,16):
            ret.append(str(random.randint(0,1)))
        self.count += 1
        return "".join(ret)

class dummyFeeder:
    def __init__(self):
        self.count = 0

    def serve(self):
        if self.count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        
        self.count += 1
        return "000000000001000000000000"

class experiment_on_time:#Default is game 4, the base game.
    def __init__(self, size=24, limit=24, mapGenerator=cellularAutomata.elementary_cellular_automata, mapPolisher=caPolisher.polisher, sprPlanner=spritePlanner.dualSpritePlanner, spin=spinner.SpinClass_Game4, parser=spinParser.spinParser, player=player.MazeGameClass, feed=startFeederEight, mcts=player.MCTS_Runner_Regular):
        self.mapgen = mapGenerator
        self.mappolish = mapPolisher
        self.spriter = sprPlanner
        self.spinner = spin
        self.parser = parser
        self.game = player
        self.rng = feed
        self.mcts = mcts
        self.size = size
        self.limit = limit
    #@profile
    def pipeline(self):
        rng = self.rng()
        totalExceptions = 0
        while True:
            ##############################################################
            rngtime = time.time()
            try:
                line = rng.serve()
            except FeederException:
                totalExceptions += 1
                return None
            rngtime = time.time() - rngtime
            ##############################################################
            mapgentime = time.time()
            try:
                map_ = self.mappolish(ca=self.mapgen(size=8, limit=8, start=line)).perform()
            except:
                totalExceptions += 1
                continue
            mind = self.spriter(map_)
            mind.perform()
            map_ = mind.getMap()
            #caPolisher.map_print(map_)
            mapgentime = time.time() - mapgentime
            ##############################################################
            modeltime = time.time()
            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform()
            except spinner.spinCompileException:
                totalExceptions += 1
                continue
            get_moves = self.parser()
            try:
                avatar, opponent = get_moves.perform()
                opponent = []
            except spinParser.cannotWinException:
                totalExceptions += 1
                continue
            modeltime = time.time() - modeltime
            if len(avatar) < 5:
                continue
            game = self.game(action_list = avatar, level_desc = map_)
            spin_reward = game.play()
            ##############################################################
            mcts_object = self.mcts(game_desc=player.skeleton_game_4,level_desc=player.stringify_list_level(map_),render=False)
            mcts_result = mcts_object.run()
            avatar_mcts = mcts_result[0][0]
            game2 = self.game(action_list=avatar_mcts, level_desc=map_)
            mcts_reward = game2.play()
            ##############################################################
            if mcts_reward > spin_reward:
                print("  __  __  _____ _______ _____  __          ______  _   _ \n |  \/  |/ ____|__   __/ ____| \ \        / / __ \| \ | |\n | \  / | |       | | | (___    \ \  /\  / / |  | |  \| |\n | |\/| | |       | |  \___ \    \ \/  \/ /| |  | | . ` |\n | |  | | |____   | |  ____) |    \  /\  / | |__| | |\  |\n |_|  |_|\_____|  |_| |_____/      \/  \/   \____/|_| \_|\n                                                       ")
            else:
                print("   _____ _____ _____ _   _  __          ______  _   _ \n  / ____|  __ \_   _| \ | | \ \        / / __ \| \ | |\n | (___ | |__) || | |  \| |  \ \  /\  / / |  | |  \| |\n  \___ \|  ___/ | | | . ` |   \ \/  \/ /| |  | | . ` |\n  ____) | |    _| |_| |\  |    \  /\  / | |__| | |\  |\n |_____/|_|   |_____|_| \_|     \/  \/   \____/|_| \_|\n                                                      ")
            print("MCTS' reward: " + str(mcts_reward) + " SPIN's reward: " + str(spin_reward))
            print("The time: " + str(modeltime))
            return

class experiment_on_reward:
    def __init__(self, goal_ratio=10,mapGenerator=cellularAutomata.elementary_cellular_automata, mapPolisher=caPolisher.polisher, sprPlanner=spritePlanner.dualSpritePlanner, spin=spinner.SpinClass_Game4, parser=spinParser.spinParser, player=player.MazeGameClass, feed=startFeeder, mcts=player.MCTS_Runner_Reward):
        self.mapgen = mapGenerator
        self.mappolish = mapPolisher
        self.spriter = sprPlanner
        self.spinner = spin
        self.parser = parser
        self.game = player
        self.rng = startFeeder
        self.mcts = mcts
        self.ratio = 10

    def pipeline(self):
        rng = self.rng()
        totalExceptions = 0
        while True:
            ##############################################################
            rngtime = time.time()
            try:
                line = rng.serve()
            except FeederException:
                totalExceptions += 1
                return None
            rngtime = time.time() - rngtime
            ##############################################################
            mapgentime = time.time()
            try:
                map_ = self.mappolish(ca=self.mapgen(size=24, limit=24, start=line)).perform()
            except:
                totalExceptions += 1
                continue
            mind = self.spriter(map_)
            mind.perform()
            map_ = mind.getMap()
            #caPolisher.map_print(map_)
            mapgentime = time.time() - mapgentime
            ##############################################################
            modeltime = time.time()
            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform()
            except spinner.spinCompileException:
                totalExceptions += 1
                continue
            get_moves = self.parser()
            try:
                avatar, opponent = get_moves.perform()
                opponent = []
            except spinParser.cannotWinException:
                totalExceptions += 1
                continue
            modeltime = time.time() - modeltime
            if len(avatar) < 5:
                continue
            game = self.game(action_list = avatar, level_desc = map_)
            spin_reward = game.play()
            ##############################################################
            mctstime = time.time()
            mcts_object = self.mcts(max_d=1000,reward_goal=(spin_reward*20),game_desc=player.skeleton_game_4,level_desc=player.stringify_list_level(map_),render=False)
            mcts_result = mcts_object.run()
            mctstime = time.time() - mctstime
            avatar_mcts = mcts_result[0][0]
            game2 = self.game(action_list=avatar_mcts, level_desc=map_)
            mcts_reward = game2.play()
            ##############################################################
            #if mcts_reward > spin_reward:
            #    print("  __  __  _____ _______ _____  __          ______  _   _ \n |  \/  |/ ____|__   __/ ____| \ \        / / __ \| \ | |\n | \  / | |       | | | (___    \ \  /\  / / |  | |  \| |\n | |\/| | |       | |  \___ \    \ \/  \/ /| |  | | . ` |\n | |  | | |____   | |  ____) |    \  /\  / | |__| | |\  |\n |_|  |_|\_____|  |_| |_____/      \/  \/   \____/|_| \_|\n                                                       ")
            #else:
            #   print("   _____ _____ _____ _   _  __          ______  _   _ \n  / ____|  __ \_   _| \ | | \ \        / / __ \| \ | |\n | (___ | |__) || | |  \| |  \ \  /\  / / |  | |  \| |\n  \___ \|  ___/ | | | . ` |   \ \/  \/ /| |  | | . ` |\n  ____) | |    _| |_| |\  |    \  /\  / | |__| | |\  |\n |_____/|_|   |_____|_| \_|     \/  \/   \____/|_| \_|\n                                                      ")
            print("MCTS' reward: " + str(mcts_reward) + ". MCTS' time to finish: " + str(modeltime) + "\nSPIN's reward: " + str(spin_reward) + ". SPIN's time to finish: "+str(mctstime))

class experiment_on_both:
    def __init__(self, goal_ratio=25, to_ratio=1000, mapGenerator=cellularAutomata.elementary_cellular_automata, mapPolisher=caPolisher.polisher, sprPlanner=spritePlanner.dualSpritePlanner, spin=spinner.SpinClass_Game4, parser=spinParser.spinParser, player=player.MazeGameClass, feed=startFeederEight, mcts=player.MCTS_Runner_Reward_Timeout):
        self.mapgen = mapGenerator
        self.mappolish = mapPolisher
        self.spriter = sprPlanner
        self.spinner = spin
        self.parser = parser
        self.game = player
        self.rng = feed
        self.mcts = mcts
        self.ratio = goal_ratio
        self.ratio2= to_ratio

    def pipeline(self):
        rng = self.rng()
        totalExceptions = 0
        while True:
            ##############################################################
            rngtime = time.time()
            try:
                line = rng.serve()
                print(line)
            except FeederException:
                totalExceptions += 1
                return None
            rngtime = time.time() - rngtime
            ##############################################################
            mapgentime = time.time()
            try:
                map_ = self.mappolish(ca=self.mapgen(size=8, limit=8, start=line)).perform()
            except:
                totalExceptions += 1
                print("a")
                continue
            mind = self.spriter(map_)
            mind.perform()
            map_ = mind.getMap()
            caPolisher.map_print(map_)
            mapgentime = time.time() - mapgentime
            ##############################################################
            modeltime = time.time()
            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform()
            except spinner.spinCompileException:
                totalExceptions += 1
                continue
            get_moves = self.parser()
            try:
                avatar, opponent = get_moves.perform()
                opponent = []
            except spinParser.cannotWinException:
                totalExceptions += 1
                continue
            modeltime = time.time() - modeltime
            if len(avatar) < 5:
                continue
            game = self.game(action_list = avatar, level_desc = map_)
            spin_reward = game.play()
            ##############################################################
            mctstime = time.time()
            #(spin_reward*self.ratio)
            mcts_object = self.mcts(max_d=100000,reward_goal=spin_reward-1000,seconds=(modeltime*self.ratio2),game_desc=player.skeleton_game_4,level_desc=player.stringify_list_level(map_),render=False)
            mcts_result = mcts_object.run()
            mctstime = time.time() - mctstime
            avatar_mcts = mcts_result[0][0]
            game2 = self.game(action_list=avatar_mcts, level_desc=map_)
            mcts_reward = game2.play()
            ##############################################################
            #if mcts_reward > spin_reward:
            #    print("  __  __  _____ _______ _____  __          ______  _   _ \n |  \/  |/ ____|__   __/ ____| \ \        / / __ \| \ | |\n | \  / | |       | | | (___    \ \  /\  / / |  | |  \| |\n | |\/| | |       | |  \___ \    \ \/  \/ /| |  | | . ` |\n | |  | | |____   | |  ____) |    \  /\  / | |__| | |\  |\n |_|  |_|\_____|  |_| |_____/      \/  \/   \____/|_| \_|\n                                                       ")
            #else:
            #   print("   _____ _____ _____ _   _  __          ______  _   _ \n  / ____|  __ \_   _| \ | | \ \        / / __ \| \ | |\n | (___ | |__) || | |  \| |  \ \  /\  / / |  | |  \| |\n  \___ \|  ___/ | | | . ` |   \ \/  \/ /| |  | | . ` |\n  ____) | |    _| |_| |\  |    \  /\  / | |__| | |\  |\n |_____/|_|   |_____|_| \_|     \/  \/   \____/|_| \_|\n                                                      ")
            print("MCTS' reward: " + str(mcts_reward) +  "\nSPIN's reward: " + str(spin_reward) + ". SPIN's time to finish: "+str(mctstime))

class SimManager:
    #@classmethod
    #def createSimManager(mapgenclass, polisherclass, plannerclass, spinnerclass=SpinClass, parserclass=spinParser, playerclass=GameClass, startFeed)
        
    def __init__(self, isOK=isOKDummy, mapGenerator=cellularAutomata.elementary_cellular_automata, mapPolisher=caPolisher.polisher, sprPlanner=spritePlanner.spritePlanner, spin=spinner.SpinClass, parser=spinParser.spinParser, player=player.RacerGameClass_Smart, feed=startFeeder, json_args=None):#Gets class definitions as parameters, which is kinda cool.
        self.mapgen = mapGenerator
        self.mappolish = mapPolisher
        self.spriter = sprPlanner
        self.spinner = spin
        self.parser = parser
        self.game = player
        self.rng = startFeeder
        self.isOK = isOK
        #if json_args != None:
            #To be implemented. Just wanna see if the pipeline works well.
    
    def pipeline(self):

        rng = self.rng()
        totalExceptions = 0
        while(True):
            #print ("________________________________")
            rngtime = time.time()
            try:
                line = rng.serve()
            except FeederException: # No more to serve, imagine recovering from that. For me, this is the point we fail to build.
                totalExceptions += 1
                return None
            rngtime = time.time() - rngtime


            mapgentime = time.time()
            try:
                map_ = self.mappolish(ca = self.mapgen(size=24, limit=24, start = line)).perform()
            except caPolisher.polisherException:
                #this map cannot be polished. Let's get a new one.
                print("asd")
                totalExceptions += 1
                continue
            #caPolisher.map_print(map_)
            mind = self.spriter(map_)
            mind.perform()
            map_ = mind.getMap() #Throws, but if you get an exception at this point, there is something you need to fix. Thus I let it propagate.
            #caPolisher.map_print(map_)
            mapgentime = time.time() - mapgentime
            modeltime = time.time()
            #print ("________________________________")
            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform() #Your output is at your filesystem now.
            except spinner.spinCompileException:
                totalExceptions += 1
                continue # I let it flow by now, but this shouldn't happen if your PROMELA code was correct.

            get_moves = self.parser()
            try:
                avatar, opponent= get_moves.perform()
                #opponent = []
                #print(avatar)
            except spinParser.cannotWinException:
                totalExceptions += 1
                continue # You created an unplayable level. Move on with a new one.
            
            print (opponent)
            modeltime = time.time() - modeltime
            ret = {"map": map_, 'avatar': avatar, 'opponent': opponent, 'timings': {"rng": rngtime, "map_gen": mapgentime, "modelling": modeltime}, "exceptions": totalExceptions}

            if self.isOK(ret) is False:
                continue
            #print ("________________________________")
            game = self.game(action_list = avatar, level_desc = map_)

            #print ("________________________________")
            if game.play() == 1:
                #def insertQ(self, line, linetime, ca, cap, sp, maptime, modeltime, game, seq, func_id, isOK):
                #self.db.insertQ(line,rngtime,self.mapgen.__name__,self.mappolish.__name__,self.spriter.__name__,mapgentime,modeltime,"1",avatar,"1","1")
                print ("qqq")
            
                

            else: #We couldn't win while we think we will, best to fix this. Raise with all info.
                #print ("________________________________")
                caPolisher.map_print(map_)
                print("OP_LEN:")
                print(len(opponent))
                print("AV_LEN:")
                print(len(avatar))
                raise NameError("Nuncked up")
                #raise ("Map: " + map_ + " avatar_moves: " + "".join(avatar) + " opponent_moves: " + "".join(opponent) + " failed.") #This can be reconstructed.

#Notes on the below simulation:
#1- SpritePlanner is kinda shitty and lets you win near %50. Probably a new one is needed.

class Simulation:
    def __init__(self, map_percentage=30, level_size=24, map_generator=cellularAutomata.elementary_cellular_automata, map_polisher=caPolisher.polisher, sprite_planner=spritePlanner.equalSpritePlanner, spin=spinner.SpinClass_Game3_smart, parser=spinParser.spinParser, searcher=spinner.MCTS_Runner_Regular, player=player.RacerGameClass_Smart, feed=randomFeeder_Generic):
        self.pol_pct = map_percentage
        self.lvl_sz  = 24
        self.map_gen = map_generator
        self.map_pol = map_polisher
        self.spr_pln = sprite_planner
        self.spinner = spin
        self.parser  = parser
        self.player  = player
        self.rng_fdr = feed
        self.mcts_ag = searcher

    def pipeline(self):
        rng_feed = self.rng_fdr(size=level_size)
        while(True):
        ############################ LEVEL-GEN PHASE    
            try:
                line = rng.serve()
            except FeederException:
                #You get this, you're depleted
                return None

            try:
                map_ = self.map_pol(ca=self.map_gen(size=self.lvl_sz, limit=self.lvl_sz, start=line), minimumArea=self.pol_pct).perform()
            except caPolisher.polisherException:
                continue
            #Sprite Planners do raise, but if you didn't throw at polisher, you shouldn't be here. Fix your polisher first.
            mind = self.spr_pln(map_)
            mind.perform()
            map_ = mind.getMap()
        ############################ LEVEL-SOLVING PHASE

            modelling_time = time.time()

            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform()
            except spinner.spinCompileException:
                continue

            get_moves = self.parser()
            try:
                avatar, opponent = get_moves.perform()
            except spinParser.cannotWinException:
                continue

            modelling_time = time.time()-modelling_time

            game = self.player(action_list=avatar, level_desc=map_)
            spin_score, spin_terminal = game.play()

            map2 = "\n".join(map_)
        ############################ MCTS: 1
            mcts1_time = time.time()
            moves_1 = self.mcts_ag(max_d= level_size*20, n_playouts=level_size*20, game_desc=game.level, level_desc=map2, render=False).run()[0][0]
            mcts1_time = time.time() - mcts1_time
            mcts1_score, mcts1_terminal = self.player(action_list=moves_1, level_desc=map_).play()
        ############################ MCTS: 2
            mcts2_time = time.time()
            moves_2 = self.mcts_ag(max_d= level_size*40, n_playouts=level_size*10, game_desc=game.level, level_desc=map2, render=False).run()[0][0]
            mcts2_time = time.time() - mcts2_time
            mcts2_score, mcts2_terminal = self.player(action_list=moves_2, level_desc=map_).play()
        ############################ MCTS: 3
            mcts3_time = time.time()
            moves_3 = self.mcts_ag(max_d= level_size*80, n_playouts=level_size*5, game_desc= game.level, level_desc=map2, render=False).run()[0][0]
            mcts3_time = time.time() - mcts3_time
            mcts3_score, mcts3_terminal = self.player(action_list=moves_3, level_desc=map_).play()
        ############################ MCTS: 4
            mcts4_time = time.time()
            moves_4 = self.mcts_ag(max_d= level_size*10, n_playouts=level_size*40, game_desc= game.level, level_desc=map2, render=False).run()[0][0]
            mcts4_time = time.time() - mcts4_time
            mcts4_score, mcts4_terminal = self.player(action_list=moves_4, level_desc=map_).play()
        ############################ MCTS: 5
            mcts5_time = time.time()
            moves_5 = self.mcts_ag(max_d= level_size*5, n_playouts=level_size*80, game_desc= game.level, level_desc=map2, render=False).run()[0][0]
            mcts5_time = time.time() - mcts5_time
            mcts5_score, mcts5_terminal = self.player(action_list=moves_5, level_desc=map_).play()
        ############################ FINISHING PHASE
            line_to_write = ""
            #### SUB-PHASE 1 - Record Level
                line_to_write += "{},{},{}".format(self.lvl_sz, self.pol_pct, self.line, self.map2)
            #### SUB-PHASE 2 - Record SPIN performance
            #### SUB-PHASE 3 - Record MCTS performance
            #### SUB-PHASE 4 - Record
            





if __name__ == "__main__":
    
    ss = SimManager()
    ss.pipeline()