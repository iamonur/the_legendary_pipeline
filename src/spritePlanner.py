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


if __name__ == "__main__":
    s = spritePlanner(caPolisher.polisher().perform())
    s.perform()
    caPolisher.map_print(s.getMap())
