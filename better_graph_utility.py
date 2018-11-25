"""
graphy_utility has all utility classes for making the peg solitaire game boards.

By: Spencer Chang, Jacob Marshall

The following baseline for the following code was found at
http://interactivepython.org/courselib/static/pythonds/Graphs/Implementation.html
"""

import random
from pprint import pprint
from typing import List, Tuple

PIN = '*'
HOLE = 'O'

class Graph2:
    def __init__(self, width, height):
        # Create a width*height board full of pins (*)
        board = []
        for i in range(height):
            board.append([PIN] * width)

        # Find a random hole in the board and make it a hole
        hole_x = random.randint(0, width - 1)
        hole_y = random.randint(0, height - 1)
        board[hole_x][hole_y] = HOLE

        self.width = width - 1
        self.height = height - 1
        self.board = board

    def __getitem__(self, key):
        return self.board[key]

    def __iter__(self):
        return self.board

    def total_moves(self):
        moves = 0

        holes = self._find_holes()

        for hole in holes:
            # The '*' in this function call expands the tuple into two arguments
            moves += self._find_moves_around_hole(*hole)

        return moves

    def _find_holes(self) -> List[Tuple[int, int]]:
        holes = []

        # Go through entire board
        for i, row in enumerate(self.board):
            for j, spot in enumerate(row):
                # If you find a hole, add a tuple of the x,y coordinate to a list
                if spot == HOLE:
                    holes.append((i, j))

        return holes

    # A "move" is defined as such:
    # If there are two pins in a row in any direction around the hole, there is a move
    # HOLE PIN PIN is a move, HOLE PIN HOLE is not a move
    def _find_moves_around_hole(self, x: int, y: int) -> int:
        moves = 0

        if y <= (self.width - 2): # Check pins to the right
            if self.board[x][y+1] == PIN and self.board[x][y+2] == PIN:
                moves += 1
        if y >= 2: # Check pins to the left
            if self.board[x][y-1] == PIN and self.board[x][y-2] == PIN:
                moves += 1
        if x >= 2: # Check pins above
            if self.board[x-1][y] == PIN and self.board[x-2][y] == PIN:
                moves += 1
        if x <= (self.height - 2): # Check pins below
            if self.board[x+1][y] == PIN and self.board[x+2][y] == PIN:
                moves += 1
        return moves


# p = Graph2(5, 5)
# p[4][4] = HOLE
# pprint(p.board)
# print(p.total_moves())


