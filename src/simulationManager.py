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
        #DO NOT DEPLETE
        #if self.count == 10:
        #    raise FeederException("Your feeder is depleted.")
        ret = []
        for i in range(0,self.size):
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
class Sim_Nov:
    def __init__(
        self, 
        time_multiplier=300,
        map_percentage=50, 
        level_size=24, 
        map_generator=cellularAutomata.elementary_cellular_automata, 
        map_polisher=caPolisher.CAPolisher_MinArea, 
        sprite_planner=spritePlanner.equalSpritePlanner, 
        spin=spinner.SpinClass_Game3_smart, 
        parser=spinParser.spinParser, 
        searcher=player.MCTS_Runner_Regular_with_Time_Limit, 
        player=player.RacerGameClass_Smart, 
        feed=randomFeeder_Generic):
        
        self.pol_pct = map_percentage
        self.lvl_sz  = level_size
        self.map_gen = map_generator
        self.map_pol = map_polisher
        self.spr_pln = sprite_planner
        self.spinner = spin
        self.parser  = parser
        self.player  = player
        self.rng_fdr = feed
        self.mcts_ag = searcher
        self.time_mul= time_multiplier

    def pipeline(self):
        rng_feeder = self.rng_fdr(size=self.lvl_sz)
        while(True):
            try:
                line = rng_feeder.serve()
            except FeederException:
                print("Feeder depleted")
                return None
            try:
                map_ = self.map_pol(ca=self.map_gen(size=self.lvl_sz, limit = self.lvl_sz, start=line), minimumArea=self.pol_pct).perform()
            except caPolisher.polisherException:
                print("Polisher fault")
                continue
            mind = self.spr_pln(map_)
            mind.perform()
            map_ = mind.getMap()
            temp = ""
            for i in range(0, self.lvl_sz+2):
                temp += "1"
            map2 = temp + "\n1"+"1\n1".join(map_)+"1\n" + temp
            """
            At this point, your level is generated.
            You better save the level at this point,
            because this may result in calculation of your spinner's quality.
            """
            level_line = "Level size: {}\nPolisher percentage: {}\nStarter line: {},\nWhole Level:\n{}".format(
                self.lvl_sz, self.pol_pct, line, map2)
            """
            This boolean will decide if you will play this level or not (is it playable?)
            """
            modelling_success = True
            modelling_time = time.time()
            
            modelChecker = self.spinner(map_)
            try:
                modelChecker.perform()
            except spinner.spinCompileException:
                modelling_success = False
            if modelling_success:
                get_moves = self.parser()
                try:
                    avatar, opponent = get_moves.perform()
                except spinParser.cannotWinException:
                    modelling_success = False

                if modelling_success:
                    modelling_time = time.time() - modelling_time

                    game = self.player(action_list=avatar, level_desc=map_)
                    spin_score, spin_terminal = game.play()
                    
                    """
                    If modelling is not successful, don't wait for mcts to run.
                    """
                    mcts_time_limit   = self.time_mul * modelling_time # Thanks to this, you can pass huge params without scaring.
                    number_of_loops   = 99999
                    max_search_depth  = len(avatar) 
                    max_rollout_depth = len(avatar) * 2
                    number_of_playouts= len(avatar) ** 2
                    mcts_time = time.time()
                    mcts_moves = self.mcts_ag(mcts_time_limit, nloops=number_of_loops,max_d=max_search_depth, n_playouts=number_of_playouts, rollout_depth=max_rollout_depth, game_desc=game.game, level_desc=map2, render=False).run()[0][0]
                    mcts_time = time.time() - mcts_time
                    mcts_score, mcts_terminal = self.player(action_list=mcts_moves, level_desc=map_).play()



                    mcts_moves = list(map(str,mcts_moves))
                    avatar = list(map(str, avatar))
                    spin_line  = "Spin score: {}\nSpin terminal:{}\nSpin time: {}\nSpin moves: {}".format(
                        spin_score, (spin_terminal and (spin_score > 0)), modelling_time, "*".join(avatar))
                    mcts_line  = "MCTS score: {}\nMCTS terminal: {}\nMCTS time:{}\nMCTS moves: {}".format(
                        mcts_score,(mcts_terminal and (mcts_score > 0)),mcts_time, "*".join(mcts_moves))

                    return level_line, spin_line, mcts_line, (mcts_terminal and (mcts_score > 0))
            return level_line, None, None, None

"""
A game is a list of:
    - Sprite planner
    - Spinner
    - Player
    - Name of the game
"""

sizes_to_try = [8,10,12,14,16,18,20,22,24]
games_implemented = [
    #[spritePlanner.dualSpritePlanner,       spinner.SpinClass_Game4,                        player.MazeGameClass,           "Regular_Maze"  ],
    [spritePlanner.equalSpritePlanner,      spinner.SpinClass_Game3_smart,                  player.RacerGameClass_Smart,    "Regular_Race"  ],
    [spritePlanner.reverseSpritePlanner,    spinner.SpinClass_Game3_smart,                  player.RacerGameClass_Smart,    "Race_Easy_Mode"],
    [spritePlanner.spritePlanner,           spinner.SpinClass_Game3_smart,                  player.RacerGameClass_Smart,    "Race_Hard_Mode"]]
