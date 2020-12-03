import os
import subprocess
import copy

class spinCompileException(Exception):
  pass

class MCTS_Exception(Exception):
  pass
promela_comment_01_sokoban = """
//Game:
//Push all boxes into all holes to win.
//After pushing a box into a hole, both will disappear.
//'.' -> Floor
//'W' -> Wall
//'A' -> Avatar
//'B' -> Box
//'H' -> Hole
"""
promela_comment_02_sokoban = """
//The level as enumeration
//0 -> Floor
//1 -> Wall
//2 -> Avatar
//3 -> Box
//4 -> Hole
"""
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
promela_header_for_sokoban = """
typedef row {{
  byte a[{}];
}}
byte remaining_goals = {};
bit win = 0;
bit lose = 0;
row map[{}];
"""
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
""" 
promela_header_for_game_1_smart = """
typedef row{{ //This is for creating 2-D arrays, since they are not supported.
    byte a[{}];
  }}
  c_code{{\#include "../spin/bfs.c"}};
  bit win  = 0;
  bit dead = 0;
  row map[{}]; //This is your 2-D array.

  int next_x;
  int next_y;
  chan avatar_turn = [0] of {{bit}}; //randez-vous at (start of avatar, end of opponent). 0: avatar is dead.
  chan opponent_turn = [0] of {{byte, byte}}; //the opposite randez-vous. Avatar's location is server with channel.
  chan opponent_turn2 = [0] of {{bit}};
"""
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
promela_header_for_game_3_smart = """
typedef row{{ //This is for creating 2-D arrays, since they are not supported.
    byte a[{0}];
  }}
  c_code{{\#include "../spin/bfs.c"}};
  bit win  = 0;
  bit dead = 0;
  bit turn = 0;
  bit lock = 0;
  row map[{1}]; //This is your 2-D array.

  int next_x;
  int next_y;
"""
promela_avatar_sokoban = """
proctype avatar_sokoban(int x; int y){
  map[x].a[y] = 2;
  byte w, a, s, d;

  do
  ::(win == 0) ->
    w = map[x].a[y-1];
    a = map[x-1].a[y];
    s = map[x].a[y+1];
    d = map[x+1].a[y];

    if
    :: (w != 1 && w != 4) -> //Cannot move into a wall or hole.
      printf("Avatar - W\\n");
      if
      :: w == 0 -> //Empty cell
        map[x].a[y] = 0;
        map[x].a[y - 1] = 2;
        y = y - 1
      :: w == 3 -> //Pusha-pusha
        if
        :: map[x].a[y - 2] == 1 -> //This is a wall, so stop pushing.
          skip
        :: map[x].a[y - 2] == 4 -> //This is a hole, so congrats on reducing the targets by one.
          map[x].a[y] = 0;
          map[x].a[y - 1] = 2;
          map[x].a[y - 2] = 0;
          remaining_goals = remaining_goals - 1;
          if
          :: remaining_goals == 0 -> win = 1
          :: else -> skip
          fi
        :: map[x].a[y - 2] == 0 -> //This is a floor, a valid push.
          map[x].a[y] = 0;
          map[x].a[y - 1] = 2;
          map[x].a[y - 2] = 3
        fi
      fi
    :: (a != 1 && a != 4) -> //Cannot move into a wall or hole.
      printf("Avatar - A\\n");
      if
      :: a == 0 -> //Empty cell
        map[x].a[y] = 0;
        map[x-1].a[y] = 2;
        x = x - 1
      :: a == 3 -> //Pusha-pusha
        if
        :: map[x - 2].a[y] == 1 ->
          skip
        :: map[x - 2].a[y] == 4 ->
          map[x].a[y] = 0;
          map[x - 1].a[y] = 2;
          map[x - 2].a[y] = 0;
          remaining_goals = remaining_goals - 1;
          if
          :: remaining_goals == 0 -> win = 1
          :: else -> skip
          fi
        :: map[x - 2].a[y] == 0 ->
          map[x].a[y] = 0;
          map[x - 1].a[y] = 2;
          map[x - 2].a[y] = 3
        fi
      fi
    :: (s != 1 && s != 4) -> //Cannot move into a wall or hole.
      printf("Avatar - S\\n");
      if
      :: s == 0 -> //Empty cell
        map[x].a[y] = 0;
        map[x].a[y+1] = 2;
        y = y + 1
      :: s == 3 -> //Pusha-pusha
        if
        :: map[x].a[y + 2] == 1 -> 
          skip
        :: map[x].a[y + 2] == 4 ->
          map[x].a[y] = 0;
          map[x].a[y + 1] = 2;
          map[x].a[y + 2] = 0;
          remaining_goals = remaining_goals - 1;
          if
          :: remaining_goals == 0 -> win = 1
          :: else -> skip
          fi
        :: map[x].a[y + 2] == 0 ->
          map[x].a[y] = 0;
          map[x].a[y + 1] = 2;
          map[x].a[y + 2] = 3
        fi
      fi
    :: (d != 1 && d != 4) -> //Cannot move into a wall or hole.
      printf("Avatar - D\\n");
      if
      :: d == 0 -> //Empty cell
        map[x].a[y] = 0;
        map[x + 1].a[y] = 2;
        x = x + 1
      :: d == 3 -> //Pusha-pusha
        if
        :: map[x + 2].a[y] == 1 ->
          skip
        :: map[x + 2].a[y] == 4 ->
          map[x].a[y] = 0;
          map[x + 1].a[y] = 2;
          map[x + 2].a[y] = 0;
          remaining_goals = remaining_goals - 1;
          if
          :: remaining_goals == 0 -> win = 1
          :: else -> skip
          fi
        :: map[x + 2].a[y] == 0 ->
          map[x].a[y] = 0;
          map[x + 1].a[y] = 2;
          map[x + 2].a[y] = 3
        fi
      fi
    //One of these should happen. Don't see why we need an else here.
    fi
  :: else -> break
  od;
  printf("Avatar - Win \\n")
}
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
 
       :: true -> c_code{printf("Avatar- Skip\\n");};//skip
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

		:: true -> c_code{printf("Avatar- Skip\\n");};//
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

		:: true -> c_code{printf("Avatar- Skip\\n");};//
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
promela_avatar_game_3_smart = """
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

		:: true -> c_code{printf("Avatar- Skip\\n");};//
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
promela_avatar_for_game_1_smart = """
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

		:: true -> c_code{printf("Avatar- Skip\\n");};//
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
 
   do
   :: (win == 0 && dead == 0) ->
       !lock;
      
       if
       :: win == 1 -> break
       :: else -> skip
       fi;
       
       c_code{calculate_next_move_to_portal(Popponent_runner->x, Popponent_runner->y, &(now.next_x), &(now.next_y));};

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
promela_opponent_for_game_3_smart = """
proctype opponent_same_goal(int x; int y; int xx; int yy){ //Works on a global turn variable
  map[x].a[y] = 4;
  int foo;
 
   do
   :: (win == 0 && dead == 0) ->
       !lock;
      
       if
       :: win == 1 -> break
       :: else -> skip
       fi;
       
       c_code{calculate_next_move_to_portal_avatar_blocks(Popponent_same_goal->x, Popponent_same_goal->y, &(now.next_x), &(now.next_y));};
       
       map[x].a[y] = 0;
       foo = map[next_x].a[next_y];
       map[next_x].a[next_y] = 4;
      
       x = next_x;
       y = next_y;
       if
       :: foo == 3 -> dead = 1; break
       :: else -> skip
       fi;
      
       lock = 1;
   :: else -> break
   od;
 
   if
   :: win == 1 -> c_code{printf("Opponent - Win\\n");}
   :: dead == 1 -> c_code{printf("Opponent - Dead\\n");}
   fi;
 
   lock = 1;
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
promela_opponent_for_game_1_smart = """
proctype opponent(int x; int y){
  //This is by the way, a sh*tty implementation. I know.
  //TODO: Fix this bs.
	map[x].a[y] = 4;
	int xx, yy, foo;
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
    c_code{calculate_next_move_to_avatar(Popponent->x, Popponent->y, Popponent->xx, Popponent->yy, &(now.next_x), &(now.next_y));};
    map[x].a[y] = 0;
    foo = map[next_x].a[next_y];
    map[next_x].a[next_y] = 4;
      
    x = next_x;
    y = next_y;

    if
    :: foo == 2 -> //Stomped on it dude. No need to play anymore.
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
promela_init_sokoban = """
init {{
  int i, ii;
  for (i : 0 .. {length}){{
    map[i].a[0] = 1;
    map[i].a[{width}] = 1;
  }}
  for (i : 0 .. {length}){{
    map[0].a[i] = 1;
    map[{length}].a[i] = 1;
  }}
  for (i : 1 .. {length2}){{
    for (ii : 1 .. {width2}){{
      map[i].a[ii] = 0;
    }}
  }}

  {wall_str}

  {boxes_str}

  {holes_str}

  run avatar_sokoban({avatar_y},{avatar_x});
}}
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
promela_init_for_game_3_smart = """
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
promela_init_for_game_1_smart = """
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
    import time
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    tt = time.time()
    os.system("rm ../spin/temp.pml > /dev/null")
    f = open("../spin/temp.pml", "a")
    f.write(self.promela_whole_file)
    f.close()
    tt = time.time() - tt
    print("   creating temp.pml: " + str(tt))
    tt = time.time()
    os.system("spin -a -DREACH ../spin/temp.pml")
    tt = time.time() - tt
    print("   creating pan.c: " + str(tt))
    tt = time.time()
    proc = subprocess.Popen(["gcc pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    tt = time.time() - tt
    print("   creating temp.out: " + str(tt))
    tt = time.time()
    os.system("../spin/temp.out -a -i >/dev/null")
    tt = time.time() - tt
    print("   executing temp.out: " + str(tt))

class A_Star_Graph_Node:
  def __init__(self, parent=None, position=None):
    self.parent = parent
    self.position = position

    self.g = 0
    self.h = 0
    self.f = 0

  def __eq__(self, other):
    return self.position == other.position

class A_Star_Game4_Multiple_Searches():
  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])
    self.__fix_map()
    self.moves = []
  def __fix_map(self):
    self.fixed_map = []
    for line in self.map:
      self.fixed_map.append(list(line))

    checklist = 0
    for lineNum, line in enumerate(self.fixed_map):
      for chNum, ch in enumerate(line):
        if ch == '0':
          self.fixed_map[lineNum][chNum] = 0
        elif ch == 'A':
          self.avatar_location = (lineNum, chNum)
          self.fixed_map[lineNum][chNum] = 0
          checklist += 1
        elif ch == 'G':
          self.portal_location = (lineNum, chNum)
          self.fixed_map[lineNum][chNum] = 0
          checklist += 1
        elif ch == 'w' or ch == '1':
          self.fixed_map[lineNum][chNum] = 1
        else: #Probs a 'E' slipped in.  
          raise spinCompileException("Unrecognized sprite in map!")

    if checklist != 2:
      raise spinCompileException("Multiple placement of sprites!")
  def __wheresWaldo(self, level, Waldo):
    for line_num, line in enumerate(level):
      for cell_num, cell in enumerate(line):
        if cell == Waldo:
          return [line_num, cell_num]
  def __get_moves_from_map(self, level):
    moves = []
    max_ = 0
    for line in level:
      for cell in line:
        if cell > max_:
          max_ = cell

    for i in range(max__, -1, -1):
      moves.append(self.__wheresWaldo(level,i))
    return moves
  def __return_path(self, current_node):
    path = []
    result = [[-1 for i in range(self.width)] for j in range(self.length)]
    current = current_node

    while current is not None:
      path.append(current.position)
      current = current.parent

    path = path[::-1]
    start_value = 0

    for i in range(len(path)):
      result[path[i][0]][path[i][1]] = start_value
      start_value += 1
    return result
  def __search(self, frm=None):
    from math import sqrt
    cost = 1
    if frm == None:
      start = [(x) for x in self.avatar_location]
    else:
      start = [(x) for x in frm]
    end = [(x) for x in self.portal_location]

    start_node = A_Star_Graph_Node(position=tuple(start))
    start_node.g = start_node.h = start_node.f = 0

    end_node = A_Star_Graph_Node(position=tuple(end))
    end_node.g = end_node.h = end_node.f = 0

    yet_to_visit_list = []
    visited_list = []

    yet_to_visit_list.append(start_node)

    outer_iterations = 0
    max_iterations = (self.length//2)**10

    move = [
      [-1,0], #Goes up
      [0,-1], #Goes left
      [1, 0], #Goes down
      [0, 1]  #Goes right
    ]

    no_rows = len(self.fixed_map)
    no_columns = len(self.fixed_map)

    while len(yet_to_visit_list) > 0:
      outer_iterations += 1
      current_node = yet_to_visit_list[0]
      current_index= 0

      for index, item in enumerate(yet_to_visit_list):
        if item.f < current_node.f:
          current_node = item
          current_index = index

      if outer_iterations > max_iterations:
        return self.__return_path(current_node)

      yet_to_visit_list.pop(current_index)
      visited_list.append(current_node)

      if current_node == end_node:
        return self.__return_path(current_node)

      children = []

      for new_position in move:
        node_position = (current_node.position[0]+new_position[0], current_node.position[1]+new_position[1])
        if (node_position[0]>(self.length-1) or node_position[0]<0 or node_position[1]>(self.width-1) or node_position[1]<0):
          continue

        if self.fixed_map[node_position[0]][node_position[1]] != 0:
          continue

        new_node = A_Star_Graph_Node(current_node, node_position)
        children.append(new_node)

      for child in children:
        if len([visited_child for visited_child in visited_list if visited_list == child]) > 0:
          continue
        child.g = current_node.g + cost
        child.h = sqrt((child.position[0]-end_node.position[0])**2 + (child.position[1]-end_node.position[1])**2)
        child.f = child.g + child.h

        if len([i for i in yet_to_visit_list if child == i and child.g > i.g]) > 0:
          continue
        yet_to_visit_list.append(child)
  def __directionize(self, movelist):
    import vgdl.ontology.constants as consts
    movelist = movelist[::-1]
    to_ret = []
    for index, element in enumerate(movelist):
      if index == len(movelist)-1:
        break
      frm = element
      to = movelist[index+1]
      if frm[0] > to[0]:
        to_ret.append(consts.UP)
      elif frm[0] < to[0]:
        to_ret.append(consts.DOWN)
      elif frm[1] > to[1]:
        to_ret.append(consts.LEFT)
      elif frm[1] < to[1]:
        to_ret.append(consts.RIGHT)
      else:
        raise "WUT"
    return to_ret
  def perform(self):
    #GET_MOVES_ONE_BY_ONE
    pass

class A_Star_Game4():
  def __init__(self, map):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])
    self.__fix_map()
    self.moves = []
  def __fix_map(self):
    self.fixed_map = []

    for line in self.map:
      self.fixed_map.append(list(line))
        
    checklist = 0

    for lineNum, line in enumerate(self.fixed_map):
      for chNum, ch in enumerate(line):
        if ch == '0':
          self.fixed_map[lineNum][chNum] = 0
        elif ch == 'A':
          self.avatar_location = (lineNum, chNum)
          self.fixed_map[lineNum][chNum] = 0
          checklist += 1
        elif ch == 'G':
          self.portal_location = (lineNum, chNum)
          self.fixed_map[lineNum][chNum] = 0
          checklist += 1
        elif ch == 'w' or ch == '1':
          self.fixed_map[lineNum][chNum] = 1
        else: #Probs a 'E' slipped in.  
          raise spinCompileException("Unrecognized sprite in map!")

    if checklist != 2:
      raise spinCompileException("Multiple placement of sprites!")
  def __wheresWaldo(self, level, Waldo):
    for line_num, line in enumerate(level):
      for cell_num, cell in enumerate(line):
        if cell == Waldo:
          return[line_num, cell_num]
  def __get_moves_from_map(self, level):
    if self.moves != []:
      return self.moves
    max_ = 0
    for line in level:
      for cell in line:
        if cell > max_:
          max_ = cell

    for i in range(max_, -1, -1):
      self.moves.append(self.__wheresWaldo(level, i))

    return self.moves
  def __return_path(self, current_node):
    path = []
    result = [[-1 for i in range(self.width)] for j in range(self.length)]
    current = current_node

    while current is not None:
      path.append(current.position)
      current = current.parent

    path = path[::-1]
    start_value = 0

    for i in range(len(path)):
      result[path[i][0]][path[i][1]] = start_value
      start_value += 1
    return result
  def __search(self, frm=None):
    cost = 1 # Moving costs 1 by default.
    if frm == None:
      start = [(x) for x in self.avatar_location]
    else:
      start = [(x) for x in frm]
    end = [(x) for x in self.portal_location]
    start_node = A_Star_Graph_Node(position = tuple(start))
    start_node.g = start_node.h = start_node.f = 0
    end_node = A_Star_Graph_Node(position = tuple(end))
    end_node.g = end_node.h = end_node.f = 0
    yet_to_visit_list = []
    visited_list = []
    yet_to_visit_list.append(start_node)
    outer_iterations = 0
    max_iterations = (self.length//2)**10
    move = [
      [-1,0], #Goes up
      [0,-1], #Goes left
      [1, 0], #Goes down
      [0, 1]  #Goes right
    ]
    no_rows = len(self.fixed_map)
    no_colums = len(self.fixed_map[0])
    while len(yet_to_visit_list) > 0:
      outer_iterations += 1
      current_node = yet_to_visit_list[0]
      current_index= 0
      for index, item in enumerate(yet_to_visit_list):
        if item.f < current_node.f:
          current_node = item
          current_index = index
      if outer_iterations > max_iterations:
        return self.__return_path(current_node)
      yet_to_visit_list.pop(current_index)
      visited_list.append(current_node)
      if current_node == end_node:
        return self.__return_path(current_node)
      children = []
      for new_position in move:
        node_position = (
          current_node.position[0] + new_position[0],
          current_node.position[1] + new_position[1]
          )
        if (
            node_position[0] > (self.length - 1) or 
            node_position[0] < 0 or 
            node_position[1] > (self.width -1) or 
            node_position[1] < 0):
            continue

        if self.fixed_map[node_position[0]][node_position[1]] != 0:
            continue

        new_node = A_Star_Graph_Node(current_node, node_position)
        children.append(new_node)

      for child in children:
        if len([visited_child for visited_child in visited_list if visited_child == child]) > 0:
          continue
        child.g = current_node.g + cost
        child.h = abs(child.position[0]-end_node.position[0]) + abs(child.position[1]-end_node.position[1]) #Manhattan distance is my heuristic.
        child.f  = child.g + child.h

        if len([i for i in yet_to_visit_list if child == i and child.g > i.g]) > 0:
          continue

        yet_to_visit_list.append(child)
  def __directionize(self, movelist):
    #import vgdl.ontology.constants as consts
    to_ret = []
    for index, element in enumerate(movelist):
      if index == len(movelist)-1:
        break

      frm = element
      to = movelist[index + 1]
      if frm[0] > to[0]:
        to_ret.append('D')
      elif frm[0] < to[0]:
        to_ret.append('A')
      elif frm[1] > to[1]:
        to_ret.append('S')
      elif frm[1] < to[1]:
        to_ret.append('W')
      else:
        raise "WUT"
    return to_ret[::-1]

  def perform(self):
    #GET ALL THE MOVES FROM MAP
    asd = self.__search()
    self.moves_from_map = self.__get_moves_from_map(asd)
    return self.__directionize(self.moves_from_map)

class SpinClass_Sokoban():
  def __init__(self, map, goals):
    self.map = map
    self.length = len(map)
    self.width = len(map[0])
    self.fixed_map = None
    self.list_walls = []
    self.wall_string = "{}"
    self.list_holes = []
    self.hole_string = "{}"
    self.list_boxes = []
    self.box_string = "{}"
    self.promela_whole_file = """{}\n{}\n{}\n{}\n{}\n{}\n"""
    self.goal_count = goals

  def fix_map(self):
    temp_map = []

    for line in self.map:
      temp_map.append(list(line))
      checklist = 0
      must_be_zero = 0

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
        elif ch == 'B':
          self.list_boxes.append((lineNum + 1, chNum + 1))
          must_be_zero += 1
        elif ch == 'H':
          self.list_holes.append((lineNum + 1, chNum + 1))
          must_be_zero -= 1

    if must_be_zero != 0:
      raise spinCompileException("Holes not equal to boxes!")
    if checklist != 1:
      raise spinCompileException("")

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
    self.wall_string = self.wall_string.format("\n")

  def create_holes_string(self):
    for hole in self.list_holes:
      self.hole_string = self.hole_string.format("\tmap[{}].a[{}] = 4;\n{}".format(hole[0], hole[1], "{}"))
    self.hole_string = self.hole_string.format("\n")

  def create_boxes_string(self):
    for box in self.list_boxes:
      self.box_string = self.box_string.format("\tmap[{}].a[{}] = 3;\n{}".format(box[0], box[1], "{}"))
    self.box_string = self.box_string.format("\n")

  def create_spin(self):
    if self.fixed_map is None:
      self.fix_map()

    self.create_wall_string()
    self.create_boxes_string()
    self.create_holes_string()

    formatted_init = promela_init_sokoban.format(
      avatar_y = self.avatar_location[0] + 1,
      avatar_x = self.avatar_location[1] + 1,
      length = self.length + 1,
      length2 = self.length,
      width = self.width + 1,
      width2 = self.width,
      wall_str = self.wall_string,
      boxes_str = self.box_string,
      holes_str = self.hole_string
    )
    formatted_header = promela_header_for_sokoban.format(
      self.length + 2,
      self.goal_count,
      self.width + 2
    )
    self.promela_whole_file = self.promela_whole_file.format(
      promela_comment_01_sokoban,
      promela_comment_02_sokoban,
      formatted_header,
      promela_avatar_sokoban,
      formatted_init,
      promela_ltl_formula_basic
    )

  def perform(self):
    self.create_spin()
    os.system("mkdir ../spin > /dev/null 2>&1")
    os.system("rm ../spin/temp.pml > /dev/null")

    fd = open("../spin/temp.pml", "a")
    fd.write(self.promela_whole_file)
    fd.close()

    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc -std=c99 pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a -I > /dev/null")
      

class SpinClass_Game4_Parameter_Capital_I():

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
    
    os.system("spin -a ../spin/temp.pml")
    proc = subprocess.Popen(["gcc -std=c99 pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if out != b'':
      raise spinCompileException("Cannot compile with gcc.")
    os.system("../spin/temp.out -a >/dev/null") #It's already nearly impossible to win this.

class SpinClass_Game3_smart():
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

    formatted_init = promela_init_for_game_3_smart.format(
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
    formatted_header = promela_header_for_game_3_smart.format(self.length+2, self.width+2)
    self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01,
			promela_comment_02,
			formatted_header,
			promela_avatar_game_3,
			promela_opponent_for_game_3_smart,
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
    os.system("../spin/temp.out -a -i >/dev/null")

class SpinClass_Game4_smart():### XXX: Cannot be a smart game 4, it's only us!
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
        
        formatted_init = promela_init_for_game_1_smart.format(
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
        formatted_header = promela_header_for_game_1_smart.format(self.length + 2, self.width + 2)
        self.promela_whole_file = self.promela_whole_file.format(
			promela_comment_01, 
			promela_comment_02, 
			formatted_header, 
			promela_avatar_for_game_1_smart, 
			promela_opponent_for_game_1_smart, 
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
        proc = subprocess.Popen(["gcc -std=c99 pan.c -DREACH -o ../spin/temp.out -lm"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out != b'':
            raise spinCompileException("Cannot compile with gcc.")
        os.system("../spin/temp.out -a -i >/dev/null")

def create_spin_from_game_5(map_):

  from copy import deepcopy 
  _map = deepcopy(map_)
  for ln, line in enumerate(_map):
    tmp = list(line)
    for cn, char in enumerate(tmp):
      if char == 'g':
        tmp[cn] = '0'
    _map[ln] = "".join(tmp)
  return SpinClass_Game4(_map)

if __name__ == "__main__":
  
  import cellularAutomata, caPolisher, spritePlanner, spinParser, player
  ca = cellularAutomata.elementary_cellular_automata(ruleset=30, start="000101010101010101010101")
  cap = caPolisher.CApolisher(ca = ca)
  sp = spritePlanner.sokobanPlanner(cap.perform(), count_boxes=1)
  sp.perform()
  s = SpinClass_Sokoban(sp.getMap(), sp.get_goals())
  s.perform()
  spp = spinParser.spinParser()
  caPolisher.map_print(sp.getMap())
  moves = spp.perform()[0]
  player.SokobanClass(action_list=moves, level_desc=sp.getMap()).play()
  """
  ca = cellularAutomata.elementary_cellular_automata(ruleset=30, start="111110101100011010001000")
  cap = caPolisher.CApolisher(ca = ca)
  sp = spritePlanner.dualSpritePlanner(cap.perform())
  sp.perform()
  sa = A_Star_Game4(sp.getMap())
  import time
  st = time.time()
  print_1=sa.perform()
  st = time.time() - st
  print("This is the time for a-star search:" + str(st))
  ss = SpinClass_Game4(sp.getMap())
  import spinParser
  spp = spinParser.spinParser()
  st = time.time()
  ss.perform()
  st = time.time() - st
  print("This is the time for generating .pml, .c, compilation, and execution." + str(st))
  st = time.time()
  print_2=spp.perform()
  st = time.time() - st
  print("This is the time for parsing:" + str(st))

  #print(print_1)
  #print(print_2[0])
  import player
  p = player.MazeGameClass(action_list=print_1, level_desc=sp.getMap())
  print(p.play())

  p = player.MazeGameClass(action_list=print_2[0], level_desc=sp.getMap())
  print(p.play())
  """
  """
  import cellularAutomata, caPolisher, spritePlanner, spinParser, time, player
  ca = cellularAutomata.elementary_cellular_automata(ruleset=30, start="100101101001011010010110")
  cap = caPolisher.CApolisher(ca = ca)
  sp = spritePlanner.mazeWithSubGoalsPlanner(cap.perform(),goalCount=18)
  sp.perform()
  mapp = sp.getMap()
  create_spin_from_game_5(mapp).perform()
  asd, _ = spinParser.spinParser().perform()
  game = player.Maze_SubGoals_GameClass(action_list=asd, level_desc=mapp)
  print(game.play())
  temp = ""
  for i in range(0, 26):
    temp += "1"
  map2 = temp + "\n1"+"1\n1".join(mapp)+"1\n" + temp
  
  mcts = player.MCTS_Runner_Regular_with_Time_Limit(1000,max_d=14,n_playouts=25000,rollout_depth=80,game_desc=game.game, render=True, level_desc=map2, discount_factor=0.99)
  mcts.run()"""