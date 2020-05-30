import cellularAutomata #self-referencing cellular automata
import operator #To get key with maximum value.

class polisherException(Exception):
    pass

space_identifiers = {
    0:'0',
    1:'1',
    2:'2',
    3:'3',
    4:'4',
    5:'5',
    6:'6',
    7:'7',
    8:'8',
    9:'9',
    10:'A',
    11:'B',
    12:'C',
    13:'D',
    14:'E',
    15:'F',
    16:'G',
    17:'H',
    18:'I',
    19:'J',
    20:'K',
    21:'L',
    22:'M',
    23:'N',
    24:'O',
    25:'P',
    26:'Q',
    27:'R',
    28:'S',
    29:'T',
    30:'U',
    31:'V',
    32:'W',
    33:'X',
    34:'Y',
    35:'Z',
    36:'a',
    37:'b',
    38:'c',
    39:'d',
    40:'e',
    41:'f',
    42:'g',
    43:'h',
    44:'i',
    45:'j',
    46:'k',
    47:'l',
    48:'m',
    49:'n',
    50:'o',
    51:'p',
    52:'q',
    53:'r',
    54:'s',
    55:'t',
    56:'u',
    57:'v',
    58:'w',
    59:'x',
    60:'y',
    61:'z',
    62:'!',
    63:'^',
    64:'+',
    65:'%',
    66:'&',
    67:'/',
    68:'(',
    69:')',
    70:'=',
    71:'*',
    72:'?',
    73:'-',
    74:'_',
    75:'£',
    76:'#',
    77:'$',
    78:'½',
    79:'¾',
    80:'{',
    81:'[',
    82:']',
    83:'}',
    84:'é',
    85:',',
    86:';',
    87:'`',
    88:'.',
    89:':',
    90:'@',
    91:'€',
    92:'¶',
    93:'₺',
    94:'←',
    95:'û',
    96:'î',
    97:'ô',
    98:'~',
    99:'<',
    100:'>',
    101:'|',
    102:'"',
    }

reverse_space_identifiers = {}

for item in space_identifiers:
    reverse_space_identifiers.update({space_identifiers[item]:item})


