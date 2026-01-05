import re
from collections import defaultdict, Counter

def parse_games(pgn_text):
    raw_games = re.split(r'(?=\[Event\s)', pgn_text.strip())
    games = []
    header_regex = re.compile(r'^\[([A-Za-z0-9_]+)\s+"([^"]*)"\]\s*$', re.MULTILINE)

    for raw in raw_games:
        if not raw.strip(): continue
        headers = dict(header_regex.findall(raw))
        if headers:
            games.append(headers)
    return games

def get_points(result):
    result = result.strip()
    if result == '1-0': return 1.0, 0.0, 'win'
    if result == '0-1': return 0.0, 1.0, 'loss'
    if result in ('1/2-1/2', '½-½', '1/2–1/2'): return 0.5, 0.5, 'draw'
    return 0.0, 0.0, 'unknown'

def analyse_tournament(games):
    stats = defaultdict(lambda: {
        'games': 0,
        'players': defaultdict(lambda: {
            'score': 0.0, 'wins': 0, 'draws': 0, 'losses': 0,
            'reasons': defaultdict(Counter) 
        })
    })

    for g in games:
        tc = g.get('TimeControl', 'Unknown TC')
        white = g.get('White', 'White')
        black = g.get('Black', 'Black')
        result = g.get('Result', '*')
        termination = g.get('Termination', 'normal')

        for category in [tc, "Overall"]:
            s = stats[category]
            s['games'] += 1
            
            w_pts, b_pts, res_type = get_points(result)

            p_white = s['players'][white]
            p_white['score'] += w_pts

            p_black = s['players'][black]
            p_black['score'] += b_pts

            if w_pts == 1.0:
                p_white['wins'] += 1
                p_white['reasons']['win'][termination] += 1
                p_black['losses'] += 1
                p_black['reasons']['loss'][termination] += 1
            
            elif b_pts == 1.0:
                p_black['wins'] += 1
                p_black['reasons']['win'][termination] += 1
                p_white['losses'] += 1
                p_white['reasons']['loss'][termination] += 1
            
            elif w_pts == 0.5:
                p_white['draws'] += 1
                p_white['reasons']['draw'][termination] += 1
                p_black['draws'] += 1
                p_black['reasons']['draw'][termination] += 1

    return stats

def format_reasons(reason_dict):
    if not reason_dict: return ""
    items = [f"{k}:{v}" for k, v in reason_dict.items()]
    return f"[{', '.join(items)}]"

def print_results(stats):
    categories = sorted([k for k in stats.keys() if k != "Overall"]) + ["Overall"]
    
    for cat in categories:
        if cat not in stats: continue
        data = stats[cat]
        
        print("-" * 60)
        print(f"TimeControl: {cat} (Games: {data['games']})")
        print("-" * 60)

        ranking = sorted(data['players'].items(), key=lambda x: x[1]['score'], reverse=True)

        for name, p_data in ranking:
            print(f"{name:12s} : {p_data['score']:5.1f} pts  (W:{p_data['wins']} D:{p_data['draws']} L:{p_data['losses']})")

            if p_data['wins'] > 0:
                print(f"    Wins   : {format_reasons(p_data['reasons']['win'])}")
            if p_data['draws'] > 0:
                print(f"    Draws  : {format_reasons(p_data['reasons']['draw'])}")
            if p_data['losses'] > 0:
                print(f"    Losses : {format_reasons(p_data['reasons']['loss'])}")
            print()

        if ranking:
            top_score = ranking[0][1]['score']
            winners = [n for n, d in ranking if d['score'] == top_score]
            if len(winners) > 1:
                print(f">> Result: Tie between {', '.join(winners)}")
            else:
                print(f">> Winner: {winners[0]}")
        print("\n")

if __name__ == '__main__':
    path = 'games.pgn'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            pgn_content = f.read()
        
        games_list = parse_games(pgn_content)
        if not games_list:
            print("No games found in file")
        else:
            tournament_stats = analyse_tournament(games_list)
            print_results(tournament_stats)
            
    except FileNotFoundError:
        print(f"Error: File '{path}' not found")

