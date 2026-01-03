from engine.core.constants import (
    WHITE, BLACK,
    FILE_A, INFINITY, PIECE_VALUES,
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WP, WN, WB, WR, WQ, WK,
    BP, BN, BB, BR, BQ, BK,
    WHITE, BLACK, FLIP_BOARD, SQUARE_TO_BB
)
from engine.moves.precomputed import (
    KNIGHT_ATTACKS, KING_ATTACKS,
    BISHOP_MASKS, BISHOP_TABLE,
    ROOK_MASKS, ROOK_TABLE
)
from engine.search.psqt import PSQTs

# piece values
MG_VALUES = {PAWN: 82, KNIGHT: 337, BISHOP: 365, ROOK: 477, QUEEN: 1025, KING: 0}
EG_VALUES = {PAWN: 94, KNIGHT: 281, BISHOP: 297, ROOK: 512, QUEEN: 936, KING: 0}

# game phase increments
PHASE_INC = {PAWN: 0, KNIGHT: 1, BISHOP: 1, ROOK: 2, QUEEN: 4, KING: 0}
MAX_PHASE = 4 * PHASE_INC[KNIGHT] + 4 * PHASE_INC[BISHOP] + 4 * PHASE_INC[ROOK] + 2 * PHASE_INC[QUEEN]

# core features
BISHOP_PAIR_BONUS = 40
ROOK_OPEN_FILE = 10
ROOK_SEMI_OPEN_FILE = 4

# mobility bonuses (per legal square)
KNIGHT_MOBILITY = 3
BISHOP_MOBILITY = 2
ROOK_MOBILITY = 2
QUEEN_MOBILITY = 1

# king safety bonuses (pawns in front of king in opening / middlegame)
KING_PAWN_SHIELD_BONUS = 4 # per pawn in front of king

# trading behaviour parameters
WINNING_THRESHOLD = 150
LOSING_THRESHOLD = -100
TRADE_BONUS_PER_PIECE = 8
TRADE_PENALTY_PER_PIECE = 10


MG_TABLE = [[0] * 64 for _ in range(16)]
EG_TABLE = [[0] * 64 for _ in range(16)]
PHASE_WEIGHTS = [0] * 16

PASSED_PAWN_MASKS = [[0] * 64 for _ in range(2)]
FILE_MASKS = [0] * 8
ADJACENT_FILE_MASKS = [0] * 8

class PawnHashTable:
    def __init__(self, size_mb=16):
        total_bytes = size_mb * 1024 * 1024
        self.size = total_bytes // 12
        self.table = [None] * self.size
    
    def probe(self, pawn_hash):
        idx = pawn_hash % self.size
        entry = self.table[idx]
        if entry and entry[0] == pawn_hash:
            return entry[1]
        return None
    
    def store(self, pawn_hash, score):
        idx = pawn_hash % self.size
        self.table[idx] = (pawn_hash, score)

def init_eval_tables():
    piece_type_map = {
        PAWN: (PAWN, MG_VALUES[PAWN], EG_VALUES[PAWN], PHASE_INC[PAWN]),
        KNIGHT: (KNIGHT, MG_VALUES[KNIGHT], EG_VALUES[KNIGHT], PHASE_INC[KNIGHT]),
        BISHOP: (BISHOP, MG_VALUES[BISHOP], EG_VALUES[BISHOP], PHASE_INC[BISHOP]),
        ROOK: (ROOK, MG_VALUES[ROOK], EG_VALUES[ROOK], PHASE_INC[ROOK]),
        QUEEN: (QUEEN, MG_VALUES[QUEEN], EG_VALUES[QUEEN], PHASE_INC[QUEEN]),
        KING: (KING, MG_VALUES[KING], EG_VALUES[KING], PHASE_INC[KING])
    }
    
    for p_type, (base_type, mg_val, eg_val, phase_inc) in piece_type_map.items():
        mg_psqt, eg_psqt = PSQTs[base_type]
        
        w_piece = WHITE | p_type
        PHASE_WEIGHTS[w_piece] = phase_inc
        MG_TABLE[w_piece] = [mg_val + val for val in mg_psqt]
        EG_TABLE[w_piece] = [eg_val + val for val in eg_psqt]
        
        b_piece = BLACK | p_type
        PHASE_WEIGHTS[b_piece] = phase_inc
        for sq in range(64):
            flipped_sq = sq ^ FLIP_BOARD
            MG_TABLE[b_piece][sq] = -(mg_val + mg_psqt[flipped_sq])
            EG_TABLE[b_piece][sq] = -(eg_val + eg_psqt[flipped_sq])
    
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
                w_mask |= SQUARE_TO_BB[r * 8 + f_adj]
        PASSED_PAWN_MASKS[WHITE][sq] = w_mask
        
        b_mask = 0
        for r in range(rank - 1, -1, -1):
            for f_adj in range(max(0, file - 1), min(8, file + 2)):
                b_mask |= SQUARE_TO_BB[r * 8 + f_adj]
        PASSED_PAWN_MASKS[BLACK][sq] = b_mask

