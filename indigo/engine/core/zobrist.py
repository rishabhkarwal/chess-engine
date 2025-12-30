import random
from engine.core.constants import ALL_PIECES, NO_SQUARE, BLACK

def init_zobrist_keys():
    """Initialises random 64-bit integers for Zobrist hashing"""
    random.seed(42) 
    table = {}
    # pieces: 'P': {0: rand, 1: rand...}, 'n': ...
    for piece in ALL_PIECES: table[piece] = [random.getrandbits(64) for _ in range(64)]
    # castling: 16 combinations (0-15)
    table['castling'] = [random.getrandbits(64) for _ in range(16)]
    # en-passant: file 0-7, or none (use 8 for None)
    table['ep'] = [random.getrandbits(64) for _ in range(9)]
    # side to move (black to move)
    table['black_to_move'] = random.getrandbits(64)

    return table

ZOBRIST_KEYS = init_zobrist_keys()

def compute_hash(state) -> int:
    """Computes the full Zobrist hash of a state"""
    h = 0
    # piece positions
    for piece, bb in state.bitboards.items():
        if piece not in ZOBRIST_KEYS: continue
        temp_bb = bb
        while temp_bb:
            sq = (temp_bb & -temp_bb).bit_length() - 1
            h ^= ZOBRIST_KEYS[piece][sq]
            temp_bb &= temp_bb - 1
            
    # castling rights
    h ^= ZOBRIST_KEYS['castling'][state.castling]
    
    # en passant
    file = state.en_passant % 8 if state.en_passant != NO_SQUARE else 8
    h ^= ZOBRIST_KEYS['ep'][file]
        
    # side to move (if black)
    if state.player == BLACK: h ^= ZOBRIST_KEYS['black_to_move']
        
    return h

def z_piece(piece, square):
    return ZOBRIST_KEYS[piece][square]

def z_castle(rights):
    return ZOBRIST_KEYS['castling'][rights]

def z_ep(square):
    if square == NO_SQUARE: return ZOBRIST_KEYS['ep'][8]
    return ZOBRIST_KEYS['ep'][square % 8]

def z_black_move():
    return ZOBRIST_KEYS['black_to_move']