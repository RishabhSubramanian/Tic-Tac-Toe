import numpy as np
from copy import deepcopy
from typing import Optional

Point = tuple[int, int]

class Grid:
    """
    Specialized class for a grid, a two-dimensional array of integers that represents a TicTacToe
        Game State
    
    Attributes:
        size [int]: 
        values [list[list[int]]]: 
        transposed_values [list[list[int]]]: 
        full [bool]: 
    
    Methods:
        get_cell: 
        change_value: 
    """

    size: int
    values: list[list[int]]

    def __init__(self, size: int) -> None:
        """
        Constructor
        """
        self.size = size
        self.values = [[0 for i in range(size)] for j in range(size)]

    def __repr__(self) -> str:
        return str(np.array(self.values))

    @property
    def transposed_values(self) -> list[list[int]]:
        """
        Property that holds the matrix of values in the grid transposed
        """
        return [list(row) for row in zip(*self.values)]

    @property
    def full(self) -> bool:
        """
        Property that represents whether the grid is full, which means that there are no free spaces,
            or zeros, in the grid.
        """
        for row in self.values:
            if 0 in row:
                return False

        return True

    # Methods

    def get_cell(self, loc: Point) -> int:
        """
        Method that returns the value of the grid at a given location
        
        Inputs:
            loc [Point]: Tuple of the location wanted
        
        Returns [int]: Value at the given point
        """
        if (0 > loc[0] or loc[0] >= self.size) and (0 > loc[1] or loc[1] >= self.size):
            raise ValueError('Trying to get value outside of Grid')

        return self.values[loc[0]][loc[1]]

    def change_value(self, loc: Point, new_value: int) -> None:
        """
        Method that changes the value of the grid at a given location
        
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
        num_players [int]: 
        size [int]: 
        cur_player [int]: 
        grid [Grid]: 
        copy [TicTacToe]: 
        game_over [bool]: 

    Methods:
        winning_line: 
        winners: 
        try_move: 
    """

    num_players: int
    size: int
    cur_player: int
    grid: Grid

    def __init__(self, num_players: int = 2, size: int = 3) -> None:
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

    @property
    def copy(self) -> "TicTacToe":
        return deepcopy(self)

    @property
    def game_over(self) -> bool:
        """
        Property to check whether the game is over, which is determined by checking if there a row,
            column, or diagonal which has been completely filled by a player or if there are no more
            empty cells in the grid
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

    def winning_line(self) -> Optional[list[Point]]:
        if self.grid.full:
            return []

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

        return None

    def winners(self) -> list[int]:
        line = self.winning_line()
        if line is None:
            return []

        if not line:
            return list(range(1, self.num_players + 1))

        return [self.grid.get_cell(line[0])]

    def try_move(self, move: Point) -> bool:
        if self.grid.get_cell(move) != 0:
            return False

        self.grid.change_value(move, self.cur_player)
        self.cur_player = ((self.cur_player) % self.num_players) + 1

        return True
