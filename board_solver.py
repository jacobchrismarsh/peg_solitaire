"""
board_solver has all utility classes for making the peg solitaire game boards.

By: Spencer Chang, Jacob Marshall
"""

import os
import sys
# import termios
import time
# import tty
from pprint import pprint, pformat
from queue import PriorityQueue
# from termcolor import cprint
from typing import FrozenSet, List, Tuple


HOLE = 0
PEG = 1
WALL = 3

X = 0
Y = 0
# Define new types for this file
BoardSet = FrozenSet[Tuple[str, Tuple[int, int]]]
CompleteBoard = List[List[str]]

########################################################################################
########################################################################################
########################################################################################

# class _Getch:
#     def __call__(self):
#             fd = sys.stdin.fileno()
#             old_settings = termios.tcgetattr(fd)
#             try:
#                 tty.setraw(sys.stdin.fileno())
#                 ch = sys.stdin.read(3)
#             finally:
#                 termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#             return ch

########################################################################################
########################################################################################
########################################################################################

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
                board.append([WALL] * width)

            # Add all the pegs and walls to the board
            for item in instructions:
                if item[0] == "out":
                    x, y = item[1][0] - 1, item[1][1] - 1
                    board[x][y] = WALL
                elif item[0] == "peg":
                    x, y = item[1][0] - 1, item[1][1] - 1
                    board[x][y] = PEG
                elif item[0] == "linked":
                    x, y = item[1][0] - 1, item[1][1] - 1
                    if board[x][y] != PEG:
                        board[x][y] = HOLE
                # else:
                #     print(item[0])

            self.width = width - 1
            self.height = height - 1
            self.board = board

########################################################################################

    def copy(self):
        """ Returns a copy of the current board """
        return PegSolitaire(None, [x[:] for x in self.board])

########################################################################################

    # These two functions allow you to index this object, i.e. PegSolitaire[0][1]
    def __getitem__(self, key: int) -> List[str]:
        return self.board[key]

########################################################################################

    def __iter__(self):
        return self.board

########################################################################################

    def __repr__(self):
        """ Returns a printable version of the board """
        return pformat(self.board)

########################################################################################

    def __lt__(self, other):
        # first = self.pegs_remaining() + len(self.total_moves())
        # second = other.pegs_remaining() + len(other.total_moves())
        # return first < second
        return self.pegs_remaining() < other.pegs_remaining()

########################################################################################

    def __eq__(self, other):
        return self.board == other.board

########################################################################################

    def __hash__(self):
        return hash(tuple([tuple(b) for b in self.board]))

########################################################################################

    def perform_move(self, x1: int, y1: int, x2: int, y2: int):
        """ Given two sets of xy coordinates, SOURCE -> DESTINATION, this will move
            the peg located at SOURCE and move it to DESTINATION

            NOTE: This does NO error checking. It assumes the move is valid
        """
        # Place a peg in the new location
        self.board[x2][y2] = PEG

        # Find out which peg you have to remove
        if x1 < x2:  # Remove peg from above hole
            self.board[x2 - 1][y2] = HOLE
        elif x1 > x2:  # Remove peg from below hole
            self.board[x2 + 1][y2] = HOLE
        elif y1 < y2:  # Remove peg from left of hole
            self.board[x2][y2 - 1] = HOLE
        elif y1 > y2:  # Remove peg from right of hole
            self.board[x2][y2 + 1] = HOLE

        # Remove old peg from its former position
        self.board[x1][y1] = HOLE

########################################################################################

    def total_moves(self):
        """ Will return a list of available moves on a board """
        moves = []

        holes = self._find_holes()

        for hole in holes:
            # The '*' in this function call expands the tuple into two arguments
            moves += self._find_moves_around_hole(*hole)

        return moves

########################################################################################

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

########################################################################################

    def _find_holes(self) -> List[Tuple[int, int]]:
        holes = []

        # Go through entire board
        for i, row in enumerate(self.board):
            for j, spot in enumerate(row):
                # If you find a hole, add a tuple of the x,y coordinate to a list
                if spot == HOLE:
                    holes.append((i, j))

        return holes

########################################################################################

    # A "move" is defined as such:
    # If there are two pins in a row in any direction around the hole, there is a move
    # HOLE PEG PEG is a move, HOLE PEG HOLE is not a move. A move is a tuple of
    # 4 xy coordinates, representing x1, y1 moving to x2, y2. As such, the first set of
    # coordinates of a move are from the peg being moves, and the second set it the
    # place you are moving to
    def _find_moves_around_hole(self, x: int, y: int) -> int:
        moves = []

        if y <= (self.width - 2):  # Check pins to the right
            if self.board[x][y + 1] == PEG and self.board[x][y + 2] == PEG:
                moves.append((x, y + 2, x, y))
        if y >= 2:  # Check pins to the left
            if self.board[x][y - 1] == PEG and self.board[x][y - 2] == PEG:
                moves.append((x, y - 2, x, y))
        if x >= 2:  # Check pins above
            if self.board[x - 1][y] == PEG and self.board[x - 2][y] == PEG:
                moves.append((x - 2, y, x, y))
        if x <= (self.height - 2):  # Check pins below
            if self.board[x + 1][y] == PEG and self.board[x + 2][y] == PEG:
                moves.append((x + 2, y, x, y))
        return moves

########################################################################################
########################################################################################
########################################################################################

