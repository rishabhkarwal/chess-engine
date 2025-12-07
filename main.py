from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    game = Game(white_player=IterativeDeepeningBot(WHITE, time_limit=5), black_player=QuiescenceBot(BLACK, depth=3))
    results = game.test(20)
    print(results)

    #game.run(debug=True)

"""

Testing: 100%|---| 20/20 [2:37:54<00:00, 473.73s/game, => White (IterativeDeepeningBot): 0, Black (QuiescenceBot): 1, Draw: 19]
Testing:  20%|--- | 4/20 [32:34<2:10:47, 490.45s/game, => White (IterativeDeepeningBot): 0, Black (QuiescenceBot): 0, Draw: 4]

White (IterativeDeepeningBot): 0.0%
Black (QuiescenceBot): 4.0%
Draw: 96.0%
    
    Uses iterative deepening to search as deep as possible within a time limit
    checks the best move from previous depth first to optimise pruning
    
    good for end-game when there are less moves; can look deeper

However results aren't as expected
"""