from dataclasses import dataclass

@dataclass(frozen=False)
class State:
    """A data container for the current game position"""

    bitboards: dict[str, int]

    player: int # 0 or 1

    castling: int # 4 bit integer
    en_passant: int # en passant target square

    halfmove_clock: int
    fullmove_number: int

    history: list[tuple[any]] # to make & un-make moves