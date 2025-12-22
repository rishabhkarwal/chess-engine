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
        stats.print_stats(30)


if __name__ == '__main__':
        fen = '8/3K4/1k6/8/8/8/7p/8 w - - 0 1'
        time = 60
        test(position=fen, time_limit=time)
        

"""
SCENARIO:
    Position:    8/3K4/1k6/8/8/8/7p/8 w - - 0 1 
    Time Limit: 60 seconds

=========================================================================================================

    Search Depth:   20
    Nodes/Sec:      ~37,360
    Total Time:     59.605s
    Function Calls: 62,236,965

    Search Log:
        info depth 1 currmove d7e6 score cp -914 nodes 30 nps 18589 time 1 hashfull 0
        info depth 2 currmove d7e6 score cp -914 nodes 70 nps 24664 time 2 hashfull 0
        info depth 3 currmove d7d6 score cp -911 nodes 331 nps 28890 time 11 hashfull 0
        info depth 4 currmove d7d6 score cp -975 nodes 900 nps 28758 time 31 hashfull 0
        info depth 5 currmove d7d6 score cp -975 nodes 1319 nps 29012 time 45 hashfull 0
        info depth 6 currmove d7d6 score cp -987 nodes 2511 nps 29033 time 86 hashfull 0
        info depth 7 currmove d7d6 score cp -989 nodes 3893 nps 28183 time 138 hashfull 1
        info depth 8 currmove d7e6 score cp -994 nodes 12484 nps 29967 time 416 hashfull 2
        info depth 9 currmove d7e6 score cp -994 nodes 17099 nps 31126 time 549 hashfull 3
        info depth 10 currmove d7e6 score cp -998 nodes 48291 nps 35069 time 1376 hashfull 8
        info depth 11 currmove d7e6 score cp -999 nodes 63445 nps 35065 time 1809 hashfull 12
        info depth 12 currmove d7e6 score cp -999 nodes 83918 nps 34957 time 2400 hashfull 15
        info depth 13 currmove d7e6 score cp -999 nodes 113372 nps 35616 time 3183 hashfull 20
        info depth 14 currmove d7e6 score cp -999 nodes 177321 nps 36078 time 4914 hashfull 28
        info depth 15 currmove d7e6 score cp -1001 nodes 266342 nps 36570 time 7282 hashfull 44
        info depth 16 currmove d7e6 score cp -1015 nodes 422449 nps 36841 time 11466 hashfull 60
        info depth 17 currmove d7e6 score cp -1016 nodes 593141 nps 36087 time 16436 hashfull 77
        info depth 18 currmove d7e6 score cp -1049 nodes 978216 nps 36542 time 26769 hashfull 106
        info depth 19 currmove d7e6 score cp -1053 nodes 1375461 nps 37563 time 36616 hashfull 131
        info depth 20 currmove d7e6 score cp -1100 nodes 2226982 nps 37362 time 59604 hashfull 168

    Profile Stats:
        ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000   59.605   59.605 engine/search/search.py:23(get_best_move)
            21    0.001    0.000   59.599    2.838 engine/search/search.py:109(_search_root)
    1655111/129    9.512    0.000   59.596    0.462 engine/search/search.py:145(_alpha_beta)
    571871/461303   1.430    0.000   15.840    0.000 engine/search/search.py:244(_quiescence)
        549402    2.052    0.000   10.844    0.000 engine/moves/generator.py:35(generate_pseudo_legal_moves)
        1752516    8.414    0.000    9.287    0.000 engine/board/move_exec.py:46(make_move)
        2642352    2.880    0.000    7.645    0.000 engine/moves/legality.py:52(is_in_check)
        465973    4.143    0.000    5.829    0.000 engine/search/evaluation.py:177(evaluate) -> !!!
        1752516    4.979    0.000    5.382    0.000 engine/board/move_exec.py:174(unmake_move)
        549402    3.608    0.000    5.321    0.000 engine/moves/generator.py:151(_gen_king_moves)

Note that evaluate takes ~6 seconds for a 60 second search
Instead I am now evaluating in-place => the scores are stored within the state => O(1) lookup

=========================================================================================================

    Search Depth:   20
    Nodes/Sec:      ~43,697
    Total Time:     60.038s
    Function Calls: 61,995,129

    Search Log:
        info depth 1 currmove d7e6 score cp -915 nodes 30 nps 28442 time 1 hashfull 0
        info depth 2 currmove d7e6 score cp -915 nodes 70 nps 30466 time 2 hashfull 0
        info depth 3 currmove d7d6 score cp -912 nodes 275 nps 38628 time 7 hashfull 0
        info depth 4 currmove d7d6 score cp -976 nodes 844 nps 38617 time 21 hashfull 0
        info depth 5 currmove d7d6 score cp -976 nodes 1263 nps 36415 time 34 hashfull 0
        info depth 6 currmove d7d6 score cp -988 nodes 2453 nps 39325 time 62 hashfull 0
        info depth 7 currmove d7d6 score cp -990 nodes 3846 nps 38042 time 101 hashfull 1
        info depth 8 currmove d7e6 score cp -995 nodes 11958 nps 43768 time 273 hashfull 2
        info depth 9 currmove d7e6 score cp -995 nodes 17845 nps 43801 time 407 hashfull 3
        info depth 10 currmove d7e6 score cp -998 nodes 28853 nps 45987 time 627 hashfull 5
        info depth 11 currmove d7e6 score cp -998 nodes 47628 nps 44879 time 1061 hashfull 10
        info depth 12 currmove d7e6 score cp -1002 nodes 69252 nps 45509 time 1521 hashfull 13
        info depth 13 currmove d7e6 score cp -1002 nodes 99530 nps 45982 time 2164 hashfull 18
        info depth 14 currmove d7e6 score cp -1002 nodes 147378 nps 46445 time 3173 hashfull 24
        info depth 15 currmove d7e6 score cp -1002 nodes 216623 nps 46641 time 4644 hashfull 34
        info depth 16 currmove d7e6 score cp -1002 nodes 325254 nps 46732 time 6959 hashfull 47
        info depth 17 currmove d7e6 score cp -1003 nodes 467347 nps 46076 time 10142 hashfull 66
        info depth 18 currmove d7e6 score cp -1050 nodes 1181732 nps 45446 time 26002 hashfull 124
        info depth 19 currmove d7e6 score cp -1051 nodes 1383598 nps 45130 time 30657 hashfull 136
        info depth 20 currmove d7e6 score cp -1051 nodes 1794401 nps 44745 time 40102 hashfull 156
        info nodes 2623488 nps 43697 time 60038 hashfull 191

    Profile Stats:
        ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000   60.038   60.038 engine/search/search.py:23(get_best_move)
            22    0.001    0.000   60.029    2.729 engine/search/search.py:109(_search_root)
    1.95M/130     10.459    0.000   60.027    0.462 engine/search/search.py:145(_alpha_beta)
        650137      2.199    0.000   11.818    0.000 engine/moves/generator.py:35(generate_pseudo_legal_moves)
    2061421     10.132    0.000   11.059    0.000 engine/board/move_exec.py:47(make_move)
    0.66M/0.53M    1.479    0.000   11.046    0.000 engine/search/search.py:244(_quiescence)
    3109684      3.169    0.000    8.264    0.000 engine/moves/legality.py:52(is_in_check)
    2061411      5.599    0.000    6.038    0.000 engine/board/move_exec.py:216(unmake_move)
        650137      3.974    0.000    5.884    0.000 engine/moves/generator.py:151(_gen_king_moves)
                                            ...
        540109      0.318    0.000    0.318    0.000 engine/search/evaluation.py:214(evaluate) -> !!!


Now only takes 0.3 seconds

    Implemented incremental evaluation for O(1) scoring

    - Flattened PSQTs for fast index access
    - Added middlegame and endgame score, and phase fields to state
    - Update move make / unmake to incrementally update scores
    - Refactored evaluate() to use pre-calculated scores (O(N) -> O(1))
"""
