from subprocess import Popen, PIPE
from time import time

def warmup(process, seconds):
    print(f'Starting {seconds}s warm-up')
    start_time = time()

    move_time = seconds * 1000
    process.stdin.write('position startpos\n')
    process.stdin.write(f'go movetime {move_time}\n')
    process.stdin.flush()
    
    while True:
        elapsed = time() - start_time
        remaining = seconds - elapsed
        print(f'~{remaining:.1f}s left', end='\r', flush=True)
        line = process.stdout.readline()
        if line.startswith('bestmove'): break
    
    print('Warmup complete')

def benchmark(position='startpos', time_limit=5.0, engine_path='engine.bat'):

    try:
        process = Popen(
            engine_path,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print(f"Error: Could not find '{engine_path}'")
        return

    try:
        process.stdin.write('uci\n')
        process.stdin.flush()

        while True: # engine -> gui
            line = process.stdout.readline()
            if not line: break
            if line.strip() == 'uciok': break

        warmup(process, 60) # 'warms-up' pypy JIT compiler to simulate how it'd be compiled in a real game

        if position == 'startpos': 
            process.stdin.write('position startpos\n') # gui -> engine
        else:
            process.stdin.write(f'position fen {position}\n') # gui -> engine
        
        move_time = int(time_limit * 1000)
        process.stdin.write(f'go movetime {move_time}\n') # gui -> engine
        process.stdin.flush()

        print(f'Testing Position: {position}')
        print(f'Time Limit: {time_limit}s\n')

        start_time = time()
        
        node_count = 0
        best_move = '0000'

        while True:
            line = process.stdout.readline()
            if not line: break
            line = line.strip()

            print(line) # engine -> gui

            if line.startswith('info'):
                parts = line.split()
                if 'nodes' in parts:
                    idx = parts.index('nodes')
                    if idx + 1 < len(parts):
                        node_count = int(parts[idx + 1])
            
            if line.startswith('bestmove'):
                best_move = line.split()[1]
                break
        
        end_time = time()
        duration = end_time - start_time
        
        nps = int(node_count / duration) if duration > 0 else 0

        print(f'\nBest Move: {best_move}')
        print(f'Time: {duration:.4f} seconds')
        print(f'Nodes: {node_count:,}')
        print(f'NPS: {nps:,} nodes/sec')

    except Exception as e:
        print(f'An error occurred: {e}')
    
    finally:
        process.stdin.write('quit\n') # gui -> engine
        process.stdin.flush()
        process.terminate()

if __name__ == '__main__':
    fen = '8/3K4/1k6/8/8/8/7p/8 w - - 0 1'
    time_limit = 60
    benchmark(position=fen, time_limit=time_limit)

"""
Testing Position: 8/3K4/1k6/8/8/8/7p/8 w - - 0 1
Time Limit: 60s

    info depth 1 currmove d7e6 score cp -914 nodes 30 nps 3136 time 9 hashfull 509
    info depth 2 currmove d7e6 score cp -914 nodes 111 nps 6296 time 17 hashfull 509
    info depth 3 currmove d7d6 score cp -911 nodes 231 nps 5835 time 39 hashfull 509
    info depth 4 currmove d7d6 score cp -975 nodes 749 nps 9507 time 78 hashfull 509
    info depth 5 currmove d7d6 score cp -975 nodes 1195 nps 12106 time 98 hashfull 509
    info depth 6 currmove d7d6 score cp -987 nodes 2595 nps 10869 time 238 hashfull 509
    info depth 7 currmove d7d6 score cp -989 nodes 4219 nps 11896 time 354 hashfull 510
    info depth 8 currmove d7e6 score cp -994 nodes 12477 nps 16186 time 770 hashfull 510
    info depth 9 currmove d7d6 score cp -996 nodes 21527 nps 17560 time 1225 hashfull 512
    info depth 10 currmove d7e6 score cp -1000 nodes 39680 nps 22316 time 1778 hashfull 513
    info depth 11 currmove d7d6 score cp -995 nodes 71491 nps 29811 time 2398 hashfull 516
    info depth 12 currmove d7d6 score cp -1000 nodes 89546 nps 33480 time 2674 hashfull 517
    info depth 13 currmove d7d6 score cp -1000 nodes 115176 nps 37810 time 3046 hashfull 518
    info depth 14 currmove d7d6 score cp -1029 nodes 220996 nps 49791 time 4438 hashfull 524
    info depth 15 currmove d7d6 score cp -1029 nodes 291411 nps 54961 time 5302 hashfull 528
    info depth 16 currmove d7d6 score cp -1029 nodes 412716 nps 63980 time 6450 hashfull 534
    info depth 17 currmove d7d6 score cp -1029 nodes 648492 nps 73588 time 8812 hashfull 545
    info depth 18 currmove d7d6 score cp -1032 nodes 1112969 nps 85996 time 12942 hashfull 563
    info depth 19 currmove d7d6 score cp -1035 nodes 1819370 nps 94639 time 19224 hashfull 581
    info depth 20 currmove d7d6 score cp -1036 nodes 2868075 nps 102759 time 27910 hashfull 607
    info depth 21 currmove d7d6 score cp -1051 nodes 4127923 nps 110231 time 37447 hashfull 625
    info depth 22 currmove d7d6 score cp -1098 nodes 6570022 nps 117933 time 55709 hashfull 647
    bestmove d7d6

    Best Move: d7d6
    Time: 55.7295 seconds
    Nodes: 6,570,022
    NPS: 117,891 nodes/sec
"""