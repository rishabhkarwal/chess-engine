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

    info depth 1 currmove d7e6 score cp -915 nodes 30 nps 11911 time 2 hashfull 712
    info depth 2 currmove d7e6 score cp -915 nodes 111 nps 6445 time 17 hashfull 712
    info depth 3 currmove d7d6 score cp -912 nodes 231 nps 6500 time 35 hashfull 712
    info depth 4 currmove d7d6 score cp -976 nodes 767 nps 11874 time 64 hashfull 712
    info depth 5 currmove d7c8 score cp -975 nodes 1385 nps 12039 time 115 hashfull 712
    info depth 6 currmove d7d6 score cp -988 nodes 2766 nps 12548 time 220 hashfull 712
    info depth 7 currmove d7d6 score cp -990 nodes 4371 nps 12243 time 356 hashfull 712
    info depth 8 currmove d7d6 score cp -996 nodes 9441 nps 15766 time 598 hashfull 712
    info depth 9 currmove d7d6 score cp -994 nodes 15404 nps 18245 time 844 hashfull 713
    info depth 10 currmove d7d6 score cp -998 nodes 27408 nps 23088 time 1187 hashfull 713
    info depth 11 currmove d7d6 score cp -1000 nodes 40194 nps 27130 time 1481 hashfull 714
    info depth 12 currmove d7d6 score cp -1000 nodes 59746 nps 31917 time 1871 hashfull 715
    info depth 13 currmove d7d6 score cp -1000 nodes 95347 nps 38526 time 2474 hashfull 717
    info depth 14 currmove d7d6 score cp -1001 nodes 157069 nps 46452 time 3381 hashfull 719
    info depth 15 currmove d7d6 score cp -1001 nodes 226663 nps 53461 time 4239 hashfull 721
    info depth 16 currmove d7d6 score cp -1016 nodes 350395 nps 58145 time 6026 hashfull 725
    info depth 17 currmove d7d6 score cp -1016 nodes 517263 nps 64865 time 7974 hashfull 729
    info depth 18 currmove d7d6 score cp -1033 nodes 873392 nps 73486 time 11885 hashfull 737
    info depth 19 currmove d7d6 score cp -1033 nodes 1227523 nps 79417 time 15456 hashfull 743
    info depth 20 currmove d7d6 score cp -1034 nodes 1883917 nps 85227 time 22104 hashfull 751
    info depth 21 currmove d7d6 score cp -1035 nodes 3037780 nps 92254 time 32928 hashfull 763
    info depth 22 currmove d7d6 score cp -1037 nodes 4618769 nps 102082 time 45245 hashfull 771
    info nodes 6821888 nps 113693 time 60002 hashfull 783
    bestmove d7d6

    Best Move: d7d6
    Time: 60.0032 seconds
    Nodes: 6,821,888
    NPS: 113,692 nodes/sec
"""