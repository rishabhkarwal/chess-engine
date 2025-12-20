from engine.uci.handler import UCI

def test(position='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', time_limit=2.0):
    uci = UCI(debug=True)

    print(f'Testing Position: {position}\n')

    position_args = ['fen'] + position.split()
    uci.handle_position(position_args)

    uci.engine.time_limit = time_limit * 1000
    
    best_move = uci.engine.get_best_move(uci.state)
    
    print(f'\nBest Move: {best_move}')

if __name__ == '__main__':
    fen = '8/3K4/1k6/8/8/8/7p/8 w - - 0 1 '
    time = 5
    test(position=fen, time_limit=time)