"""
From debugging and analysing the game logs - illegal moves were returned because game would end due to time and the bestmove would send just when the next game started => illegal move

Although score is ~50 / 50; new version has more checkmates

NOTE: benchmark is previous version

------------------------------------------------------------
TimeControl: 180+1 (Games: 40)
------------------------------------------------------------
benchmark    :  26.5 pts  (W:21 D:11 L:8)
    Wins   : [Checkmate:7, Time Forfeit:13, Illegal Move (e7e5):1]
    Draws  : [Fivefold Repetition:11]
    Losses : [Checkmate:8]

sophia       :  13.5 pts  (W:8 D:11 L:21)
    Wins   : [Checkmate:8]
    Draws  : [Fivefold Repetition:11]
    Losses : [Checkmate:7, Time Forfeit:13, Illegal Move (e7e5):1]

>> Winner: benchmark


------------------------------------------------------------
TimeControl: 60+0 (Games: 40)
------------------------------------------------------------
sophia       :  25.0 pts  (W:23 D:4 L:13)
    Wins   : [Checkmate:16, Time Forfeit:7]
    Draws  : [Fivefold Repetition:4]
    Losses : [Checkmate:7, Time Forfeit:6]

benchmark    :  15.0 pts  (W:13 D:4 L:23)
    Wins   : [Checkmate:7, Time Forfeit:6]
    Draws  : [Fivefold Repetition:4]
    Losses : [Checkmate:16, Time Forfeit:7]

>> Winner: sophia


------------------------------------------------------------
TimeControl: 600+1 (Games: 19)
------------------------------------------------------------
sophia       :  11.5 pts  (W:10 D:3 L:6)
    Wins   : [Checkmate:6, Time Forfeit:1, Illegal Move (e6d6):1, Illegal Move (g1f3):1, Illegal Move (c7c5):1]
    Draws  : [Fivefold Repetition:3]
    Losses : [Checkmate:5, Illegal Move (0000):1]

benchmark    :   7.5 pts  (W:6 D:3 L:10)
    Wins   : [Checkmate:5, Illegal Move (0000):1]
    Draws  : [Fivefold Repetition:3]
    Losses : [Checkmate:6, Time Forfeit:1, Illegal Move (e6d6):1, Illegal Move (g1f3):1, Illegal Move (c7c5):1]

>> Winner: sophia


------------------------------------------------------------
TimeControl: Overall (Games: 99)
------------------------------------------------------------
sophia       :  50.0 pts  (W:41 D:18 L:40)
    Wins   : [Checkmate:30, Time Forfeit:8, Illegal Move (e6d6):1, Illegal Move (g1f3):1, Illegal Move (c7c5):1]
    Draws  : [Fivefold Repetition:18]
    Losses : [Checkmate:19, Time Forfeit:19, Illegal Move (e7e5):1, Illegal Move (0000):1]

benchmark    :  49.0 pts  (W:40 D:18 L:41)
    Wins   : [Checkmate:19, Time Forfeit:19, Illegal Move (e7e5):1, Illegal Move (0000):1]
    Draws  : [Fivefold Repetition:18]
    Losses : [Checkmate:30, Time Forfeit:8, Illegal Move (e6d6):1, Illegal Move (g1f3):1, Illegal Move (c7c5):1]

>> Winner: sophia
"""

