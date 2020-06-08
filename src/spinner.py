import os
import subprocess
import copy

class spinCompileException(Exception):
  pass

class MCTS_Exception(Exception):
  pass

promela_comment_01 = """
//Game-1: Escape from opponent to the portal
//Game-2: Catch the opponent before it gets into the portal.
//Game-3: Race the opponent to the portal.
//'.' -> Floor
//'W' -> Wall
//'A' -> Avatar
//'E' -> End Portal
//'O' -> Opponent
"""
promela_comment_02 = """
//The level as enumeration
//0 -> Floor
//1 -> Wall
//2 -> Avatar
//3 -> End Portal
//4 -> Opponent
"""

# 0 -> width of the map
# 1 -> height of the map
promela_header_for_game_1 = """
typedef row{{ //This is for creating 2-D arrays, since they are not supported.
    byte a[{}];
}}

bit win  = 0;
bit dead = 0;
row map[{}]; //This is your 2-D array.

chan avatar_turn = [0] of {{bit}}; //randez-vous at (start of avatar, end of opponent). 0: avatar is dead.
chan opponent_turn = [0] of {{byte, byte}}; //the opposite randez-vous. Avatar's location is server with channel.
chan opponent_turn2 = [0] of {{bit}};
""" # TODO: Check if I'm using the opponent_turn2.
# 0 -> width of the map
# 1 -> height of the map
promela_header_for_game_3 = """
typedef row{ //This is for creating 2-D arrays, since they are not supported.
    byte a[{0}];
}

bit win  = 0;
bit dead = 0;
bit turn = 0;
bit lock = 0;
row map[{1}]; //This is your 2-D array.
"""

promela_avatar_game_3 = """
proctype avatar_same_goal(int x; int y){
  map[x].a[y] = 2;
  byte w, a, s, d;
  bit foo;
  //bool start = true;
  do
  ::((win == 0) && (dead == 0)) ->

    lock;

		if
		:: dead == 1 -> break //Dude cannot win on opponent's turn anyways.
    :: else -> skip
		fi;
    //Look-up:
    w = map[x].a[y-1];
    a = map[x-1].a[y];
    s = map[x].a[y+1];
    d = map[x+1].a[y];

    if
    :: ((w != 1) && (w != 4)) -> printf("Avatar - W\\n");

      if
      :: w == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x].a[y-1] = 2;
				y = y - 1
			:: w == 3 -> //Moved to the goal, we won zulul
				win = 1
			fi

    :: ((a != 1) && (a != 4)) -> printf("Avatar - A\\n");

			if
			:: a == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x-1].a[y] = 2;
				x = x - 1
			:: a == 3 -> //Moved to the goal, we won zulul
				win = 1
			fi

    :: ((s != 1) && (s != 4)) -> printf("Avatar - S\\n");

			if
			:: s == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x].a[y+1] = 2;
				y = y + 1
			:: s == 3 -> //Moved to the goal, we won zulul
				win = 1
			fi

    :: ((d != 1) && (d != 4)) -> printf("Avatar - D\\n");

			if
			:: d == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x+1].a[y] = 2;
				x = x + 1
			:: d == 3 -> //Moved to the goal, we won zulul
				win = 1
			fi

		:: true -> skip
    fi;
		lock = 0;
  :: else ->	break
  od;
  //In game of thrones, you either win or die
	if
	:: (win == 1) -> printf("Avatar - Win\\n");
	:: (dead == 1) -> printf("Avatar - Dead\\n");
	fi;
  lock = 0
}
"""
promela_avatar_for_game_1 = """
proctype avatar(int x; int y){
  map[x].a[y] = 2;
  byte w, a, s, d;
  bit foo;
  //bool start = true;
  do
  ::((win == 0) && (dead == 0)) ->
    /*if
    :: start ->
      foo = 1;
    :: else ->
      avatar_turn ? <foo>; //empty the channel to make next randez-vous possible
      start = false;
    fi;*/

    avatar_turn ? foo

		if
		:: foo == 0 -> //OMG THEY KILLED KENNY! USTEDES BASTARDOS!
			dead = 1;
			break
    :: else -> skip
		fi
    //Look-up:
    w = map[x].a[y-1];
    a = map[x-1].a[y];
    s = map[x].a[y+1];
    d = map[x+1].a[y];

    if
    :: w != 1 -> printf("Avatar - W\\n");

      if
      :: w == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x].a[y-1] = 2;
				y = y - 1
			:: w == 3 -> //Moved to the goal, we won zulul
				win = 1
			:: w == 4 -> //You killed yourself boy
				dead = 1
			fi

    :: a != 1 -> printf("Avatar - A\\n");

			if
			:: a == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x-1].a[y] = 2;
				x = x - 1
			:: a == 3 -> //Moved to the goal, we won zulul
				win = 1
			:: a == 4 -> //You killed yourself boy
				dead = 1
			fi

    :: s != 1 -> printf("Avatar - S\\n");

			if
			:: s == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x].a[y+1] = 2;
				y = y + 1
			:: s == 3 -> //Moved to the goal, we won zulul
				win = 1
			:: s == 4 -> //You killed yourself boy
				dead = 1
			fi

    :: d != 1 -> printf("Avatar - D\\n");

			if
			:: d == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x+1].a[y] = 2;
				x = x + 1
			:: d == 3 -> //Moved to the goal, we won zulul
				win = 1
			:: d == 4 -> //You killed yourself boy
				dead = 1
			fi

		:: true -> skip
    fi

    if
    :: (win || dead) ->
      opponent_turn2!0;
    :: else ->
      opponent_turn2!1;
      opponent_turn!x,y
    fi
		//TODO: Send coordinates & condition no matter what you do.
  :: else ->	break
  od;

	if
	:: (win == 1) -> printf("Avatar - Win\\n");
		//TODO: Send that you win - Dude, this is not cool, this is a randezvous point. not cool at all. JUST NO.
	:: (dead == 1) -> printf("Avatar - Dead\\n");
		//TODO: Send that you lost
	fi
}
"""

