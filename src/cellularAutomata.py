
import abc #Abstract Base Class

lookupTable = { '000':0, '001':1, '010':2, '011':3, '100':4, '101':5, '110':6, '111':7}

class elementary_cellular_automata:

    def __init__(self, ruleset=30, size=24, limit=24, start="000000000000100000000000", borders='0'):

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

        while len(self.map) < self.limit:
            self.iterate_once()

        self.map.append(self.line)
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
    def __init__(self, size=24, limit=24, start="010101010101010101010101", borders='0'):
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
