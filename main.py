from engine.game import Game
from engine.bot import *
from engine.constants import WHITE, BLACK

if __name__ == "__main__":
    player_1 = KillerBot(WHITE, time_limit=3, tt_size_mb=32)
    player_2 = TranspositionBot(BLACK, time_limit=3, tt_size_mb=32)
    game = Game(player_1, player_2)
    
    results = game.test(10)
    print(results)

    #game.run(debug=True)

"""
Fixed scoring as Black and White switch positions after each game
"""