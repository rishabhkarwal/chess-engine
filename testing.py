from engine.bot import *
from engine.constants import WHITE, BLACK
from engine.fen_parser import load_from_fen

from time import time_ns
from tqdm import tqdm
from numpy import mean

bots = [SearchTreeBot, AlphaBetaBot, QuiescenceBot]
move_count = 80
search_depth = 2

print(f'{move_count} moves @ depth {search_depth}\n')

results = {}
for bot in bots:
    state = load_from_fen()
    w, b = bot(WHITE, depth=search_depth), bot(BLACK, depth=search_depth)
    turn = w if state.player == WHITE else b
    times = []
    nodes = []

    with tqdm(total=move_count, desc=f'{turn}', unit='move') as pbar:
        for _ in range(move_count):
            if (not get_legal_moves(state)) or (state.halfmove_clock >= 100): # game over => start again
                state = load_from_fen()
                continue
            
            start = time_ns()
            move = turn.get_best_move(state)
            dt = time_ns() - start

            state = make_move(state, move)

            turn = b if turn == w else w

            times.append(dt)
            nodes.append(turn.nodes_searched)
            pbar.set_postfix({'Average ': f'> time: {mean(times) / 1e9 :.6f} nodes: {int(mean(nodes))}'})
            pbar.update(1)

    results[turn] = sum(times)
    print('\n')

for bot, t in sorted(results.items(), key=lambda x: x[1]):
    print(f'{bot} {t / 1e9 :.4f}')

""" 
Testing framework used to see metrics such as average time per move and average nodes searched
Good to see effects of changes
"""