from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    game = Game(PositionalBot(WHITE), MaterialBot(BLACK))
    results = game.test(10000)
    print(results)

"""
Testing: 100%|---| 10000/10000 [17:36<00:00,  9.46game/s, => White (PositionalBot): 427, Black (MaterialBot): 602, Draw: 8971]

White (PositionalBot): 4.27%
Black (MaterialBot): 6.02%
Draw: 89.71%

Rather counter-intuitive result; but this is likely due to the fact it's only a 1-ply search and so the advantage isn't clear
"""