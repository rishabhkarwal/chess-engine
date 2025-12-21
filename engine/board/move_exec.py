from engine.board.state import State
from engine.core.move import (
    QUIET, CAPTURE, EP_CAPTURE, 
    CASTLE_KS, CASTLE_QS,
    PROMOTION_N, PROMOTION_B, PROMOTION_R, PROMOTION_Q,
    PROMO_CAP_N, PROMO_CAP_B, PROMO_CAP_R, PROMO_CAP_Q
)
from engine.core.constants import (
    WHITE, BLACK, NO_SQUARE,
    CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ,
    WHITE_PIECES, BLACK_PIECES, ALL_PIECES,
    A1, H1, A8, H8, E1, C1, G1, E8, C8, G8, F1, D1, F8, D8,
    MASK_SOURCE, MASK_TARGET, MASK_FLAG
)
from engine.core.utils import BitBoard
from engine.core.zobrist import ZOBRIST_KEYS

# Helper mapping for promotion flags to piece characters
# Q=11, R=10, B=9, N=8
PROMO_MAP = {
    PROMOTION_Q: 'q', PROMOTION_R: 'r', PROMOTION_B: 'b', PROMOTION_N: 'n',
    PROMO_CAP_Q: 'q', PROMO_CAP_R: 'r', PROMO_CAP_B: 'b', PROMO_CAP_N: 'n'
}

def is_threefold_repetition(state: State) -> bool:
    if not state.history: return False
    current_hash = state.hash
    count = 0
    for i in range(len(state.history) - 2, -1, -2):
        if state.history[i] == current_hash:
            count += 1
            if count >= 2: return True 
    return False

def make_null_move(state: State):
    old_ep = state.en_passant
    old_hash = state.hash
    if old_ep != NO_SQUARE:
        state.hash ^= ZOBRIST_KEYS['ep'][old_ep % 8]
    state.en_passant = NO_SQUARE
    state.hash ^= ZOBRIST_KEYS['ep'][8]
    state.player = not state.player
    state.hash ^= ZOBRIST_KEYS['black_to_move']
    return (old_ep, old_hash)

def unmake_null_move(state: State, undo_info):
    old_ep, old_hash = undo_info
    state.en_passant = old_ep
    state.hash = old_hash
    state.player = not state.player

def make_move(state: State, move: int) -> tuple:
    """Apply a move IN-PLACE. 'move' is now a 16-bit integer."""
    
    # 1. Decode Move
    start_sq = move & MASK_SOURCE
    target_sq = (move & MASK_TARGET) >> 6
    flag = (move & MASK_FLAG) >> 12
    
    # 2. Save Irreversible State
    old_hash = state.hash
    old_castling = state.castling
    old_ep = state.en_passant
    old_halfmove = state.halfmove_clock
    captured_piece = None

    bitboards = state.bitboards 
    
    if state.player == WHITE:
        active_pieces = WHITE_PIECES
        opponent_pieces = BLACK_PIECES
        active_colour = 'white'
        opponent_colour = 'black'
        ep_offset = -8
        my_pawn = 'P'
        enemy_pawn = 'p'
    else:
        active_pieces = BLACK_PIECES
        opponent_pieces = WHITE_PIECES
        active_colour = 'black'
        opponent_colour = 'white'
        ep_offset = 8
        my_pawn = 'p'
        enemy_pawn = 'P'
    
    start_mask = 1 << start_sq
    target_mask = 1 << target_sq
    
    # 3. Identify Moving Piece
    moving_piece = None
    for piece in active_pieces:
        if bitboards[piece] & start_mask:
            moving_piece = piece
            break
    
    # Remove from start
    bitboards[moving_piece] &= ~start_mask
    bitboards[active_colour] &= ~start_mask
    state.hash ^= ZOBRIST_KEYS[moving_piece][start_sq]

    # 4. Handle Captures
    # Logic: CAPTURE=4, EP=5, PROMO_CAPs >= 12
    if flag == CAPTURE or flag == EP_CAPTURE or flag >= PROMO_CAP_N:
        if flag == EP_CAPTURE:
            capture_sq = target_sq + ep_offset
            captured_piece = enemy_pawn
            cap_mask = 1 << capture_sq
            
            bitboards[captured_piece] &= ~cap_mask
            bitboards[opponent_colour] &= ~cap_mask
            state.hash ^= ZOBRIST_KEYS[captured_piece][capture_sq]
        else:
            for piece in opponent_pieces:
                if bitboards[piece] & target_mask:
                    captured_piece = piece
                    bitboards[piece] &= ~target_mask
                    bitboards[opponent_colour] &= ~target_mask
                    state.hash ^= ZOBRIST_KEYS[piece][target_sq]
                    break
    
    # 5. Place Piece at Target
    if flag >= PROMOTION_N: # Any promotion (8-15)
        promo_char = PROMO_MAP[flag]
        target_piece = promo_char.upper() if state.player == WHITE else promo_char.lower()
    else:
        target_piece = moving_piece
    
    bitboards[target_piece] |= target_mask
    bitboards[active_colour] |= target_mask
    state.hash ^= ZOBRIST_KEYS[target_piece][target_sq]
    
    # 6. Handle Castling (Rook Move)
    if flag == CASTLE_KS or flag == CASTLE_QS:
        rook_key = 'R' if state.player == WHITE else 'r'
        r_from, r_to = 0, 0
        
        if target_sq == G1: r_from, r_to = H1, F1
        elif target_sq == C1: r_from, r_to = A1, D1
        elif target_sq == G8: r_from, r_to = H8, F8
        elif target_sq == C8: r_from, r_to = A8, D8
        
        bitboards[rook_key] &= ~(1 << r_from)
        bitboards[rook_key] |= (1 << r_to)
        bitboards[active_colour] &= ~(1 << r_from)
        bitboards[active_colour] |= (1 << r_to)
        
        state.hash ^= ZOBRIST_KEYS[rook_key][r_from]
        state.hash ^= ZOBRIST_KEYS[rook_key][r_to]
        
    # 7. Update Castling Rights
    state.hash ^= ZOBRIST_KEYS['castling'][state.castling]
    
    if moving_piece == 'K': state.castling &= ~(CASTLE_WK | CASTLE_WQ)
    elif moving_piece == 'k': state.castling &= ~(CASTLE_BK | CASTLE_BQ)
    
    if start_sq == A1 or target_sq == A1: state.castling &= ~CASTLE_WQ
    if start_sq == H1 or target_sq == H1: state.castling &= ~CASTLE_WK
    if start_sq == A8 or target_sq == A8: state.castling &= ~CASTLE_BQ
    if start_sq == H8 or target_sq == H8: state.castling &= ~CASTLE_BK

    state.hash ^= ZOBRIST_KEYS['castling'][state.castling]

    # 8. Update En Passant
    state.hash ^= ZOBRIST_KEYS['ep'][state.en_passant % 8 if state.en_passant != NO_SQUARE else 8]
    state.en_passant = NO_SQUARE
    
    is_pawn = moving_piece.lower() == 'p'
    if is_pawn and abs(start_sq - target_sq) == 16:
        state.en_passant = (start_sq + target_sq) // 2
        
    state.hash ^= ZOBRIST_KEYS['ep'][state.en_passant % 8]

    # 9. Update Clocks & Sides
    if is_pawn or (flag == CAPTURE or flag >= PROMO_CAP_N): state.halfmove_clock = 0
    else: state.halfmove_clock += 1
    
    if state.player == BLACK: state.fullmove_number += 1
    
    state.player = not state.player
    state.hash ^= ZOBRIST_KEYS['black_to_move']
    
    # 10. Finalise
    bitboards['all'] = bitboards['white'] | bitboards['black']
    state.history.append(old_hash)
    
    return (captured_piece, old_castling, old_ep, old_halfmove, old_hash)

