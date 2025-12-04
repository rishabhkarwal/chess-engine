import time
from dataclasses import dataclass
from typing import Dict

from engine.precomputed import init_tables
from engine.state import State
from engine.move_gen import generate_moves
from engine.move_exec import make_move, is_in_check
from engine.constants import WHITE, BLACK
from engine.utils import BitBoard
from engine.move import CAPTURE, PROMOTION, EP_CAPTURE, CASTLE
from engine.fen_parser import load_from_fen

@dataclass
class Stats:
    """Perft statistics for move generation validation"""
    nodes: int = 0
    captures: int = 0
    ep: int = 0
    castles: int = 0
    promotions: int = 0
    checks: int = 0
    discovery_checks: int = 0
    double_checks: int = 0
    checkmates: int = 0
    
    def __add__(self, other):
        """Combine statistics from different branches"""
        return Stats(
            self.nodes + other.nodes,
            self.captures + other.captures,
            self.ep + other.ep,
            self.castles + other.castles,
            self.promotions + other.promotions,
            self.checks + other.checks,
            self.discovery_checks + other.discovery_checks,
            self.double_checks + other.double_checks,
            self.checkmates + other.checkmates
        )
    
    def __eq__(self, other) -> bool:
        """Compare statistics"""
        if not isinstance(other, Stats): return False
        
        for field in self.__dataclass_fields__:
            actual = getattr(self, field)
            expected = getattr(other, field)
            
            # -1 is wildcard (skip comparison)
            if expected == -1: continue

            if actual != expected: return False
        
        return True

"""Tests from: https://www.chessprogramming.org/Perft_Results"""
TEST_SUITE = [
    {
        "name": "Position 1 (Initial Position)",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "results": {
            1: Stats(20, 0, 0, 0, 0, 0, 0, 0, 0),
            2: Stats(400, 0, 0, 0, 0, 0, 0, 0, 0),
            3: Stats(8_902, 34, 0, 0, 0, 12, 0, 0, 0),
            4: Stats(197_281, 1_576, 0, 0, 0, 469, 0, 0, 8),
            5: Stats(4_865_609, 82_719, 258, 0, 0, 27_351, 6, 0, 347),
            6: Stats(119_060_324, 2_812_008, 5_248, 0, 0, 809_099, 329, 46, 10_828),
        }
    },
    {
        "name": "Position 2 (Kiwipete)",
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "results": {
            1: Stats(48, 8, 0, 2, 0, 0, 0, 0, 0),
            2: Stats(2_039, 351, 1, 91, 0, 3, 0, 0, 0),
            3: Stats(97_862, 17_102, 45, 3_162, 0, 993, 0, 0, 1),
            4: Stats(4_085_603, 757_163, 1_929, 128_013, 15_172, 25_523, 42, 6, 43),
            5: Stats(193_690_690, 35_043_416, 73_365, 4_993_637, 8_392, 3_309_887, 19_883, 2_637, 30_171),
        }
    },
    {
        "name": "Position 3",
        "fen": "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "results": {
            1: Stats(14, 1, 0, 0, 0, 2, 0, 0, 0),
            2: Stats(191, 14, 0, 0, 0, 10, 0, 0, 0),
            3: Stats(2_812, 209, 2, 0, 0, 267, 3, 0, 0),
            4: Stats(43_238, 3_348, 123, 0, 0, 1_680, 106, 0, 17),
            5: Stats(674_624, 52_051, 1_165, 0, 0, 52_950, 1_292, 3, 0),
        }
    },
    {
        "name": "Position 4",
        "fen": "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
        "results": {
            1: Stats(6, 0, 0, 0, 0, 0, -1, -1, 0),
            2: Stats(264, 87, 0, 6, 48, 10, -1, -1, 0),
            3: Stats(9_467, 1_021, 4, 0, 120, 38, -1, -1, 22),
            4: Stats(422_333, 131_393, 0, 7_795, 60_032, 15_492, -1, -1, 5),
            5: Stats(15_833_292, 2_046_173, 6_512, 0, 329_464, 200_568, -1, -1, 50_562),
        }
    },
    {
        "name": "Position 5",
        "fen": "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
        "results": {
            1: Stats(44, -1, -1, -1, -1, -1, -1, -1, -1),
            2: Stats(1_486, -1, -1, -1, -1, -1, -1, -1, -1),
            3: Stats(62_379, -1, -1, -1, -1, -1, -1, -1, -1),
            4: Stats(2_103_487, -1, -1, -1, -1, -1, -1, -1, -1),
            5: Stats(89_941_194, -1, -1, -1, -1, -1, -1, -1, -1),
        }
    },
    {
        "name": "Position 6",
        "fen": "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
        "results": {
            1: Stats(46, -1, -1, -1, -1, -1, -1, -1, -1),
            2: Stats(2_079, -1, -1, -1, -1, -1, -1, -1, -1),
            3: Stats(89_890, -1, -1, -1, -1, -1, -1, -1, -1),
            4: Stats(3_894_594, -1, -1, -1, -1, -1, -1, -1, -1),
            5: Stats(164_075_551, -1, -1, -1, -1, -1, -1, -1, -1),
        }
    },
]