promela_opponent_for_game_3 = """
proctype opponent_same_goal(int x; int y; int xx; int yy){ //Works on a global turn variable
  map[x].a[y] = 4;
  byte w, a, s, d;

  do

  ::((win == 0) && (dead == 0)) -> //Play on

    !lock;

    if
    :: win == 1 -> break; //Dude cannot lost on its turn.
    :: else -> skip
    fi

    w = map[x].a[y-1];
    a = map[x-1].a[y];
    s = map[x].a[y+1];
    d = map[x+1].a[y];

    if

    :: (y > yy) ->
        if
        :: (w != 1) && (w != 2) ->
            printf("Opponent - W\\n");
            map[x].a[y] = 0;
            y = y - 1;
            map[x].a[y] = 4
        :: else -> skip
        fi;

    :: else ->

        if

        :: (x > xx) ->
            if
            :: (a != 1) && (a != 2) ->
                printf("Opponent - A\\n");
                map[x].a[y] = 0;
                x = x - 1;
                map[x].a[y] = 4
            :: else -> skip
            fi;

        :: else ->
            if
            :: (y < yy) ->
                if
                :: (s != 1) && (s != 2) ->
                    printf("Opponent - S\\n");
                    map[x].a[y] = 0;
                    y = y + 1;
                    map[x].a[y] = 4
                :: else -> skip
                fi;
            :: else ->

                if

                :: (x < xx) ->
                    if
                    ::  (d != 1) && (d != 2) ->
                        printf("Opponent - D\\n");
                        map[x].a[y] = 0;
                        x = x + 1;
                        map[x].a[y] = 4
                    :: else -> skip
                    fi;

                :: else -> skip

                fi;

            fi;

        fi;

    fi;
    //Movement ended here. Check if you win.

    if

    :: ((x == xx) && (y == yy)) -> //Stomped on it dude. No need to play anymore.

      dead = 1;
      break

    :: else -> //Avatar survived.

      skip

    fi;

    lock = 1;

  :: else -> break

  od;

  if

  :: win == 1 ->

    printf("Opponent - Win\\n")

  :: dead == 1 ->

    printf("Opponent - Dead\\n")

  fi

  lock = 1
}
"""

