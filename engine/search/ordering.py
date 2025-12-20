from engine.core.constants import WHITE, WHITE_PIECES, BLACK_PIECES, INFINITY
from engine.search.evaluation import MG_VALUES, EG_VALUES

class MoveOrdering:
    def __init__(self):
        # killer moves: [depth][slot]
        self.killer_moves = [[None] * 2 for _ in range(102)] # 100 used as arbritrary max depth
        # history table: 64 x 64 array [from sq][to sq]
        self.history_table = [[0] * 64 for _ in range(64)]
        
        self.PIECE_VALUES = {piece : (MG_VALUES[piece] + EG_VALUES[piece]) / 2 for piece in MG_VALUES}
        self.PIECE_VALUES['K'] = INFINITY 

    def store_killer(self, depth, move):
        if move.is_capture: return 
        if self.killer_moves[depth][0] == move: return
        self.killer_moves[depth][1] = self.killer_moves[depth][0]
        self.killer_moves[depth][0] = move

    def store_history(self, move, depth):
        if move.is_capture: return
        self.history_table[move.start][move.target] += depth * depth

    def _get_mvv_lva_score(self, state, move):
        if not move.is_capture: return 0
        
        target_mask = 1 << move.target
        start_mask = 1 << move.start
        
        victim_val = 0
        aggressor_val = 0
        
        if state.player == WHITE:
            # aggressor is white
            for p in WHITE_PIECES:
                if state.bitboards.get(p, 0) & start_mask:
                    aggressor_val = self.PIECE_VALUES[p]
                    break
            # victim is black
            for p in BLACK_PIECES:
                if state.bitboards.get(p, 0) & target_mask:
                    victim_val = self.PIECE_VALUES[p.upper()]
                    break
        else:
            # aggressor is black
            for p in BLACK_PIECES:
                if state.bitboards.get(p, 0) & start_mask:
                    aggressor_val = self.PIECE_VALUES[p.upper()]
                    break
            # victim is white
            for p in WHITE_PIECES:
                if state.bitboards.get(p, 0) & target_mask:
                    victim_val = self.PIECE_VALUES[p]
                    break
                
        if victim_val == 0: victim_val = 100 
            
        return (10 * victim_val) - aggressor_val

    def get_move_score(self, move, tt_move, state, depth, killer_1, killer_2):
        if move == tt_move: return INFINITY * 100
        if move.is_capture: return INFINITY * 10 + self._get_mvv_lva_score(state, move)
        if move == killer_1: return INFINITY * 9
        if move == killer_2: return INFINITY * 8
        return self.history_table[move.start][move.target]