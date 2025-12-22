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

    info depth 1 currmove d7e6 score cp -941 nodes 30 nps 2219 time 13 hashfull 621
    info depth 2 currmove d7e6 score cp -941 nodes 111 nps 5653 time 19 hashfull 621
    info depth 3 currmove d7d6 score cp -932 nodes 231 nps 8680 time 26 hashfull 621
    info depth 4 currmove d7d6 score cp -996 nodes 749 nps 6471 time 115 hashfull 621
    info depth 5 currmove d7c8 score cp -996 nodes 1376 nps 6751 time 203 hashfull 622
    info depth 6 currmove d7e6 score cp -1010 nodes 3774 nps 10830 time 348 hashfull 622
    info depth 7 currmove d7d6 score cp -1018 nodes 5543 nps 10402 time 532 hashfull 622
    info depth 8 currmove d7d6 score cp -1022 nodes 9050 nps 11961 time 756 hashfull 622
    info depth 9 currmove d7d6 score cp -1022 nodes 14223 nps 13734 time 1035 hashfull 623
    info depth 10 currmove d7d6 score cp -1026 nodes 22451 nps 17102 time 1312 hashfull 623
    info depth 11 currmove d7d6 score cp -1026 nodes 36043 nps 21941 time 1642 hashfull 624
    info depth 12 currmove d7d6 score cp -1029 nodes 60217 nps 28888 time 2084 hashfull 626
    info depth 13 currmove d7d6 score cp -1031 nodes 94067 nps 34942 time 2692 hashfull 628
    info depth 14 currmove d7d6 score cp -1040 nodes 152973 nps 43391 time 3525 hashfull 631
    info depth 15 currmove d7d6 score cp -1040 nodes 223548 nps 51211 time 4365 hashfull 634
    info depth 16 currmove d7d6 score cp -1046 nodes 354960 nps 60333 time 5883 hashfull 640
    info depth 17 currmove d7d6 score cp -1046 nodes 526313 nps 70616 time 7453 hashfull 646
    info depth 18 currmove d7d6 score cp -1046 nodes 806383 nps 83930 time 9607 hashfull 654
    info depth 19 currmove d7d6 score cp -1046 nodes 1246460 nps 96598 time 12903 hashfull 664
    info depth 20 currmove d7d6 score cp -1046 nodes 2056889 nps 109651 time 18758 hashfull 676
    info depth 21 currmove d7d6 score cp -1047 nodes 2794047 nps 113943 time 24521 hashfull 696
    info depth 22 currmove d7d6 score cp -1047 nodes 3714276 nps 118163 time 31433 hashfull 711
    info depth 23 currmove d7d6 score cp -1048 nodes 5121661 nps 122299 time 41877 hashfull 724
    info nodes 8019968 nps 133609 time 60025 hashfull 745
    bestmove d7d6

    Best Move: d7d6
    Time: 60.0259 seconds
    Nodes: 8,019,968
    NPS: 133,608 nodes/sec
"""