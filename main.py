from engine.utils import BitBoard

board = 0x0000000000000000 # empty board initialisation for testing

A2 = BitBoard.algebraic_to_bit("A2") # number representation for square 'a2'
A1 = BitBoard.algebraic_to_bit("A1") # number representation for square 'a1'
H6 = BitBoard.algebraic_to_bit("H6") # number representation for square 'h6'

board = BitBoard.set_bit(board, A2) # sets square 'a2'
board = BitBoard.set_bit(board, A1) # sets square 'a1'

print("Y\n" if BitBoard.check_bit(board, A1) else "N\n") # checks if square 'a1' has been set
print("Y\n" if BitBoard.check_bit(board, H6) else "N\n") # checks if square 'h6' has been set

BitBoard.pprint(board) # debug print of board