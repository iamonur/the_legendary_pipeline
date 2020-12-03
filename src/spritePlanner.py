import caPolisher

#TODO: implement more game types than just Basic, which is game -1 

class spritePlannerException(Exception):
    pass

class dualSpritePlanner:
    """
    Plans as:
    - Portal at one corner
    - Avatar at the opposite corner
    #Best used in the game "MazeSolver"
    """
    def __init__(self, map):
        self.map = map
        self.avatarAt = (-1,-1)
        self.portalAt = (-1,-1)

    def findMostDistantCells(self):

        maxDist = 0
        cells =((-1,-1),(-1,-1))

        for ln1, l1 in enumerate(self.map):
            for cn1, c1 in enumerate(l1):
                if c1 == "1":
                    continue
                for ln2, l2 in enumerate(self.map):
                    for cn2, c2 in enumerate(l2):
                        if c2 == '1':
                            continue
                        if (abs(ln1-ln2)+abs(cn1-cn2)) > maxDist:
                            maxDist = (abs(ln1-ln2)+abs(cn1-cn2))
                            cells = ((ln1,cn1),(ln2,cn2))

        return cells

    def perform(self):
        (self.avatarAt,self.portalAt) = self.findMostDistantCells()

    def getMap(self):
        if self.avatarAt == (-1,-1) or self.portalAt == (-1,-1):
            raise spritePlannerException("Plan the sprites first before placing!")

        dummy_map = []
        for line in self.map:
            dummy_map.append(list(line))

        (y, x) = self.avatarAt
        dummy_map[y][x] = 'A'

        (y, x) = self.portalAt
        dummy_map[y][x] = 'G'
       

        for ln, line in enumerate(dummy_map):
            self.map[ln] = "".join(line)

        return self.map

