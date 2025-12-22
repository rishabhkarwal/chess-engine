from engine.core.constants import ALL_PIECES, WHITE, BLACK, FILE_A, FILE_H, FULL_BOARD
from engine.core.utils import BitBoard
from engine.moves.precomputed import (
    KNIGHT_ATTACKS, 
    KING_ATTACKS, 
    BISHOP_MASKS, 
    BISHOP_TABLE, 
    ROOK_MASKS, 
    ROOK_TABLE
)

"""PeSTO Evaluation Function"""

# piece values
MG_VALUES = {'P': 82, 'N': 337, 'B': 365, 'R': 477, 'Q': 1025, 'K': 0}
EG_VALUES = {'P': 94, 'N': 281, 'B': 297, 'R': 512, 'Q': 936, 'K': 0}

# game phase increments
PHASE_INC = {'P': 0, 'N': 1, 'B': 1, 'R': 2, 'Q': 4, 'K': 0}
MAX_PHASE = 24

PASSED_PAWN_BONUS = [0, 10, 17, 15, 62, 168, 276, 0] 

ISOLATED_PAWN_PENALTY = -10
DOUBLED_PAWN_PENALTY = -12
BISHOP_PAIR_BONUS = 35
ROOK_OPEN_FILE = 20
ROOK_SEMI_OPEN_FILE = 10
CONNECTED_ROOKS_BONUS = 15

MG_PAWN = [
      0,   0,   0,   0,   0,   0,   0,   0,
     98, 134,  61,  95,  68, 126,  34, -11,
     -6,   7,  26,  31,  65,  56,  25, -20,
    -14,  13,   6,  21,  23,  12,  17, -23,
    -27,  -2,  -5,  12,  17,   6,  10, -25,
    -26,  -4,  -4, -10,   3,   3,  33, -12,
    -35,  -1, -20, -23, -15,  24,  38, -22,
      0,   0,   0,   0,   0,   0,   0,   0,
]

EG_PAWN = [
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0,
]

MG_KNIGHT = [
   -167, -89, -34, -49,  61, -97, -15, -107,
    -73, -41,  72,  36,  23,  62,   7, -17,
    -47,  60,  37,  65,  84, 129,  73,  44,
     -9,  17,  19,  53,  37,  69,  18,  22,
    -13,   4,  16,  13,  28,  19,  21,  -8,
    -23,  -9,  12,  10,  19,  17,  25, -16,
    -29, -53, -12,  -3,  -1,  18, -14, -19,
   -105, -21, -58, -33, -17, -28, -19, -23,
]

EG_KNIGHT = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64,
]

MG_BISHOP = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
]

EG_BISHOP = [
    -14, -21, -11,  -8,  -7,  -9, -17, -24,
     -8,  -4,   7, -12,  -3, -13,  -4, -14,
      2,  -8,   0,  -1,  -2,   6,   0,   4,
     -3,   9,  12,   9,  14,  10,   3,   2,
     -6,   3,  13,  19,   7,  10,  -3,  -9,
    -12,  -3,   8,  10,  13,   3,  -7, -15,
    -14, -18,  -7,  -1,   4,  -9, -15, -27,
    -23,  -9, -23,  -5,  -9, -16,  -5, -17,
]

MG_ROOK = [
     32,  42,  32,  51,  63,   9,  31,  43,
     27,  32,  58,  62,  80,  67,  26,  44,
     -5,  19,  26,  36,  17,  45,  61,  16,
    -24, -11,   7,  26,  24,  35,  -8, -20,
    -36, -26, -12,  -1,   9,  -7,   6, -23,
    -45, -25, -16, -17,   3,   0,  -5, -33,
    -44, -16, -20,  -9,  -1,  11,  -6, -71,
    -19, -13,   1,  17,  16,   7, -37, -26,
]

EG_ROOK = [
     13,  10,  18,  15,  12,  12,   8,   5,
     11,  13,  13,  11,  -3,   3,   8,   3,
      7,   7,   7,   5,   4,  -3,  -5,  -3,
      4,   3,  13,   1,   2,   1,  -1,   2,
      3,   5,   8,   4,  -5,  -6,  -8, -11,
     -4,   0,  -5,  -1,  -7, -12,  -8, -16,
     -6,  -6,   0,   2,  -9,  -9, -11,  -3,
     -9,   2,   3,  -1,  -5, -13,   4, -20,
]

MG_QUEEN = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
]

EG_QUEEN = [
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  57,  40,  57,  36,
    -18,  28,  19,  47,  31,  34,  39,  23,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41,
]

MG_KING = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
]

EG_KING = [
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43,
]

