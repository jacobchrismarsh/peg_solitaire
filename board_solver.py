"""
graphy_utility has all utility classes for making the peg solitaire game boards.

By: Spencer Chang, Jacob Marshall

The following baseline for the following code was found at
http://interactivepython.org/courselib/static/pythonds/Graphs/Implementation.html
"""

import sys
from pprint import pprint, pformat
from queue import PriorityQueue
from typing import FrozenSet, List, Tuple

PEG = '*'
HOLE = 'O'
WALL = "█"

# Define new types for this file
BoardSet = FrozenSet[Tuple[str, Tuple[int, int]]]
CompleteBoard = List[List[str]]

class PegSolitaire:
    def __init__(self, instructions: BoardSet, finished_board: CompleteBoard = None):
        board = []

        # If the user provides a complete board, just use that, no frozenset stuff
        if finished_board != None:
            self.width = len(finished_board[0]) - 1
            self.height = len(finished_board) - 1
            self.board = finished_board

        # Else go throught the frozenset and put things together
        else:
            # Find the dimensions of the board
            for item in instructions:
                if item[0] == "size":
                    width, height = item[1]

            # Create a width*height board full of holes (O)
            for i in range(height):
                board.append([HOLE] * width)

            # Add all the pegs and walls to the board
            for item in instructions:
                if item[0] == "out":
                    x, y = item[1][0] - 1, item[1][1] - 1
                    board[x][y] = WALL
                elif item[0] == "peg":
                    x, y = item[1][0] - 1, item[1][1] - 1
                    board[x][y] = PEG

            self.width = width - 1
            self.height = height - 1
            self.board = board

    def copy(self):
        """ Returns a copy of the current board """
        return PegSolitaire(None, [x[:] for x in self.board])

    # These two functions allow you to index this object, i.e. PegSolitaire[0][1]
    def __getitem__(self, key: int) -> List[str]:
        return self.board[key]
    def __iter__(self):
        return self.board

    def __repr__(self):
        """ Returns a printable version of the board """
        return pformat(self.board)

    def __lt__(self, other):
        return self.pegs_remaining() < other.pegs_remaining()

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple([tuple(b) for b in self.board]))

    def perform_move(self, x1: int, y1: int, x2: int, y2: int):
        """ Given two sets of xy coordinates, SOURCE -> DESTINATION, this will move
            the peg located at SOURCE and move it to DESTINATION

            NOTE: This does NO error checking. It assumes the move is valid
        """
        # Place a peg in the new location
        self.board[x2][y2] = PEG

        # Find out which peg you have to remove
        if x1 < x2: # Remove peg from above hole
            self.board[x2-1][y2] = HOLE
        elif x1 > x2: # Remove peg from below hole
            self.board[x2+1][y2] = HOLE
        elif y1 < y2: # Remove peg from left of hole
            self.board[x2][y2-1] = HOLE
        elif y1 > y2: # Remove peg from right of hole
            self.board[x2][y2+1] = HOLE

        # Remove old peg from its former position
        self.board[x1][y1] = HOLE

    def total_moves(self):
        """ Will return a list of available moves on a board """
        moves = []

        holes = self._find_holes()

        for hole in holes:
            # The '*' in this function call expands the tuple into two arguments
            moves += self._find_moves_around_hole(*hole)

        return moves

    def pegs_remaining(self) -> int:
        """ Returns the total amount of remaining pegs. This is used as a heuristic
            for checking if the board is solvable
        """
        pegs = 0
        for row in self.board:
            for spot in row:
                if spot == PEG:
                    pegs += 1
        return pegs

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
    # HOLE PEG PEG is a move, HOLE PEG HOLE is not a move. A move is a tuple of
    # 4 xy coordinates, representing x1, y1 moving to x2, y2. As such, the first set of
    # coordinates of a move are from the peg being moves, and the second set it the
    # place you are moving to
    def _find_moves_around_hole(self, x: int, y: int) -> int:
        moves = []

        if y <= (self.width - 2): # Check pins to the right
            if self.board[x][y+1] == PEG and self.board[x][y+2] == PEG:
                moves.append((x, y+2, x, y))
        if y >= 2: # Check pins to the left
            if self.board[x][y-1] == PEG and self.board[x][y-2] == PEG:
                moves.append((x, y-2, x, y))
        if x >= 2: # Check pins above
            if self.board[x-1][y] == PEG and self.board[x-2][y] == PEG:
                moves.append((x-2, y, x, y))
        if x <= (self.height - 2): # Check pins below
            if self.board[x+1][y] == PEG and self.board[x+2][y] == PEG:
                moves.append((x+2, y, x, y))
        return moves

def process_frozen_sets(input_file: str) -> BoardSet:
    boards = []

    with open(input_file) as f:
        lines = f.readlines()[0::2] # Grab every other line from start to EOF

        # Go through each string and convert it to a frozenset
        for line in lines:
            boards.append(eval(line))

    return boards

def a_star_solve(board: PegSolitaire) -> bool:
    board_queue = PriorityQueue()
    board_set = set()

    board_queue.put(board)

    # While the queue is not empty
    while not board_queue.empty():

        # Get a board and all its available moves.
        curr_board = board_queue.get()
        moves = curr_board.total_moves()

        # Keep track of which boards you've seen
        board_set.add(curr_board)

        # If there are no more moves, you might have found a successfull puzzle!
        if len(moves) == 0:
            # Congrats! You found a board that can be solved!
            if curr_board.pegs_remaining() == 1:
                return True
            continue

        # Do every possible move, and add each new board back into the PriorityQueue
        for move in moves:
            temp = curr_board.copy()
            temp.perform_move(*move)

            # Only add a board to the queue if you've never seen it before
            if temp not in board_set:
                board_queue.put(temp)

    return False

def main():
    fzs = process_frozen_sets(sys.argv[1])
    boards = []
    for fz in fzs:
        boards.append(PegSolitaire(fz))

    print(a_star_solve(boards[0]))

if __name__ == "__main__":
    main()