class mazeWithSubGoalsPlanner:
    def __init__(self, map, goalCount=3):
        self.map = map
        self.avatarAt = (-1,-1)
        self.portalAt = (-1, 1)
        self.goalCount = goalCount
        self.goalLocations = []

    def findMostDistantCells(self):
        maxDist = 0
        cells =((-1,-1),(-1,-1))

        for ln1, l1 in enumerate(self.map):
            for cn1, c1 in enumerate(l1):
                if c1 == "1":
                    continue
                for ln2, l2 in enumerate(self.map):
                    for cn2, c2 in enumerate(l2):
                        if c2 == '1':
                            continue
                        if (abs(ln1-ln2)+abs(cn1-cn2)) > maxDist:
                            maxDist = (abs(ln1-ln2)+abs(cn1-cn2))
                            cells = ((ln1,cn1),(ln2,cn2))

        return cells
    
    def place_subgoals(self):
        total_pieces = self.goalCount + 1
        import spinner
        tmp = spinner.A_Star_Game4(self.getMap())
        tmp.perform()
        shortest_path = tmp.moves_from_map
        if self.goalCount > (len(shortest_path)-2):
            self.goalCount = (len(shortest_path) - 2)
        
        for index in range(self.goalCount):
            print(index)
            place = (len(shortest_path)*(index+1) // (self.goalCount+2))
            coordinates = shortest_path[place]
            self.goalLocations.append((coordinates[0], coordinates[1]))

    def perform(self):
        (self.avatarAt, self.portalAt) = self.findMostDistantCells()
        self.place_subgoals()
        #return self.getMap()

    def getMap(self):
        if self.avatarAt == (-1,-1) or self.portalAt == (-1,-1):
            raise spritePlannerException("Plan the sprites first before placing!")

        if len(self.goalLocations) == 0:
            dummy_map = []
            for line in self.map:
                dummy_map.append(list(line))

            (y, x) = self.avatarAt
            dummy_map[y][x] = 'A'

            (y, x) = self.portalAt
            dummy_map[y][x] = 'G'
       

            for ln, line in enumerate(dummy_map):
                self.map[ln] = "".join(line)

            return self.map

        else:
            dummy_map = []

            for line in self.map:
                dummy_map.append(list(line))

            (y,x) = self.avatarAt
            dummy_map[y][x] = 'A'
            (y,x) = self.portalAt
            dummy_map[y][x] = 'G'

            for subgoal in self.goalLocations:
                (y,x) = subgoal
                dummy_map[y][x]='g'

            for ln, line in enumerate(dummy_map):
                self.map[ln] = "".join(line)

            return self.map

class spritePlanner:
    """
    Plans as:
    - Portal to one corner
    - Avatar at the other corner
    - Enemy in the middle
    #This planner best be used in the game "Run". Because the avatar cannot race, and certainly not catch.
    """
    def __init__(self, map, gameType='Basic'):
        self.gameType = gameType
        self.map = map
        self.avatarAt = (-1,-1)
        self.portalAt = (-1,-1)
        self.enemyAt  = (-1,-1)

    def findMostDistantCells(self):

        maxDist = 0
        cells =((-1,-1),(-1,-1))

        for ln1, l1 in enumerate(self.map):
            for cn1, c1 in enumerate(l1):
                if c1 == "1":
                    continue
                for ln2, l2 in enumerate(self.map):
                    for cn2, c2 in enumerate(l2):
                        if c2 == '1':
                            continue
                        if (abs(ln1-ln2)+abs(cn1-cn2)) > maxDist:
                            maxDist = (abs(ln1-ln2)+abs(cn1-cn2))
                            cells = ((ln1,cn1),(ln2,cn2))

        return cells

    def findMidCell(self):
        (y1, x1) = self.avatarAt
        (y2, x2) = self.portalAt
        (yy, xx) = ((y1+y2)/2,(x1+x2)/2)
        toRet = (-1, -1)
        minDist = 2147483647

        for ln, l in enumerate(self.map):
            for cn, c in enumerate(l):
                if c != '0':
                    continue
                if (ln,cn) == (y1,x1) or (ln,cn) == (y1,x1):
                    continue
                if (abs(yy - ln) + abs(xx - cn)) < minDist:
                    minDist = abs(yy - ln) + abs(xx - cn)
                    toRet = (ln, cn)
                    if minDist == 0 or minDist == 0.5:
                        return toRet

        return toRet

    def perform(self):
        if self.gameType == 'Basic':
            (self.avatarAt,self.portalAt) = self.findMostDistantCells()
            self.enemyAt = self.findMidCell()
            

    def getMap(self):
        if self.avatarAt == (-1,-1) or self.portalAt == (-1,-1) or self.enemyAt == (-1,-1):
            raise spritePlannerException("Plan the sprites first before placing!")

        dummy_map = []
        for line in self.map:
            dummy_map.append(list(line))

        (y, x) = self.enemyAt
        dummy_map[y][x] = 'E'

        (y, x) = self.avatarAt
        dummy_map[y][x] = 'A'

        (y, x) = self.portalAt
        dummy_map[y][x] = 'G'

        

        for ln, line in enumerate(dummy_map):
            self.map[ln] = "".join(line)

        return self.map

class reverseSpritePlanner:
    """
    Plans as:
    - Portal at one corner
    - Enemy at the other
    - Avatar in the middle
    #This planner best be used on the game "Catch". Because it can run and race so easily.
    """
    def __init__(self, map, gameType='Basic'):
        self.gameType = gameType
        self.map = map
        self.avatarAt = (-1,-1)
        self.portalAt = (-1,-1)
        self.enemyAt  = (-1,-1)

    def findMostDistantCells(self):

        maxDist = 0
        cells =((-1,-1),(-1,-1))

        for ln1, l1 in enumerate(self.map):
            for cn1, c1 in enumerate(l1):
                if c1 == "1":
                    continue
                for ln2, l2 in enumerate(self.map):
                    for cn2, c2 in enumerate(l2):
                        if c2 == '1':
                            continue
                        if (abs(ln1-ln2)+abs(cn1-cn2)) > maxDist:
                            maxDist = (abs(ln1-ln2)+abs(cn1-cn2))
                            cells = ((ln1,cn1),(ln2,cn2))

        return cells

    def findMidCell(self):
        (y1, x1) = self.avatarAt
        (y2, x2) = self.portalAt
        (yy, xx) = ((y1+y2)/2,(x1+x2)/2)
        toRet = (-1, -1)
        minDist = 2147483647

        for ln, l in enumerate(self.map):
            for cn, c in enumerate(l):
                if c != '0':
                    continue
                if (ln,cn) == (y1,x1) or (ln,cn) == (y1,x1):
                    continue
                if (abs(yy - ln) + abs(xx - cn)) < minDist:
                    minDist = abs(yy - ln) + abs(xx - cn)
                    toRet = (ln, cn)
                    if minDist == 0 or minDist == 0.5:
                        return toRet

        return toRet

    def perform(self):
        if self.gameType == 'Basic':
            (self.avatarAt,self.portalAt) = self.findMostDistantCells()
            self.enemyAt = self.findMidCell()
            

    def getMap(self):
        if self.avatarAt == (-1,-1) or self.portalAt == (-1,-1) or self.enemyAt == (-1,-1):
            raise spritePlannerException("Plan the sprites first before placing!")

        dummy_map = []
        for line in self.map:
            dummy_map.append(list(line))

        (y, x) = self.enemyAt
        dummy_map[y][x] = 'A'

        (y, x) = self.avatarAt
        dummy_map[y][x] = 'E'

        (y, x) = self.portalAt
        dummy_map[y][x] = 'G'

        

        for ln, line in enumerate(dummy_map):
            self.map[ln] = "".join(line)

        return self.map

class equalSpritePlanner:
    """
    Plans as:
    - Avatar at a corner.
    - Enemy at the other.
    - Portal in the middle.
    # This planner better used on the game "race", since it minimizes conflict between the opponent and the avatar. However, remember that against the perfect opponent, this game has nearly 50% win chance.
    """
    def __init__(self, map, gameType='Basic'):
        self.gameType = gameType
        self.map = map
        self.avatarAt = (-1,-1)
        self.portalAt = (-1,-1)
        self.enemyAt  = (-1,-1)

    def findMostDistantCells(self):

        maxDist = 0
        cells =((-1,-1),(-1,-1))

        for ln1, l1 in enumerate(self.map):
            for cn1, c1 in enumerate(l1):
                if c1 == "1":
                    continue
                for ln2, l2 in enumerate(self.map):
                    for cn2, c2 in enumerate(l2):
                        if c2 == '1':
                            continue
                        if (abs(ln1-ln2)+abs(cn1-cn2)) > maxDist:
                            maxDist = (abs(ln1-ln2)+abs(cn1-cn2))
                            cells = ((ln1,cn1),(ln2,cn2))

        return cells

    def findMidCell(self):
        (y1, x1) = self.avatarAt
        (y2, x2) = self.enemyAt
        (yy, xx) = ((y1+y2)/2,(x1+x2)/2)
        toRet = (-1, -1)
        minDist = 2147483647

        for ln, l in enumerate(self.map):
            for cn, c in enumerate(l):
                if c != '0':
                    continue
                if (ln,cn) == (y1,x1) or (ln,cn) == (y1,x1):
                    continue
                if (abs(yy - ln) + abs(xx - cn)) < minDist:
                    minDist = abs(yy - ln) + abs(xx - cn)
                    toRet = (ln, cn)
                    if minDist == 0 or minDist == 0.5:
                        return toRet

        return toRet

    def perform(self):
        if self.gameType == 'Basic':
            (self.avatarAt,self.enemyAt) = self.findMostDistantCells()
            self.portalAt = self.findMidCell()
            

    def getMap(self):
        if self.avatarAt == (-1,-1) or self.portalAt == (-1,-1) or self.enemyAt == (-1,-1):
            raise spritePlannerException("Plan the sprites first before placing!")

        dummy_map = []
        for line in self.map:
            dummy_map.append(list(line))

        (y, x) = self.enemyAt
        dummy_map[y][x] = 'A'

        (y, x) = self.avatarAt
        dummy_map[y][x] = 'E'

        (y, x) = self.portalAt
        dummy_map[y][x] = 'G'

        

        for ln, line in enumerate(dummy_map):
            self.map[ln] = "".join(line)

        return self.map

class sokobanPlanner:
    """
    Some rules for planning:
    - A box can be in a place where it could move to all sides at first move.(Meaning we can move around it and push where-ever we want)
        [1][2][3]
        [4][B][5]
        [6][7][8]
        {2,4,5,7} are must
        3 or more of {1,3,6,8}

    - A hole can be in anywhere, but should not block a road:
        [1][2][3]
        [4][H][5]
        [6][7][8]
        If 5 and 2: Then 3
        If 5 and 7: Then 8
        If 5 and 4: Either {1,2,3} or {6,7,8}
        If 2 and 4: Then 1
        If 2 and 7: Either {1,4,6} or {3,5,8}
        If 4 and 7: Then 6
        If 7 and 5: Then 8
    
    - Count of boxes = Count of holes
    
    - Count of boxes > 0
    """
    def __init__(self, map, count_boxes=1):
        self.maximum_boxes = count_boxes
        self.map = map
        self.boxes = []
        self.holes = []
        self.avatarAt = self.__findAvatarLocation()

    def get_goals(self):
        return len(self.holes)

    def __findAvatarLocation(self):
        maxDist = 0
        cells =[(-1,-1),(-1,-1)]

        for ln1, l1 in enumerate(self.map):
            for cn1, c1 in enumerate(l1):
                if c1 == "1":
                    continue
                for ln2, l2 in enumerate(self.map):
                    for cn2, c2 in enumerate(l2):
                        if c2 == '1':
                            continue
                        if (abs(ln1-ln2)+abs(cn1-cn2)) > maxDist:
                            maxDist = (abs(ln1-ln2)+abs(cn1-cn2))
                            cells = [(ln1,cn1),(ln2,cn2)]

        return cells[0]

    def __placeAPair(self):
        box_pos = (-1,-1)
        hole_pos = (-1,-1)
        #Place a box
        for ln, l in enumerate(self.map):
            for cn, c in enumerate(l):
                try:
                    block_1 = self.map[ln - 1][cn - 1]
                except:
                    block_1 = '1'

                try:
                    block_2 = self.map[ln - 1][cn]
                except:
                    block_2 = '1'

                try:
                    block_3 = self.map[ln - 1][cn + 1]
                except:
                    block_3 = '1'

                try:
                    block_4 = self.map[ln][cn - 1]
                except:
                    block_4 = '1'

                try:
                    block_5 = self.map[ln][cn + 1]
                except:
                    block_5 = '1'

                try:
                    block_6 = self.map[ln + 1][cn - 1]
                except:
                    block_6 = '1'

                try:
                    block_7 = self.map[ln + 1][cn]
                except:
                    block_7 = '1'

                try:
                    block_8 = self.map[ln + 1][cn + 1]
                except:
                    block_8 = '1'

                if not ((block_2 == '0') and (block_4 == '0') and (block_5 == '0') and (block_7 == '0')):
                    continue

                if (int(block_1)+int(block_3)+int(block_6)+int(block_8)) > 1:
                    continue

                box_pos = (ln, cn)

                if (box_pos in self.boxes) or (box_pos in self.holes) or (box_pos == self.avatarAt):
                    box_pos = (-1,-1)
                    continue

                else:
                    break

            if box_pos != (-1, -1):
                break

        #Place a hole
        for ln, l in enumerate(self.map):
            for cn, c in enumerate(l):
                okay_to_place = False

                try:
                    block_1 = self.map[ln - 1][cn - 1]
                except:
                    block_1 = '1'

                try:
                    block_2 = self.map[ln - 1][cn]
                except:
                    block_2 = '1'

                try:
                    block_3 = self.map[ln - 1][cn + 1]
                except:
                    block_3 = '1'

                try:
                    block_4 = self.map[ln][cn - 1]
                except:
                    block_4 = '1'

                try:
                    block_5 = self.map[ln][cn + 1]
                except:
                    block_5 = '1'

                try:
                    block_6 = self.map[ln + 1][cn - 1]
                except:
                    block_6 = '1'

                try:
                    block_7 = self.map[ln + 1][cn]
                except:
                    block_7 = '1'

                try:
                    block_8 = self.map[ln + 1][cn + 1]
                except:
                    block_8 = '1'

                ways = int(block_2)+int(block_4)+int(block_5)+int(block_7)

                if ways == 1:
                    okay_to_place = True
                elif ways == 0:
                    okay_to_place = False
                elif (block_5 == '0' and block_2 == '0' and block_3 == '0'):
                    okay_to_place = True
                elif (block_5 == '0' and block_7 == '0' and block_8 == '0'):
                    okay_to_place = True
                elif (block_4 == '0' and block_2 == '0' and block_1 == '0'):
                    okay_to_place = True
                elif (block_4 == '0' and block_7 == '0' and block_6 == '0'):
                    okay_to_place = True
                else:
                    okay_to_place = False

                if not ((block_2 == '0') and (block_4 == '0') and (block_5 == '0') and (block_7 == '0')):
                    continue

                if (int(block_1)+int(block_3)+int(block_6)+int(block_8)) > 1:
                    continue

                hole_pos = (ln, cn)

                if (hole_pos in self.boxes) or (hole_pos in self.holes) or (hole_pos == self.avatarAt) or (hole_pos == box_pos):
                    hole_pos = (-1,-1)
                    continue

                else:
                    break

            if hole_pos != (-1, -1):
                break

        

        if box_pos == (-1,-1) or hole_pos == (-1,-1):
            return None

        self.boxes.append(box_pos)
        self.holes.append(hole_pos)
        return True #Return any non-None value.
    
    def __placeAllPairs(self):
        for index in range(self.maximum_boxes):
            ret_val = self.__placeAPair()
            if ret_val == None:
                break
        return index

    def perform(self):
        total_pairs = self.__placeAllPairs()

    def getMap(self):
        dummy_map = []

        for line in self.map:
            dummy_map.append(list(line))

        (y,x) = self.avatarAt
        dummy_map[y][x] = 'A'

        for hole in self.holes:
            (y,x) = hole
            dummy_map[y][x] = 'H'

        for box in self.boxes:
            (y,x) = box
            dummy_map[y][x] = 'B'

        for ln, line in enumerate(dummy_map):
            self.map[ln] = "".join(line)

        return self.map

if __name__ == "__main__":
    #s = spritePlanner(caPolisher.polisher().perform())
    #s.perform()
    #caPolisher.map_print(s.getMap())
    import cellularAutomata
    s = sokobanPlanner(caPolisher.CAPolisher_MinArea(ca=cellularAutomata.elementary_cellular_automata(size=24, limit=24, start="000001010011100101110111")).perform(),count_boxes=10)
    s.perform()
    caPolisher.map_print(s.getMap())