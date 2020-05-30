
import abc #Abstract Base Class

lookupTable = { '000':0, '001':1, '010':2, '011':3, '100':4, '101':5, '110':6, '111':7}

class elementary_cellular_automata:

    def __init__(self, ruleset=150, size=24, limit=24, start="000000000000100000000000", borders='0'):

        if len(start) != size:

            raise ValueError("Size or start is not OK!")

        self.line = start
        self.border = borders
        self.limit = limit
        self.size = size
        self.d_rule = ruleset
        self.b_rule = self.binaryRule()
        self.map = []

    def perform(self):

        while len(self.map) < self.limit -1:
            self.iterate_once()

        self.map.append(self.line)
        print(self.map)
        return self.map

    def binaryRule(self):
        temp = format(self.d_rule, "b")
        while len(temp) < 8:
            temp = '0' + temp
        return temp

    def cellCalculate(self, parent):
        return self.b_rule[(-1-lookupTable[parent])]

    def iterate_once(self):
        self.map.append(self.line)
        tempStr = ""
        self.line = self.border + self.line + self.border

        for chnum, ch in enumerate(self.line):

            if chnum == 0 or chnum == (self.size+1):
                continue
            tempStr += self.cellCalculate((self.line[chnum-1] + ch + self.line[chnum+1]))

        self.line = tempStr





class selfref_ca(abc.ABC): #I am not inheriting this for now, just copying-pasting for the interface.
    #There is no __init__ since, this class cannot be used to create instances anyway.
    @abc.abstractmethod
    def calculateRule(self):
        pass

    def cellCalculate(self, parent):
        return self.b_rule[(-1-lookupTable[parent])]

    def iterate_once(self):
        self.b_rule = self.calculateRule()
        self.map.append(self.line)
        tempStr = ""
        self.line = self.border + self.line + self.border

        for chnum, ch in enumerate(self.line):
            if chnum == 0 or chnum == (self.size + 1):
                continue
            tempStr += self.cellCalculate((self.line[chnum - 1] + ch + self.line[chnum + 1]))

        self.line = tempStr

    def perform(self):
        while len(self.map) < self.limit:
            self.iterate_once()

        
        return self.map

class block_ones_majority_srca(selfref_ca):
    def __init__(self, size=24, limit=24, start="110100101110000111011001", borders='0'):
        if len(start) != size:
            raise ValueError("Size or start is not OK!")

        self.line = start
        self.border = borders
        self.limit = limit
        self.size = size
        self.map = []

    def calculateRule(self):
        block = ""
        rule = ""
        for cell in self.line:

            block += cell
            if len(block) == 3:
                if block.count('1') > 1: #1 is majority
                    rule += '1'
                else:
                    rule += '0'

                block = ""

        return rule

class block_ones_odd_parity_srca(selfref_ca):
    def __init__(self, size=24, limit=24, start="110100101110000111011001", borders='0'):
        if len(start) != size:
            raise ValueError("Size or start is not OK!")

        self.line = start
        self.border = borders
        self.limit = limit
        self.size = size
        self.map = []

    def calculateRule(self):
        block = ""
        rule = ""
        for cell in self.line:
            block += cell
            if len(block) == 3:
                if block.count('1') == 3 or block.count('1') == 1:
                    rule += '1'
                else:
                    rule += '0'
                block = ""
        return rule

class block_transition_odd_parity_srca(selfref_ca):
    def __init__(self, size=24, limit=24, start="110100101110000111011001", borders='1'):
        if len(start) != size:
            raise ValueError("Size or start is not OK!")

        self.line = start
        self.border = borders
        self.limit = limit
        self.size = size
        self.map = []

    def calculateRule(self):
        block = ""
        rule = ""
        for cell in self.line:
            block += cell
            if len(block) == 3:
                transitions = block.count('10') + block.count('01')
                if transitions == 1:
                    rule += '1'
                else:
                    rule += '0'
                block = ""
        return rule

