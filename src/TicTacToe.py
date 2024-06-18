from copy import deepcopy
from typing import Optional

Point = tuple[int, int] # Type alias for a point in the grid

PIECES = {0: ' ', 1: 'X', 2: 'O', 3: 'V', 4: 'W'} # Characters that represent the players in the game

class Grid:
    """
    Specialized class for a square grid, a two-dimensional array of integers that is used to represent
        a TicTacToe Game State
    
    Attributes:
        size [int]: Size of the grid
        values [list[list[int]]]: Two-dimensional array of values in the grid
        transposed_values [list[list[int]]]: Transposed values of the grid
        full [bool]: Whether the grid is full, which means that there are no free spaces, or zeros,
            in the grid.
    
    Methods:
        get_cell: Returns the value of the grid at a given location
        change_value: Changes the value of the grid at a given location
    """

    size: int
    values: list[list[int]]

    def __init__(self, size: int) -> None:
        """
        Initializes the grid with a given size and sets all values to 0
        
        Arguments:
            size [int]: Size of the grid
        """
        self.size = size
        self.values = [[0 for i in range(size)] for j in range(size)]

    @property
    def transposed_values(self) -> list[list[int]]:
        """
        Transposed values of the grid
        """
        return [list(row) for row in zip(*self.values)]

    @property
    def full(self) -> bool:
        """
        Whether the grid is full, which means that there are no free spaces, or zeros, in the grid.
        """
        for row in self.values:
            if 0 in row:
                return False

        return True

    # Methods

    def get_cell(self, loc: Point) -> int:
        """
        Returns the value of the grid at a given location
        
        Inputs:
            loc [Point]: Tuple of the location wanted
        
        Returns [int]: Value at the given point
        """
        if (0 > loc[0] or loc[0] >= self.size) and (0 > loc[1] or loc[1] >= self.size):
            raise ValueError('Trying to get value outside of Grid')

        return self.values[loc[0]][loc[1]]

    def change_value(self, loc: Point, new_value: int) -> None:
        """
        Changes the value of the grid at a given location
        
        Inputs:
            loc [Point]: Tuple of the location at which the value should be changed
            new_value [int]: New value for that location in the grid
        """
        if (0 > loc[0] or loc[0] >= self.size) and (0 > loc[1] or loc[1] >= self.size):
            raise ValueError('Trying to change value outside of Grid')

        self.values[loc[0]][loc[1]] = new_value


class TicTacToe:
    """
    Class that contains the Game Logic for TicTacToe, extended to allow larger boards and more than
        2 players in a game

    Attributes:
        num_players [int]: Number of players in the game
        size [int]: Size of the board
        cur_player [int]: Current player
        grid [Grid]: Grid object that represents the game state
        game_over [bool]: Whether the game is over or not
    
    Methods:
        copy [TicTacToe]: Returns a deep copy of the current game state
        winning_line: Returns the winning line of the game, if there is one.
        winners: Returns the list of winners of the game
        try_move: Attempts to make a move in the game and returns whether the move was successful
        available_moves: Returns the list of available moves in the game state
    """

    num_players: int
    size: int
    cur_player: int
    grid: Grid

    def __init__(self, num_players: int = 2, size: int = 3) -> None:
        """
        Initializes the game with a given number of players and board size
        
        Arguments:
            num_players [int]: Number of players in the game (default 2)
            size [int]: Size of the board (default 3)
        """
        if num_players < 2:
            raise ValueError('Too few players to play game')
        if num_players > 4:
            raise ValueError('Too many players to play game')
        if size < 3:
            raise ValueError('Board is too small for a valid game')
        if size > 7:
            raise ValueError('Board is too large to play game')

        if size == 3 and num_players > 2:
            raise ValueError('Size must be greater than 3 for a game with more than 2 players')

        self.num_players = num_players
        self.size = size
        self.cur_player = 1
        self.grid = Grid(size)
    
    def __str__(self) -> str:
        """
        String representation of the current state of the game
        """
        string = '|'.join([PIECES[cell] for cell in self.grid.values[0]]) + '\n'
        for row in self.grid.values[1:]:
            string += '-' * (2 * self.size - 1) + '\n'
            string += '|'.join([PIECES[cell] for cell in row]) + '\n'

        return string

    @property
    def game_over(self) -> bool:
        """
        Whether the game is over, which is determined by checking if there a row, column, or diagonal
            which has been completely filled by a player or if there are no more empty cells in the grid
        """
        if self.grid.full:
            return True

        if (all(self.grid.values[i][i] == self.grid.values[0][0] for i in range(self.size)) and
            self.grid.values[0][0] != 0):
            return True

        if (all(self.grid.values[self.size - 1 - i][i] == self.grid.values[self.size - 1][0]
                for i in range(self.size)) and self.grid.values[self.size - 1][0] != 0):
            return True

        for row in self.grid.values:
            if all(x == row[0] for x in row) and (row[0] != 0):
                return True

        for col in self.grid.transposed_values:
            if all(x == col[0] for x in col) and (col[0] != 0):
                return True

        return False

    # Methods
    
    def copy(self) -> "TicTacToe":
        """
        Returns a deep copy of the current game state
        
        Returns [TicTacToe]: Deep copy of the current game state
        """
        return deepcopy(self)

    def winning_line(self) -> Optional[list[Point]]:
        """
        Returns the winning line of the game, which is a list of points that represent the row, column,
        
        Returns [Optional[list[Point]]]: List of points that represent the winning line of the game
        """
        if (all(self.grid.values[i][i] == self.grid.values[0][0] for i in range(self.size)) and
            self.grid.values[0][0] != 0):
            return [(i, i) for i in range(self.size)]

        if (all(self.grid.values[self.size - 1 - i][i] == self.grid.values[self.size - 1][0]
                for i in range(self.size)) and self.grid.values[self.size - 1][0] != 0):
            return [(self.size - 1 - i, i) for i in range(self.size)]

        for r in range(self.size):
            row = self.grid.values[r]
            if all(x == row[0] for x in row) and (row[0] != 0):
                return [(r, i) for i in range(self.size)]

        for c in range(self.size):
            col = self.grid.transposed_values[c]
            if all(x == col[0] for x in col) and (col[0] != 0):
                return [(i, c) for i in range(self.size)]
        
        if self.grid.full:
            return []

        return None

    def winners(self) -> list[int]:
        """
        Returns the list of winners of the game, which is a list of the players that have won the game.
            If there is no winner, an empty list is returned. If the game is a tie, a list of all players
            is returned.
        """
        line = self.winning_line()
        if line is None:
            return []

        if not line:
            return list(range(1, self.num_players + 1))

        return [self.grid.get_cell(line[0])]

    def try_move(self, move: Point) -> bool:
        """
        Attempts to make a move for the current player in the game and returns whether the move
            was successful
        
        Arguments:
            move [Point]: Tuple of the location to make the move
        
        Returns [bool]: Whether the move was successful
        """
        if self.grid.get_cell(move) != 0:
            return False

        self.grid.change_value(move, self.cur_player)
        self.cur_player = ((self.cur_player) % self.num_players) + 1

        return True

    def available_moves(self) -> list[Point]:
        """
        Returns the list of available moves in the game state, which are the locations that are empty
            in the grid
        
        Returns [list[Point]]: List of available moves in the game state
        """
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid.get_cell((r, c)) == 0:
                    moves.append((r, c))
        return moves
