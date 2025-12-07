from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    game = Game(white_player=IterativeDeepeningBot(WHITE, time_limit=5), black_player=QuiescenceBot(BLACK, depth=3))
    #results = game.test(50)
    #print(results)

    game.run()

"""
Testing: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 50/50 [7:26:59<00:00, 536.39s/game, => White (IterativeDeepeningBot): 6, Black (QuiescenceBot): 3, Draw: 41]

White (IterativeDeepeningBot): 12.0%
Black (QuiescenceBot): 6.0%
Draw: 82.0%
        50-move rule: 41
        Stalemate: 0

Through debugging, have found that all games were the EXACT same as its a deterministic process so results weren't accurate
and so have sourced a collection of positions that are roughly equal (evaluated by stockfish) 
also noticed that games end in a draw by 50 move rule a lot

I believe this is because quiescence is still stronger as it searches deeper in middlegame scenarios;
and so although iterative deepening can search deeper in endgame; it has already lost
"""