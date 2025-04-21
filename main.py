import pygame
import sys
import random
import Maze
import time
import solver
from settings import Colors, GameState

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
def generateMazeonly(maze: "Maze.MazeMap", generatorName:str = "dfs", fpsSpeed: int = 60):
    # Init program for the necessary algorithms
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

    running = True
    generating = False
    mazeGenerated = False
    paused = False
    saving = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Toggle pause
                    paused = not paused
                    if paused:
                        print("Program paused")
                elif event.key == pygame.K_RETURN:
                    generating = True
                    print("Generating....")
                # Saving and loading mode
                elif event.key == pygame.K_q:
                    if mazeGenerated:
                        print("Saving...")
                        saving = True
                    else:
                        print("Maze Generation not finished yet, please wait until completion then press Q to save maze...")
        
        if mazeGenerated and saving:
            maze.save2file(filename="saved_maze_test")
            saving = False
        # -------------------------------------------------------------------------------------
        # Algorithm handling
        if not mazeGenerated and generating:
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
        # Fill the screen with the background color first and foremost
        maze.screen.fill(maze.backgroundColor)
        # Update the maze's grids' Cell objects 
        for x in range(maze.cols):
            for y in range(maze.rows): 
                maze.MazeGrid[x][y].DrawCell(maze.screen)
        # Update the display
        pygame.display.update()
        # Control the frame rate
        maze.clock.tick(fpsSpeed)
    pygame.quit()

def checkObjectAttributes(object):
    print("Checking {}'s attributes:".format(object.__class__.__name__))
    print(vars(object))

def solve_PreloadedMaze(maze:"Maze.MazeMap", mouseSolver :"solver.Mouse",fpsSpeed: int= 60):
    # Hardcoding the saved maze map
    maze.load_file("saved_maze_test")
    # States
    solving = False
    running = True
    paused = False
    stepMode = False
    advanceOnestep = False
    reachedGoal = False
    initSolver = False # a state of the overhead solving states if we need to initiliaze any step before the iterative solving
                        # TODO: add initSolver later

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Toggle pause
                    if not stepMode: # This is to prevent the program from resuming if we are in stepMode
                        paused = not paused
                    if paused:
                        print("Program paused")
                elif event.key == pygame.K_RETURN:
                    if reachedGoal:
                        print("Maze is already Solved!")
                    else:
                        print("Solving....")
                    solving = True
                    mouseSolver.dijkstra_init()
                    mouseSolver.astar_init()
                elif event.key == pygame.K_TAB:
                    stepMode = not stepMode # fix the step mode (we just want a per time-step visualization) -> FIXED
                    if stepMode:
                        print("Step mode enabled. Press the Right-arrow key to Step Forward per iteration.")
                        paused = True # Set the pause button to false so we don
                    else:
                        print("Step mode disabled. Resuming normal execution.")
                        paused = False
                    
                elif event.key == pygame.K_RIGHT and stepMode:  # Perform one step in step mode
                    print("Performing one step...")
                    # Temporarily resume for one loop
                    advanceOnestep = True
        
        if paused:
            if stepMode and advanceOnestep:
                # Since we are pressing the right key, so we just run for one iteration
                advanceOnestep = False
            else:
                continue
    
        if solving and not reachedGoal:
            mouseSolver.astar_iter()
            mouseSolver.updateTrailsofMouse()
            if mouseSolver.MazeSolved:
                reachedGoal = True
                print("Reach goal at x = {}| y = {}".format(mouseSolver.endX, mouseSolver.endY))
                mouseSolver.highlightFinalPath()
        # DISPLAY SECTION            
        # Fill the screen with the background color first and foremost
        maze.screen.fill(maze.backgroundColor)
        # Update the maze's grids' Cell objects as ALL CELLS ATTRIBUTES SHOULD BE UPDATED
        for x in range(maze.cols):
            for y in range(maze.rows): 
                maze.MazeGrid[x][y].DrawCell(maze.screen)
        # Mouse solver should be drawn after
        if solving:
            if not reachedGoal:
                print("Mouse is now at x = {} | y = {}".format(mouseSolver.x, mouseSolver.y))
            # I forgot this is another way using f-string: print(f"Mouse currently at x = {mouseSolver.x} | y = {mouseSolver.y}")
            # mouseCell = maze.MazeGrid[mouseSolver.x][mouseSolver.y]
            # maze.showSpecifiedCell(screen=maze.screen, chosenCell=mouseCell, cellColor=Colors.YELLOW.value)

        # Update the display
        pygame.display.update()
        # Control the frame rate
        maze.clock.tick(fpsSpeed)
    pygame.quit()

