"""
 Example program to show using an array to back a grid on-screen.
 
 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/
 
 Explanation video: http://youtu.be/mdTeqiWyFnc
"""
import pygame
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (50, 50, 255)
DKGREEN = (0, 100, 0)
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 5
N_SQ = 7

PEG_NONE = 0
PEG_EXIST = 1
PEG_SELECT = 2
PEG_WALL = 3

mouseDown = False

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
                if (grid[r][c] == PEG_NONE and coord != [-1, -1] and (abs(coord[0] - r) == 2 or abs(coord[1] - c) == 2)):
                    grid = jumpPeg(grid, coord, r, c)
                elif [r, c] == coord:
                    grid[coord[0]][coord[1]] = PEG_EXIST
                elif coord != [-1, -1] and coord != [r, c] and (grid[r][c] != PEG_NONE and grid[r][c] != PEG_WALL):
                    grid[coord[0]][coord[1]] = PEG_EXIST
                    grid[r][c] = PEG_SELECT
                elif coord == [-1, -1] and (grid[r][c] != PEG_NONE and grid[r][c] != PEG_WALL):
                   grid[r][c] = PEG_SELECT 
                
        print("Click ", pos, "Grid coordinates: ", row, column)
 
    return grid, screen

def jumpPeg(grid, selCoord, row, col):
    '''
    Provides the logic for jumping pegs in the solitaire game
    Pre-condition: 2 pegs and 1 hole in a line, the selected peg is at the end of this line, [i.e. (P P H), (H P P)]
    Post-condition: 2 holes and 1 peg in a line, [i.e. (H H P), (P H H)]

    We know that the given selCoord should be a selected peg and the 'row' and 'col' are the hole.
    '''
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


if __name__ == "__main__":

    # Create a 2 dimensional array. A two dimensional
    # array is simply a list of lists.
    grid = []
    for row in range(N_SQ):
        # Add an empty array that will hold each cell
        # in this row
        grid.append([])
        for column in range(N_SQ):
            if (row < 2 and column < 2) or (row >= 5 and column < 2) or (row >= 5 and column >= 5) or (row < 2 and column >= 5):
                grid[row].append(PEG_WALL)
            else:
                grid[row].append(PEG_EXIST)  # Append a cell
    
    # Set row 1, cell 5 to one. (Remember rows and
    # column numbers start at zero.)
    grid[3][3] = 0
    
    # Initialize pygame
    pygame.init()
    
    # Set the HEIGHT and WIDTH of the screen
    windowSize = [HEIGHT * N_SQ + MARGIN * N_SQ + MARGIN, WIDTH * N_SQ + MARGIN * N_SQ + MARGIN]
    screen = pygame.display.set_mode(windowSize)
    
    # Set title of screen
    pygame.display.set_caption("Peg Solitaire Puzzles")
    
    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # mouseDown = True
                grid, screen = mouseColorSpace(grid, screen)
            # elif event.type == pygame.MOUSEBUTTONUP:
            #     # mouseDown = False

        # Set the screen background
        screen.fill(BLACK)
    
        # Draw the grid
        for row in range(N_SQ):
            for column in range(N_SQ):
                if grid[row][column] == PEG_NONE:
                    color = DKGREEN
                elif grid[row][column] == PEG_EXIST:
                    color = WHITE
                elif grid[row][column] == PEG_SELECT:
                    color = BLUE
                else:
                    color = BLACK
                pygame.draw.rect(screen,
                                color,
                                [(MARGIN + WIDTH) * column + MARGIN,
                                (MARGIN + HEIGHT) * row + MARGIN,
                                WIDTH,
                                HEIGHT])
        # Limit to 60 frames per second
        clock.tick(60)
    
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
    
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