class bl_tr_odd_p_mid_nybble_switch_srca(selfref_ca):
    def __init__(self, size=24, limit=24, start="110100101110000111011001", borders='1'):
        if len(start) != size:
            raise ValueError("Size or start is not OK!")

        self.line = start
        self.border = borders
        self.limit = limit
        self.size = size
        self.map = []

    def calculateRule(self):
        block = ""
        rule = ""
        for cell in self.line:
            block += cell
            if len(block) == 3:
                transitions = block.count('10') + block.count('01')
                if transitions == 1:
                    rule += '1'
                else:
                    rule += '0'
                block = ""
        rule_list = list(rule)

        temp = rule_list[2]
        rule_list[2] = rule_list[1]
        rule_list[1] = temp

        temp = rule_list[5]
        rule_list[5] = rule_list[6]
        rule_list[6] = temp
        rule = "".join(rule_list)
        return rule

class bl_tr_even_p_mid_nybble_switch_srca(selfref_ca):
    def __init__(self, size=24, limit=24, start ="110100101110000111011001", borders ='1'):
        if len(start) != size:
            raise ValueError("Size or start is not OK!")

        self.line = start
        self.border = borders
        self.limit = limit
        self.size = size
        self.map = []

    def calculateRule(self):
        block = ""
        rule = ""
        for cell in self.line:
            block += cell
            if len(block) == 3:
                transitions = block.count('10') + block.count('01')
                if transitions == 1:
                    rule += '0'
                else:
                    rule += '1'
                block = ""
        rule_list = list(rule)

        temp = rule_list[2]
        rule_list[2] = rule_list[1]
        rule_list[1] = temp

        temp = rule_list[5]
        rule_list[5] = rule_list[6]
        rule_list[6] = temp
        rule = "".join(rule_list)
        return rule

#class two_level_cellular

class two_level_cellular_von_neumann_automata:

    def __init__(self, firstlevel_generator=elementary_cellular_automata, size =24, limit =24, start="110100101110000111011001", t_level=3, borders=0): #Assuming a square btw
        lev_gen = firstlevel_generator(start=start, limit=limit, size=size)
        self.limit = limit
        self.border = borders
        self.threshold = t_level
        self.map = []
        self.first_out = lev_gen.perform()
        for line in self.first_out:
            self.map.append(list(line))

        self.size=size
        self.limit=limit

    def iterate_cell(self, n0, n1, n2, n3, n4):
        if n1[0] == -1 or n1[1] == -1 or n1[0] == self.limit or n1[1] == self.limit:
            neighbor1 = self.border
        else:
            neighbor1 = self.map[n1[0]][n1[1]]

        if n2[0] == -1 or n2[1] == -1 or n2[0] == self.limit or n2[1] == self.limit:
            neighbor2 = self.border
        else:
            neighbor2 = self.map[n2[0]][n2[1]]

        if n3[0] == -1 or n3[1] == -1 or n3[0] == self.limit or n3[1] == self.limit:
            neighbor3 = self.border
        else:
            neighbor3 = self.map[n3[0]][n3[1]]

        if n4[0] == -1 or n4[1] == -1 or n4[0] == self.limit or n4[1] == self.limit:
            neighbor4 = self.border
        else:
            neighbor4 = self.map[n4[0]][n4[1]]

            
        count = 0
        if neighbor1 is '1':
            count += 1
        if neighbor2 is '1':
            count += 1
        if neighbor3 is '1':
            count += 1
        if neighbor4 is '1':
            count += 1

        if count < self.threshold:
            self.map[n0[0]][n0[1]] = '0'
        else:
            self.map[n0[0]][n0[1]] = '1'

    def map_iterate(self): # You can iterate multiple times.
        for ln, line in enumerate(self.map):
            for cn, char in enumerate(line):
                self.iterate_cell((ln, cn), (ln-1, cn), (ln+1, cn), (ln, cn-1), (ln, cn+1))

        return self.map

    def perform(self):
        #self.map_iterate()
        return self.map_iterate()

def formatline(line):
    temp = ""
    for ch in line:
        if ch == '1':
            temp += '#'
        elif ch == '0':
            temp += ' '
        else:
            temp += ch

    return temp

if __name__ == "__main__":
    a = bl_tr_odd_p_mid_nybble_switch_srca()
    res = a.perform()
    for line in res:
        print(formatline(line))
