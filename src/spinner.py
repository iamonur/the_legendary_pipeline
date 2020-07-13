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
//Game-4: Solve the maze.
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
promela_header_for_game_2 = """
typedef row{{
  byte a[{}];
}}
bit win = 0;
bit dead = 0;
bit turn = 0;
bit lock = 0;
row map[{}];
"""
promela_header_for_game_2_smart = """
typedef row{{
   byte a[{}];
}}
bit win = 0;
bit dead = 0;
bit turn = 0;
bit lock = 0;
c_code{{\#include "../spin/bfs.c"}};
row map[{}];
int next_x;
int next_y;
"""
promela_header_for_game_4 = """
typedef row{{
  byte a[{}]
}}
bit win = 0;
row map[{}];
"""
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
typedef row{{ //This is for creating 2-D arrays, since they are not supported.
    byte a[{0}];
}}

bit win  = 0;
bit dead = 0;
bit turn = 0;
bit lock = 0;
row map[{1}]; //This is your 2-D array.
"""
promela_avatar_game_4 = """
proctype avatar_mazesolver(int x; int y){
    map[x].a[y] = 2;
    byte w, a, s, d;
    bit foo;

    do
    ::(win == 0) ->
        w = map[x].a[y-1];
        a = map[x-1].a[y];
        s = map[x].a[y+1];
        d = map[x+1].a[y];

        if
        :: w != 1 -> printf("Avatar - W\\n");

            if
            :: w == 0 ->
                map[x].a[y] = 0;
                map[x].a[y-1] = 2;
                y = y - 1
            :: w == 3 ->
                win = 1
            fi;
        :: a != 1 -> printf("Avatar - A\\n");
            
            if
            :: a == 0 ->
                map[x].a[y] = 0;
                map[x-1].a[y] = 2;
                x = x - 1
            :: a == 3 ->
                win = 1
            fi;

        :: s != 1 -> printf("Avatar - S\\n");

            if
            :: s == 0 ->
                map[x].a[y] = 0;
                map[x].a[y+1]=2;
                y = y + 1
            :: s == 3 ->
                win = 1
            fi;

        :: d != 1 -> printf("Avatar - D\\n");

            if
            :: d == 0 ->
                map[x].a[y] = 0;
                map[x+1].a[y] = 2;
                x = x + 1
            :: d == 3 ->
                win = 1
            fi

        //Normally, there would be a skip option. But not now.
        fi
    :: else -> break
    od;
    printf("Avatar - Win\\n")
}
"""
promela_avatar_game_2_smart = """
proctype avatar_chaser(int x; int y){
   map[x].a[y] = 2;
   byte w,a,s,d;
   do
   :: ((win == 0) && (dead == 0))->
       //c_code{printf("0\\n");};
       lock;
      
       if
       :: dead == 1 -> break
       :: else -> skip
       fi;
 
       w = map[x].a[y-1];
       a = map[x-1].a[y];
       s = map[x].a[y+1];
       d = map[x+1].a[y];
 
       if
       :: ((w != 1) && (w != 3)) -> c_code{printf("Avatar - W\\n");};
 
           if
           :: w == 0 ->
               map[x].a[y] = 0;
               map[x].a[y-1] = 2;
               y = y - 1
           :: w == 4 ->
               win = 1
           fi
 
       :: ((a != 1) && (a != 3)) -> c_code{printf("Avatar - A\\n");};
 
           if
           :: a == 0 ->
               map[x].a[y] = 0;
               map[x-1].a[y] = 2;
               x = x - 1
           :: a == 4 ->
               win = 1
           fi
 
       :: ((s != 1) && (s != 3)) -> c_code{printf("Avatar - S\\n");};
 
           if
           :: s == 0 ->
               map[x].a[y] = 0;
               map[x].a[y+1] = 2;
               y = y + 1
           :: s == 4 ->
               win = 1
           fi
 
       :: ((d != 1) && (d != 3)) -> c_code{printf("Avatar - D\\n");};
 
           if
           :: d == 0 ->
               map[x].a[y] = 0;
               map[x+1].a[y] = 2;
               x = x + 1
           :: d == 4 ->
               win = 1
           fi
 
       :: true -> skip
       fi;
       //c_code{printf("1\\n");};
       //c_code{map_print2();}
       lock = 0;
   :: else -> break
   od;
 
   if
   :: win == 1 -> c_code{printf("Avatar - Win\\n");};
   :: dead == 1 -> c_code{printf("Avatar - Dead\\n");};
   fi;
   lock = 0;
}

