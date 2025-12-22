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

            print('\t' + line) # engine -> gui

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
    fen = '5B2/1P2P2P/2P1r3/2b1p3/6p1/2K2P1k/p7/nN5B w - - 0 1'
    time_limit = 60
    benchmark(position=fen, time_limit=time_limit)

"""
Testing Position: 5B2/1P2P2P/2P1r3/2b1p3/6p1/2K2P1k/p7/nN5B w - - 0 1
Time Limit: 60s

        info depth 1 currmove h7h8q score cp 1664 nodes 4528 nps 7385 time 613 hashfull 534
        info depth 2 currmove h7h8q score cp 1664 nodes 6829 nps 7225 time 945 hashfull 534
        info depth 3 currmove h7h8q score cp 1664 nodes 9290 nps 8489 time 1094 hashfull 534
        info depth 4 currmove h7h8q score cp 1664 nodes 23028 nps 11887 time 1937 hashfull 534
        info depth 5 currmove h7h8q score cp 1594 nodes 115351 nps 17542 time 6575 hashfull 536
        info depth 6 currmove h7h8q score cp 1594 nodes 175539 nps 20208 time 8686 hashfull 538
        info depth 7 currmove h7h8q score cp 1594 nodes 254026 nps 22839 time 11122 hashfull 540
        info depth 8 currmove h7h8q score cp 1594 nodes 605114 nps 26832 time 22551 hashfull 554
        info depth 9 currmove h7h8q score cp 1717 nodes 1200605 nps 32417 time 37036 hashfull 572
        info depth 10 currmove h7h8q score cp 1729 nodes 1898586 nps 36559 time 51931 hashfull 599
        info nodes 2048000 nps 34126 time 60012 hashfull 602
        bestmove h7h8q

    Best Move: h7h8q
    Time: 60.0196 seconds
    Nodes: 2,048,000
    NPS: 34,122 nodes/sec
"""