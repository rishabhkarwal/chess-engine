from engine.uci.handler import UCI
from engine.core.move import move_to_uci

import cProfile
import pstats

def test(position='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', time_limit=2.0):
        uci = UCI(debug=True)

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
        stats.print_stats(10)


if __name__ == '__main__':
        fen = '5B2/1P2P2P/2P1r3/2b1p3/6p1/2K2P1k/p7/nN5B w - - 0 1'
        time = 60
        test(position=fen, time_limit=time)
        

"""
SCENARIO:
    Position:    5B2/1P2P2P/2P1r3/2b1p3/6p1/2K2P1k/p7/nN5B w - - 0 1
    Time Limit:  60 seconds

Search Depth:   8
Nodes/Sec:      ~14,507
Total Time:     60.279s
Function Calls: 71,570,954

Search Log:
    info depth 1 currmove h7h8q score cp 1664 nodes 4043 nps 12638 time 319 hashfull 0
    info depth 2 currmove h7h8q score cp 1664 nodes 6438 nps 12649 time 508 hashfull 0
    info depth 3 currmove h7h8q score cp 1664 nodes 9069 nps 13341 time 679 hashfull 0
    info depth 4 currmove h7h8q score cp 1664 nodes 23258 nps 13977 time 1663 hashfull 1
    info depth 5 currmove h7h8q score cp 1594 nodes 80869 nps 15032 time 5379 hashfull 1
    info depth 6 currmove h7h8q score cp 1594 nodes 148448 nps 14613 time 10158 hashfull 7
    info depth 7 currmove h7h8q score cp 1594 nodes 223782 nps 15422 time 14509 hashfull 11
    info depth 8 currmove h7h8q score cp 1594 nodes 510115 nps 14645 time 34831 hashfull 42
    info nodes 874496 nps 14507 time 60278 hashfull 59

    Best Move: h7h8q

Profile Stats:
      ncalls         tottime  percall  cumtime  percall  filename:lineno(function)
           1           0.000    0.000   60.279   60.279  search.py:23(get_best_move)
          11           0.001    0.000   60.274    5.479  search.py:109(_search_root)
  132210/241         0.957    0.000   60.270    0.250  search.py:145(_alpha_beta)
 0.74M/95438         3.659    0.000   53.626    0.001  search.py:244(_quiescence)
      665892          13.797    0.000   18.782    0.000  evaluation.py:268(evaluate)
      310097           1.167    0.000   10.615    0.000  generator.py:35(generate_pseudo_legal_moves)
     1447639           8.102    0.000    8.868    0.000  move_exec.py:47(make_move)
      310108           1.429    0.000    6.850    0.000  {method 'sort' of 'list' objects}
     2215969           2.165    0.000    5.698    0.000  legality.py:52(is_in_check)
     3427851           1.280    0.000    4.466    0.000  search.py:257(<lambda>)
     1447630           4.016    0.000    4.400    0.000  move_exec.py:216(unmake_move)
     4297518           2.195    0.000    3.817    0.000  ordering.py:62(get_move_score)
     2215969           3.140    0.000    3.140    0.000  legality.py:12(is_square_attacked)
    16316190           2.674    0.000    2.674    0.000  {method 'bit_length' of 'int' objects}
      310097           1.657    0.000    2.413    0.000  generator.py:222(_gen_queen_moves)
      310097           1.413    0.000    2.313    0.000  generator.py:62(_gen_pawn_moves)

Evaluation now takes a LOT longer...

TODO: incremental evaluation heursitic
"""