promela_opponent_for_game_1 = """
proctype opponent(int x; int y){
  //This is by the way, a sh*tty implementation. I know.
  //TODO: Fix this bs.
	map[x].a[y] = 4;
	int xx, yy;
  byte w, a, s, d;
	bit send;
	do
  ::((win == 0) && (dead == 0)) -> //Play on
    opponent_turn2?send;
    if
    :: send == 0 -> break; //Game ended.
    :: else -> skip
    fi
    opponent_turn ? xx, yy; //Wait your turn here

    //Then move!
    //Lookup!
    w = map[x].a[y-1];
    a = map[x-1].a[y];
    s = map[x].a[y+1];
    d = map[x+1].a[y];

    //try moving close to it, do not consider walls etc.
    //default operation: noop

    if
    :: (y > yy) ->
        if
        :: (w != 1) && (w != 3) ->
            printf("Opponent - W\\n");
            map[x].a[y] = 0;
            y = y - 1;
            map[x].a[y] = 4
        :: else -> skip
        fi;

    :: else ->

        if

        :: (x > xx) ->
            if
            :: (a != 1) && (a != 3) ->
                printf("Opponent - A\\n");
                map[x].a[y] = 0;
                x = x - 1;
                map[x].a[y] = 4
            :: else -> skip
            fi;

        :: else ->
            if
            :: (y < yy) ->
                if
                :: (s != 1) && (s != 3) ->
                    printf("Opponent - S\\n");
                    map[x].a[y] = 0;
                    y = y + 1;
                    map[x].a[y] = 4
                :: else -> skip
                fi;
            :: else ->

                if

                :: (x < xx) ->
                    if
                    ::  (d != 1) && (d != 3) ->
                        printf("Opponent - D\\n");
                        map[x].a[y] = 0;
                        x = x + 1;
                        map[x].a[y] = 4
                    :: else -> skip
                    fi;

                :: else -> skip

                fi;

            fi;

        fi;

    fi;

    if
    :: ((x == xx) && (y == yy)) -> //Stomped on it dude. No need to play anymore.
      dead = 1;
      avatar_turn!0;
      break
    :: else -> //Avatar survived.
      avatar_turn!1;
    fi;
  :: else -> break
	od;

  if
  :: win == 1 ->
    printf("Opponent - Win\\n")
  :: dead == 1 ->
    printf("Opponent - Dead\\n")
  fi

}
"""

promela_ltl_formula_basic = """
// LTL Formula : In any time, win never be true.
// Counter-Example will be generated -> A scenario to win.
ltl  { [] !win };
"""

promela_init_for_game_3 = """
init{{
    int i, ii;
    for (i : 0 .. {}) {{
        // Initialize walls
        map[{}].a[i] = 1;
        map[0].a[i] = 1;
        map[i].a[0] = 1;
        map[i].a[{}] = 1;
    }}
    for (i : 1 .. {}) {{
        for (ii : 1 .. {}) {{
            // Initialize floors
            map[i].a[ii] = 0;
        }}
    }}
    //Generic placement of walls
    {}
    //Place portal
    map[{}].a[{}] = 3;
    run avatar_same_goal({},{});
    run opponent_same_goal({},{},{},{});

}}
"""