PSQTs = {
    'P': (MG_PAWN, EG_PAWN),
    'N': (MG_KNIGHT, EG_KNIGHT),
    'B': (MG_BISHOP, EG_BISHOP),
    'R': (MG_ROOK, EG_ROOK),
    'Q': (MG_QUEEN, EG_QUEEN),
    'K': (MG_KING, EG_KING)
}

PIECE_INDICES = {
    'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
    'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
}

MG_TABLE = [[0] * 64 for _ in range(12)]
EG_TABLE = [[0] * 64 for _ in range(12)]
PHASE_WEIGHTS = [0] * 12

PASSED_PAWN_MASKS = [[0] * 64 for _ in range(2)]
FILE_MASKS = [0] * 8
ADJACENT_FILE_MASKS = [0] * 8

def init_eval_tables():
    for piece, (mg_val, eg_val) in PSQTs.items():
        idx = PIECE_INDICES[piece]
        PHASE_WEIGHTS[idx] = PHASE_INC[piece]
        MG_TABLE[idx] = [MG_VALUES[piece] + val for val in mg_val]
        EG_TABLE[idx] = [EG_VALUES[piece] + val for val in eg_val]

    for piece, (mg_val, eg_val) in PSQTs.items():
        black_piece = piece.lower()
        idx = PIECE_INDICES[black_piece]
        PHASE_WEIGHTS[idx] = PHASE_INC[piece]
        for sq in range(64):
            flipped_sq = sq ^ 56 
            MG_TABLE[idx][sq] = -(MG_VALUES[piece] + mg_val[flipped_sq])
            EG_TABLE[idx][sq] = -(EG_VALUES[piece] + eg_val[flipped_sq])
    
    for f in range(8):
        mask = FILE_A << f
        FILE_MASKS[f] = mask
        adj = 0
        if f > 0: adj |= FILE_A << (f - 1)
        if f < 7: adj |= FILE_A << (f + 1)
        ADJACENT_FILE_MASKS[f] = adj

    for sq in range(64):
        file, rank = sq % 8, sq // 8
        w_mask = 0
        for r in range(rank + 1, 8):
            for f_adj in range(max(0, file - 1), min(8, file + 2)):
                w_mask |= (1 << (r * 8 + f_adj))
        PASSED_PAWN_MASKS[WHITE][sq] = w_mask
        b_mask = 0
        for r in range(rank - 1, -1, -1):
            for f_adj in range(max(0, file - 1), min(8, file + 2)):
                b_mask |= (1 << (r * 8 + f_adj))
        PASSED_PAWN_MASKS[BLACK][sq] = b_mask

init_eval_tables()

def calculate_initial_score(state):
    mg, eg, phase = 0, 0, 0

    for piece_char, bb in state.bitboards.items():
        if piece_char not in PIECE_INDICES: continue

        p_idx = PIECE_INDICES[piece_char]
        count = bb.bit_count()
        phase += PHASE_WEIGHTS[p_idx] * count

        while bb:
            lsb = bb & -bb
            sq = lsb.bit_length() - 1
            mg += MG_TABLE[p_idx][sq]
            eg += EG_TABLE[p_idx][sq]
            bb &= bb - 1

    state.mg_score = mg
    state.eg_score = eg
    state.phase = phase

def get_mop_up_score(state, winning_colour):
    winning_king_bb = state.bitboards['K' if winning_colour == WHITE else 'k']
    losing_king_bb = state.bitboards['k' if winning_colour == WHITE else 'K']

    if not winning_king_bb or not losing_king_bb: return 0

    winning_sq = (winning_king_bb & -winning_king_bb).bit_length() - 1
    losing_sq = (losing_king_bb & -losing_king_bb).bit_length() - 1

    losing_rank, losing_file = losing_sq // 8, losing_sq % 8

    centre_dist = max(3 - losing_rank, losing_rank - 4) + max(3 - losing_file, losing_file - 4)

    mop_up = 4 * centre_dist

    winning_rank, winning_file = winning_sq // 8, winning_sq % 8

    dist_between_kings = abs(winning_rank - losing_rank) + abs(winning_file - losing_file)

    mop_up += 2 * (14 - dist_between_kings)

    return mop_up if winning_colour == WHITE else -mop_up

