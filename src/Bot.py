from copy import deepcopy
from TicTacToe import TicTacToe

class Bot:
    game: TicTacToe
    player: int
    
    def __init__(self, game: TicTacToe, player: int) -> None:
        self.game = game
        self.player = player
    
    @staticmethod
    def evaluate_state(game: TicTacToe, player: int) -> float:
        if player in game.winners():
            return 10
