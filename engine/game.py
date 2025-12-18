import time
from tqdm import tqdm

from .fen_parser import load_from_fen
from .move_exec import make_move, is_in_check, get_legal_moves, is_threefold_repetition
from .constants import WHITE, BLACK

from .gui import GUI

from book import start_positions
from random import choice

class Game:
    def __init__(self, player_1, player_2, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        self.state = load_from_fen(fen)
        self.gui = GUI()

        self.white_player, self.black_player = player_1, player_2

        self.fen = fen

    def run(self, delay=0.0, silent=False, debug=False):
        winner = None
        reason = None
        while 1:
            if not silent and not debug: self.gui.clear_screen()

            legal_moves = get_legal_moves(self.state)
            is_check = is_in_check(self.state, self.state.player)
            is_white = self.state.player == WHITE

            if not silent:
                turn_color = f"White | {self.white_player}" if is_white else f"Black | {self.black_player}"
                check_msg = " | Check" if is_check else ""
                print(f"{turn_color} {check_msg}\n")

            if not silent: self.gui.print_board(self.state)
        
            if not silent: print(f"\n{self.gui.format_move_history(self.state.history)}\n")

            if not legal_moves: # no legal moves
                if is_check: # player to move in check
                    winner = BLACK if is_white else WHITE
                    if not silent: print(f"{"Black" if winner == BLACK else "White"} | Checkmate")
                    reason = "Checkmate"
                else:
                    if not silent: print("Draw | Stalemate")
                    reason = "Stalemate"
                break
                
            if self.state.halfmove_clock >= 100:
                if not silent: print("Draw | 50-Move Rule")
                reason = "50-Move Rule"
                break

            if is_threefold_repetition(self.state):
                if not silent: print("Draw | Threefold Repetition")
                reason = "Threefold Repetition"
                break

            if not silent: time.sleep(delay) # so the game is watchable

            move = (self.white_player if is_white else self.black_player).get_best_move(self.state)

            self.state = make_move(self.state, move)

        return winner, reason

    def test(self, n):

        def reset():
            self.fen = choice(start_positions)
            reload()

        def reload():
            self.state = load_from_fen(self.fen)

        def format_results(results, draws={}, final=False):
            lines = []
            for value, result in {self.white_player : 'White', self.black_player : 'Black', None : 'Draw'}.items():
                player = str(value)
                if value != None: player += f' ({result})'
                else: player = result
                lines.append(f'{player}: {results[value] if not final else str(round(results[value] / (i + 1) * 100, 2)) + "%"}')

            if draws:
                for reason, count in draws.items():
                    lines.append(f'\t{reason}: {count}')

            return "\n".join(lines)

        results = {state : 0 for state in [self.white_player, self.black_player, None]}
        draws = {reason : 0 for reason in ['50-Move Rule', 'Stalemate', 'Threefold Repetition']}

        with tqdm(total=n, desc=f"Testing", unit="game") as pbar:
            try:
                for i in range(n):
                    if not(i & 1): # even iteration
                        if i: # i > 0
                            reset() # start a new game
                        else:
                            reload()
                    else:
                        reload()

                    self.white_player.colour, self.black_player.colour = WHITE, BLACK
                    result, reason = self.run(silent=True)

                    result = self.white_player if result == WHITE else self.black_player if result == BLACK else None

                    results[result] += 1

                    self.white_player, self.black_player = self.black_player, self.white_player # switch black and white

                    if reason in draws.keys():
                        draws[reason] += 1

                    pbar.set_postfix({"": f'> {format_results(results).replace("\n", ", ")}'})
                    pbar.update(1)

            except KeyboardInterrupt:
                pass

        print()

        return format_results(results, draws, final=True)