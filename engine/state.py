from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

from .constants import ALL_PIECES, WHITE_PIECES, BLACK_PIECES

@dataclass(frozen=False, slots=True)
class State:
    bitboards: Dict[str, int]
    player: int
    castling: int
    en_passant: int
    halfmove_clock: int
    fullmove_number: int
    history: List[Tuple[Any, ...]]