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
        fen = '8/3K4/1k6/8/8/8/7p/8 w - - 0 1'
        time = 5
        test(position=fen, time_limit=time)
        

"""
SCENARIO:
    Position:    8/3K4/1k6/8/8/8/7p/8 w - - 0 1 
    Time Limit: 5 seconds

--------------------------------------------------------------------------------
[ ORIGINAL ]
--------------------------------------------------------------------------------
Search Depth:   9
Nodes/Sec:      ~5,900
Total Time:     3.413s
Function Calls: 4,949,322

Search Log:
    info depth 1 currmove d7e6 score cp -914 nodes 30 nps 6492 time 4 hashfull 0
    info depth 2 currmove d7e6 score cp -914 nodes 70 nps 6961 time 10 hashfull 0
    info depth 3 currmove d7d6 score cp -911 nodes 329 nps 4957 time 66 hashfull 0
    info depth 4 currmove d7d6 score cp -975 nodes 874 nps 5230 time 167 hashfull 0
    info depth 5 currmove d7d6 score cp -975 nodes 1409 nps 4924 time 286 hashfull 0
    info depth 6 currmove d7d6 score cp -987 nodes 2689 nps 5176 time 519 hashfull 1
    info depth 7 currmove d7d6 score cp -994 nodes 5343 nps 5535 time 965 hashfull 3
    info depth 8 currmove d7d6 score cp -996 nodes 10329 nps 5865 time 1760 hashfull 5
    info depth 9 currmove d7d6 score cp -999 nodes 20794 nps 5955 time 3491 hashfull 12

Profile Stats:
     ncalls   tottime  percall  cumtime  percall  filename:lineno(function)
       61839   0.725    0.000    2.205    0.000    engine/board/move_exec.py:37(make_move)
       62345   0.407    0.000    0.507    0.000    engine/core/zobrist.py:21(compute_hash)
       61840   0.187    0.000    0.416    0.000    {method 'join' of 'str' objects}
     1602720   0.278    0.000    0.278    0.000    {method 'get' of 'dict' objects}
      803907   0.229    0.000    0.229    0.000    engine/board/move_exec.py:15(<genexpr>)
      220769   0.088    0.000    0.109    0.000    engine/core/utils.py:6(bit_scan)

--------------------------------------------------------------------------------
[ BEFORE ]
--------------------------------------------------------------------------------
Search Depth:   12
Nodes/Sec:      ~34,000
Total Time:     2.911s
Function Calls: 3,418,946

Search Log:
    info depth 1 currmove d7e8 score cp -904 nodes 57 nps 26838 time 2 hashfull 0
    info depth 2 currmove d7e8 score cp -904 nodes 97 nps 24175 time 4 hashfull 0
    info depth 3 currmove d7c8 score cp -905 nodes 577 nps 28222 time 20 hashfull 0
    info depth 4 currmove d7c8 score cp -993 nodes 1371 nps 28136 time 48 hashfull 0
    info depth 5 currmove d7d8 score cp -938 nodes 2472 nps 30526 time 80 hashfull 0
    info depth 6 currmove d7e6 score cp -1008 nodes 5691 nps 28732 time 198 hashfull 1
    info depth 7 currmove d7e7 score cp -999 nodes 12177 nps 29768 time 409 hashfull 6
    info depth 8 currmove d7e7 score cp -1009 nodes 28946 nps 33240 time 870 hashfull 10
    info depth 9 currmove d7e8 score cp -1007 nodes 42486 nps 32563 time 1304 hashfull 17
    info depth 10 currmove d7e8 score cp -1009 nodes 55765 nps 32961 time 1691 hashfull 21
    info depth 11 currmove d7e8 score cp -1009 nodes 72963 nps 33524 time 2176 hashfull 28
    info depth 12 currmove d7e8 score cp -1009 nodes 98974 nps 34020 time 2909 hashfull 36

Profile Stats:
     ncalls   tottime  percall  cumtime  percall  filename:lineno(function)
       60117   0.312    0.000    2.903    0.028    engine/search/search.py:135(_alpha_beta)
       27618   0.071    0.000    1.281    0.000    engine/moves/generator.py:30(get_legal_moves)
       38857   0.065    0.000    0.857    0.000    engine/search/search.py:224(_quiescence)
      165169   0.204    0.000    0.760    0.000    engine/moves/legality.py:59(is_legal)
      119886   0.456    0.000    0.507    0.000    engine/board/move_exec.py:52(make_move)
       27618   0.088    0.000    0.450    0.000    engine/moves/generator.py:35(generate_pseudo_legal_moves)

--------------------------------------------------------------------------------
[ AFTER ]
--------------------------------------------------------------------------------
Search Depth:   14
Nodes/Sec:      ~41,200
Total Time:     5.049s
Function Calls: 6,375,825

Search Log:
    info depth 1 currmove d7e6 score cp -914 nodes 30 nps 29167 time 1 hashfull 0
    info depth 2 currmove d7e6 score cp -914 nodes 70 nps 27485 time 2 hashfull 0
    info depth 3 currmove d7d6 score cp -911 nodes 331 nps 28837 time 11 hashfull 0
    info depth 4 currmove d7d6 score cp -975 nodes 900 nps 32092 time 28 hashfull 0
    info depth 5 currmove d7e7 score cp -923 nodes 1489 nps 31843 time 46 hashfull 0
    info depth 6 currmove d7d6 score cp -996 nodes 4317 nps 32632 time 132 hashfull 1
    info depth 7 currmove d7e6 score cp -996 nodes 8465 nps 33997 time 248 hashfull 4
    info depth 8 currmove d7e6 score cp -995 nodes 16584 nps 37360 time 443 hashfull 6
    info depth 9 currmove d7e6 score cp -995 nodes 21781 nps 37570 time 579 hashfull 9
    info depth 10 currmove d7e6 score cp -997 nodes 42445 nps 39373 time 1077 hashfull 15
    info depth 11 currmove d7e6 score cp -996 nodes 75833 nps 39345 time 1927 hashfull 28
    info depth 12 currmove d7e6 score cp -998 nodes 106541 nps 40122 time 2655 hashfull 36
    info depth 13 currmove d7e6 score cp -998 nodes 150982 nps 40489 time 3728 hashfull 52
    info depth 14 currmove d7e6 score cp 998 nodes 208122 nps 41224 time 5048 hashfull 67

Profile Stats:
     ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
          1    0.000    0.000    5.049    5.049  engine/search/search.py:23(get_best_move)
         18    0.000    0.000    5.043    0.280  engine/search/search.py:105(_search_root)
 128252/108    0.662    0.000    5.042    0.047  engine/search/search.py:141(_alpha_beta)
79870/65157    0.160    0.000    1.816    0.000  engine/search/search.py:238(_quiescence)
      58255    0.188    0.000    0.987    0.000  engine/moves/generator.py:35(generate_pseudo_legal_moves)
      67445    0.509    0.000    0.725    0.000  engine/search/evaluation.py:177(evaluate)
     151735    0.647    0.000    0.715    0.000  engine/board/move_exec.py:47(make_move)
     256754    0.244    0.000    0.629    0.000  engine/moves/legality.py:52(is_in_check)

================================================================================

Main optimisations:

    Switched to "lazy" legality checking: replaced retrieving the legal moves generating pseudo-legal moves + deferred legality check (only check AFTER making the best move) -> this eliminated legality check from the bottleneck

    Fixed quiescence sorting: added MVV-LVA sorting to q-search to prioritise good captures, fixing the "horizon effect"

    Added safety checks: move execution now aborts operations safely if a move is attempted on an empty square, preventing crashes


Micro-optimisations: 

    Reduced time management overhead: loosened the time-check constraints to allow searching deeper if time remains

    Removed redundant legality check calls: relying on checking if is check on the resulting state is ~4x faster than simulating the move twice
"""
