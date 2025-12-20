from dataclasses import dataclass
from typing import Optional

from engine.core.utils import BitBoard

QUIET = 0 # 0000: normal move
CAPTURE = 1 # 0001: captures enemy piece
PROMOTION = 2 # 0010: pawn promotion
EP_CAPTURE = 4 # 0100: en-passant capture
CASTLE = 8 # 1000: castling move

@dataclass(frozen=True, slots=True)
class Move:
    start: int
    target: int
    flag: int = QUIET
    promo_type: Optional[str] = None

    @property
    def is_capture(self) -> bool:
        """True if move captures a piece"""
        return bool(self.flag & (CAPTURE | EP_CAPTURE))
    
    @property
    def is_promotion(self) -> bool:
        """True if move is a promotion"""
        return bool(self.flag & PROMOTION)
    
    @property
    def is_en_passant(self) -> bool:
        """True if move is en passant capture"""
        return bool(self.flag & EP_CAPTURE)
    
    @property
    def is_castle(self) -> bool:
        """True if move is castling"""
        return bool(self.flag & CASTLE)
    
    @property
    def is_quiet(self) -> bool:
        """True if move has no special flags"""
        return self.flag == QUIET

    def __str__(self):
        """Convert move object to UCI format"""

        # Not supported by UCI 
        """
        if self.flag & CASTLE:
            if (self.target % 8) > (self.start % 8):
                return "O-O"
            else:
                return "O-O-O"
        """
        
        start_sq = BitBoard.bit_to_algebraic(self.start)
        target_sq = BitBoard.bit_to_algebraic(self.target)
        
        move_str = start_sq + target_sq
        
        if self.flag & PROMOTION:
            p_char = self.promo_type if self.promo_type else 'q'
            move_str += p_char.lower()
            
        return move_str