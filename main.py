from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    player_1 = LMRBot(WHITE, time_limit=3, tt_size_mb=32)
    player_2 = NMPBot(BLACK, time_limit=3, tt_size_mb=32)
    game = Game(player_1, player_2)
    
    results = game.test(10)
    print(results)

    #game.run(debug=True)

"""
Testing: 100%|---| 10/10 [46:52<00:00, 281.30s/game, => LMRBot (White): 0, NMPBot (Black): 1, Draw: 9]

LMRBot (White): 0.0%
NMPBot (Black): 10.0%
Draw: 90.0%
        50-Move Rule: 0
        Stalemate: 0
        Threefold Repetition: 9


Null move pruning: give the opponent a "free turn" (pass); if our position is so strong that, even after doing nothing, the opponent still cannot find a move that improves their position enough to beat our expectations (beta), then can safely cut off the search

Allows searching large subtrees where one side is overwhelmingly winning or position is static 

However zugzwang positions are falsely evaluated as wins when using NMP; so just check if at least 1 major piece is present
"""