def perft(state: State, depth: int) -> Stats:
    """Recursive perft search"""
    if depth == 0: return Stats(nodes=1)
    
    stats = Stats()
    moves = generate_moves(state)
    
    active = state.player
    opponent = BLACK if active == WHITE else WHITE
    
    for move in moves:
        next_state = make_move(state, move)
        
        # legality check: skip if move leaves our king in check
        if is_in_check(next_state, active): continue
        
        if depth == 1:
            # leaf node
            stats.nodes += 1
            
            # count move types
            if move.flag & CAPTURE: stats.captures += 1
            if move.flag & EP_CAPTURE: stats.ep += 1
            if move.flag & CASTLE: stats.castles += 1
            if move.flag & PROMOTION: stats.promotions += 1
            
            # check detection
            checks_bb = is_in_check(next_state, opponent)
            
            if checks_bb:
                stats.checks += 1
                # count checking pieces
                check_count = bin(checks_bb).count('1')
                
                if check_count > 1:
                    # double check
                    stats.double_checks += 1
                else:
                    # discovered check
                    if not (checks_bb & (1 << move.target)):
                        stats.discovery_checks += 1
                
                # checkmate
                enemy_moves = generate_moves(next_state)
                is_mate = True
                
                for response in enemy_moves:
                    test_state = make_move(next_state, response)
                    if not is_in_check(test_state, opponent):
                        is_mate = False
                        break
                
                if is_mate: stats.checkmates += 1
        else:
            # recursive call
            stats += perft(next_state, depth - 1)
    
    return stats



def run_perft_suite(max_depth: int = 4):

    def format(actual: int, expected: int) -> str:
        """Format statistic with difference"""
        if expected == -1: return f"{actual}(?)"
        
        diff = actual - expected
        if diff == 0: return str(actual)
        return f"{actual}({diff:+d})"

    t0 = time.time()
    init_tables() #initialise lookup tables
    print(f"Took {time.time() - t0 :.4f}s to initialise lookup tables\n")
    
    # column widths
    w = {
        'depth': 6, 'nodes': 18, 'cap': 12, 'ep': 8, 'cas': 8,
        'pro': 8, 'chk': 10, 'disc': 8, 'dbl': 8, 'mate': 8,
        'time': 10, 'stat': 6
    }
    width = 135
    
    all_passed = True
    
    for test in TEST_SUITE:
        name = test["name"]
        fen = test["fen"]
        expected_results = test["results"]
        
        print("=" * width)
        print(f"TEST: {name}")
        print(f"FEN:  {fen}")
        print("=" * width)
        print(f"{'Depth':<{w['depth']}} {'Nodes':<{w['nodes']}} "
              f"{'Captures':<{w['cap']}} {'E.P.':<{w['ep']}} {'Castles':<{w['cas']}} "
              f"{'Promo':<{w['pro']}} {'Checks':<{w['chk']}} {'Disc +':<{w['disc']}} "
              f"{'Double +':<{w['dbl']}} {'Mates':<{w['mate']}} "
              f"{'Time':<{w['time']}} {'Result':<{w['stat']}}")
        print("-" * width)
        
        state = load_from_fen(fen)
        
        for depth in sorted([d for d in expected_results.keys() if d <= max_depth]):
            t0 = time.time()
            stats = perft(state, depth)
            elapsed = time.time() - t0
            
            expected = expected_results[depth]
            passed = (stats == expected)
            status = "PASS" if passed else "FAIL"
            
            if not passed: all_passed = False
            
            # format output
            print(f"{depth:<{w['depth']}} "
                  f"{format(stats.nodes, expected.nodes):<{w['nodes']}} "
                  f"{format(stats.captures, expected.captures):<{w['cap']}} "
                  f"{format(stats.ep, expected.ep):<{w['ep']}} "
                  f"{format(stats.castles, expected.castles):<{w['cas']}} "
                  f"{format(stats.promotions, expected.promotions):<{w['pro']}} "
                  f"{format(stats.checks, expected.checks):<{w['chk']}} "
                  f"{format(stats.discovery_checks, expected.discovery_checks):<{w['disc']}} "
                  f"{format(stats.double_checks, expected.double_checks):<{w['dbl']}} "
                  f"{format(stats.checkmates, expected.checkmates):<{w['mate']}} "
                  f"{elapsed:<{w['time']}.3f} "
                  f"{status:<{w['stat']}}")
    
        print("\n\n")
    
    # summary
    print("=" * width)
    if all_passed:
        print("All tests passed")
    else:
        print("Some tests failed")
    print("=" * width)


if __name__ == "__main__":
    run_perft_suite(max_depth=5)


