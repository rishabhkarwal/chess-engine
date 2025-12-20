class BitBoard:
    @staticmethod
    def pprint(bitboard, piece = '1'):
        [print(''.join([f'{piece}  ' if (bitboard & (1 << rank * 8 + file)) else '·  ' for file in range(8)])) for rank in range(7, -1, -1)], print()
    
    @staticmethod
    def bit_scan(bitboard):
        while bitboard:
            lsb = bitboard & -bitboard  # isolate the least significant bit
            yield lsb.bit_length() - 1  # return the index of the bit
            bitboard &= bitboard - 1  # clear the least significant bit

    @staticmethod
    def set_bit(bitboard, square):
        """Sets bit at 'square' to 1"""
        return bitboard | (1 << square)

    @staticmethod
    def clear_bit(bitboard, square):
        """Sets bit at 'square' to 0"""
        return bitboard & ~(1 << square)

    @staticmethod
    def check_bit(bitboard, square):
        """Returns True if bit at 'square' is set"""
        return (bitboard >> square) & 1

    @staticmethod
    def algebraic_to_bit(square):
        file, rank = square[0], square[1]
        return (int(rank) - 1) * 8 + ord(file.lower()) - ord('a')

    @staticmethod
    def bit_to_algebraic(square):
        file, rank = square % 8, square // 8
        return f"{'abcdefgh'[file]}{rank + 1}"