"""
promela_avatar_game_2 = """
proctype avatar_chaser(int x; int y){
  map[x].a[y] = 2;
  byte w, a, s, d;
  bit foo;
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
    :: ((w != 1) && (w != 3)) -> printf("Avatar - W\\n");

      if
      :: w == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x].a[y-1] = 2;
				y = y - 1
			:: w == 4 -> //Moved to the goal, we won zulul
				win = 1
			fi

    :: ((a != 1) && (a != 3)) -> printf("Avatar - A\\n");

			if
			:: a == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x-1].a[y] = 2;
				x = x - 1
			:: a == 4 -> //Moved to the goal, we won zulul
				win = 1
			fi

    :: ((s != 1) && (s != 3)) -> printf("Avatar - S\\n");

			if
			:: s == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x].a[y+1] = 2;
				y = y + 1
			:: s == 4 -> //Moved to the goal, we won zulul
				win = 1
			fi

    :: ((d != 1) && (d != 3)) -> printf("Avatar - D\\n");

			if
			:: d == 0 -> //Moved to an empty cell
        map[x].a[y] = 0;
				map[x+1].a[y] = 2;
				x = x + 1
			:: d == 4 -> //Moved to the goal, we won zulul
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
promela_opponent_for_game_4 = ""
promela_opponent_for_game_2_smart = """
proctype opponent_runner(int x; int y){
   map[x].a[y] = 4;
   int foo;
   c_code{put_map();};
 
   do
   :: (win == 0 && dead == 0) ->
       //c_code{printf("2\\n");};
       !lock;
      
       if
       :: win == 1 -> break
       :: else -> skip
       fi;
       //c_code{printf("3\\n");};
       c_code{calculate_next_move(Popponent_runner->x, Popponent_runner->y, &(now.next_x), &(now.next_y));};
       //c_code{printf("4\\n");};
       map[x].a[y] = 0;
       foo = map[next_x].a[next_y];
       map[next_x].a[next_y] = 4;
      
       x = next_x;
       y = next_y;
       if
       :: foo == 3 -> dead = 1; break
       :: foo == 2 -> win = 1; break
       :: else -> skip
       fi;
      
       lock = 1;
       //c_code{printf("5\\n");};
   :: else -> break
   od;
 
   if
   :: win == 1 -> c_code{printf("Opponent - Win\\n");}
   :: dead == 1 -> c_code{printf("Opponent - Dead\\n");}
   fi;
 
   lock = 1;
}

"""
promela_opponent_for_game_2 = """
proctype opponent_runner(int x; int y; int xx; int yy){ //Works on a global turn variable
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
promela_init_for_game_4 = """
init{{
    int i, ii;
    for (i : 0 .. {length}){{
      //Initialize walls.
        map[i].a[0] = 1;
        map[i].a[{width}] = 1;
    }}
    for (i : 0 .. {length}){{
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
    run avatar_mazesolver({avatar_y},{avatar_x});
}}
"""
promela_init_for_game_3 = """
init{{
    int i, ii;
    for (i : 0 .. {length}){{
      //Initialize walls.
        map[i].a[0] = 1;
        map[i].a[{width}] = 1;
    }}
    for (i : 0 .. {length}){{
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
    run avatar_same_goal({avatar_y},{avatar_x});
    run opponent_same_goal({opponent_y},{opponent_x},{portal_y},{portal_x});
}}
"""
promela_init_for_game_2 = """
init{{
    int i, ii;
    for (i : 0 .. {length}){{
      //Initialize walls.
        map[i].a[0] = 1;
        map[i].a[{width}] = 1;
    }}
    for (i : 0 .. {length}){{
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
    run avatar_chaser({avatar_y},{avatar_x});
    run opponent_runner({opponent_y},{opponent_x},{portal_y},{portal_x});
}}
"""
promela_init_for_game_2_smart = """
init{{
    int i, ii;
    for (i : 0 .. {length}){{
      //Initialize walls.
        map[i].a[0] = 1;
        map[i].a[{width}] = 1;
    }}
    for (i : 0 .. {length}){{
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
    run avatar_chaser({avatar_y},{avatar_x});
    run opponent_runner({opponent_y},{opponent_x});
}}
"""
promela_init_for_game_1 = """
init{{
    int i, ii;
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
promela_c_code_for_game_2_smart = """
#define FALSE 0
#define TRUE 1
#define WIDTH {width}
#define LENGTH {length}
 
#define IS_FLOOR 0
#define IS_WALL 1
#define IS_AVATAR 2
#define IS_PORTAL 3
#define IS_ENEMY 4
 
#define FLOOR -2
#define WALL -1
#define AVATAR -2
#define PORTAL 0
#define ENEMY -2
 
void map_print(int input[][WIDTH]){{
       int mpi, mpj;
       printf("\\n");
       for(mpi = 0; mpi < LENGTH; mpi++){{
 
               for(mpj = 0; mpj < WIDTH; mpj++){{
 
                       if(input[mpi][mpj] == -1) printf("1");
                       else if(input[mpi][mpj] == -2) printf("2");
 
                       else printf("%d",input[mpi][mpj]);
 
               }}
 
               printf("\\n");
       }}
}}
 
void map_print2(){{
   int mp2i, mp2j;
   for(mp2i = 0; mp2i < LENGTH; mp2i++){{
       for(mp2j = 0; mp2j < WIDTH; mp2j++){{
           printf("%d",now.map[mp2i].a[mp2j]);
       }}
       printf("\\n");
   }}
 
}}
 
 
int isComplete(int input[][WIDTH]){{
   int ici, icj, a = 0;//For traversal
   for(ici = 0; ici < LENGTH; ici++)
       for(icj = 0; icj < WIDTH; icj++){{
           if(input[ici][icj] == FLOOR)
               return FALSE;
       }}
   return TRUE;
}}
 
void mark(int input[][WIDTH]){{
   int mi, mj, a = 0;//For traversal
   while(isComplete(input) == FALSE){{
       for(mi = 0; mi < LENGTH; mi++){{
          
           for(mj = 0; mj < WIDTH; mj++){{
              
               if(input[mi][mj] == WALL)//shouldnt marked
                   continue;
 
               else if(input[mi][mj] >= 0){{//marked
                   if((input[mi - 1][mj] == FLOOR) || ((input[mi - 1][mj] > 0) && (input[mi][mj] < input[mi - 1][mj]))){{
                           input[mi - 1][mj] = input[mi][mj] + 1;
                   }}
                   if((input[mi + 1][mj] == FLOOR) || ((input[mi + 1][mj] > 0) && (input[mi][mj] < input[mi + 1][mj]))){{
                           input[mi + 1][mj] = input[mi][mj] + 1;
                   }}
                   if((input[mi][mj - 1] == FLOOR ) || ((input[mi][mj - 1] > 0) && (input[mi][mj] < input[mi][mj - 1]))){{
                           input[mi][mj - 1] = input[mi][mj] + 1;
                   }}
                   if((input[mi][mj + 1] == FLOOR)  || ((input[mi][mj + 1] > 0) && (input[mi][mj] < input[mi][mj + 1]))){{
                           input[mi][mj + 1] = input[mi][mj] + 1;
                   }}
                   
               }}
           }}
       }}
   }}
}}
 
void calculate_next_move(int x, int y, int* next_x, int* next_y){{
   *next_x = x;
   *next_y = y;
   int _map[LENGTH][WIDTH];
   int index, index2;//For traversal
   for(index = 0; index < LENGTH; index++)
       for(index2 = 0; index2 < WIDTH; index2++)
           switch(now.map[index].a[index2]){{
               case IS_FLOOR:
                   _map[index][index2] = FLOOR;
                   break;
               case IS_WALL:
                   _map[index][index2] = WALL;
                   break;
               case IS_AVATAR:
                   _map[index][index2] = AVATAR;
                   break;
               case IS_PORTAL:
                   _map[index][index2] = PORTAL;
                   break;
               case IS_ENEMY:
                   _map[index][index2] = ENEMY;
                   break;
           }}
           
   mark(_map);
  
   if (_map[x-1][y] < _map[x][y] && _map[x-1][y] != -1){{
       *next_y = y;
       *next_x = x-1;
   }}
   else if(_map[x+1][y] < _map[x][y] && _map[x+1][y] != -1){{
       *next_y = y;
       *next_x = x+1;
   }}
   else if(_map[x][y-1] < _map[x][y] && _map[x][y-1] != -1){{
       *next_y = y-1;
       *next_x = x;
   }}
   else if(_map[x][y+1] < _map[x][y] && _map[x][y+1] != -1){{
       *next_y = y+1;
       *next_x = x;
   }}
   printf("%d, %d\\n", *next_x, *next_y);
   return;
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
        self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01, 
			promela_comment_02, 
			formatted_header, 
			promela_avatar_for_game_1, 
			promela_opponent_for_game_1, 
			formatted_init, 
			promela_ltl_formula_basic
		)

    def perform(self):
        self.create_spin()
        os.system("mkdir ../spin >/dev/null 2>&1")
        os.system("rm ../spin/temp.pml > /dev/null")
        f = open("../spin/temp.pml", "a")
        f.write(self.promela_whole_file)
        f.close()
        os.system("spin -a ../spin/temp.pml")
        proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out != b'':
            raise spinCompileException("Cannot compile with gcc.")
        os.system("../spin/temp.out -a -I >/dev/null")

class SpinClass_Game3():

	#self.map = map fed to instance
    #self.width = width of the map
    #self.length = length of the map
    #self.fixed_map = map changed to vgdl compliancy
    #self.avatar_location = (y,x) location of the avatar
    #self.enemy_location = (y,x) location of the enemy
    #self.portal_location = (y,x) location of the enemy
    #self.map_to_feed = Map with outer walls.

  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])#Assuming a rectangle
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

    formatted_init = promela_init_for_game_3.format(
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
            wall_str = self.wall_string
		)
    formatted_header = promela_header_for_game_3.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_3,
			promela_opponent_for_game_3,
			formatted_init,
			promela_ltl_formula_basic
		)

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")
    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a -I >/dev/null")

class SpinClass_Game4():

	#self.map = map fed to instance
    #self.width = width of the map
    #self.length = length of the map
    #self.fixed_map = map changed to vgdl compliancy
    #self.avatar_location = (y,x) location of the avatar
    #self.enemy_location = (y,x) location of the enemy
    #self.portal_location = (y,x) location of the enemy
    #self.map_to_feed = Map with outer walls.

  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])#Assuming a rectangle
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

    if checklist != 2:
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

    formatted_init = promela_init_for_game_4.format(
			avatar_y = self.avatar_location[0]+1,
			avatar_x = self.avatar_location[1]+1,
			portal_y = self.portal_location[0]+1,
      portal_x = self.portal_location[1]+1,
      length = self.length+1,
      length2 = self.length,
      width = self.width+1,
      width2 = self.width,
      wall_str = self.wall_string
		)
    formatted_header = promela_header_for_game_3.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_4,
			promela_opponent_for_game_4,
			formatted_init,
			promela_ltl_formula_basic
		)

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")
    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a -I >/dev/null")

class SpinClass_Game2():

	#self.map = map fed to instance
    #self.width = width of the map
    #self.length = length of the map
    #self.fixed_map = map changed to vgdl compliancy
    #self.avatar_location = (y,x) location of the avatar
    #self.enemy_location = (y,x) location of the enemy
    #self.portal_location = (y,x) location of the enemy
    #self.map_to_feed = Map with outer walls.

  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])#Assuming a rectangle
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

    formatted_init = promela_init_for_game_2.format(
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
            wall_str = self.wall_string
		)
    formatted_header = promela_header_for_game_2.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_2,
			promela_opponent_for_game_2,
			formatted_init,
			promela_ltl_formula_basic
		)

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")
    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out  -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a -I >/dev/null")

class SpinClass_Game2_smart():
  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])
    self.fixed_map = None
    self.list_walls = []
    self.promela_whole_file = """{}\n{}\n{}\n{}\n{}\n{}\n{}"""
    self.wall_string = "{}"
    self.c_code = "{}"

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

    formatted_init = promela_init_for_game_2_smart.format(
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
            wall_str = self.wall_string
		)
    formatted_header = promela_header_for_game_2_smart.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_2_smart,
			promela_opponent_for_game_2_smart,
			formatted_init,
			promela_ltl_formula_basic
		)

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")

    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    
    #os.system("rm ../spin/bfs.c > /dev/null")
    #f = open("../spin/bfs.c", "a")
    #f.write(promela_c_code_for_game_2_smart.format(width=self.width+2, length=self.length+2))
    #f.close()

    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a >/dev/null") #It's already nearly impossible to win this.

class SpinClass_Game3_smart():### XXX: NOT DONE YET.
  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])#Assuming a rectangle
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

    formatted_init = promela_init_for_game_3.format(
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
            wall_str = self.wall_string
		)
    formatted_header = promela_header_for_game_3.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_3,
			promela_opponent_for_game_3,
			formatted_init,
			promela_ltl_formula_basic
		)

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")
    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc -std=c99 pan.c -DREACH -o ../spin/temp.out  -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a -I >/dev/null")

class SpinClass_Game4_smart():### XXX: NOT DONE YET.
  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])#Assuming a rectangle
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

    if checklist != 2:
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

    formatted_init = promela_init_for_game_4.format(
			avatar_y = self.avatar_location[0]+1,
			avatar_x = self.avatar_location[1]+1,
			portal_y = self.portal_location[0]+1,
      portal_x = self.portal_location[1]+1,
      length = self.length+1,
      length2 = self.length,
      width = self.width+1,
      width2 = self.width,
      wall_str = self.wall_string
		)
    formatted_header = promela_header_for_game_3.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_4,
			promela_opponent_for_game_4,
			formatted_init,
			promela_ltl_formula_basic
		)

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")
    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a -I >/dev/null")

class SpinClass_smart(): ### XXX: NOT DONE YET.
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
        self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01, 
			promela_comment_02, 
			formatted_header, 
			promela_avatar_for_game_1, 
			promela_opponent_for_game_1, 
			formatted_init, 
			promela_ltl_formula_basic
		)

    def perform(self):
        self.create_spin()
        os.system("mkdir ../spin >/dev/null 2>&1")
        os.system("rm ../spin/temp.pml > /dev/null")
        f = open("../spin/temp.pml", "a")
        f.write(self.promela_whole_file)
        f.close()
        os.system("spin -a ../spin/temp.pml")
        proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out != b'':
            raise spinCompileException("Cannot compile with gcc.")
        os.system("../spin/temp.out -a -I >/dev/null")

if __name__ == "__main__":

  import cellularAutomata, caPolisher, spritePlanner
  ca = cellularAutomata.elementary_cellular_automata(ruleset=30, start="010101010011001100011100")
  cap = caPolisher.CApolisher(ca = ca)
  sp = spritePlanner.dualSpritePlanner(cap.perform())
  sp.perform()
  sa = SpinClass_Game4(sp.getMap())
  sa.perform()