class Sim_Nov_Wrapper:
    def __init__(self, number_of_episodes, level_sizes=sizes_to_try, game_types=games_implemented):
        self.magic = random.random()
        self.my_sizes = level_sizes
        self.my_types = game_types
        self.numOfEps = number_of_episodes

    def record_episode_(self, num, size, game_name, levelStr):
        filename = str(self.magic) + "_" + str(size) + "_" + game_name + "_" + str(num) 

        f = open(filename + "_level", "a")
        f.write(levelStr)
        f.close()

    def record_episode(self, num, size, game_name, levelStr, spinStr, mctsStr):
        filename = str(self.magic) + "_" + str(size) + "_" + game_name + "_" + str(num)

        f = open(filename + "_level", "a")
        f.write(levelStr)
        f.close()

        f = open(filename + "_spin", "a")
        f.write(spinStr)
        f.close()

        f = open(filename + "_mcts", "a")
        f.write(mctsStr)
        f.close()



    def run_simulation(self):

        for game in self.my_types:
            for size in self.my_sizes:
                sim = Sim_Nov(level_size=size,sprite_planner=game[0],spin=game[1],player=game[2])
                for i in range(0,self.numOfEps):
                    print("---")
                    level_str, spin_str, mcts_str, _ = sim.pipeline()
                    if spin_str == None:
                        self.record_episode_(i, size, game[3], level_str)
                    else:
                        self.record_episode(i, size, game[3], level_str, spin_str, mcts_str)




class Simulation:
    def __init__(self, map_percentage=30, level_size=24, map_generator=cellularAutomata.elementary_cellular_automata, map_polisher=caPolisher.CAPolisher_MinArea, sprite_planner=spritePlanner.equalSpritePlanner, spin=spinner.SpinClass_Game3_smart, parser=spinParser.spinParser, searcher=player.MCTS_Runner_Regular, player=player.RacerGameClass_Smart, feed=randomFeeder_Generic):
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

    def pipeline(self, mcts_adv=1):
        if mcts_adv <= 0:
            raise Exception("ERROR ON PIPELINE DUDE!")
        level_size = self.lvl_sz
        rng_feed = self.rng_fdr(size=level_size)
        while(True):
        ############################ LEVEL-GEN PHASE    
            try:
                line = rng_feed.serve()
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

            map2 = "11111111111111111111111111\n1"+"1\n1".join(map_)+"1\n11111111111111111111111111"
        ############################ MCTS
            mcts_time = time.time()
            print("Mcts params = # of loops: {}  Maximum depth: {}   Rollout depth: {}    Number of playouts: {}".format(mcts_adv*2, len(avatar)*mcts_adv/5, len(avatar)+5, level_size*16))
            mcts_moves = self.mcts_ag(nloops = mcts_adv*2,max_d= len(avatar)*mcts_adv/5,rollout_depth=len(avatar)+5, n_playouts=level_size*16, game_desc= game.game, level_desc=map2, render=False).run()[0][0]
            mcts_time = time.time() - mcts_time
            mcts_score, mcts_terminal = self.player(action_list=mcts_moves, level_desc=map_).play()
        ############################ FINISHING PHASE
            mcts_moves = list(map(str,mcts_moves))
            avatar = list(map(str, avatar))
            #### SUB-PHASE 1 - Record Level
            level_line = "Level size: {}\nPolisher percentage: {}\nStarter line: {},\nWhole Level:\n{}".format(self.lvl_sz, self.pol_pct, line, map2)
            #### SUB-PHASE 2 - Record SPIN performance
            spin_line  = "Spin score: {}\nSpin terminal:{}\nSpin time: {}\nSpin moves: {}".format(spin_score, (spin_terminal and (spin_score > 0)), modelling_time, "*".join(avatar))
            #### SUB-PHASE 3 - Record MCTS performance
            mcts_line  = "MCTS score: {}\nMCTS terminal: {}\nMCTS time:{}\nMCTS moves: {}".format(mcts_score,(mcts_terminal and (mcts_score > 0)),mcts_time, "*".join(mcts_moves))
            #### SUB-PHASE 4 - Record
            return level_line, spin_line, mcts_line, (mcts_terminal and (mcts_score > 0))
            

def record_simulation(simno, levelinfo, spininfo, mctsinfo):
    filename = str(magic_number) + str(simno)
    
    f = open(filename + "_level", "a")
    f.write(levelinfo)
    f.close()

    f = open(filename + "_spin", "a")
    f.write(spininfo)
    f.close()

    f = open(filename + "_mcts", "a")
    f.write(mctsinfo)
    f.close()

magic_number = 0

if __name__ == "__main__":
    """ 
    magic_number = random.random()
    ss = Simulation(map_percentage=50)
    sim_no = 0
    mcts_lost_count = 0
    while True:
        lline, sline, mline, mwin = ss.pipeline(mcts_lost_count + 1)
        if mwin == False:
            mcts_lost_count += 1
        record_simulation(sim_no, lline, sline, mline)
        sim_no += 1
    """
    Sim_Nov_Wrapper(8).run_simulation()
