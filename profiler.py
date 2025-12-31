import sys
import os
import cProfile
import pstats
import io
import re

def setup(engine_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, engine_name)

    if target_dir not in sys.path: sys.path.insert(0, target_dir)
    
    print(f"Engine: {engine_name.capitalize()}")

def pretty_print(profiler, n_stats=15):
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats('tottime')
    stats.print_stats(n_stats)
    raw_output = stream.getvalue()

    calls_match = re.search(r"(\d+) function calls", raw_output)
    total_calls = f"{int(calls_match.group(1)):,}" if calls_match else "N/A"

    header_regex = r"ncalls\s+tottime\s+percall\s+cumtime\s+percall\s+filename:lineno\(function\)"
    match = re.search(header_regex, raw_output)

    n = 100

    print("\n" + "=" * n)
    print(f"Total Function Calls: {total_calls}")
    print("-" * n)

    print(f"{'n-calls':^15}   {'tot-time':^8}   {'per-call':^8}   {'cum-time':^8}   {'function'}")
    print("-" * n)

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
            
            full_path = " ".join(parts[5:])

            path_clean_match = re.search(r"((?:moves|board|search|core|uci)[\\/].+)", full_path)
            
            if path_clean_match:
                clean_path = path_clean_match.group(1).replace('\\', '/')
            else:
                clean_path = full_path

            print(f"{ncalls:^15}   {tottime:^8}   {percall_1:^8}   {cumtime:^8}   {clean_path}")
            
    print("-" * n)
    print("\n")

def run(position, time_sec):
    try:
        from engine.uci.handler import UCI
        from engine.core.move import move_to_uci
    except ImportError as e:
        print(f"ERROR: Could not import engine modules\n{e}")
        return

    uci = UCI()
    
    print(f'\n\nPosition: {position}')
    uci.handle_position(['fen'] + position.split())

    uci.engine.time_limit = int(time_sec * 1000)

    print(f'Time: {time_sec}s\n')

    profiler = cProfile.Profile()
    profiler.enable()

    best_move = uci.engine.get_best_move(uci.state)

    profiler.disable()

    if isinstance(best_move, int):
        move_str = move_to_uci(best_move)
    else:
        move_str = str(best_move)

    print(f'\nBest Move: {move_str}')
    pretty_print(profiler)

if __name__ == '__main__':
    engine_choice = sys.argv[1] if len(sys.argv) > 1 else 'sophia'

    setup(engine_choice)

    FEN = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
    TIME_LIMIT = 100 # long enough to let JIT optimise

    run(FEN, TIME_LIMIT)

"""pypy3 profiler.py sophia"""



"""
Previous:

info depth 9 currmove e2a6 score cp -35 nodes 4081072 nps 42432 time 96177 hashfull 113 pv e2a6 b4c3 d2c3 e6d5 e5g4 e7e4 f3e4 f6e4 c3g7

====================================================================================================
Total Function Calls: 313,704,330
----------------------------------------------------------------------------------------------------
    n-calls       tot-time   per-call   cum-time   function
    7801185        7.685      0.000      7.685     moves/legality.py:17(is_square_attacked)
----------------------------------------------------------------------------------------------------

"""

"""
Now:

info depth 9 currmove e2a6 score cp -35 nodes 4081072 nps 41932 time 97323 hashfull 113 pv e2a6 b4c3 d2c3 e6d5 e5g4 e7e4 f3e4 f6e4 c3g7

====================================================================================================
Total Function Calls: 313,704,330
----------------------------------------------------------------------------------------------------
    n-calls       tot-time   per-call   cum-time   function
    7801185        5.249      0.000      5.249     moves/legality.py:16(is_square_attacked)
----------------------------------------------------------------------------------------------------
"""