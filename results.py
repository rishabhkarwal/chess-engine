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
    """Return (white_points, black_points) from result string."""
    result = result.strip()
    if result == '1-0': return 1.0, 0.0
    if result == '0-1': return 0.0, 1.0
    if result in ('1/2-1/2', '½-½', '1/2–1/2'): return 0.5, 0.5
    return 0.0, 0.0

def analyse_tournament(games):
    stats = {}

    for g in games:
        tc = g.get('TimeControl', 'UNKNOWN')
        white = g.get('White', 'White')
        black = g.get('Black', 'Black')
        result = g.get('Result', '*')

        if tc not in stats:
            stats[tc] = {
                'games': 0,
                'scores': defaultdict(float),
                'wins': Counter(),
                'draws': Counter(),
                'losses': Counter()
            }

        w_pts, b_pts = get_points(result)
        
        stats[tc]['games'] += 1
        stats[tc]['scores'][white] += w_pts
        stats[tc]['scores'][black] += b_pts

        if w_pts == 1.0:
            stats[tc]['wins'][white] += 1
            stats[tc]['losses'][black] += 1
        elif b_pts == 1.0:
            stats[tc]['wins'][black] += 1
            stats[tc]['losses'][white] += 1
        elif w_pts == 0.5:
            stats[tc]['draws'][white] += 1
            stats[tc]['draws'][black] += 1

    return stats

def print_results(stats):
    for tc, data in sorted(stats.items()):
        print(f"TimeControl: {tc}")
        print(f"  Games: {data['games']}")

        ranking = sorted(data['scores'].items(), key=lambda x: x[1], reverse=True)
        
        for name, score in ranking:
            w = data['wins'][name]
            d = data['draws'][name]
            l = data['losses'][name]
            print(f"    {name:12s} : {score:4.1f} pts  (W:{w}  D:{d}  L:{l})")

        if not ranking:
            print("  Winner: None")
        else:
            top_score = ranking[0][1]
            winners = [name for name, s in ranking if s == top_score]
            
            if len(winners) > 1:
                print(f"  Tie")
            else:
                print(f"  Winner: {winners[0]}")
        print()

if __name__ == '__main__':
    path = 'games.pgn'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            pgn_content = f.read()
        
        games_list = parse_games(pgn_content)
        tournament_stats = analyse_tournament(games_list)
        print_results(tournament_stats)
        
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")

"""
TimeControl: 60+0
  Games: 30
    sophia       : 17.5 pts  (W:13  D:9  L:8)
    indigo       : 12.5 pts  (W:8  D:9  L:13)
  Winner: sophia
"""
