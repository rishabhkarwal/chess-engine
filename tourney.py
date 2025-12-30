from gui.tournament import Tournament
from gui.config import Config

if __name__ == '__main__':
    config = Config(time_control=600, increment=1, total_games=5)

    tourney = Tournament(config)
    tourney.run()