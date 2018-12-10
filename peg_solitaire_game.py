"""
Peg Solitaire Puzzle Implementation
Author: Spencer Chang, Jacob Marshall

This program implements the peg solitaire game for 3 different game boards.
Solvability is not guaranteed on at least one...yet.

The program used the following websites to create its base code.

# Example program to show using an array to back a grid on-screen.
#
# Sample Python/Pygame Programs
# Simpson College Computer Science
# http://programarcadegames.com/
# http://simpson.edu/computer-science/

# Explanation video: http://youtu.be/mdTeqiWyFn
"""
import board_solver as bs
import os
import pygame
import sys
# import termios
import time
import copy
# import tty

from pprint import pprint, pformat
from queue import PriorityQueue
from typing import FrozenSet, List, Tuple

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (50, 50, 255)
GOLD = (255, 215, 0)
DKGREEN = (0, 100, 0)

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 50
HEIGHT = 50

# This sets the margin between each cell
MARGIN = 5
N_SQ = 7

PEG_NONE = 0
PEG_EXIST = 1
PEG_SELECT = 2
PEG_WALL = 3

mouseDown = False

# This class represents the player
# It derives from the "Sprite" class in Pygame
class Button:
    # Constructor. Pass in the color of the block, and its x and y position
    def __init__(self, origin, advanceBoard):
        # Determines whether we are meant to advance the board list or not
        self.adv = advanceBoard

        # Variables to hold the height and width of the block
        self.width = 20
        self.height = 20

        # Create an image of the player, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(DKGREEN)
        self.rect = self.image.get_rect()
        self.rect.x = origin[0]
        self.rect.y = origin[1]
        self.point_list = []
        if self.adv:
            self.point_list.append([self.rect.x + 5, self.rect.y + 2])
            self.point_list.append([self.rect.x + 17, self.rect.y + 9])
            self.point_list.append([self.rect.x + 17, self.rect.y + 10])
            self.point_list.append([self.rect.x + 5, self.rect.y + 17])
        else:
            self.point_list.append([self.rect.x + 17, self.rect.y + 2])
            self.point_list.append([self.rect.x + 5, self.rect.y + 9])
            self.point_list.append([self.rect.x + 5, self.rect.y + 10])
            self.point_list.append([self.rect.x + 17, self.rect.y + 17])

    # Update the position of the player
    def update(self, screen, board_list, og_list, idx):
        pos = pygame.mouse.get_pos()
        grid = board_list[idx]
        midpoint = [self.rect.x + self.width // 2, self.rect.y + self.height // 2]

        # The mouse click was not meant for this button
        if abs(pos[0] - midpoint[0]) > 8 or abs(pos[1] - midpoint[1]) > 8:
            return grid, idx
        if self.adv and idx >= len(board_list) - 1:
            # There are no more boards to be had
            return grid, idx
        elif not self.adv and idx <= 0:
            return grid, idx

        # Advance or retreat on boards
        if self.adv:
            idx += 1
        else:
            idx -= 1
        # Reset the board to the original; this is the reset functionality
        board_list[idx] = copy.deepcopy(og_list[idx])
        grid = board_list[idx]
        print("Button clicked: " + str(self.adv))
        return grid, idx

    # When we update the screen, we need to call the following method
    def drawIcon(self, screen):
        pygame.draw.rect(screen, DKGREEN, self.rect)
        pygame.draw.polygon(screen, GOLD, self.point_list)


def mouseColorSpace(grid, screen):
    # User clicks the mouse. Get the position
    pos = pygame.mouse.get_pos()
    column = pos[0] // (WIDTH + MARGIN)
    row = pos[1] // (HEIGHT + MARGIN)
    coord = list([-1, -1])

    # Find which peg is considered selected amongst them all.
    for r in range(N_SQ):
        for c in range(N_SQ):
            if grid[r][c] == PEG_SELECT:
                coord = list([r, c])

    # If the mouse is clicked within the board's border, do the following.
    if column < N_SQ or row < N_SQ:
        # Look through all to see if any further action is needed
        for r in range(N_SQ):
            for c in range(N_SQ):
                # continue loop if we're not looking at the square touched by the user or it's a wall
                if [r, c] != [row, column]:
                    continue

                # We're looking at the same coord touched by mouse
                if (
                    grid[r][c] == PEG_NONE
                    and coord != [-1, -1]
                    and (abs(coord[0] - r) == 2 or abs(coord[1] - c) == 2)
                ):
                    grid = jumpPeg(grid, coord, r, c)
                elif [r, c] == coord:
                    grid[coord[0]][coord[1]] = PEG_EXIST
                elif (
                    coord != [-1, -1]
                    and coord != [r, c]
                    and (grid[r][c] != PEG_NONE and grid[r][c] != PEG_WALL)
                ):
                    grid[coord[0]][coord[1]] = PEG_EXIST
                    grid[r][c] = PEG_SELECT
                elif coord == [-1, -1] and (
                    grid[r][c] != PEG_NONE and grid[r][c] != PEG_WALL
                ):
                    grid[r][c] = PEG_SELECT

        print("Click ", pos, "Grid coordinates: ", row, column)

    return grid, screen


def jumpPeg(grid, selCoord, row, col):
    """
    Provides the logic for jumping pegs in the solitaire game
    Pre-condition: 2 pegs and 1 hole in a line, the selected peg is at the end of this
                   line, [i.e. (P P H), (H P P)]
    Post-condition: 2 holes and 1 peg in a line, [i.e. (H H P), (P H H)]

    We know that the given selCoord should be a selected peg and the 'row' and 'col' are
    the hole.
    """
    # We want to check that the selected peg is in line with proper preconditions
    if row != selCoord[0] and col != selCoord[1]:
        return grid
    elif grid[(row + selCoord[0]) // 2][(col + selCoord[1]) // 2] == PEG_NONE:
        # Check the midpoint between the two for an existing peg
        return grid
    # It appears we have passed the precondition; execute post-conditions
    grid[row][col] = PEG_EXIST
    grid[(row + selCoord[0]) // 2][(col + selCoord[1]) // 2] = PEG_NONE
    grid[selCoord[0]][selCoord[1]] = PEG_NONE

    return grid


def makeTestBoards(board_list):
    # Create a 2 dimensional array. A two dimensional
    # array is simply a list of lists.
    grid = []
    for row in range(N_SQ):
        # Add an empty array that will hold each cell
        # in this row
        grid.append([])
        for column in range(N_SQ):
            # MAKE A CROSS SHAPE
            if (
                (row < 2 and column < 2)
                or (row >= 5 and column < 2)
                or (row >= 5 and column >= 5)
                or (row < 2 and column >= 5)
            ):
                grid[row].append(PEG_WALL)
            else:
                grid[row].append(PEG_EXIST)  # Append a cell
    # Need at least one hole in the center
    grid[3][3] = 0
    board_list.append(grid)

    grid = []
    for row in range(N_SQ):
        grid.append([])
        for column in range(N_SQ):
            # MAKE A SQUARE SHAPE
            grid[row].append(PEG_EXIST)  # Append a cell
    grid[3][3] = 0
    board_list.append(grid)

    grid = []
    for row in range(N_SQ):
        grid.append([])
        for column in range(N_SQ):
            # MAKE AN H SHAPE
            if (row < 2 and column == 3) or (row >= 5 and column == 3):
                grid[row].append(PEG_WALL)
            else:
                grid[row].append(PEG_EXIST)
    grid[3][3] = 0
    board_list.append(grid)
    return board_list


def main(frozensets=None):
    # Reference the global variable N_SQ
    global N_SQ

    # Process a file to get frozen sets
    gameBoards = []
    if frozensets == None:
        fzs = bs.process_frozen_sets(sys.argv[1])
    else:
        fzs = frozensets

    for i, fz in enumerate(fzs):
        gameBoards.append(bs.PegSolitaire(fz))

    # Sort the boards into a hash table where keys are the number of pegs and values
    # are a list of boards
    sorted_board_hash = {}
    for board in gameBoards:
        peg_count = board.pegs_remaining()
        if peg_count not in sorted_board_hash:
            sorted_board_hash[peg_count] = [board]
        else:
            sorted_board_hash[peg_count].append(board)

    # Try to solve the game boards
    solvable = []
    fail_limit = 30
    n_fails = 0
    # print("Generating {} Boards".format(len(sorted_board_hash.keys())))
    print("Checking Board Solvability")
    [print("Key {0} - {1} boards".format(x, len(sorted_board_hash[x]))) for x in sorted_board_hash.keys()]
    sys.stdout.flush()
    t_0 = time.clock()
    for key in sorted(sorted_board_hash.keys()):
        bd_time_0 = time.clock()
        n_fails = 0
        for board in sorted_board_hash[key]:
            if bs.bialostocki_solver(board) == True and bs.a_star_solve(board) == True:
                print("\nFound a solvable board with {} pegs!".format(key), end="")
                # print("\nNumber of fails: {0}".format(n_fails), end="")
                solvable.append(board)
                n_fails = 0
                break
            else:
                n_fails += 1
            # Break for failing too many boards
            if (n_fails >= fail_limit):
                print("|", end="")
                sys.stdout.flush()
                n_fails = 0
                break
        bd_time_1 = time.clock()
        print("\nBoard Check - key[{0}] took {1} seconds.".format(key, bd_time_1 - bd_time_0))
        sys.stdout.flush()
        if len(solvable) >= 5:
            break
    t_1 = time.clock()

    print("Check took {0} seconds".format(t_1 - t_0))

    if len(solvable) == 0:
        print("No solvable boards found. Press enter to exit.")
        input()
        exit()

    # Preserve the original board configurations
    originals = copy.deepcopy(solvable)

    # Grab the number of squares in one row of a game board
    N_SQ = len(solvable[0][0])

    # gameBoards = makeTestBoards(gameBoards)
    boardIdx = 0

    # Initialize pygame
    pygame.init()

    # Set the HEIGHT and WIDTH of the screen
    navWinOrigin = [0, N_SQ * (HEIGHT + MARGIN) + MARGIN]
    navWinHeight = HEIGHT * 4
    windowSize = [
        N_SQ * (WIDTH + MARGIN) + MARGIN,
        N_SQ * (HEIGHT + MARGIN) + MARGIN + navWinHeight,
    ]
    screen = pygame.display.set_mode(windowSize)

    # Set title of screen
    pygame.display.set_caption("Peg Solitaire Puzzles")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    leftButton = Button(
        [
            windowSize[0] // 2 - (N_SQ * WIDTH // 2 // 2),
            navWinOrigin[1] + (N_SQ * HEIGHT // 2 // 2),
        ],
        False,
    )
    rightButton = Button(
        [
            windowSize[0] - (N_SQ * WIDTH // 2),
            navWinOrigin[1] + (N_SQ * HEIGHT // 2 // 2),
        ],
        True,
    )
    button_list = [leftButton, rightButton]

    grid = solvable[boardIdx]

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                grid, screen = mouseColorSpace(grid, screen)
                grid, boardIdx = rightButton.update(screen, solvable, originals, boardIdx)
                grid, boardIdx = leftButton.update(screen, solvable, originals, boardIdx)

        # Set the screen background
        screen.fill(BLACK)

        # Draw the grid
        for row in range(N_SQ):
            for column in range(N_SQ):
                if grid[row][column] == PEG_NONE:
                    color = DKGREEN
                    pygame.draw.circle(
                        screen,
                        color,
                        [
                            ((MARGIN + WIDTH) * column + MARGIN) + WIDTH // 2 + 1,
                            ((MARGIN + HEIGHT) * row + MARGIN) + WIDTH // 2 + 1,
                        ],
                        WIDTH // 2 + 1
                    )
                    color = BLACK
                    pygame.draw.circle(
                        screen,
                        color,
                        [
                            ((MARGIN + WIDTH) * column + MARGIN) + WIDTH // 2 + 1,
                            ((MARGIN + HEIGHT) * row + MARGIN) + WIDTH // 2 + 1,
                        ],
                        WIDTH // 2 - 4
                    )
                    continue
                elif grid[row][column] == PEG_EXIST:
                    color = WHITE
                    pygame.draw.circle(
                        screen,
                        color,
                        [
                            ((MARGIN + WIDTH) * column + MARGIN) + WIDTH // 2 + 1,
                            ((MARGIN + HEIGHT) * row + MARGIN) + WIDTH // 2 + 1,
                        ],
                        WIDTH // 2
                    )
                    continue
                elif grid[row][column] == PEG_SELECT:
                    color = BLUE
                    pygame.draw.circle(
                        screen,
                        color,
                        [
                            ((MARGIN + WIDTH) * column + MARGIN) + WIDTH // 2 + 1,
                            ((MARGIN + HEIGHT) * row + MARGIN) + WIDTH // 2 + 1,
                        ],
                        WIDTH // 2
                    )
                    continue
                else:
                    color = BLACK
                pygame.draw.rect(
                    screen,
                    color,
                    [
                        (MARGIN + WIDTH) * column + MARGIN,
                        (MARGIN + HEIGHT) * row + MARGIN,
                        WIDTH,
                        HEIGHT,
                    ],
                )
        leftButton.drawIcon(screen)
        rightButton.drawIcon(screen)
        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()


if __name__ == "__main__":
    main()
