import sys
import time

from .fen_parser import load_from_fen
from .move_exec import make_move
from .constants import WHITE, BLACK
from .bot import KillerBot as Bot

class UCI:
    def __init__(self):
        self.engine = Bot(WHITE)
        self.state = load_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def run(self):
        """Main UCI loop"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                command = parts[0]

                if command == "uci":
                    self.handle_uci()
                elif command == "isready":
                    print("readyok")
                    sys.stdout.flush()
                elif command == "ucinewgame":
                    self.handle_new_game()
                elif command == "position":
                    self.handle_position(parts[1:])
                elif command == "go":
                    self.handle_go(parts[1:])
                elif command == "quit":
                    break
                
            except Exception:
                continue

    def handle_uci(self):
        print("id name [NAME]")
        print("id author Rish")
        print("uciok")
        sys.stdout.flush()

    def handle_new_game(self):
        self.engine = Bot(WHITE)

    def handle_position(self, args):
        fen_idx = -1
        moves_idx = -1

        if args[0] == "startpos":
            self.state = load_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            if "moves" in args:
                moves_idx = args.index("moves")
        elif args[0] == "fen":
            if "moves" in args:
                moves_idx = args.index("moves")
                fen_str = " ".join(args[1:moves_idx])
            else:
                fen_str = " ".join(args[1:])
            self.state = load_from_fen(fen_str)

        if moves_idx != -1:
            moves = args[moves_idx + 1:]
            for move_str in moves:
                from .move_exec import get_legal_moves
                legal_moves = get_legal_moves(self.state)
                
                found = False
                for legal_move in legal_moves:
                    if str(legal_move).lower() == move_str.lower():
                        self.state = make_move(self.state, legal_move)
                        found = True
                        break
                
                if not found:
                    pass

    def handle_go(self, args):
        wtime = None
        btime = None
        winc = 0
        binc = 0
        movetime = None

        try:
            for i in range(len(args)):
                if args[i] == "wtime": wtime = int(args[i+1])
                elif args[i] == "btime": btime = int(args[i+1])
                elif args[i] == "winc": winc = int(args[i+1])
                elif args[i] == "binc": binc = int(args[i+1])
                elif args[i] == "movetime": movetime = int(args[i+1])
        except IndexError:
            pass

        time_limit = 1.0
        
        """
        if movetime:
            time_limit = movetime / 1000.0
        elif wtime is not None and btime is not None:
            if self.state.player == WHITE:
                time_limit = (wtime / 1000.0) / 20.0 + (winc / 1000.0)
            else:
                time_limit = (btime / 1000.0) / 20.0 + (binc / 1000.0)
            
            time_limit = max(0.1, time_limit - 0.1) # safety
        """

        time_limit = 2.0

        self.engine.time_limit = time_limit
        self.engine.colour = self.state.player

        best_move = self.engine.get_best_move(self.state)
        
        print(f"bestmove {best_move}")
        sys.stdout.flush()

if __name__ == "__main__":
    uci = UCI()
    uci.run()