promela_init_for_game_1 = """
init{{
    byte i, ii;
    for (i : 0 .. {length}) {{
        // Initialize walls

        map[i].a[0] = 1;
        map[i].a[{width}] = 1;
    }}
    for (i : 0 .. {width}){{
        map[0].a[i] = 1;
        map[{length}].a[i] = 1;
    }}

    for (i : 1 .. {length2}) {{
        for (ii : 1 .. {width2}) {{
            // Initialize floors
            map[i].a[ii] = 0;
        }}
    }}
    //Generic placement of walls
    {wall_str}
    //Place portal
    map[{portal_y}].a[{portal_x}] = 3;
    run avatar({avatar_y},{avatar_x});
    run opponent({opponent_y},{opponent_x});

    opponent_turn2!1;
    opponent_turn!{avatar_y},{avatar_x}

	//avatar_turn!1
}}
"""

class SpinClass:

    #self.map = map fed to instance
    #self.width = width of the map
    #self.length = length of the map
    #self.fixed_map = map changed to vgdl compliancy
    #self.avatar_location = (y,x) location of the avatar
    #self.enemy_location = (y,x) location of the enemy
    #self.portal_location = (y,x) location of the enemy
    #self.map_to_feed = Map with outer walls.
    #gameType 1 is supported for now, more will come in this module.

    def __init__(self, map):
        self.map = map
        self.width = len(map[0])
        self.length = len(map)
        self.fixed_map = None
        self.list_walls = []
        self.promela_whole_file = """{}\n{}\n{}\n{}\n{}\n{}\n{}"""
        self.wall_string = "{}"

    def fix_map(self):
        temp_map = []

        for line in self.map:
            temp_map.append(list(line))

        checklist = 0

        for lineNum, line in enumerate(temp_map):
            for chNum, ch in enumerate(line):
                if ch == '0':
                    temp_map[lineNum][chNum] = '.'
                elif ch == '1':
                    temp_map[lineNum][chNum] = 'w'
                    self.list_walls.append((lineNum + 1, chNum + 1))
                elif ch == 'A':
                    self.avatar_location = (lineNum, chNum)
                    checklist += 1
                elif ch == 'G':
                    self.portal_location = (lineNum, chNum)
                    checklist += 1
                elif ch == 'E':
                    self.enemy_location  = (lineNum, chNum)
                    checklist += 1

        if checklist != 3:
          raise spinCompileException("Inproper placement of sprites!")


        self.fixed_map = []

        to_attach = ""
        to_attach_list = []
        for i in range(0, self.width + 2):
            to_attach_list.append('w')

        to_attach = to_attach.join(to_attach_list)

        for ln, line in enumerate(temp_map):
            temp = ''.join(line)
            temp = 'w' + temp + 'w'
            self.fixed_map.append(temp)

        self.fixed_map.insert(0, to_attach)
        self.fixed_map.append(to_attach)

    def create_wall_string(self):
        for wall in self.list_walls:
            self.wall_string = self.wall_string.format("\tmap[{}].a[{}] = 1;\n{}".format(wall[0], wall[1], "{}"))
        self.wall_string = self.wall_string.format(" ")


    def create_spin(self):
        if self.fixed_map is None:
            self.fix_map()
        self.create_wall_string()
        
        formatted_init = promela_init_for_game_1.format(
            avatar_y = self.avatar_location[0]+1,
            avatar_x = self.avatar_location[1]+1,
            portal_y = self.portal_location[0]+1,
            portal_x = self.portal_location[1]+1,
            opponent_y = self.enemy_location[0]+1,
            opponent_x = self.enemy_location[1]+1,
            length = self.length+1,
            length2 = self.length,
            width = self.width+1,
            width2 = self.width,
            wall_str = self.wall_string)
        formatted_header = promela_header_for_game_1.format(self.length + 2, self.width + 2)
        self.promela_whole_file = self.promela_whole_file.format(promela_comment_01, promela_comment_02, formatted_header, promela_avatar_for_game_1, promela_opponent_for_game_1, formatted_init, promela_ltl_formula_basic)

    def perform(self):
        self.create_spin()
        os.system("mkdir ../spin >/dev/null 2>&1")
        os.system("rm ../spin/temp.pml > /dev/null")
        f = open("../spin/temp.pml", "a")
        f.write(self.promela_whole_file)
        f.close()
        os.system("spin -a ../spin/temp.pml")
        proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out != b'':
            raise spinCompileException("Cannot compile with gcc.")
        os.system("../spin/temp.out -a -I >/dev/null")

