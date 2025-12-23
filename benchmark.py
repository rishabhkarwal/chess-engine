from subprocess import Popen, PIPE
from time import time

from rich.console import Console

_console = Console()
def log(message):
    _console.log(message)

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

        warmup(process, 1) # 'warms-up' pypy JIT compiler to simulate how it'd be compiled in a real game

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
        if process.poll() is None:
            try:
                process.stdin.write('quit\n') # gui -> engine
                process.stdin.flush()
            except OSError:
                pass
        
        process.terminate()
        process.wait()

if __name__ == '__main__':
    fen = '8/4k2p/8/8/8/8/P7/2KR3b w - - 2 2'
    #fen = 'startpos'
    
    time_limit = 10
    benchmark(position=fen, time_limit=time_limit)

"""
Testing Position: 8/4k2p/8/8/8/8/P7/2KR3b w - - 2 2 (syzygy)
Time Limit: 10s

info depth 1 currmove d1h1 score mate 1 nodes 36 nps 605 time 59 hashfull 0 pv d1h1
bestmove d1h1

Best Move: d1h1
Time: 0.0608 seconds
Nodes: 36
NPS: 592 nodes/sec


Testing Position: startpos (opening book)
Time Limit: 10s

info string found book move: e2e4
bestmove e2e4

Best Move: e2e4
Time: 0.0020 seconds
Nodes: 0
NPS: 0 nodes/sec
"""