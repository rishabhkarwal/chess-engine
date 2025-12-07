from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    game = Game(IterativeDeepeningBot(WHITE, time_limit=5), QuiescenceBot(BLACK, depth=3))
    results = game.test(50)
    print(results)

    #game.run()

"""
Testing:  24%|---      | 12/50 [49:08<2:35:35, 245.68s/game, => White (IterativeDeepeningBot): 0, Black (QuiescenceBot): 0, Draw: 12]

White (IterativeDeepeningBot): 0.0%
Black (QuiescenceBot): 0.0%
Draw: 100%
        50-move rule: 12
        Stalemate: 0

Made it so every position is played twice and each engine plays both sides
This makes results more accurate as they allow each engine a fair chance
"""