init_eval_tables()

def calculate_initial_score(state):
    mg, eg, phase = 0, 0, 0
    
    for p_idx in [WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK]:
        bb = state.bitboards[p_idx]
        if not bb: continue
        
        count = bb.bit_count()
        phase += PHASE_WEIGHTS[p_idx] * count

        while bb:
            lsb = bb & -bb
            sq = lsb.bit_length() - 1
            mg += MG_TABLE[p_idx][sq]
            eg += EG_TABLE[p_idx][sq]
            bb &= bb - 1

    return mg, eg, phase

def calculate_initial_passed_pawns(state):
    w_pawns = state.bitboards[WP]
    b_pawns = state.bitboards[BP]
    
    w_passed = 0
    b_passed = 0
    
    temp = w_pawns
    while temp:
        lsb = temp & -temp
        sq = lsb.bit_length() - 1
        if not (PASSED_PAWN_MASKS[WHITE][sq] & b_pawns):
            w_passed |= lsb
        temp &= temp - 1
    
    temp = b_pawns
    while temp:
        lsb = temp & -temp
        sq = lsb.bit_length() - 1
        if not (PASSED_PAWN_MASKS[BLACK][sq] & w_pawns):
            b_passed |= lsb
        temp &= temp - 1
    
    return w_passed, b_passed

def get_mop_up_score(state, winning_colour):
    winning_king_bb = state.bitboards[WK if winning_colour == WHITE else BK]
    losing_king_bb = state.bitboards[BK if winning_colour == WHITE else WK]

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

def _evaluate_pawn_structure_fast(state, w_pawns, b_pawns):
    pawn_score = 0

    PASSED_BONUS = [0, 10, 17, 15, 62, 168, 276, 0]
    
    temp = state.white_passed_pawns
    while temp:
        lsb = temp & -temp
        sq = lsb.bit_length() - 1
        rank = sq // 8
        pawn_score += PASSED_BONUS[rank]
        temp &= temp - 1
    
    temp = state.black_passed_pawns
    while temp:
        lsb = temp & -temp
        sq = lsb.bit_length() - 1
        rank = sq // 8
        pawn_score -= PASSED_BONUS[7 - rank]
        temp &= temp - 1
    
    return pawn_score

def evaluate_trading_bonus(state, base_eval):
    if abs(base_eval) < 100:
        return 0
    
    w_pieces = (state.bitboards[WN].bit_count() + state.bitboards[WB].bit_count() + 
                state.bitboards[WR].bit_count() + state.bitboards[WQ].bit_count())
    b_pieces = (state.bitboards[BN].bit_count() + state.bitboards[BB].bit_count() + 
                state.bitboards[BR].bit_count() + state.bitboards[BQ].bit_count())
    
    total_pieces = w_pieces + b_pieces
    simplification_level = 24 - total_pieces
    
    trading_adjustment = 0
    
    if base_eval > WINNING_THRESHOLD:
        trading_adjustment = simplification_level * TRADE_BONUS_PER_PIECE
    elif base_eval < LOSING_THRESHOLD:
        trading_adjustment = -simplification_level * TRADE_PENALTY_PER_PIECE
    
    return trading_adjustment

def evaluate_king_safety(state, king_sq, own_pawns, phase):
    # skip in endgame
    if phase < int(MAX_PHASE * 0.5):
        return 0
    
    king_file = king_sq % 8
    king_rank = king_sq // 8
    
    safety_score = 0
    
    # check pawns in front of king (up to 2 ranks ahead)
    if king_rank < 6: # white king
        for rank_offset in range(1, 3):
            check_rank = king_rank + rank_offset
            if check_rank > 7:
                break
            
            # check same file and adjacent files
            for file_offset in range(-1, 2):
                check_file = king_file + file_offset
                if check_file < 0 or check_file > 7:
                    continue
                
                check_sq = check_rank * 8 + check_file
                if SQUARE_TO_BB[check_sq] & own_pawns:
                    safety_score += KING_PAWN_SHIELD_BONUS
    
    return safety_score

