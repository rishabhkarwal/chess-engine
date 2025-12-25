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

"""
SCENARIO:

    Position:    r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1 

    Time Limit: 60 seconds


Search Depth:   7
Nodes/Sec:      ~17,840
Total Time:     60.154s
Function Calls: 99,395,691


Search Log:

    info depth 1 currmove e2a6 score cp 42 nodes 1682 nps 2898 time 580 hashfull 0 pv e2a6
    info depth 2 currmove e2a6 score cp 42 nodes 5019 nps 3780 time 1327 hashfull 0 pv e2a6 h3g2
    info depth 3 currmove e2a6 score cp 42 nodes 14467 nps 5641 time 2564 hashfull 0 pv e2a6 h3g2 f3g2
    info depth 4 currmove e2a6 score cp 42 nodes 71499 nps 8502 time 8409 hashfull 2 pv e2a6 h3g2 f3g2 b4c3
    info depth 5 currmove e2a6 score cp 29 nodes 176855 nps 11543 time 15320 hashfull 3 pv e2a6 b4c3 d2c3 e6d5 e1c1
    info depth 6 currmove e2a6 score cp 29 nodes 386126 nps 14765 time 26151 hashfull 12 pv e2a6 b4c3 d2c3 e6d5 e1c1 h3g2
    info depth 7 currmove e2a6 score cp 29 nodes 927669 nps 17972 time 51616 hashfull 20 pv e2a6 b4c3 d2c3 e6d5 e1c1 h3g2 f3g2


Profile Stats:

     ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
          1    0.001    0.001   60.153   60.153  engine/search/search.py:76(get_best_move)
          8    0.004    0.000   60.147    7.518  engine/search/search.py:173(_search_root)
 146633/344    1.536    0.000   60.136    0.175  engine/search/search.py:209(_alpha_beta)
 926519/112    3.997    0.000   53.087    0.000  engine/search/search.py:321(_quiescence)
     363683    2.416    0.000   14.363    0.000  engine/moves/generator.py:35(generate_pseudo_legal_moves)
     843976   11.425    0.000   13.389    0.000  engine/search/evaluation.py:137(evaluate)
    2191882   12.901    0.000   13.244    0.000  engine/board/move_exec.py:45(make_move)
    3143377    0.804    0.000    6.423    0.000  engine/moves/legality.py:57(is_in_check)
    3332530    6.072    0.000    6.072    0.000  engine/moves/legality.py:17(is_square_attacked)
    2191877    3.380    0.000    3.456    0.000  engine/board/move_exec.py:193(unmake_move)
     363691    2.312    0.000    3.135    0.000  {method 'sort' of 'list' objects}
     363683    2.692    0.000    3.015    0.000  engine/moves/generator.py:223(_gen_queen_moves)
     363683    1.926    0.000    2.299    0.000  engine/moves/generator.py:61(_
"""