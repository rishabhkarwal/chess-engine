from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    game = Game(KillerBot(WHITE, time_limit=4, tt_size_mb=64), TranspositionBot(BLACK, time_limit=4, tt_size_mb=64))
    
    results = game.test(20)
    print(results)

    #game.run(debug=True)

"""
Added 3-fold repetition check to make games end faster (rather than wait for 50-move rule)
Also added new bot with killer move heuristic

Testing:  24%|---  | 12/50 [27:36<1:27:26, 138.05s/game, => White (KillerBot): 2, Black (TranspositionBot): 2, Draw: 8]

White (KillerBot): 15.38%
Black (TranspositionBot): 15.38%
Draw: 61.54%
        50-Move Rule: 0
        Stalemate: 0
        Threefold Repetition: 8
"""