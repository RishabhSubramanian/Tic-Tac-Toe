from copy import deepcopy
from TicTacToe import *

class Bot:
    game: TicTacToe
    player: int

    def __init__(self, game: TicTacToe, player: int) -> None:
        self.game = game
        self.player = player

    @staticmethod
    def evaluate_state(game: TicTacToe, player: int) -> float:
        if game.winners() == [player]:
            return 10
        elif len(game.winners()) == 1:
            return -10
        elif len(game.winners()) > 1:
            return 0.0
        else:
            score = 0.0
            for move in game.available_moves():
                game_copy = deepcopy(game)
                game_copy.try_move(move)
                if game_copy.winners() == [player]:
                    score += 0.5
                elif len(game_copy.winners()) == 1:
                    score -= 0.5
            return score

    @staticmethod
    def minimax(game: TicTacToe, depth: int, maximizing: bool, alpha: float, beta: float) -> float:
        if depth == 0 or game.game_over:
            return Bot.evaluate_state(game, 1)

        if maximizing:
            max_eval = float("-inf")
            for move in game.available_moves():
                game_copy = deepcopy(game)
                game_copy.try_move(move)
                eval = Bot.minimax(game_copy, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in game.available_moves():
                game_copy = deepcopy(game)
                game_copy.try_move(move)
                eval = Bot.minimax(game_copy, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_move(self) -> Point:
        best_eval = float("-inf")
        available_moves = self.game.available_moves()

        if len(available_moves) in (self.game.size**2, self.game.size**2 - 1):
            return available_moves[0]

        for move in available_moves:
            game_copy = deepcopy(self.game)
            game_copy.try_move(move)
            eval = Bot.minimax(game_copy, min(len(available_moves), 15-2*self.game.size), False, float("-inf"), float("inf"))
            if eval > best_eval:
                best_eval = eval
                best_move = move

        return best_move