class MCTSNode:
  def __init__(self, map, parent):
    #caPolisher.map_print(map)
    self.leftChild = None
    self.rightChild = None
    self.upChild = None
    self.downChild = None
    self.skipChild = None
    self.map = map
    self.myHash = self.hashMap()
    self.isEnd = False
    self.avatar_nearbySprites = {}
    self.avatar_pos = (-1,-1)
    self.opponent_nearbySprites = {}
    self.opponent_pos = (-1,-1)
    self.portal_pos = (-1,-1)
    self.graspMap_opponent()
    self.respectiveOpponentMove()#Remember that the first to move is the opponent.
    self.graspMap_avatar()

  def graspMap_opponent(self):

    for lineNum, line in enumerate(self.map):

      for charNum, char in enumerate(line):
        if char == 'A':
          self.avatar_pos = (lineNum, charNum)

        if char == 'E':
          self.opponent_pos = (lineNum, charNum)
          #NORTH
          if lineNum == 0:
            self.opponent_nearbySprites['North'] = 'Wall'
          elif self.map[lineNum - 1][charNum] == '1':
            self.opponent_nearbySprites['North'] = 'Wall'
          elif self.map[lineNum - 1][charNum] == 'A':
            self.opponent_nearbySprites['North'] = 'Enemy'
          elif self.map[lineNum - 1][charNum] == 'G':
            self.opponent_nearbySprites['North'] = 'Portal'
          elif self.map[lineNum - 1][charNum] == '0':
            self.opponent_nearbySprites['North'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")
          #SOUTH
          if lineNum == len(self.map)-1:
            self.opponent_nearbySprites['South'] = 'Wall'
          elif self.map[lineNum + 1][charNum] == '1':
            self.opponent_nearbySprites['South'] = 'Wall'
          elif self.map[lineNum + 1][charNum] == 'A':
            self.opponent_nearbySprites['South'] = 'Enemy'
          elif self.map[lineNum + 1][charNum] == 'G':
            self.opponent_nearbySprites['South'] = 'Portal'
          elif self.map[lineNum + 1][charNum] == '0':
            self.opponent_nearbySprites['South'] = 'Floor'
          else:
            #caPolisher.map_print(self.map)
            raise MCTS_Exception("Unknown sprite in map!")
          #WEST
          if charNum == 0:
            self.opponent_nearbySprites['West'] = 'Wall'
          elif self.map[lineNum][charNum - 1] == '1':
            self.opponent_nearbySprites['West'] = 'Wall'
          elif self.map[lineNum][charNum - 1] == 'A':
            self.opponent_nearbySprites['West'] = 'Enemy'
          elif self.map[lineNum][charNum - 1] == 'G':
            self.opponent_nearbySprites['West'] = 'Portal'
          elif self.map[lineNum][charNum - 1] == '0':
            self.opponent_nearbySprites['West'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")
          #EAST
          if charNum == len(self.map[0])-1:
            self.opponent_nearbySprites['East'] = 'Wall'
          elif self.map[lineNum][charNum + 1] == '1':
            self.opponent_nearbySprites['East'] = 'Wall'
          elif self.map[lineNum][charNum + 1] == 'A':
            self.opponent_nearbySprites['East'] = 'Enemy'
          elif self.map[lineNum][charNum + 1] == 'G':
            self.opponent_nearbySprites['East'] = 'Portal'
          elif self.map[lineNum][charNum + 1] == '0':
            self.opponent_nearbySprites['East'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")

  def graspMap_avatar(self):
    for lineNum, line in enumerate(self.map):

      for charNum, char in enumerate(line):
        
        if char == 'A':
          self.avatar_pos = (lineNum, charNum)
          #NORTH
          if lineNum == 0:
            self.avatar_nearbySprites['North'] = 'Wall'
          elif self.map[lineNum - 1][charNum] == '1':
            self.avatar_nearbySprites['North'] = 'Wall'
          elif self.map[lineNum - 1][charNum] == 'E':
            self.avatar_nearbySprites['North'] = 'Enemy'
          elif self.map[lineNum - 1][charNum] == 'G':
            self.avatar_nearbySprites['North'] = 'Portal'
          elif self.map[lineNum - 1][charNum] == '0':
            self.avatar_nearbySprites['North'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")
          #SOUTH
          if lineNum == len(self.map)-1:
            self.avatar_nearbySprites['South'] = 'Wall'
          elif self.map[lineNum + 1][charNum] == '1':
            self.avatar_nearbySprites['South'] = 'Wall'
          elif self.map[lineNum + 1][charNum] == 'E':
            self.avatar_nearbySprites['South'] = 'Enemy'
          elif self.map[lineNum + 1][charNum] == 'G':
            self.avatar_nearbySprites['South'] = 'Portal'
          elif self.map[lineNum + 1][charNum] == '0':
            self.avatar_nearbySprites['South'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")
          #WEST
          if charNum == 0:
            self.avatar_nearbySprites['West'] = 'Wall'
          elif self.map[lineNum][charNum - 1] == '1':
            self.avatar_nearbySprites['West'] = 'Wall'
          elif self.map[lineNum][charNum - 1] == 'E':
            self.avatar_nearbySprites['West'] = 'Enemy'
          elif self.map[lineNum][charNum - 1] == 'G':
            self.avatar_nearbySprites['West'] = 'Portal'
          elif self.map[lineNum][charNum - 1] == '0':
            self.avatar_nearbySprites['West'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")
          #EAST
          if charNum == len(self.map[0])-1:
            self.avatar_nearbySprites['East'] = 'Wall'
          elif self.map[lineNum][charNum + 1] == '1':
            self.avatar_nearbySprites['East'] = 'Wall'
          elif self.map[lineNum][charNum + 1] == 'E':
            self.avatar_nearbySprites['East'] = 'Enemy'
          elif self.map[lineNum][charNum + 1] == 'G':
            self.avatar_nearbySprites['East'] = 'Portal'
          elif self.map[lineNum][charNum + 1] == '0':
            self.avatar_nearbySprites['East'] = 'Floor'
          else:
            raise MCTS_Exception("Unknown sprite in map!")

        if char == 'G':
          self.portal_pos = (lineNum, charNum)
          self.win = False

    if self.portal_pos == (-1,-1):
      self.isEnd = True
      self.win = True

    elif (self.avatar_pos == (-1,-1)) or (self.opponent_pos == (-1,-1)):
      #
      #caPolisher.map_print(self.map)
      print("Dude")
      #print(self.map)
      self.isEnd = True

  def serializeMap(self):
    ret = ""
    for line in self.map:
      ret += "".join(line)

    return ret
    
  def hashMap(self):
    return hash(self.serializeMap())

  def who(self):
    return self.myHash

  def pressLeft(self):
    #print("left")
    #Returns true if already won, false if already lost.
    #If cannot move to left, then skip your move.
    if self.isEnd:
      #print("l")
      return self.win
    if self.leftChild is not None: #Already done this.
      return self.leftChild
    if self.avatar_nearbySprites['West'] == 'Wall':
      self.leftChild = self.pressNothing()
      return self.leftChild
    #You need to move to left for sure.
    mapToPass = copy.deepcopy(self.map)
    

    temp = list(mapToPass[self.avatar_pos[0]])
    temp[self.avatar_pos[1]] = '0'
    mapToPass[self.avatar_pos[0]] = "".join(temp)

    temp = list(mapToPass[self.avatar_pos[0]])
    temp[self.avatar_pos[1] - 1] = 'A'
    mapToPass[self.avatar_pos[0]] = "".join(temp)

    
    self.leftChild = MCTSNode(mapToPass, self)
    return self.leftChild

  def pressRight(self):
    #print("right")
    #Returns true if already won, false if already lost.
    #If cannot move to right, then skip your move.
    if self.isEnd:
      #print("r")
      return self.win
    if self.rightChild is not None: #Already done this.
      return self.rightChild
    if self.avatar_nearbySprites['East'] == 'Wall':
      self.rightChild = self.pressNothing()
      return self.rightChild
    #You need to move to right for sure.
    mapToPass = copy.deepcopy(self.map)

    temp = list(mapToPass[self.avatar_pos[0]])
    temp[self.avatar_pos[1]] = '0'
    mapToPass[self.avatar_pos[0]] = "".join(temp)

    temp = list(mapToPass[self.avatar_pos[0]])
    temp[self.avatar_pos[1] + 1] = 'A'
    mapToPass[self.avatar_pos[0]] = "".join(temp)


    self.rightChild = MCTSNode(mapToPass, self)
    return self.rightChild
  
  def pressDown(self):
    #Returns true if already won, false if already lost.
    #If cannot move to down, then skip your move.
    #print("down")
    
    if self.isEnd:
      #print("d")
      return self.win
    if self.downChild is not None: #Already done this.
      return self.downChild
    if self.avatar_nearbySprites['South'] == 'Wall':
      self.downChild = self.pressNothing()
      return self.downChild
    #You need to move to down for sure.
    mapToPass = copy.deepcopy(self.map)

    temp = list(mapToPass[self.avatar_pos[0]])
    temp[self.avatar_pos[1]] = '0'
    mapToPass[self.avatar_pos[0]] = "".join(temp)

    temp = list(mapToPass[self.avatar_pos[0] + 1])
    temp[self.avatar_pos[1]] = 'A'
    mapToPass[self.avatar_pos[0] + 1] = "".join(temp)

    self.downChild = MCTSNode(mapToPass, self)
    return self.downChild
  
  def pressUp(self):
    #Returns true if already won, false if already lost.
    #If cannot move to down, then skip your move.
    #print("up")
    
    if self.isEnd:
      return self.win
    if self.upChild is not None: #Already done this.
      return self.upChild
    if self.avatar_nearbySprites['North'] == 'Wall':
      self.upChild = self.pressNothing()
      return self.upChild
    #You need to move to up for sure.
    mapToPass = copy.deepcopy(self.map)

    temp = list(mapToPass[self.avatar_pos[0]])
    temp[self.avatar_pos[1]] = '0'
    mapToPass[self.avatar_pos[0]] = "".join(temp)

    temp = list(mapToPass[self.avatar_pos[0] - 1])
    temp[self.avatar_pos[1]] = 'A'
    mapToPass[self.avatar_pos[0] - 1] = "".join(temp)
    
    self.upChild = MCTSNode(mapToPass, self)
    return self.upChild
  
  def pressNothing(self):
    #print("nothing")
    if self.isEnd:
      return self.win
    if self.skipChild is not None: #Already done this.
      return self.skipChild
    
    mapToPass = copy.deepcopy(self.map)
    self.skipChild = MCTSNode(mapToPass, self)
    return self.skipChild
  
  def respectiveOpponentMove(self):
    #Priority is W>A>S>D. But, the thing is broken at some point, thus S>D>W>A.
    #If cannot move to most prior, skips.
    #Cannot move on walls, portal. Can move on floor, avatar.
    #caPolisher.map_print(self.map)
    if self.avatar_pos[0] > self.opponent_pos[0]:  #S
      if self.opponent_nearbySprites['South'] == 'Enemy' or self.opponent_nearbySprites['South'] == 'Floor':
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)
        
        temp = list(self.opponent_pos)
        temp[0] += 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False

        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)

    elif self.avatar_pos[1] > self.opponent_pos[1]:#D
      if self.opponent_nearbySprites['East'] == 'Enemy' or self.opponent_nearbySprites['East'] == 'Floor':
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)

        temp = list(self.opponent_pos)
        temp[1] += 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False

        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)
        
    elif self.avatar_pos[0] < self.opponent_pos[0]:#W
      if self.opponent_nearbySprites['North'] == 'Enemy' or self.opponent_nearbySprites['North'] == 'Floor':
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)

        temp = list(self.opponent_pos)
        temp[0] -= 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False
        
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)
        
    elif self.avatar_pos[1] < self.opponent_pos[1]:#A
      if self.opponent_nearbySprites['West'] == 'Enemy' or self.opponent_nearbySprites['West'] == 'Floor':
        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = '0'
        self.map[self.opponent_pos[0]] = "".join(temp)

        temp = list(self.opponent_pos)
        temp[1] -= 1
        self.opponent_pos = tuple(temp)

        if self.map[self.opponent_pos[0]][self.opponent_pos[1]] == 'A':
          self.isEnd = True
          self.win = False

        temp = list(self.map[self.opponent_pos[0]])
        temp[self.opponent_pos[1]] = 'E'
        self.map[self.opponent_pos[0]] = "".join(temp)
       
    else: # Cannot happen
        raise MCTS_Exception('Opponent_move, something wrong!')

  def findChild(self, lookto):
    if self.leftChild != None:
      if self.leftChild.who() == lookto:
        return self.leftChild
    elif self.rightChild != None:
      if self.rightChild.who() == lookto:
        return self.rightChild
    elif self.upChild != None:
      if self.upChild.who() == lookto:
        return self.upChild
    elif self.downChild != None:
      if self.downChild.who() == lookto:
        return self.downChild
    elif self.skipChild != None:
      if self.skipChild.who() == lookto:
        return self.skipChild
    raise MCTS_Exception('Erroneous lookup!')

