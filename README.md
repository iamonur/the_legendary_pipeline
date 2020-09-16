# How to use?
You need to implement:
- A function that validates your level getting a dictionary input and calculates if the level is OK(True) or NOK(False), example one is not scientific or relies on truth. It is best to implement your own.
- A map generator that implements cellularAutomata.selfrefCa, or has the same method interfaces. You also can use example generators.
- A map polisher, that shapes your output of map generator due to your regulations. Example one makes sure that the playable space is at least n%. This polisher will be fed with your map generator and has to implement perform()
- A sprite planner, that will place your sprites to your polished map.
- A model checker, if you are not using one of my games, it will be hard to implement. You need to model your game, then implement a PROMELA file accordingly. If you're using one of mine, you can just use one of my own implementations.
- An output parser, this will return you the moves the avatar needs to do in order to win the game. For smaller levels(like 8 by 8), your compiled SPIN output is OK to run with argument -i. However, I moved to larger levels(like 24 by 24) and the -i is just not bearable as computation time. In that case, you may try to use -I like me. Or purchase more computational power. Before moving on:
  - -i: Absolute fastest way to victory.
  - -I: Somewhat fastest way to victory (Let me tell you, it is NOT).
- A game class, you may develop your own, but I guess mine will do for that job.
- A random feeder, a class to generate you a random line to start your generation. It does not have to be completely random, also it does not need to feed you continuously. A trained agent may replace this at some point.

You will pass the class and function definitions to the simulation manager, and you are good to go! You may alsowant to check the implementations in the code base.

# What are the dependencies?
- *SPIN*: the model checker, and somewhat backbone of the study.
- *gcc*: Will compile SPIN output.
- *Linux-based environment*: I did not, also not going to, test it to work on other OSes. It will mostly not work. If anyone develops on other environments, you will probably need to take your own fork and change system commands.
- *python>=3.6*: py-vgdl requires this "to have nice things"
- *pybrain*: py-vgdl also demands this
- *py-vgdl(my fork)*: The fork I have has both RecordedController, and also a predictable and modellable implementation of the class Chaser. It is at: https://github.com/iamonur/py-vgdl

# My games
- *Run*: Avatar tries to run away from the opponent to the portal : This game is full implemented&tested
- *Catch*: Avatar tries to catch the opponent before it *run*s away : This game is full implemented&tested
- *Race*: Avatar tries to run past the opponent to the portal : This game is full implemented&tested
- *MazeSolver*: Avatar solves the maze that has no enemy on it.

# TODO
- implement at least functional tests
-- implement all units' tests
-- Refactor like hell
- ~~implement all the games via PROMELA.~~
- ~~Implement base game via MCTS just to benchmark. ~~

# Contributions
If your contribution is meaningful and you code tests for your code, your pull request will be merged 99% of the time. I will be giving feedback & special thanks to you every time. Don't judge me on the tests, I just started developing them.