def evaluate(state, pawn_hash_table=None):
    mg_phase = min(state.phase, MAX_PHASE)
    eg_phase = MAX_PHASE - mg_phase
    
    base_score = (state.mg_score * mg_phase + state.eg_score * eg_phase) // MAX_PHASE
    
    evaluation = base_score
    
    bitboards = state.bitboards
    all_pieces = bitboards[WHITE] | bitboards[BLACK]
    w_pawns = bitboards[WP]
    b_pawns = bitboards[BP]
    
    # bishop pair
    if bitboards[WB].bit_count() >= 2: evaluation += BISHOP_PAIR_BONUS
    if bitboards[BB].bit_count() >= 2: evaluation -= BISHOP_PAIR_BONUS

    # passed pawns
    pawn_score = _evaluate_pawn_structure_fast(state, w_pawns, b_pawns)
    evaluation += pawn_score

    # king safety (pawns in front of king in opening)
    w_king_sq = (bitboards[WK] & -bitboards[WK]).bit_length() - 1 if bitboards[WK] else -1
    b_king_sq = (bitboards[BK] & -bitboards[BK]).bit_length() - 1 if bitboards[BK] else -1
    
    if w_king_sq >= 0:
        evaluation += evaluate_king_safety(state, w_king_sq, w_pawns, state.phase)
    if b_king_sq >= 0:
        evaluation -= evaluate_king_safety(state, b_king_sq, b_pawns, state.phase)

    # rook evaluation
    for colour, rook_piece in [(WHITE, WR), (BLACK, BR)]:
        score_adj = 0
        
        temp_rooks = bitboards[rook_piece]
        while temp_rooks:
            sq = (temp_rooks & -temp_rooks).bit_length() - 1
            f = sq % 8
            if not (w_pawns & FILE_MASKS[f]) and not (b_pawns & FILE_MASKS[f]): 
                score_adj += ROOK_OPEN_FILE
            elif not ((b_pawns if colour == WHITE else w_pawns) & FILE_MASKS[f]): 
                score_adj += ROOK_SEMI_OPEN_FILE
            temp_rooks &= temp_rooks - 1
        
        evaluation += score_adj if colour == WHITE else -score_adj

    # mobility evaluation (count legal moves per piece)
    # only evaluate in middlegame as unneccesary
    if mg_phase > int(MAX_PHASE * 0.3):
        for colour, pieces in [(WHITE, [(WN, KNIGHT_MOBILITY), (WB, BISHOP_MOBILITY), (WR, ROOK_MOBILITY), (WQ, QUEEN_MOBILITY)]),
                               (BLACK, [(BN, KNIGHT_MOBILITY), (BB, BISHOP_MOBILITY), (BR, ROOK_MOBILITY), (BQ, QUEEN_MOBILITY)])]:
            mobility_score = 0
            
            for piece_key, mobility_bonus in pieces:
                piece_bb = bitboards[piece_key]
                piece_type = piece_key & ~WHITE
                
                while piece_bb:
                    sq = (piece_bb & -piece_bb).bit_length() - 1
                    
                    # count legal squares (count attacks to non-friendly squares)
                    if piece_type == KNIGHT:
                        legal_squares = (KNIGHT_ATTACKS[sq] & ~bitboards[colour]).bit_count()
                    elif piece_type == BISHOP:
                        legal_squares = (BISHOP_TABLE[sq][all_pieces & BISHOP_MASKS[sq]] & ~bitboards[colour]).bit_count()
                    elif piece_type == ROOK:
                        legal_squares = (ROOK_TABLE[sq][all_pieces & ROOK_MASKS[sq]] & ~bitboards[colour]).bit_count()
                    else: # queen
                        b_att = BISHOP_TABLE[sq][all_pieces & BISHOP_MASKS[sq]]
                        r_att = ROOK_TABLE[sq][all_pieces & ROOK_MASKS[sq]]
                        legal_squares = ((b_att | r_att) & ~bitboards[colour]).bit_count()
                    
                    mobility_score += legal_squares * mobility_bonus
                    
                    piece_bb &= piece_bb - 1
            
            evaluation += mobility_score if colour == WHITE else -mobility_score

    # trading behaviour adjustment
    trading_bonus = evaluate_trading_bonus(state, evaluation)
    evaluation += trading_bonus

    # mop up in endgame
    if mg_phase < int(MAX_PHASE * 0.4):
        score_no_mopup = evaluation if state.is_white else -evaluation
        if score_no_mopup > 200: 
            evaluation += get_mop_up_score(state, state.is_white)
        elif score_no_mopup < -200: 
            evaluation += get_mop_up_score(state, not state.is_white)
    
    return evaluation if state.is_white else -evaluation