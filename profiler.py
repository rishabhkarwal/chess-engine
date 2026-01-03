import sys
import os
import cProfile
import pstats
import io
import re
import time

BAR_WIDTH = 100

def setup(engine_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, engine_name)

    if target_dir not in sys.path: sys.path.insert(0, target_dir)
    
    print(f'Engine: {target_dir}')

def pretty_print(profiler, n_stats=15):
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats('tottime')
    stats.print_stats(n_stats)
    raw_output = stream.getvalue()

    calls_match = re.search(r'(\d+) function calls', raw_output)
    total_calls = f'{int(calls_match.group(1)):,}' if calls_match else 'N/A'

    header_regex = r'ncalls\s+tottime\s+percall\s+cumtime\s+percall\s+filename:lineno\(function\)'
    match = re.search(header_regex, raw_output)

    print('\n' + '=' * BAR_WIDTH)
    print(f'Total Function Calls: {total_calls}')
    print('-' * BAR_WIDTH)

    print(f"{'n-calls':^15}   {'tot-time':^8}   {'per-call':^8}   {'cum-time':^8}   {'function'}")
    print('-' * BAR_WIDTH)

    if match:
        table_content = raw_output[match.end():]
        
        for line in table_content.strip().split('\n'):
            if not line.strip(): continue
            
            parts = line.split()
            if len(parts) < 6: continue
            
            ncalls = parts[0]
            tottime = parts[1]
            percall_1 = parts[2]
            cumtime = parts[3]
            
            full_path = ' '.join(parts[5:])

            path_clean_match = re.search(r'((?:moves|board|search|core|uci)[\\/].+)', full_path)
            
            if path_clean_match:
                clean_path = path_clean_match.group(1).replace('\\', '/')
            else:
                clean_path = full_path

            print(f'{ncalls:^15}   {tottime:^8}   {percall_1:^8}   {cumtime:^8}   {clean_path}')
            
    print('-' * BAR_WIDTH)
    print('\n')

def run(position, time_sec, engine_name):
    try:
        from engine.uci.handler import UCI
        from engine.core.move import move_to_uci
    except ImportError as e:
        print(f'ERROR: Could not import engine modules\n{e}')
        return

    uci = UCI()
    
    print(f'\n\nPosition: {position}')
    uci.handle_position(['fen'] + position.split())

    uci.engine.time_limit = int(time_sec * 1000)

    print(f'Time: {time_sec}s\n')

    profiler = cProfile.Profile()
    profiler.enable()

    t_start = time.time()
    best_move = uci.engine.get_best_move(uci.state)
    t_end = time.time()

    profiler.disable()

    elapsed = t_end - t_start
    nodes = uci.engine.nodes_searched
    nps = int(nodes / elapsed) if elapsed > 0 else 0
    depth = uci.engine.depth_reached

    if isinstance(best_move, int):
        move_str = move_to_uci(best_move)
    else:
        move_str = str(best_move)

    print('\n' + '=' * BAR_WIDTH + '\n')
    print(f'Engine: {engine_name.capitalize()}\n')

    print(f'Nodes: {nodes:,}')
    print(f'NPS:   {nps:,}')
    print(f'Time:  {elapsed:.2f}s')
    print(f'Depth: {depth}')
    print(f'Move:  {move_str}')

    pretty_print(profiler)

if __name__ == '__main__':
    engine_choice = sys.argv[1] if len(sys.argv) > 1 else 'sophia'

    setup(engine_choice)

    FEN = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
    TIME_LIMIT = 120 # long enough to let JIT optimise

    run(FEN, TIME_LIMIT, engine_choice)

"""pypy3 profiler.py sophia"""

"""
Position: r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1
Time: 120s

info depth 1 seldepth 23 score cp 11 nodes 3706 nps 1190 time 3111 hashfull 0 tbhits 0 pv e2a6
info depth 2 seldepth 23 score cp 11 nodes 7499 nps 1904 time 3937 hashfull 0 tbhits 0 pv e2a6 b4c3
info depth 3 seldepth 23 score cp 11 nodes 10949 nps 2492 time 4392 hashfull 0 tbhits 0 pv e2a6 b4c3 d2c3
info string aspiration tightened: 42
info depth 4 seldepth 31 score cp 11 nodes 55975 nps 5909 time 9472 hashfull 0 tbhits 0 pv e2a6 b4c3 d2c3 h3g2
info depth 5 seldepth 31 score cp 11 nodes 115216 nps 7851 time 14674 hashfull 0 tbhits 0 pv e2a6 b4c3 d2c3 h3g2 f3g2
info string aspiration failed: 42
info depth 6 seldepth 31 score cp -37 nodes 276404 nps 12229 time 22601 hashfull 2 tbhits 0 pv e2a6 e6d5 c3d5 f6d5 e4d5 e7e5
info depth 7 seldepth 34 score cp 11 nodes 419492 nps 13796 time 30405 hashfull 4 tbhits 0 pv e2a6 b4c3 d2c3 h3g2 f3g2 e6d5 e4d5
info depth 8 seldepth 34 score cp 11 nodes 637485 nps 16334 time 39027 hashfull 9 tbhits 0 pv e2a6 b4c3 d2c3 h3g2 f3g2 e6d5 e4d5 b6d5
info string aspiration tightened: 63
info depth 9 seldepth 34 score cp -71 nodes 1416982 nps 20394 time 69477 hashfull 28 tbhits 0 pv d5e6 e7e6 e2a6 e6e5 d2f4 e5d4 c3d1 h3g2 f3g2
info depth 10 seldepth 34 score cp -66 nodes 2929291 nps 24363 time 120230 hashfull 55 tbhits 0 pv e2a6 b4c3 d2c3 e6d5 e5g4 d5e4 g4f6 g7f6 f3f6 e7f6

====================================================================================================

Engine: Sophia

Nodes: 2,929,291
NPS:   24,355
Time:  120.27s
Depth: 10
Move:  e2a6

====================================================================================================
Total Function Calls: 418,224,888
----------------------------------------------------------------------------------------------------
    n-calls       tot-time   per-call   cum-time   function
----------------------------------------------------------------------------------------------------
    7357232        23.610     0.000      24.379    board/move_exec.py:61(make_move)
    2540002        18.252     0.000      25.860    search/evaluation.py:256(evaluate)
2623797/120668     9.979      0.000     103.896    search/search.py:453(_quiescence)
   10975217        9.866      0.000      10.193    moves/legality.py:67(is_in_check)
    7357232        9.207      0.000      9.516     board/move_exec.py:266(unmake_move)
    7357129        7.549      0.000      10.848    search/ordering.py:117(pick_next_move)
    1321842        4.465      0.000      4.894     moves/generator.py:207(_gen_rook_moves)
    1321842        3.935      0.000      24.643    moves/generator.py:35(generate_pseudo_legal_moves)
  305494/530       3.127      0.000     120.184    search/search.py:263(_alpha_beta)
    1321842        3.060      0.000      3.794     moves/generator.py:62(_gen_pawn_moves)
    1321842        2.600      0.000      2.936     moves/generator.py:224(_gen_queen_moves)
   80539415        2.494      0.000      2.494     {method 'bit_length' of 'int' objects}
   126917967       2.479      0.000      3.142     search/ordering.py:82(get_move_score)
    1321842        2.449      0.000      2.730     moves/generator.py:190(_gen_bishop_moves)
    1321842        2.396      0.000      2.735     moves/generator.py:153(_gen_king_moves)
----------------------------------------------------------------------------------------------------
"""