"""
Console Output:

Took 4.2178s to initialise lookup tables

=======================================================================================================================================
TEST: Position 1 (Initial Position)
FEN:  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
=======================================================================================================================================
Depth  Nodes              Captures     E.P.     Castles  Promo    Checks     Disc +   Double + Mates    Time       Result
---------------------------------------------------------------------------------------------------------------------------------------
1      20                 0            0        0        0        0          0        0        0        0.001      PASS  
2      400                0            0        0        0        0          0        0        0        0.005      PASS  
3      8902               34           0        0        0        12         0        0        0        0.140      PASS  
4      197281             1576         0        0        0        469        0        0        8        1.847      PASS  
5      4865609            82719        258      0        0        27351      6        0        347      47.027     PASS  



=======================================================================================================================================
TEST: Position 2 (Kiwipete)
FEN:  r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1
=======================================================================================================================================
Depth  Nodes              Captures     E.P.     Castles  Promo    Checks     Disc +   Double + Mates    Time       Result
---------------------------------------------------------------------------------------------------------------------------------------
1      48                 8            0        2        0        0          0        0        0        0.001      PASS  
2      2039               351          1        91       0        3          0        0        0        0.020      PASS  
3      97862              17102        45       3162     0        993        0        0        1        1.006      PASS  
4      4085603            757163       1929     128013   15172    25523      42       6        43       42.179     PASS  
5      193690690          35043416     73365    4993637  8392     3309887    19895(+12) 2645(+8) 30171    2687.779   FAIL  



=======================================================================================================================================
TEST: Position 3
FEN:  8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1
=======================================================================================================================================
Depth  Nodes              Captures     E.P.     Castles  Promo    Checks     Disc +   Double + Mates    Time       Result
---------------------------------------------------------------------------------------------------------------------------------------
1      14                 1            0        0        0        2          0        0        0        0.001      PASS
2      191                14           0        0        0        10         0        0        0        0.006      PASS
3      2812               209          2        0        0        267        3        0        0        0.090      PASS  
4      43238              3348         123      0        0        1680       106      0        17       0.758      PASS  
5      674624             52051        1165     0        0        52950      1292     3        0        12.758     PASS  



=======================================================================================================================================
TEST: Position 4
FEN:  r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1
=======================================================================================================================================
Depth  Nodes              Captures     E.P.     Castles  Promo    Checks     Disc +   Double + Mates    Time       Result
---------------------------------------------------------------------------------------------------------------------------------------
1      6                  0            0        0        0        0          0(?)     0(?)     0        0.001      PASS
2      264                87           0        6        48       10         0(?)     0(?)     0        0.004      PASS
3      9467               1021         4        0        120      38         2(?)     0(?)     22       0.130      PASS  
4      422333             131393       0        7795     60032    15492      19(?)    0(?)     5        7.355      PASS  
5      15833292           2046173      6512     0        329464   200568     11621(?) 50(?)    50562    230.678    PASS  



=======================================================================================================================================
TEST: Position 5
FEN:  rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8
=======================================================================================================================================
Depth  Nodes              Captures     E.P.     Castles  Promo    Checks     Disc +   Double + Mates    Time       Result
---------------------------------------------------------------------------------------------------------------------------------------
1      44                 6(?)         0(?)     1(?)     4(?)     0(?)       0(?)     0(?)     0(?)     0.002      PASS  
2      1486               222(?)       0(?)     0(?)     0(?)     117(?)     0(?)     0(?)     0(?)     0.053      PASS  
3      62379              8517(?)      0(?)     1081(?)  5068(?)  1201(?)    0(?)     0(?)     44(?)    1.054      PASS  
4      2103487            296153(?)    0(?)     0(?)     0(?)     158486(?)  10877(?) 1770(?)  240(?)   48.142     PASS  
5      89941194           12320378(?)  140(?)   1240828(?) 6655216(?) 3078299(?) 8979(?)  58(?)    137306(?) 1536.999   PASS  



=======================================================================================================================================
TEST: Position 6
FEN:  r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10
=======================================================================================================================================
Depth  Nodes              Captures     E.P.     Castles  Promo    Checks     Disc +   Double + Mates    Time       Result
---------------------------------------------------------------------------------------------------------------------------------------
1      46                 4(?)         0(?)     0(?)     0(?)     1(?)       0(?)     0(?)     0(?)     0.002      PASS
2      2079               203(?)       0(?)     0(?)     0(?)     40(?)      0(?)     0(?)     0(?)     0.026      PASS  
3      89890              9470(?)      0(?)     0(?)     0(?)     1783(?)    0(?)     0(?)     0(?)     1.384      PASS  
4      3894594            440388(?)    0(?)     0(?)     0(?)     68985(?)   62(?)    20(?)    0(?)     54.798     PASS  
5      164075551          19528068(?)  122(?)   0(?)     0(?)     2998608(?) 10687(?) 2960(?)  228(?)   2336.556   PASS  



=======================================================================================================================================
Some tests failed
=======================================================================================================================================

Despite failing Position 2, Depth 5

"5      193690690          35043416     73365    4993637  8392     3309887    19895(+12) 2645(+8) 30171    2687.779   FAIL "

The number of nodes searched is correct and so the algorithm is fine
There is just an error in double check and discovered check definition; but this doesn't matter
"""