import pygame, sys
from settings import *
import Maze
import solver
import threading # using threading to run the tkinter menu and Pygame window display simultaneously
import tkinter as tk
from tkinter import ttk

class MainApp(object):
    """MainApp to store the state machines flow during the main application run

    Parameters
    ----------
    screen : pygame's screen
        Pygame screen to work on
    states : dict
        States of the working app
        - GENERATING = 1
        - SOLVING = 2
        - PAUSED = 3
        - RESUMED = 4
        - SAVING = 5
        - LOADING = 6
        - IDLE = 7  
    Returns
    -------
    None
    """
    def __init__(self, screen, states, start_state, mazeWidth, mazeHeight, cellSize):
        pygame.init()
        self.running = True # flag to stop the program
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.states = states # actual representation of all state objects
        self.state_name = start_state # Naming for the state to begin with, the IDLE
        self.state = self.states[self.state_name] 

        self.maze = Maze.MazeMap(mazeWidth=mazeWidth, mazeHeight=mazeHeight, cellSize=cellSize, startX=0, startY=0)
        self.solver = solver.Mouse(maze=self.maze) # referencing the maze to the mouse for solving

    def event_loop(self):
        for event in pygame.event.get():
            self.state.get_event(event)

    def flip_state(self):
        current_state = self.state_name
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        persistent = self.state.persist
        self.state = self.states[self.state_name]
        self.state.startup(persistent)

    def update(self, dt):
        """Check for the next state"""
        if self.state.quit:
            self.running = True
        elif self.state.done:
            self.flip_state()
        self.state.update(dt)

    def draw(self):
        self.state.draw(self.screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()

def mainMazeProgram(maze: "Maze.MazeMap", mouseSolver: "solver.Mouse", fpsSpeed: int= 60, generatorName: str="dfs", solver: str='dfs', log_data:bool = False) -> None:
    # TODO TODO TODO: add utility functions to initialize algorithms and runnning generator/solver to make
    # the programs more compact
    # Init program for the necessary algorithms
    pygame.init()
    main_screen = pygame.display.set_mode((MAZE_WIDTH, MAZE_HEIGHT))
    mainclock = pygame.time.Clock()

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

    # State and Flags for running flow
    running = True
    current_state = GameState.IDLE
    stepMode = False
    advanceOnestep = False
    paused = False
    mazeGenerated = False
    mazeLoaded = False # a flag to signal that maze is already loaded and disable for further loading
    reachedGoal = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # Key-press events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Toggle pause
                    if not stepMode: # preventing the program from resuming if in stepMode
                        # if current_state == GameState.PAUSED:
                        #     current_state = GameState.RESUMED
                        #     print("Resuming program...")
                        # elif current_state in [GameState.IDLE, GameState.RESUMED, GameState.SOLVING, GameState.GENERATING]:
                        #     current_state = GameState.PAUSED
                        #     print("Program paused.")
                        paused = not paused
                        if paused:
                            print("Program paused")
                        else:
                            print("Program resuming")

                elif event.key == pygame.K_TAB:
                    stepMode = not stepMode # (we just want a per-time-step visualization advancing mode)
                    if stepMode:
                        current_state = GameState.PAUSED
                        print("Step mode enabled. Press right-arrow key (->) to step through the program.")
                    else:
                        current_state = GameState.RESUMED
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
                    if not mazeGenerated:
                        current_state = GameState.GENERATING
                    elif mazeGenerated:
                        print("Enter Key pressed, now solving...")
                        current_state = GameState.SOLVING
                        if solver == 'dijsktra':
                            mouseSolver.dijkstra_init()
                        elif solver == 'a_star':
                            mouseSolver.astar_init()
                    else:
                        print("Maze Generation is not finished yet. Please wait then press Enter to solve")
                # Saving and loading mode
                elif event.key == pygame.K_q:
                    if mazeGenerated:
                        print("Saving...")
                        maze.save2file(filename="saved_maze_test")
                    else:
                        print("Maze Generation not finished yet, please wait until completion then press Q to save maze...")
                elif event.key == pygame.K_p:
                    if not mazeLoaded:
                        print("Key P is pressed, loading the maze now...")
                        maze.load_file('saved_maze_test')
                        mazeGenerated = True
                    else:
                        print("Maze already loaded, please reset the whole program if you want to reload the maze")
        # -------------------------------------------------------------------------
        
        if paused:
            if stepMode and advanceOnestep:
                # Since we are pressing the right key, so we just run for one iteration
                advanceOnestep = False #  
            else:
                continue

        else:
            if current_state == GameState.IDLE:
                pass
            # Resume solving or other tasks
            elif current_state == GameState.GENERATING:
                if not mazeGenerated:
                    # Generating state
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
                # Condition check to flag the state
                if mazeGenerated:
                    current_state = GameState.IDLE
            elif current_state == GameState.SOLVING and not reachedGoal:
                if not mouseSolver.MazeSolved:
                    if solver == 'dfs':
                        mouseSolver.depthFirstSearch_iter()
                    elif solver == 'bfs':
                        mouseSolver.breadthFirstSearch_iter()
                    elif solver == 'djikstra':
                        mouseSolver.dijkstra_iter()
                    elif solver == 'a_star':  
                        mouseSolver.astar_iter()
                    mouseSolver.updateTrailsofMouse()
                else:
                    reachedGoal = True
                    print("Reach goal at x = {}| y = {}".format(mouseSolver.endX, mouseSolver.endY))
                    mouseSolver.highlightFinalPath()
                    current_state = GameState.IDLE

        # -------------------------------------------------------------------------------------
        # DISPLAY SECTION            
        # Fill the screen with the background color first and foremost
        maze.screen.fill(maze.backgroundColor)
        # Update the maze's grids' Cell objects - 
        for x in range(maze.cols):
            for y in range(maze.rows): 
                maze.MazeGrid[x][y].DrawCell(main_screen)
        # Add a blinking effect to a specific cell (e.g., the starting cell)
        maze.blinkSpecifiedCell(main_screen, maze.MazeGrid[mouseSolver.x][mouseSolver.y])
        # Update for the solver mouse if we are solving
        if current_state == GameState.SOLVING:
        # Get the current position of the maze solver mouse on the map, see where it is at
            print("Update after running solver: Mouse currently at x = {} | y = {}".format(mouseSolver.x, mouseSolver.y))
        # Update the display
        pygame.display.update()
        # Control the frame rate
        mainclock.tick(fpsSpeed)
        if log_data:
            # Logging info stuff- not that it is necessary but is good to know when working with data-intensive applications
            print("Time passed in pygame's Clock: ",maze.clock.get_time())
            print("Current Frame per Second: ", maze.clock.get_fps())
    pygame.quit()

# Function to run the Pygame maze program
def run_pygame(maze, mouseSolver, fpsSpeed, generatorName, solver):
    mainMazeProgram(maze, mouseSolver, fpsSpeed, generatorName, solver)

# Function to create the Tkinter settings menu
def create_settings_menu(maze, mouseSolver):
    # Shared variables to control the Pygame program
    control_vars = {
        "paused": False,
        "step_mode": False,
        "advance_one_step": False,
        "reset": False
    }

    def start_pygame():
        # Retrieve settings from the GUI
        generator = generator_var.get()
        solver = solver_var.get()
        fps = fps_var.get()

        # Start the Pygame program in a separate thread
        threading.Thread(target=run_pygame, args=(maze, mouseSolver, fps, generator)).start()
    
    # Create the Tkinter window
    root = tk.Tk()
    root.title("Maze GUI")

    # Maze Generation Algorithm
    tk.Label(root, text="Maze Generation Algorithm:").pack(pady=5)
    generator_var = tk.StringVar(value="dfs")
    generator_dropdown = ttk.Combobox(root, textvariable=generator_var, values=["dfs", "kruskal", "prim", "wilson"])
    generator_dropdown.pack(pady=5)

    # Maze Solver Algorithm
    tk.Label(root, text="Maze Solver Algorithm:").pack(pady=5)
    solver_var = tk.StringVar(value="a_star")
    solver_dropdown = ttk.Combobox(root, textvariable=solver_var, values=["a_star", "dijkstra", "random", "pledge", "dfs", "bfs"])
    solver_dropdown.pack(pady=5)

    # FPS Speed
    tk.Label(root, text="FPS Speed:").pack(pady=5)
    fps_var = tk.IntVar(value=60)
    fps_slider = tk.Scale(root, from_=10, to=240, orient="horizontal", variable=fps_var)
    fps_slider.pack(pady=5)

    # Start Button
    start_button = tk.Button(root, text="Start Maze Program", command=start_pygame)
    start_button.pack(pady=20)

    # TODO: adding pause, step, reset, solve,
    # pause_button = tk.Button(root, text="Pause Program", command=)
    # pause_button.pack(pady=20)

    # Run the Tkinter main loop
    root.mainloop()

# --- Driver Code ---
if __name__ == "__main__":
    # new maze new mouse who dis
    new_maze = Maze.MazeMap(mazeWidth=800, mazeHeight=800, cellSize=20, startX=0, startY=0)
    new_mouse = solver.Mouse(maze=new_maze)

    # Testing main program
    mainMazeProgram(new_maze, new_mouse, fpsSpeed=60, generatorName='kruskal', solver='a_star')
    
    # Run the Tkinter settings menu
    # create_settings_menu(new_maze, new_mouse)