"""
More tests: NOTE: illegal moves are still just carried over from previous games

------------------------------------------------------------
TimeControl: 120+1 (Games: 30)
------------------------------------------------------------
sophia       :  17.0 pts  (W:13 D:8 L:9)
    Wins   : [Checkmate:9, Time Forfeit:4]
    Draws  : [Insufficient Material:1, Fivefold Repetition:7]
    Losses : [Checkmate:8, Time Forfeit:1]

benchmark    :  13.0 pts  (W:9 D:8 L:13)
    Wins   : [Checkmate:8, Time Forfeit:1]
    Draws  : [Insufficient Material:1, Fivefold Repetition:7]
    Losses : [Checkmate:9, Time Forfeit:4]

>> Winner: sophia


------------------------------------------------------------
TimeControl: 180+1 (Games: 40)
------------------------------------------------------------
sophia       :  26.5 pts  (W:23 D:7 L:10)
    Wins   : [Checkmate:20, Time Forfeit:3]
    Draws  : [Fivefold Repetition:7]
    Losses : [Checkmate:6, Illegal Move (0000):1, Time Forfeit:1, Illegal Move (d4e5):1, Illegal Move (c7c5):1]

benchmark    :  13.5 pts  (W:10 D:7 L:23)
    Wins   : [Checkmate:6, Illegal Move (0000):1, Time Forfeit:1, Illegal Move (d4e5):1, Illegal Move (c7c5):1]
    Draws  : [Fivefold Repetition:7]
    Losses : [Checkmate:20, Time Forfeit:3]

>> Winner: sophia


------------------------------------------------------------
TimeControl: 180+2 (Games: 32)
------------------------------------------------------------
benchmark    :  17.0 pts  (W:11 D:12 L:9)
    Wins   : [Checkmate:11]
    Draws  : [Fivefold Repetition:12]
    Losses : [Engine Crash:1, Checkmate:8]

sophia       :  15.0 pts  (W:9 D:12 L:11)
    Wins   : [Engine Crash:1, Checkmate:8]
    Draws  : [Fivefold Repetition:12]
    Losses : [Checkmate:11]

>> Winner: benchmark


------------------------------------------------------------
TimeControl: 300+5 (Games: 2)
------------------------------------------------------------
benchmark    :   1.5 pts  (W:1 D:1 L:0)
    Wins   : [Checkmate:1]
    Draws  : [Fivefold Repetition:1]

sophia       :   0.5 pts  (W:0 D:1 L:1)
    Draws  : [Fivefold Repetition:1]
    Losses : [Checkmate:1]

>> Winner: benchmark


------------------------------------------------------------
TimeControl: 60+0 (Games: 12)
------------------------------------------------------------
sophia       :   7.5 pts  (W:7 D:1 L:4)
    Wins   : [Checkmate:6, Engine Crash:1]
    Draws  : [Fivefold Repetition:1]
    Losses : [Time Forfeit:4]

benchmark    :   4.5 pts  (W:4 D:1 L:7)
    Wins   : [Time Forfeit:4]
    Draws  : [Fivefold Repetition:1]
    Losses : [Checkmate:6, Engine Crash:1]

>> Winner: sophia


------------------------------------------------------------
TimeControl: 60+1 (Games: 20)
------------------------------------------------------------
sophia       :  15.0 pts  (W:12 D:6 L:2)
    Wins   : [Checkmate:12]
    Draws  : [Fivefold Repetition:6]
    Losses : [Checkmate:2]

benchmark    :   5.0 pts  (W:2 D:6 L:12)
    Wins   : [Checkmate:2]
    Draws  : [Fivefold Repetition:6]
    Losses : [Checkmate:12]

>> Winner: sophia


------------------------------------------------------------
TimeControl: 600+0 (Games: 20)
------------------------------------------------------------
benchmark    :  10.5 pts  (W:9 D:3 L:8)
    Wins   : [Time Forfeit:2, Checkmate:5, Illegal Move (g7h6):1, Illegal Move (e2e4):1]
    Draws  : [Fivefold Repetition:2, 75 Moves Rule:1]
    Losses : [Checkmate:7, Time Forfeit:1]

sophia       :   9.5 pts  (W:8 D:3 L:9)
    Wins   : [Checkmate:7, Time Forfeit:1]
    Draws  : [Fivefold Repetition:2, 75 Moves Rule:1]
    Losses : [Time Forfeit:2, Checkmate:5, Illegal Move (g7h6):1, Illegal Move (e2e4):1]

>> Winner: benchmark


------------------------------------------------------------
TimeControl: Overall (Games: 156)
------------------------------------------------------------
sophia       :  91.0 pts  (W:72 D:38 L:46)
    Wins   : [Engine Crash:2, Checkmate:62, Time Forfeit:8]
    Draws  : [Fivefold Repetition:36, 75 Moves Rule:1, Insufficient Material:1]
    Losses : [Checkmate:33, Time Forfeit:8, Illegal Move (g7h6):1, Illegal Move (e2e4):1, Illegal Move (0000):1, Illegal Move (d4e5):1, Illegal Move (c7c5):1]     

benchmark    :  65.0 pts  (W:46 D:38 L:72)
    Wins   : [Checkmate:33, Time Forfeit:8, Illegal Move (g7h6):1, Illegal Move (e2e4):1, Illegal Move (0000):1, Illegal Move (d4e5):1, Illegal Move (c7c5):1]     
    Draws  : [Fivefold Repetition:36, 75 Moves Rule:1, Insufficient Material:1]
    Losses : [Engine Crash:2, Checkmate:62, Time Forfeit:8]

>> Winner: sophia
"""