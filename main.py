from engine.utils import BitBoard
from engine.fen_parser import load_from_fen

state = load_from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

print(state)

"""
Console Output:

State(bitboards={'K': 16, 'k': 1152921504606846976, 'Q': 8, 'q': 576460752303423488, 'R': 129, 'r': 9295429630892703744, 'B': 36, 'b': 2594073385365405696, 'N': 66, 'n': 4755801206503243776, 'P': 65280, 'p': 71776119061217280, 'white': 65535, 'black': 18446462598732840960, 'all': 18446462598732906495}, player=1, castling=15, en_passant=-1, halfmove_clock=0, fullmove_number=1, history=[])"""