def process_frozen_sets(input_file: str) -> BoardSet:
    boards = []

    with open(input_file) as f:
        lines = f.readlines()[0::2]  # Grab every other line from start to EOF

        # Go through each string and convert it to a frozenset
        for line in lines:
            boards.append(eval(line))

    return boards


########################################################################################

def a_star_solve(board: PegSolitaire) -> bool:
    board_queue = PriorityQueue()
    board_set = set()

    board_queue.put(board)

    start = time.time()

    # While the queue is not empty
    while not board_queue.empty():
        end = time.time()

        # Move on to the next board if it takes too long to solve this puzzle
        if end - start >= 17:
            print(".", end="")
            sys.stdout.flush()
            return False

        # Get a board and all its available moves.
        curr_board = board_queue.get()
        moves = curr_board.total_moves()

        # Keep track of which boards you've seen
        board_set.add(curr_board)

        # If there are no more moves, you might have found a successfull puzzle!
        if len(moves) == 0:
            # Congrats! You found a board that can be solved!
            if curr_board.pegs_remaining() == 1:
                print("!", end="")
                sys.stdout.flush()
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

########################################################################################

# Check this website for the logic on how this works:
# http://www.cut-the-knot.org/proofs/PegsAndGroups.Bialostocki
def bialostocki_solver(board: PegSolitaire) -> bool:
    x_y_z = board.copy()
    x = True
    y = False
    z = False
    x_count = y_count = z_count = 0
    # Fill the board with x, y, and z
    for i, row in enumerate(x_y_z.board):
        for j, spot in enumerate(row):
            if x == True:
                if(spot == PEG):
                    x_count += 1
                x = False
                y = True
            elif y == True:
                if(spot == PEG):
                    y_count += 1
                y = False
                z = True
            elif z == True:
                if(spot == PEG):
                    z_count += 1
                z = False
                x = True

    x_count %= 2
    y_count %= 2
    z_count %= 2

    if (x == 0 and y == 0 and z == 0) or (x == 1 and y == 1 and z == 1):
        return False
    return True

def print_board(board: PegSolitaire) -> None:
    """ Will print out the game board.
        - The outside borders will be blue
        - The inside structure will be green
        - The pegs will be yellow if the player is not on them, red otherwise
        - The walls will be black if the player is not on them, red otherwise
        - The holes will be empty if the player is not on them, red circle otherwise
    """

    # Top border
    cprint("+", "blue", end="", attrs=["bold"])
    for _ in range(len(board.board[0])):
        cprint("---+", "blue", end="", attrs=["bold"])

    for i, row in enumerate(board.board):
        # Left-most side wall
        cprint("\n|", "blue", end="", attrs=["bold"])

        for j, spot in enumerate(row):
            # Printing the walls, pegs, and holes
            if spot == PEG:
                if i == X and j == Y:
                    cprint(" {} ".format(PEG), "red", end="", attrs=["bold"])
                else:
                    cprint(" {} ".format(PEG), "yellow", end="", attrs=["bold"])

            elif spot == WALL:
                if i == X and j == Y:
                    cprint("{}".format(WALL * 3), "red", end="")
                else:
                    cprint("{}".format(WALL * 3), "grey", end="")
            else:
                if i == X and j == Y:
                    cprint(" H ", "red", end="")
                else:
                    print("   ", end="")

            # Print out the inner walls in green, and the right-most wall blue
            if j != len(row) - 1:
                cprint("|", "green", end="", attrs=["bold"])
            else:
                cprint("|", "blue", end="", attrs=["bold"])
        print("\n", end="")

        # Horizontal inner divididing lines
        if i != len(row) - 1:
            for _ in range(len(row)):
                cprint("+---", "green", end="", attrs=["bold"])
            cprint("+", "blue", end="", attrs=["bold"])

    # Bottom Border
    cprint("+", "blue", end="", attrs=["bold"])
    for _ in range(len(board.board[0])):
        cprint("---+", "blue", end="", attrs=["bold"])
    print()
    return

########################################################################################

# def start_game(board: PegSolitaire) -> None:
#     while(True):
#         os.system("clear")
#         print_board(board)
#         get(board)

########################################################################################

# def get(board: PegSolitaire): #     global X
#     global Y
#     inkey = _Getch()
#     while(True):
#             k = inkey()
#             if k != '':
#                 break
#     if k=='\x1b[A':
#         X = max(0, X-1) #up
#     elif k=='\x1b[B':
#         X = min(board.width, X+1) #down
#     elif k=='\x1b[C':
#         Y = min(board.width, Y+1) #right
#     elif k=='\x1b[D':
#         Y = max(0, Y-1) #left
#     else:
#         exit(1)
#         print("not an arrow key!")

########################################################################################

def main():
    return
    # fzs = process_frozen_sets(sys.argv[1])
    # boards = []
    # for i, fz in enumerate(fzs):
    #     boards.append(PegSolitaire(fz))

    # solvable = []
    # for i, board in enumerate(boards[:10]):
    #     print("Board {}".format(i))
    #     if a_star_solve(board) == True:
    #         start_game(board)


            # f = open("success/successfull_boards_ascii_{}.txt".format(i), "w")
            # print("Board {} is solvable!".format(i))
            # for j, row in enumerate(board.board):
            #     for k, spot in enumerate(row):
            #         f.write(spot)
            #         if k != len(row) - 1:
            #             f.write(" ")
            #     if j != len(row) - 1:
            #         f.write("\n")
            # solvable.append(i)

    # print(solvable)
    # print("Total solvable puzzles: {}".format(len(solvable)))



if __name__ == "__main__":
    main()