def evaluate(state):
    mg_phase = min(state.phase, MAX_PHASE)
    eg_phase = MAX_PHASE - mg_phase
    evaluation = (state.mg_score * mg_phase + state.eg_score * eg_phase) // MAX_PHASE
    
    bitboards = state.bitboards
    all_pieces = bitboards['all']
    w_pawns = bitboards['P']
    b_pawns = bitboards['p']
    
    # bishop pair
    if bitboards['B'].bit_count() >= 2: evaluation += BISHOP_PAIR_BONUS
    if bitboards['b'].bit_count() >= 2: evaluation -= BISHOP_PAIR_BONUS

    # king Safety & pawn structure
    w_king_sq = (bitboards['K'] & -bitboards['K']).bit_length() - 1 if bitboards['K'] else -1
    b_king_sq = (bitboards['k'] & -bitboards['k']).bit_length() - 1 if bitboards['k'] else -1
    w_king_zone = KING_ATTACKS[w_king_sq] if w_king_sq != -1 else 0
    b_king_zone = KING_ATTACKS[b_king_sq] if b_king_sq != -1 else 0

    # white pawns & structure
    temp_w = w_pawns
    while temp_w:
        lsb = temp_w & -temp_w
        sq = lsb.bit_length() - 1
        f = sq % 8
        if not (PASSED_PAWN_MASKS[WHITE][sq] & b_pawns): evaluation += PASSED_PAWN_BONUS[sq // 8]
        if (w_pawns & FILE_MASKS[f]) != lsb: evaluation += DOUBLED_PAWN_PENALTY
        if not (w_pawns & ADJACENT_FILE_MASKS[f]): evaluation += ISOLATED_PAWN_PENALTY
        temp_w &= temp_w - 1

    # black pawns & structure
    temp_b = b_pawns
    while temp_b:
        lsb = temp_b & -temp_b
        sq = lsb.bit_length() - 1
        f = sq % 8
        if not (PASSED_PAWN_MASKS[BLACK][sq] & w_pawns): evaluation -= PASSED_PAWN_BONUS[7 - (sq // 8)]
        if (b_pawns & FILE_MASKS[f]) != lsb: evaluation -= DOUBLED_PAWN_PENALTY
        if not (b_pawns & ADJACENT_FILE_MASKS[f]): evaluation -= ISOLATED_PAWN_PENALTY
        temp_b &= temp_b - 1

    # rooks & mobility & king safety zone attacks
    for colour, p_keys in [(WHITE, ['N', 'B', 'R', 'Q']), (BLACK, ['n', 'b', 'r', 'q'])]:
        score_adj = 0
        enemy_pawns = b_pawns if colour == WHITE else w_pawns
        enemy_king_zone = b_king_zone if colour == WHITE else w_king_zone
        
        # connected rooks & open files
        rooks = bitboards['R' if colour == WHITE else 'r']
        if rooks.bit_count() >= 2:
            r1 = (rooks & -rooks).bit_length() - 1
            r2 = (rooks & (rooks - 1)).bit_length() - 1
            if ROOK_TABLE[(r1, all_pieces & ROOK_MASKS[r1])] & (1 << r2): score_adj += CONNECTED_ROOKS_BONUS
        
        temp_rooks = rooks
        while temp_rooks:
            sq = (temp_rooks & -temp_rooks).bit_length() - 1
            f = sq % 8
            if not (w_pawns & FILE_MASKS[f]) and not (b_pawns & FILE_MASKS[f]): score_adj += ROOK_OPEN_FILE
            elif not (enemy_pawns & FILE_MASKS[f]): score_adj += ROOK_SEMI_OPEN_FILE
            temp_rooks &= temp_rooks - 1

        # mobility & attacks
        for p_key in p_keys:
            pieces = bitboards[p_key]
            while pieces:
                sq = (pieces & -pieces).bit_length() - 1
                if p_key.upper() == 'N': atts = KNIGHT_ATTACKS[sq]
                elif p_key.upper() == 'B': atts = BISHOP_TABLE[(sq, all_pieces & BISHOP_MASKS[sq])]
                elif p_key.upper() == 'R': atts = ROOK_TABLE[(sq, all_pieces & ROOK_MASKS[sq])]
                else: atts = ROOK_TABLE[(sq, all_pieces & ROOK_MASKS[sq])] | BISHOP_TABLE[(sq, all_pieces & BISHOP_MASKS[sq])]
                
                score_adj += atts.bit_count() # basic mobility
                if atts & enemy_king_zone: score_adj += 15 * (atts & enemy_king_zone).bit_count() # king safety
                pieces &= pieces - 1
        
        evaluation += score_adj if colour == WHITE else -score_adj

    # mop up
    if mg_phase < int(MAX_PHASE * 0.4): 
        score_no_mopup = evaluation if state.player == WHITE else -evaluation
        if score_no_mopup > 200: evaluation += get_mop_up_score(state, state.player)
        elif score_no_mopup < -200: evaluation += get_mop_up_score(state, not state.player)
    
    return evaluation if state.player == WHITE else -evaluation