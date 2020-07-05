import caPolisher

#TODO: implement more game types than just Basic, which is game -1 

class spritePlannerException(Exception):
    pass

class dualSpritePlanner:
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

class spritePlanner:
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

if __name__ == "__main__":
    s = spritePlanner(caPolisher.polisher().perform())
    s.perform()
    caPolisher.map_print(s.getMap())
