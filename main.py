from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    player_1 = LMRBot(WHITE, time_limit=3, tt_size_mb=32)
    player_2 = PVSBot(BLACK, time_limit=3, tt_size_mb=32)
    game = Game(player_1, player_2)
    
    results = game.test(10)
    print(results)

    #game.run(debug=True)

"""
Testing: 100%|---| 10/10 [57:18<00:00, 343.88s/game, => LMRBot (White): 1, PVSBot (Black): 0, Draw: 9]

LMRBot (White): 10.0%
PVSBot (Black): 0.0%
Draw: 90.0%
        50-Move Rule: 0
        Stalemate: 0
        Threefold Repetition: 9

Late Move Reduction assumes move-ordering is perfect: if a move is sorted late in the list it implies it is likely bad

So search to a lower depth; unless the lower depth search says that its a good move - then search fully
"""