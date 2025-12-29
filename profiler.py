from engine.uci.handler import UCI
from engine.core.move import move_to_uci

import cProfile
import pstats

def test(position='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', time_limit=2.0):
        uci = UCI()

        print(f'Testing Position: {position}\n')

        position_args = ['fen'] + position.split()
        uci.handle_position(position_args)

        uci.engine.time_limit = time_limit * 1000

        profiler = cProfile.Profile()
        profiler.enable()
        
        best_move = uci.engine.get_best_move(uci.state)

        profiler.disable()
    
        print(f'\nBest Move: {move_to_uci(best_move)}\n\n')
        
        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.print_stats(30)


if __name__ == '__main__':
        fen = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1' # kiwipete
        time = 60
        test(position=fen, time_limit=time)
        
"""
pypy3 profiler.py
"""