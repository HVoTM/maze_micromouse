import pygame
import sys
import random
import Maze
import time
import solver
from settings import Colors 

pygame.init()

# Font setup
font = pygame.font.Font(None, 36)

# Function to display messages
def show_message(screen, text, position, color=(255, 255, 255)):
    message_surface = font.render(text, True, color)
    screen.blit(message_surface, position)
    pygame.display.update()  # Ensure the text appears immediately

# TODO: define these wrapper stuff, or also use PyTest
def SeedRetrieval(func):
    "time-based pseudo-random seed generator and retrieval"
    # https://stackoverflow.com/questions/5012560/how-to-query-seed-used-by-random-random
    def wrapper(*args, **kwargs):
        seed = random.Random(sys.maxsize)
        func()
        print('Generated Seed: ', seed)
    return wrapper

def runTimeCounter(func):
    "Counting time"
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func()
        end_time = time.perf_counter()
        runtime = end_time - start_time
        print(f"The code took {runtime:.4f} seconds to run.")
    return wrapper

# TODO -----
def generateMazeonly():
    pass

def loadMazeMap_thenSolve():
    pass

def mainMazeProgram(maze: "Maze.MazeMap", mouseSolver: "solver.Mouse", fpsSpeed: int= 60, generatorName: str="dfs", log_data:bool = False) -> None:
    if generatorName == "kruskal":
        maze.generateListofWalls()
    elif generatorName == "prim":
        # Iinitialize the Prim's algorithm
        # Mark the cell as visited so that we don't have to revisit it 
        maze.current.visited = True
        # Initialize the wall list with the walls of the starting cell
        maze.walls = maze.retrieveWallsasXY_Tuple(maze.current)
    elif generatorName == "wilson":
        maze.init_Wilson()

    # States
    running = True
    paused = False
    stepMode = False
    solving = False
    mazeGenerated = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Key-press events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Toggle pause
                    paused = not paused
                    if paused:
                        print("Program paused")
                elif event.key == pygame.K_TAB:
                    stepMode = not stepMode # FIXME: fix the step mode (we just want a time-step visualization)
                    if stepMode:
                        print("Step mode enabled. Press S to step through the program.")
                    else:
                        print("Step mode disabled. Resuming normal execution.")
                elif event.key == pygame.K_RIGHT and stepMode:  # Perform one step in step mode
                    print("Performing one step...")
                    maze.iterativeWilson() 
                elif event.key == pygame.K_UP:  # Increase speed
                    fpsSpeed += 5
                elif event.key == pygame.K_DOWN:  # Decrease speed
                    fpsSpeed = max(5, fpsSpeed - 5)  # Ensure FPS doesn't go below 5
                # Indicate to start running the solver, NOTE or we can just have it run automatically, maybe use a key argument
                elif event.key == pygame.K_RETURN:
                    if mazeGenerated:
                        print("Enter Key pressed, now solving...")
                        solving = True
                    else:
                        print("Maze Generation is not finished yet. Please wait then press Enter to solve")

        if paused and not stepMode:
            continue # end this iteration
        # If in step mode, wait for the user to press the step key
        if stepMode:
            continue
        # -------------------------------------------------------------------------------------
        # Algorithm handling
        if not mazeGenerated:
            if generatorName == "dfs":
                maze.iterativeDFS()
                if maze.mazeGenerated:
                    mazeGenerated = True
            elif generatorName == "kruskal":
                maze.iterativeKruskal()
            elif generatorName == "prim":
                if maze.walls:
                    maze.iterativePrim()
                else:
                    mazeGenerated = True
                    print("Maze generation complete!")
            elif generatorName == "wilson":
                if maze.remainingCells:
                    maze.iterativeWilson()
                else:
                    mazeGenerated = True

        if solving and mazeGenerated:
            print("Maze Solving is running...")
            # Call on the maze solving algorithms here
            mouseSolver.RandomMouse()
            print("Endgoal is {} {}".format(mouseSolver.endX, mouseSolver.endY))
        # -------------------------------------------------------------------------------------
        # DISPLAY SECTION            
        # Fill the screen with the background color first and foremost
        maze.screen.fill(maze.backgroundColor)
        # Update the maze's grids' Cell objects 
        for x in range(maze.cols):
            for y in range(maze.rows): 
                maze.MazeGrid[x][y].DrawCell(maze.screen)
        # DEBUG:
        # Add a blinking effect to a specific cell (e.g., the starting cell)
        maze.blinkSpecifiedCell(maze.screen, maze.MazeGrid[maze.startingX][maze.startingY])
        # Update for the solver mouse if we are solving
        if solving:
        # Get the current position of the maze solver mouse on the map, see where it is at
            print("Mouse currently at x = {} | y = {}".format(mouseSolver.x, mouseSolver.y))
            # I forgot this is another way using f-string: print(f"Mouse currently at x = {mouseSolver.x} | y = {mouseSolver.y}")
            mouseCell = maze.MazeGrid[mouseSolver.x][mouseSolver.y]
            maze.showSpecifiedCell(screen=maze.screen, chosenCell=mouseCell, cellColor=Colors.YELLOW.value)

        # Update the display
        pygame.display.update()
        # Control the frame rate
        maze.clock.tick(fpsSpeed)
        if log_data:
            # Logging info stuff- not that it is necessary but is good to know when working with data-intensive applications
            print("Time passed in pygame's Clock: ",maze.clock.get_time())
            print("Current Frame per Second: ", maze.clock.get_fps())
    pygame.quit()

# Driver Code
if __name__ == "__main__":
    new_maze = Maze.MazeMap(mazeWidth=800, mazeHeight=800, cellSize=100 ,startX=0, startY=0)
    new_mouse = solver.Mouse(maze=new_maze)
    # Testing now: iterative randomized Kruskal's algorithm
    # new_maze.generate(fpsSpeed=60, generator='wilson', preload=False)

    mainMazeProgram(new_maze, new_mouse, fpsSpeed=60, generatorName='dfs')
