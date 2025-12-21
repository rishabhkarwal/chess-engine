from engine.core.utils import BitBoard
from engine.core.constants import MASK_SOURCE, MASK_TARGET, MASK_FLAG

# flag constants (4 bits: 12-15)

QUIET = 0 # 0000
DOUBLE_PUSH = 1 # 0001
CASTLE_KS = 2 # 0010 (Kingside)
CASTLE_QS = 3 # 0011 (Queenside)
CAPTURE = 4 # 0100
EP_CAPTURE = 5 # 0101

# promotions (encoding: 1xxx)
PROMOTION_N = 8 # 1000
PROMOTION_B = 9 # 1001
PROMOTION_R = 10 # 1010
PROMOTION_Q = 11 # 1011

# promotion-captures (encoding: 11xx)
PROMO_CAP_N     = 12 # 1100
PROMO_CAP_B     = 13 # 1101
PROMO_CAP_R     = 14 # 1110
PROMO_CAP_Q     = 15 # 1111

# lookup map for promotion characters
PROMO_CHARS = {
    PROMOTION_N: 'n', PROMOTION_B: 'b', PROMOTION_R: 'r', PROMOTION_Q: 'q',
    PROMO_CAP_N: 'n', PROMO_CAP_B: 'b', PROMO_CAP_R: 'r', PROMO_CAP_Q: 'q'
}

def pack_move(start: int, target: int, flag: int = QUIET) -> int:
    """Creates a 16-bit integer move"""
    return start | (target << 6) | (flag << 12)

def get_start(move: int) -> int:
    return move & MASK_SOURCE

def get_target(move: int) -> int:
    return (move & MASK_TARGET) >> 6

def get_flag(move: int) -> int:
    return (move & MASK_FLAG) >> 12

def is_capture(move: int) -> bool:
    """Returns if the move is a capture"""
    flag = (move & MASK_FLAG) >> 12
    return flag == CAPTURE or flag == EP_CAPTURE or flag >= PROMO_CAP_N

def is_promotion(move: int) -> bool:
    """Returns if the move is a promotion"""
    flag = (move & MASK_FLAG) >> 12
    return flag >= PROMOTION_N

def is_en_passant(move: int) -> bool:
    """Returns if the move is en-passant"""
    flag = (move & MASK_FLAG) >> 12
    return flag == EP_CAPTURE

def is_castle(move: int) -> bool:
    """Returns if the move is castling"""
    flag = (move & MASK_FLAG) >> 12
    return flag == CASTLE_KS or flag == CASTLE_QS

def get_promo_piece(move: int) -> str:
    """Returns 'q', 'r', 'b', or 'n'"""
    flag = (move & MASK_FLAG) >> 12
    return PROMO_CHARS.get(flag, 'q')

def move_to_uci(move: int) -> str:
    """Converts integer move to UCI string"""
    start = move & MASK_SOURCE
    target = (move & MASK_TARGET) >> 6
    flag = (move & MASK_FLAG) >> 12
    
    uci_str = BitBoard.bit_to_algebraic(start) + BitBoard.bit_to_algebraic(target)
    
    if flag >= PROMOTION_N:
        uci_str += PROMO_CHARS[flag]
        
    return uci_str