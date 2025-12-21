from engine.core.utils import BitBoard
from engine.board.state import State
from engine.core.constants import NO_SQUARE, WHITE, BLACK, CASTLE_BK, CASTLE_BQ, CASTLE_WK, CASTLE_WQ, ALL_PIECES

def load_from_fen(fen_string : str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
    state = State(
        bitboards = {piece : 0 for piece in ALL_PIECES + ('white', 'black', 'all')},
        player = None,
        castling = 0,
        en_passant = NO_SQUARE,
        halfmove_clock = 0,
        fullmove_number = 0,
        history = [],
    )

    fields = fen_string.split(' ')
    
    _parse_pieces(fields[0], state)

    _parse_active_colour(fields[1], state)

    _parse_castling_rights(fields[2], state)

    _parse_en_passant(fields[3], state)

    state.halfmove_clock = int(fields[4])

    state.fullmove_number = int(fields[5])

    return state

def _parse_pieces(pieces_fen, state):
    """Sets all bitboards"""
    square_count = 0 # square number (0 - 63)
    ranks = pieces_fen.split()[0].split('/')

    for rank in ranks:
        for square in rank:

            if square.isnumeric(): square_count += int(square)
            
            if square.isalpha(): # piece
                index = square_count ^ 56
                state.bitboards[square] = BitBoard.set_bit(state.bitboards[square], index) # updates the appropriate bitboard
                colour = 'white' if square.isupper() else 'black'
                state.bitboards[colour] = BitBoard.set_bit(state.bitboards[colour], index)
                square_count += 1

    state.bitboards['all'] = state.bitboards['white'] | state.bitboards['black']

def _parse_active_colour(colour_fen: str, state):
    """Sets the active player"""
    colour = WHITE if colour_fen == 'w' else BLACK
    state.player = colour

def _parse_castling_rights(castling_fen: str, state):
    """Sets castling rights bitmask"""
    rights = 0

    if 'K' in castling_fen: rights |= CASTLE_WK # white kingside
    if 'Q' in castling_fen: rights |= CASTLE_WQ # white queenside
    if 'k' in castling_fen: rights |= CASTLE_BK # black kingside
    if 'q' in castling_fen: rights |= CASTLE_BQ # black queenside

    state.castling = rights

def _parse_en_passant(en_passant_fen: str, state):
    """Sets en passant square index"""
    if en_passant_fen != '-': state.en_passant = BitBoard.algebraic_to_bit(en_passant_fen)