def unmake_move(state: State, move: int, undo_info: tuple):
    captured_piece, old_castling, old_ep, old_halfmove, old_hash = undo_info
    bitboards = state.bitboards
    
    # Decode
    start_sq = move & MASK_SOURCE
    target_sq = (move & MASK_TARGET) >> 6
    flag = (move & MASK_FLAG) >> 12
    
    state.history.pop()
    state.hash = old_hash
    state.castling = old_castling
    state.en_passant = old_ep
    state.halfmove_clock = old_halfmove
    state.player = not state.player
    if state.player == BLACK: state.fullmove_number -= 1
    
    if state.player == WHITE:
        active_colour, active_pieces = 'white', WHITE_PIECES
        opponent_colour = 'black'
    else:
        active_colour, active_pieces = 'black', BLACK_PIECES
        opponent_colour = 'white'
    
    start_mask = 1 << start_sq
    target_mask = 1 << target_sq
    
    # Revert Move
    if flag >= PROMOTION_N:
        # Remove promoted piece
        promo_char = PROMO_MAP[flag]
        promoted_piece = promo_char.upper() if state.player == WHITE else promo_char.lower()
        bitboards[promoted_piece] &= ~target_mask
        bitboards[active_colour] &= ~target_mask
        
        # Restore pawn
        pawn = 'P' if state.player == WHITE else 'p'
        bitboards[pawn] |= start_mask
        bitboards[active_colour] |= start_mask
    else:
        moving_piece = None
        for piece in active_pieces:
            if bitboards[piece] & target_mask:
                moving_piece = piece
                break
        
        bitboards[moving_piece] &= ~target_mask
        bitboards[moving_piece] |= start_mask
        bitboards[active_colour] &= ~target_mask
        bitboards[active_colour] |= start_mask
        
    # Restore Captured
    if captured_piece:
        if flag == EP_CAPTURE:
            ep_offset = -8 if state.player == WHITE else 8
            capture_sq = target_sq + ep_offset
            bitboards[captured_piece] |= (1 << capture_sq)
            bitboards[opponent_colour] |= (1 << capture_sq)
        else:
            bitboards[captured_piece] |= target_mask
            bitboards[opponent_colour] |= target_mask
            
    # Revert Castling
    if flag == CASTLE_KS or flag == CASTLE_QS:
        rook_key = 'R' if state.player == WHITE else 'r'
        r_from, r_to = 0, 0
        if target_sq == G1: r_from, r_to = H1, F1
        elif target_sq == C1: r_from, r_to = A1, D1
        elif target_sq == G8: r_from, r_to = H8, F8
        elif target_sq == C8: r_from, r_to = A8, D8
        
        bitboards[rook_key] &= ~(1 << r_to)
        bitboards[rook_key] |= (1 << r_from)
        bitboards[active_colour] &= ~(1 << r_to)
        bitboards[active_colour] |= (1 << r_from)

    bitboards['all'] = bitboards['white'] | bitboards['black']