def mainMazeProgram(maze: "Maze.MazeMap", mouseSolver: "solver.Mouse", fpsSpeed: int= 60, generatorName: str="dfs", log_data:bool = False) -> None:
    # TODO TODO TODO: add utility functions to initialize algorithms and runnning generator/solver to make
    # the programs more compact
    # Init program for the necessary algorithms
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
    generatingMaze = False
    saving = False
    loadMaze = False
    advanceOnestep = False
    idle = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Key-press events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Toggle pause
                    if not stepMode: # preventing the program from resuming if in stepMode
                        paused = not paused
                    if paused:
                        print("Program paused")
                    else:
                        print("Program resuming")
                elif event.key == pygame.K_TAB:
                    stepMode = not stepMode # (we just want a per-time-step visualization advancing mode)
                    if stepMode:
                        paused = True
                        print("Step mode enabled. Press S to step through the program.")
                    else:
                        paused = False
                        print("Step mode disabled. Resuming normal execution.")
                elif event.key == pygame.K_RIGHT and stepMode:  # Perform one step in step mode
                    print("Performing one step...")
                    advanceOnestep = True

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
                # Saving and loading mode
                elif event.key == pygame.K_q:
                    if mazeGenerated:
                        print("Saving...")
                        saving = True
                    else:
                        print("Maze Generation not finished yet, please wait until completion then press Q to save maze...")
                elif event.key == pygame.K_p:
                    print("Key P is pressed, loading the maze now...")
                    loadMaze = True

        if paused:
            if stepMode and advanceOnestep:
                # Since we are pressing the right key, so we just run for one iteration
                advanceOnestep = False
            else:
                continue
    
        if solving:
            mouseSolver.RandomMouse()
        elif generatingMaze:
            # Call on whatever the maze generation algorithm is running on
            
            pass

        # Finish this outer loop of if stepMode -> while running. And continue to the next iteration 
        # -------------------------------------------------------------------------------------
        # Algorithm handling
        if not mazeGenerated:
            if generatorName == "dfs":
                maze.iterativeDFS()
                if maze.mazeGenerated:
                    mazeGenerated = True
                    print("Maze Generation complete!")
            elif generatorName == "kruskal":
                maze.iterativeKruskal()
            elif generatorName == "prim":
                if maze.walls:
                    maze.iterativePrim()
                else:
                    mazeGenerated = True
                    print("Maze Generation complete!")
            elif generatorName == "wilson":
                if maze.remainingCells:
                    maze.iterativeWilson()
                else:
                    mazeGenerated = True
                    print("Maze Generation complete!")

        if mazeGenerated and saving:
            maze.save2file(filename="saved_maze_test")
            saving = False

        if solving and mazeGenerated:
            print("Maze-Solver is running...")
            # Call on the maze solving algorithms here
            mouseSolver.RandomMouse()
            # print("Endgoal is x={}| y={}".format(mouseSolver.endX, mouseSolver.endY)) # DEBUG
        # -------------------------------------------------------------------------------------
        # DISPLAY SECTION            
        # Fill the screen with the background color first and foremost
        maze.screen.fill(maze.backgroundColor)
        # Update the maze's grids' Cell objects - 
        for x in range(maze.cols):
            for y in range(maze.rows): 
                maze.MazeGrid[x][y].DrawCell(maze.screen)
        # Add a blinking effect to a specific cell (e.g., the starting cell)
        maze.blinkSpecifiedCell(maze.screen, maze.MazeGrid[maze.startingX][maze.startingY])
        # Update for the solver mouse if we are solving
        if solving:
        # Get the current position of the maze solver mouse on the map, see where it is at
            print("Update after running solver: Mouse currently at x = {} | y = {}".format(mouseSolver.x, mouseSolver.y))
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

# --- Driver Code ---
if __name__ == "__main__":
    # New maze new mouse who dis?
    new_maze = Maze.MazeMap(mazeWidth=800, mazeHeight=800, cellSize=20 ,startX=0, startY=0)
    new_mouse = solver.Mouse(maze=new_maze) # referencing the maze to the mouse for solving
    # --------------------------------------------------------------------
    # 1. Testing generation
    # new_maze.generate(fpsSpeed=60, generator='kruskal', preload=False)
    # generateMazeonly(maze=new_maze, generatorName='prim', fpsSpeed=120)
    # --------------------------------------------------------------------
    # 2. Testing main program
    # mainMazeProgram(new_maze, new_mouse, fpsSpeed=60, generatorName='kruskal')
    # --------------------------------------------------------------------
    # 3. Testing solving a preloaded maze
    solve_PreloadedMaze(maze=new_maze, mouseSolver=new_mouse, fpsSpeed=60)