class MCTSClass_returns_first:
  def __init__(self, map):
    
    self.map = []
    for i in range(0,23):
      self.map.append(list())
    self.width = len(map[0])
    self.length = len(map)
    self.root = MCTSNode(map, None)
    self.moveStack = []
    self.hashPile = set()

  def perform(self):
    if self.checkChilderen(self.root):
      return self.moveStack
      
    return "Failed"

  def checkChilderen(self, activeNode):
    if type(activeNode) is (bool):
      return activeNode


    l = len(self.hashPile)
    self.hashPile.add(activeNode.who())
    ll = len(self.hashPile)
    
    if (l == ll):
      return False

    #print(self.moveStack)

    self.moveStack.append('A')
    if (self.checkChilderen(activeNode.pressLeft())):
      return True
    else:
      self.moveStack.pop()

    self.moveStack.append('D')
    if (self.checkChilderen(activeNode.pressRight())):
      return True
    else:
      self.moveStack.pop()

    self.moveStack.append('W')
    if (self.checkChilderen(activeNode.pressUp())):
      return True
    else:
      self.moveStack.pop()

    self.moveStack.append('S')
    if (self.checkChilderen(activeNode.pressDown())):
      return True
    else:
      self.moveStack.pop()

    self.moveStack.append('S')
    if (self.checkChilderen(activeNode.pressNothing())):
      return True
    else:
      self.moveStack.pop()

#class MCTSClass_returns_best:

#class MCTSClass_returns_minima:


if __name__ == "__main__":

  import cellularAutomata, caPolisher, spritePlanner
  ca = cellularAutomata.elementary_cellular_automata(ruleset=30, start="010101010011001100011100")
  cap = caPolisher.CApolisher(ca = ca)
  sp = spritePlanner.spritePlanner(cap.perform())
  sp.perform()
  m = MCTSClass_returns_first(sp.getMap())
  print(m.perform())