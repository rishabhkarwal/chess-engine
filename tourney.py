from gui.tournament import Tournament
from gui.config import Config

if __name__ == '__main__':
    new = 'sophia/engine.bat'
    old = 'benchmark/engine.bat'
    n_bullet = 30
    n_blitz = 40
    n_rapid = 20

    bullet = Config(engine_1_path=new, engine_2_path=old, time_control=2 * 60, increment=1, total_games=n_bullet) # 1 + 0
    blitz = Config(engine_1_path=new, engine_2_path=old, time_control=3 * 60, increment=1, total_games=n_blitz) # 3 + 2
    rapid = Config(engine_1_path=new, engine_2_path=old, time_control=5 * 60, increment=5, total_games=n_rapid) # 10 + 1

    for settings in [bullet, blitz, rapid]:
        tourney = Tournament(settings)
        tourney.run()