class polisher:
    def __init__(self, ca=cellularAutomata.bl_tr_odd_p_mid_nybble_switch_srca(), minimumArea=50):
        self.minArea = minimumArea
        self.ca = ca
        self.map_1 = self.ca.perform()
        self.whole_space = self.get_full_fs(self.map_1)
        self.connected_spaces, self.map_enumed = self.get_connected_fses(self.map_1)

    def create_distance_matrix(self, connected_fses, map):
        startingDistance = 2147483647
        dist_dict = {}
        for a in connected_fses:
            for b in connected_fses:
                dist_dict.update({(a, b): startingDistance})

        for ln, line in enumerate(map):
            for cn, ch in enumerate(line):
                if reverse_space_identifiers[ch] in connected_fses:
                    for ln2, line2 in enumerate(map):
                        for cn2, ch2 in enumerate(line2):
                            if ch2 == ch or ch2 == '1' or ch2 == '0':
                                continue
                            dist = abs(ln-ln2) + abs(cn-cn2)
                            if dist_dict[(reverse_space_identifiers[ch],reverse_space_identifiers[ch2])] > dist:
                                dist_dict[(reverse_space_identifiers[ch],reverse_space_identifiers[ch2])] = dist
                                dist_dict[(reverse_space_identifiers[ch2],reverse_space_identifiers[ch])] = dist

        return dist_dict

    def iterate_on_distance_matrix(self, d_dir, connected_fses, map):
        big_chunk = max(connected_fses, key=connected_fses.get)
        to_merge = []
        min = 2147483647
        changes = []
        for k in connected_fses:
            if d_dir[(big_chunk, k)] < min: #New minima
                to_merge.clear()
                to_merge.append(k)
                min = d_dir[(big_chunk, k)]
            elif d_dir[(big_chunk, k)] == min: #Tie to minima
                to_merge.append(k)


        for smally in to_merge:
            quadBreak = False
            #Calculate which cell to which cell, the merger will happen
            #Remove walls, there will be only walls.
            for ln1, line1 in enumerate(map):

                for cn1, cell1 in enumerate(line1):

                    if cell1 == space_identifiers[smally]:

                        for ln2, line2 in enumerate(map):

                            for cn2, cell2 in enumerate(line2):
                                if cell2 == space_identifiers[big_chunk]:

                                    if (abs(cn1-cn2) + abs(ln1-ln2)) == min:
                                        c_cn1 = cn1
                                        c_cn2 = cn2
                                        c_ln1 = ln1
                                        c_ln2 = ln2


                                        while c_cn1 > c_cn2:
                                            c_cn1 -= 1
                                            changes.append((c_ln1, c_cn1))

                                        while c_cn2 > c_cn1:
                                            c_cn2 -= 1
                                            changes.append((c_ln2, c_cn2))

                                        while c_ln2 > c_ln1:
                                            c_ln2 -= 1
                                            changes.append((c_ln2, c_cn2))

                                        while c_ln1 > c_ln2:
                                            c_ln1 -= 1
                                            changes.append((c_ln1, c_cn1))

                                        if (c_ln1 != c_ln2) or (c_cn1 != c_cn2):
                                            raise ValueError("There's something wrong in the map!")
                                            # Don't catch it in the module. Let it raise to the heavens, where it will take this module with it.
                                            # This map should not be simulated at all.
                                        quadBreak = True

                                if quadBreak:
                                    break

                            if quadBreak:
                                break

                    if quadBreak:
                        break

                if quadBreak:
                    break

        dummy_map = []
        for line in map:
            dummy_map.append(list(line))

        for (ln, cn) in changes:
            dummy_map[ln][cn] = '0'

        for ln, line in enumerate(dummy_map):
            map[ln] = "".join(line)

        return map #Other things are invalid now. Remember to re-calculate.

    def get_full_fs(self, map):
        ones = 0
        zeroes = 0
        for line in map:
            zeroes += line.count('0')
        area = len(map) * len(map[0])

        return 100 * zeroes / area

    def get_connected_fses(self, map):
        areaNumber = 2
        connected_fses = {}
        double_break = False
        while(self.get_full_fs(map) != 0):
            for lnum, line in enumerate(map):
                for chnum, ch in enumerate(line):
                    if ch == '0':
                        count, map = self.turn_neighboring_cells(map, lnum, chnum, areaNumber)
                        connected_fses.update({areaNumber: count})
                        areaNumber += 1
                        double_break = True
                    if double_break:
                        break
                if double_break:
                    double_break = False
                    break
        return connected_fses, map

    def reset_map(self, map):
        for lnum, line in enumerate(map):
            for chnum, ch in enumerate(line):
                if ch != '1' and ch != '0':
                    temp = list(line)
                    temp[chnum] = '0'
                    line = "".join(temp)
                    map[lnum] = line

        return map

    def turn_neighboring_cells(self, map, x, y, areaNumber):
        count = 1 #At least this cell is turned
        temp = list(map[x])
        if areaNumber > 102:
            raise polisherException("102 is the maximum for area numbers beacuse I ran out of unicode characters!")
        temp[y] = space_identifiers[areaNumber]
        map[x] = "".join(temp)
        if x != 0:
            if map[x - 1][y] == '0':
                temp, _ = self.turn_neighboring_cells(map, x - 1, y, areaNumber)
                count += temp
        if x != len(map)-1:
            if map[x + 1][y] == '0':
                temp, _ = self.turn_neighboring_cells(map, x + 1, y, areaNumber)
                count += temp
        if y != len(map[x])-1:
            if map[x][y + 1] == '0':
                temp, _ = self.turn_neighboring_cells(map, x, y + 1, areaNumber)
                count += temp
        if y != 0:
            if map[x][y - 1] == '0':
                temp, _ = self.turn_neighboring_cells(map, x, y - 1, areaNumber)
                count += temp

        return count, map

    def wallify(self, map, connected_fses):
        big_chunk = max(connected_fses.values())
        for (k,v) in connected_fses.items():
            if v == big_chunk:
                big_chunk = k
        big_chunk_enum = space_identifiers[big_chunk]
        for ln, line in enumerate(map):
            foo = list(line)
            for chn, ch in enumerate(foo):
                if ch != big_chunk_enum:
                    foo[chn] = '1'
            map[ln] = "".join(foo)
        return map


    def perform(self):
        
        #while self.connected_spaces[max(self.connected_spaces, key=self.connected_spaces.get)] < ((self.minArea/100)*self.ca.limit*self.ca.size):
       
        while max(self.connected_spaces.values()) < ((self.minArea/100)*self.ca.limit*self.ca.size):
            if len(self.connected_spaces) == 1:
                raise polisherException("Cannot generate map with that percentage of area!")
                
            self.map_enumed = self.iterate_on_distance_matrix(self.create_distance_matrix(self.connected_spaces, self.map_enumed), self.connected_spaces, self.map_enumed)
            self.map_1 = self.reset_map(self.map_enumed)
            self.whole_space = self.get_full_fs(self.map_1)
            self.connected_spaces, self.map_enumed = self.get_connected_fses(self.map_1)


        a, b = self.get_connected_fses(self.reset_map(self.map_enumed))
        return self.reset_map (self.wallify (self.map_enumed, a))


class dummyPolisher(polisher):
    def __init__(self, ca=cellularAutomata.bl_tr_odd_p_mid_nybble_switch_srca(), minimumArea=60):
        self.minArea = minimumArea
        self.ca = ca
        self.map_1 = self.ca.perform()
        self.whole_space = self.get_full_fs(self.map_1)
        self.connected_spaces, self.map_enumed = self.get_connected_fses(self.map_1)

    def perform(self):
        a, b = self.get_connected_fses(self.reset_map(self.map_enumed))
        return self.reset_map (self.wallify (self.map_enumed, a))

def map_print(map):
    print("")
    for line in map:
        print(cellularAutomata.formatline(line))

if __name__ == "__main__":
    p = polisher()
    map_print(p.perform())
