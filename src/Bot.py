from TicTacToe import *

class Bot:
    """
    Class for a bot player in the game. Uses the minimax algorithm to determine the best move to make.
    
    Attributes:
        game [TicTacToe]: The game object for the game the bot is playing.
        player [int]: The player number of the bot.
    
    Methods:
        evaluate_state(game: TicTacToe, player: int) -> float:
            Static method that evaluates the state of the game and returns a score for the given player.
        
        minimax(game: TicTacToe, depth: int, maximizing: bool, alpha: float, beta: float) -> float:
            Recursive function that implements the minimax algorithm to determine the score of a game
                state.
        
        get_move() -> Point:
            Searches all possible moves to determine the best move to make using the minimax algorithm.
    """
    game: TicTacToe
    player: int

    def __init__(self, game: TicTacToe, player: int) -> None:
        """
        Constructor for the Bot class.
        """
        self.game = game
        self.player = player

    @staticmethod
    def evaluate_state(game: TicTacToe, player: int) -> float:
        """
        Static method that evaluates the state of the game and returns a score for the given player.
        
        Parameters:
            game [TicTacToe]: The game object to evaluate.
            player [int]: The player number to evaluate the game for.
        
        Returns [float]: The score of the game state for the given player.
        """
        if game.winners() == [player]:
            return 10
        elif len(game.winners()) == 1:
            return -10
        elif len(game.winners()) > 1:
            return 0.0
        else:
            score = 0.0
            for move in game.available_moves():
                game_copy = game.copy()
                game_copy.try_move(move)
                if game_copy.winners() == [player]:
                    score += 0.5
                elif len(game_copy.winners()) == 1:
                    score -= 0.5
            return score

    def minimax(self, game: TicTacToe, depth: int, maximizing: bool, alpha: float, beta: float) -> float:
        """
        Recursive function that implements the minimax algorithm to determine the score of a game state.
        
        Parameters:
            game [TicTacToe]: The game object to evaluate.
            depth [int]: The depth of the search tree to evaluate.
            maximizing [bool]: Whether the current player is maximizing or minimizing.
            alpha [float]: The alpha value for the alpha-beta pruning.
            beta [float]: The beta value for the alpha-beta pruning.
        
        Returns [float]: The score of the game state for the given player.
        """
        if depth == 0 or game.game_over:
            return Bot.evaluate_state(game, self.player)

        if maximizing:
            max_eval = float("-inf")
            for move in game.available_moves():
                game_copy = game.copy()
                game_copy.try_move(move)
                eval = self.minimax(game_copy, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in game.available_moves():
                game_copy = game.copy()
                game_copy.try_move(move)
                eval = self.minimax(game_copy, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_move(self) -> Point:
        """
        Searches all possible moves to determine the best move to make using the minimax algorithm.
        
        Returns [Point]: The best move to make.
        """
        best_eval = float("-inf")
        available_moves = self.game.available_moves()

        for move in available_moves:
            game_copy = self.game.copy()
            game_copy.try_move(move)
            if self.game.size == 3:
                eval = self.minimax(game_copy, len(available_moves), False, float("-inf"), float("inf"))
            else:
                eval = self.minimax(game_copy, min(8 - self.game.size, len(available_moves)),
                                    False, float("-inf"), float("inf"))
            if eval > best_eval:
                best_eval = eval
                best_move = move

        return best_move
