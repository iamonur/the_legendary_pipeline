#Huge thing. TODO: Think about small chunks.

import cellularAutomata #my module
import caPolisher       #my module
import spritePlanner    #my module
import player           #my module
import spinner          #my module
import spinParser       #my module
import abc              #SimManager is an interface
import random

def list_sort(list): #The lists are not that big, bubblesort will do.
    for iter_num in range(len(list) - 1, 0, -1):
        for idx in range(iter_num):
            if list[idx][2] > list[idx + 1][2]:
                temp = list[idx]
                list[idx] = list[idx + 1]
                list[idx + 1] = temp

class FeederException(Exception):
    pass

class startFeeder(): #You can build rules, purely random or just serve a list. 
    def __init__(self):
        self.count = 0

    def serve(self):
        if count > 10:
            raise FeederException("Cannot succeed to create a level by this definition, feeder is depleted.")
        ret = []
        for i in range(0,23):
            ret.append(str(random.randint(0,1)))
        return "".join(ret)



class SimManager(abc.ABC):
    #@classmethod
    d#ef createSimManager(mapgenclass, polisherclass, plannerclass, spinnerclass=SpinClass, parserclass=spinParser, playerclass=GameClass, startFeed)
        
    def __init__(self, mapGenerator, mapPolisher, sprPlanner, spin=SpinClass, parser=spinParser, player=GameClass, feed=startFeeder)

    def pipeline(self)


class exampleSimManager(SimManager):
    @classmethod
    def createSimManager(mapgenclass, ):
        try:
            mg = mapgenclass()
        except ValueError:
            return None

        

    def __init__(self):
        try:
            self.map_generator = bl_tr_odd_p_mid_nybble_switch_srca()#Just using the default values for the display purposes.
        except ValueError:
            return 
        
        self.polisher = polisher(ca=self.map_generator)
