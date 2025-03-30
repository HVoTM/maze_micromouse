# Inspired by Green Code - https://youtu.be/4L7BDRmH4cM?si=UOV9GOMhMNib9Pjb
import pygame
import random
from collections import deque
from typing import List, Optional, Any, Union
from kruskal import MazeDisjointSet, test_maze_disjoint_set
import json

GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARKGRAY = (51, 51, 51)
WALL_WIDTH = 6
BLINK_OFFSET = 4

class MazeMap:
    def __init__(self, mazeWidth: int, mazeHeight:int, cellSize: int, startX: int=0, startY: int=0) -> None:
        # Set up display
        self.screen = pygame.display.set_mode((mazeWidth, mazeHeight))
        self.clock = pygame.time.Clock()
        # Set window title
        pygame.display.set_caption("Maze Solver")
        # Background color is set to black
        self.backgroundColor = BLACK
        # Defining the cell properties
        self.cellSize = cellSize
        self.cols = mazeWidth // cellSize
        self.rows = mazeHeight // cellSize 
        print('Number of cols: ', self.cols, '\nNumber of rows: ', self.rows, '\nNumber of cells: ', self.cols * self.rows)
        # List represented as a 2-Dimensional grid of cells being enumerated by the xy        
        # IDEA TODO: using pygame's Sprite group
        # NOTE: check debug note of 3/14 to understand why we do list comprehension like this
        # In short, row-index represents y and column-index represents x
        self.MazeGrid = [[Cell(x, y, cellSize) for y in range(self.rows)] for x in range(self.cols)]
        # Flag to track the status of maze generated
        self.mazeGenerated = False
        # Using a stack for graph-based backtracking
        self.stack = []
        # TODO: if start somewhere we can add them to arguments
        # For Recursive Backtracking - Iterative Method, we kinda bypass the while loop by initializing the first element of the stack
        self.current = self.MazeGrid[startX][startY] # This can be also seen as starting cell
        self.startingX, self.startingY = startX, startY
        # list of walls that can be used for either kruskal or prim's algorithm
        self.walls = [] # Each wall is represented as a tuple of two elements: the two Cells being separated by that wall
        # A disjoint set data structure for Kruskal
        self.disjointSet = MazeDisjointSet(n_rows=self.rows, n_cols=self.cols)
        # Wilson
        self.remainingCells = []
        self.currentlyRandomWalking = False
        self.randomWalk = [] # a list to store the current cell of the random walks
    # -----------------------------------------------------------------------------
    def iterativeDFS(self):
        """Recursive Backtracker, or randomized depth-first search
        NOTE: this method works on every iteration based of the pygame's clock"""
        # Given a current cell as a parameter and mark as visited
        self.current.visited = True
        # Invoking checkNeighbors() to return unvisited neighbor cells
        next_cell = self.current.checkNeighbors(self.MazeGrid, return_all=False, includeVisited=False)
        # TEST using maze's method for finding neighbors
        # next_cell = self.checkNeighbors(currentCell=self.current)

        # Check if there is a neighboring cell that has been visited or not
        if next_cell:
            # Mark as visited
            next_cell.visited = True
            self.stack.append(self.current) # add the cell into the stack for backtracking
            self.removeWalls(self.current, next_cell) # remove walls between the current and next cell
            # 
            self.current = next_cell
        # Continue with maze generation if there are still cells in the maze to backtrack to
        elif self.stack:
            self.current = self.stack.pop()
        else:
            # If stack is empty and all cells are visited, the maze generation is complete
            if all(cell.visited for row in self.MazeGrid for cell in row):
                print("Maze Generation Complete!")
                self.mazeGenerated = True 

    # -----------------------------------------------------------------------------
    def recursiveDFS(self):
        "Hardly practical for large-scale mazes because recursion max depth is usually exceeded"
        self.recursiveDFS_util(self.current)

    def recursiveDFS_util(self, currentCell: "Cell"):
        # Mark the current cell as visited
        currentCell.visited = True
        
        # Chose one of the unvisited neighbours
        nextCells = currentCell.checkNeighbors(self.MazeGrid, return_all=True)
        # print(nextCells)
        # Base case: if not unvisited neighbors, return
        if not nextCells:
            return
        for eachCell in nextCells:
            # Remove the walls between the two cells
            self.removeWalls(cell1=currentCell, cell2=eachCell)
            # Invoke the routine recursively for the chosen cell
            self.recursiveDFS_util(eachCell)
    
    # -----------------------------------------------------------------------------
    def generateListofWalls(self) -> None:
        """Utility function:
        Generate a list of all walls separating the adjacent cells in the maze for our randomized Kruskal's algorithm
        """
        self.walls = [] # Reset the wall list
        for x in range(self.cols):
            for y in range(self.rows):
                # Top 
                if y > 0:  # Ensure the top wall exists and is within bounds
                    self.walls.append(((x, y), (x, y - 1)))
                # Right 
                if x < self.cols - 1:  # Ensure the right wall exists and is within bounds
                    self.walls.append(((x, y), (x + 1, y)))
                # Bottom 
                if y < self.rows - 1:  # Ensure the bottom wall exists and is within bounds
                    self.walls.append(((x, y), (x, y + 1)))
                # Left 
                if x > 0:  # Ensure the left wall exists and is within bounds
                    self.walls.append(((x, y), (x - 1, y)))
        # Shuffle the walls for a random choice, we can do this or randomly choose from the list of walls
        random.shuffle(self.walls)         
        print(self.walls)

    def iterativeKruskal(self):
        "Iterative randomized Kruskal's Algorithm (with sets)"
        if self.walls:
            chosenWall = self.walls.pop()
            # Randomly choose a wall from the list of walls
            # chosenWall = random.choice(self.walls) # the other randomization choice, either is easy to code
            # Retrieve the information of the cells being divided by this wall
            cell1, cell2 = chosenWall
            x1, y1 = cell1
            x2, y2 = cell2    
            # Check if the two cells belong to different sets by finding their parent cells
            if self.disjointSet.find(x1, y1) != self.disjointSet.find(x2, y2):
                # Remove the wall between the two cells (basically this is the add-edge step)
                self.removeWalls(self.MazeGrid[x1][y1], self.MazeGrid[x2][y2])
                # Join the sets of the formerly divided cells - UNIONIZE the two sets!!! hell ye Marx
                self.disjointSet.union(x1, y1, x2, y2)

    def iterativeKruskal_preload(self):
        """
        Same as the randomized iterative Kruskal but we just computed them all beforehand, before getting into the loop
        """
        for chosenWall in self.walls:
            # Randomly choose a wall from the list of walls
            # chosenWall = random.choice(self.walls) # the other randomization choice, either is easy to code
            # Retrieve the information of the cells being divided by this wall
            cell1, cell2 = chosenWall
            x1, y1 = cell1
            x2, y2 = cell2    
            # Check if the two cells belong to different sets by finding their parent cells
            if self.disjointSet.find(x1, y1) != self.disjointSet.find(x2, y2):
                # Remove the wall between the two cells (basically this is the add-edge step)
                self.removeWalls(self.MazeGrid[x1][y1], self.MazeGrid[x2][y2])
                # Join the sets of the formerly divided cells - UNIONIZE the two sets!!! hell ye Marx
                self.disjointSet.union(x1, y1, x2, y2)

    # -----------------------------------------------------------------------------
    # Randomized Prim's Algorithm without stacks without sets
    def iterativePrim(self):
        """Iterative randomized Prim's algorithm where we concurrently update the Maze grid as we display onto Pygame"""
        if self.walls: 
            # Pick a random wall from the list
            chosenWall = random.choice(self.walls)
            # Retrieving the two cells divided by the wall
            cell1, cell2 = chosenWall
            x1, y1 = cell1
            x2, y2 = cell2  
            cell1: "Cell" = self.MazeGrid[x1][y1]
            cell2: "Cell" = self.MazeGrid[x2][y2]
            # Display the currently compared cell
            cell1.DrawCell(self.screen, cellColor=RED, flash=True); cell2.DrawCell(self.screen, cellColor=RED, flash=True)
            # Remove the wall from the list so we don't have to revisit
            self.walls.remove(chosenWall)

            # Check if only one of the cells that the wall divides is visited
            # if (cell1.visited == True and cell2.visited == False) or (cell1.visited == False and cell2.visited == True):
            if cell1.visited != cell2.visited:
                # Remove the all and make a passage
                self.removeWalls(cell1=cell1, cell2=cell2)
                # Mark the unvisited cell as the part of the maze, and add the neighboring walls to the list
                if cell1.visited:
                    cell2.visited = True
                    self.walls.extend(self.retrieveWallsasXY_Tuple(cell2))
                else:
                    cell1.visited = True
                    self.walls.extend(self.retrieveWallsasXY_Tuple(cell1))
        # print(self.walls)

    def iterativePrim_preload(self, startCell: "Cell"):
        # Mark the cell as visited so that we don't have to revisit it 
        startCell.visited = True

        # Initialize the wall list with the walls of the starting cell
        self.walls = self.retrieveWallsasXY_Tuple(startCell)

        while self.walls: # TODO: change this into an iterative style for maze generation
            # Pick a random wall from the list
            chosenWall = random.choice(self.walls)
            # Retrieving the two cells divided by the wall
            cell1, cell2 = chosenWall 
            x1, y1 = cell1
            x2, y2 = cell2  
            cell1 = self.MazeGrid[x1][y1]
            cell2 = self.MazeGrid[x2][y2]
            # Remove the wall from the list so we don't have to revisit
            self.walls.remove(chosenWall)

            # Check if only one of the cells that the wall divides is visited
            # if (cell1.visited == True and cell2.visited == False) or (cell1.visited == False and cell2.visited == True):
            if cell1.visited != cell2.visited:
                # Remove the all and make a passage
                self.removeWalls(cell1=cell1, cell2=cell2)
                # Mark the unvisited cell as the part of the maze, and add the neighboring walls to the list
                if cell1.visited:
                    cell2.visited = True
                    self.walls.extend(self.retrieveWallsasXY_Tuple(cell2))
                else:
                    cell1.visited = True
                    self.walls.extend(self.retrieveWallsasXY_Tuple(cell1))
        # DEBUG Check
        # print(self.walls)
    # -----------------------------------------------------------------------------
    # Wilson's Algorithm Implementation
    def init_Wilson(self):
        # Generate a list containing all the maze's Cells, which we will be using to retrieve a randomly chosen cell
        for x in range(self.cols):
            for y in range(self.rows):
                self.remainingCells.append((x, y))
        # Set the initial cell (here just using the starting point, but we can do an arbitrarily random choice)
        self.current.visited = True
        self.remainingCells.remove((self.current.x, self.current.y))
        self.currentlyRandomWalking = False
        
    def iterativeWilson(self):
        """Wilson's algorithm: Generates an unbiased sample from the uniform distribution over all mazes, using loop-erased random walks"""
        # TODO: add a feature where the random walk backtracks to erase loop -> DONE
        # TODO: show the cells as gray while the algorithm is performing a random walk -> DONE
        if self.remainingCells:
            print(f"Number of remaining cells: {len(self.remainingCells)}")  # Debugging log
            # print(self.remainingCells)
            if not self.currentlyRandomWalking:
                "1. Either starting the algorithm or just finished adding a new random walk to the maze"
                # Choose a random unvisited cell
                start_coords = random.choice(self.remainingCells)
                print(f"Starting random walk from: {start_coords}")  # Debugging log
                start_x, start_y = start_coords
                self.current: "Cell" = self.MazeGrid[start_x][start_y]
                assert start_x == self.current.x
                assert start_y == self.current.y
                self.current.visited = True
                self.current.Color = DARKGRAY
                # Reset the random walk to a new list containing this starting cell's xy-coordinate
                # and Perform a loop-erased random walk
                self.randomWalk = [(self.current.x, self.current.y)]
                self.currentlyRandomWalking = True

            else: 
                "Case 2: Currently in a random walk"
                # Choose a random neighbor, important to call the checkneighbors to include also visited cells
                newCell: "Cell" = self.current.checkNeighbors(self.MazeGrid, return_all=False, includeVisited=True)
                # If the new cell is already in the random walk, ERASE THE LOOP
                if (newCell.x, newCell.y) in self.randomWalk:
                    # Getting the index of the cell that is revisited
                    loop_start = self.randomWalk.index((newCell.x, newCell.y))
                    # For display purpose, we remove the loop out of the random walk
                    for cellx, celly in self.randomWalk[loop_start+1:]:
                        self.MazeGrid[cellx][celly].Color = BLACK
                    # Erase the loop of the random walk by resetting to the array till the start of the loop that we have identified
                    self.randomWalk = self.randomWalk[:loop_start + 1]
                    # Restart at the latest element for the reset random walk
                    self.current = self.MazeGrid[self.randomWalk[-1][0]][self.randomWalk[-1][1]]
                    # print(f"Loop detected, erasing to: {self.randomWalk}")  # Debugging log
                else:
                    # If successfully built a path and connect to the current maze we have -> Add the random walk to the maze
                    if newCell.visited:
                        # print(f"Reached visited cell: ({newCell.x}, {newCell.y})")  # Debugging log
                        # print(f"Complete loop-erased random walk for this iteration:\n")
                        # for cellposition in self.randomWalk:
                            # print(cellposition)
                        for i in range(len(self.randomWalk) - 1):
                            x1, y1 = self.randomWalk[i]
                            x2, y2 = self.randomWalk[i + 1]
                            cell1: "Cell" = self.MazeGrid[x1][y1]
                            cell2: "Cell" = self.MazeGrid[x2][y2]
                            # TODO IMPROVE on how we can optimize and reduce unnecessary operations
                            self.removeWalls(cell1, cell2)
                            cell2.visited = True # Mark the cell as part of the maze, note that we have already marked the initial cell as visited
                            # NOTE TO SELF: this is very janky, we have the cell1 visited being marked an iteration later while cell2's Color is marked (or converted) back to BLACK later
                            # Maybe figure something out in the future to iprove this
                            cell1.Color = BLACK
                            # print(f"Removing cell:", cell1.x, cell1.y)  # Debug check
                            self.remainingCells.remove((cell1.x, cell1.y)) # Remove the added cells in the random 
                        # Remove the wall between the newCell: the one in the maze, and the last cell in the array to make contact with it
                        x, y = self.randomWalk[-1]
                        self.remainingCells.remove((x, y)) # We are still missing the last cell in the random walk so we remove that also
                        lastCellinRandomWalk = self.MazeGrid[x][y]
                        lastCellinRandomWalk.Color = BLACK 
                        self.removeWalls(cell1=newCell, cell2=lastCellinRandomWalk)
                        self.currentlyRandomWalking = False
                        return
                    else:
                        # Have yet to encounter the maze, continue the random walk
                        self.randomWalk.append((newCell.x, newCell.y))
                        self.current = newCell
                        self.current.Color = DARKGRAY

    def Wilson(self):
        """Wilson's algorithm: Generates an unbiased sample from the uniform distribution over all mazes, using loop-erased random walks"""
        while self.remainingCells:
            # Choose a random unvisited cell
            start_coords = random.choice(self.remainingCells)
            start_x, start_y = start_coords
            currentCell = self.MazeGrid[start_x][start_y]

            # Perform a loop-erased random walk form the random unvisited cell
            randomWalk = [(currentCell.x, currentCell.y)]
            while True:
                # Choose a random neighbor
                newCell = currentCell.checkNeighbors(self.MazeGrid)
                if not newCell:
                    break

                # If the new cell is already in the random walk, erase the loop
                if (newCell.x, newCell.y) in randomWalk:
                    # Getting the index of the cell that is revisited causing the loop
                    loop_start = randomWalk.index((newCell.x, newCell.y))
                    # Erase the loop of the random walk by resetting to the array till the start of the loop that we have identified
                    randomWalk = randomWalk[:loop_start + 1]
                else:
                    randomWalk.append((newCell.x, newCell.y))

                # If the new cell is part of the maze that we have already defined,  walk
                if newCell.visited:
                    break

                currentCell = newCell

            # Add the random walk to the maze
            for i in range(len(randomWalk) - 1):
                x1, y1 = randomWalk[i]
                x2, y2 = randomWalk[i + 1]
                cell1 = self.MazeGrid[x1][y1]
                cell2 = self.MazeGrid[x2][y2]
                self.removeWalls(cell1, cell2)
                cell2.visited = True
                self.remainingCells.remove((cell2.x, cell2.y))
    # -----------------------------------------------------------------------------
    # TODO: Aldous-Broder Algorithm and Fractal Tessellation algorithm
    def AldousBroder(self):
        pass

    def FractalTessellation(self):
        pass

    def Eller(self):
        pass

    def Sidewinder(self):
        pass
    # -----------------------------------------------------------------------------
    # Utility functions for the cells and maze
    #TODO
    def initMaze(self):
        """To initialize variables and parameters for maze"""
        # Initialize all cells as unvisited
        # Initialize the grid full of walls
        pass

    def blinkSpecifiedCell(self, screen: pygame.Surface, chosenCell: "Cell", blinkInterval: int = 500, cellColor: tuple=RED) -> None:
        """
        Blink a specified cell in the grid
        :param screen: The Pygame surface to draw on.
        :param chosenCell: The cell to blink.
        :param blink_interval: The interval (in milliseconds) for the blinking effect.
        """
        current_time = pygame.time.get_ticks()
        # Calculate whether the cell should be visible based on the current time
        if (current_time // blinkInterval) % 2 == 0:
            # Draw the cell with a blinking effect
            x = chosenCell.x * chosenCell.size
            y = chosenCell.y * chosenCell.size
            # left, top, width, height
            pygame.draw.rect(
                surface=screen,
                color=cellColor,  # Red color for blinking
                rect=(x+BLINK_OFFSET, y+BLINK_OFFSET, chosenCell.size-BLINK_OFFSET, chosenCell.size-BLINK_OFFSET), # offset for a beauty touch
            )
    
    def showSpecifiedCell(self, screen: pygame.Surface, chosenCell: "Cell", cellColor: tuple=RED) -> None:
        """
        Show a specified cell in the grid, do not blink
        :param screen: The Pygame surface to draw on.
        :param chosenCell: The cell to blink.
        :param blink_interval: The interval (in milliseconds) for the blinking effect.
        """
        # Draw the cell with a blinking effect
        x = chosenCell.x * chosenCell.size
        y = chosenCell.y * chosenCell.size
        # left, top, width, height
        pygame.draw.rect(
            surface=screen,
            color=cellColor, 
            rect=(x+BLINK_OFFSET, y+BLINK_OFFSET, chosenCell.size-BLINK_OFFSET, chosenCell.size-BLINK_OFFSET), # offset for a beauty touch
        )

    def removeWalls(self, cell1: "Cell", cell2: "Cell"):
        "Remove walls between adjacent cells for our maze"
        # Compare between the difference in indices of the two cells
        dx = cell1.x - cell2.x
        dy = cell1.y - cell2.y
        if dx == 1:
            cell1.walls[3] = False
            cell2.walls[1] = False
        elif dx == -1:
            cell1.walls[1] = False
            cell2.walls[3] = False
        if dy == 1:
            cell1.walls[0] = False
            cell2.walls[2] = False
        elif dy == -1:
            cell1.walls[2] = False
            cell2.walls[0] = False

    def checkNeighbors(self, currentCell: "Cell", return_all: bool = False) -> Union[List["Cell"], "Cell", None]:
        "Find unvisited neighboring cells and return those Cells"
        cellX, cellY = currentCell.x, currentCell.y

        neighbors = []
        if cellX > 0 and not self.MazeGrid[cellX - 1][cellY].visited:
            neighbors.append(self.MazeGrid[cellX - 1][cellY])
        if cellX < len(self.MazeGrid) - 1 and not self.MazeGrid[cellX + 1][cellY].visited:
            neighbors.append(self.MazeGrid[cellX + 1][cellY])
        if cellY > 0 and not self.MazeGrid[cellX][cellY - 1].visited:
            neighbors.append(self.MazeGrid[cellX][cellY - 1])
        if cellY < len(self.MazeGrid[0]) - 1 and not self.MazeGrid[cellX][cellY + 1].visited:
            neighbors.append(self.MazeGrid[cellX][cellY + 1])
        if neighbors:
            if not return_all:
                return random.choice(neighbors)
            else:
                return neighbors
        return None
    
    def retrieveWallsasXY_Tuple(self, currentCell: "Cell") -> List[tuple]:
        """Retrieving the walls, each represented as a pair of tuples, for each tuple represents the x,y of the Maze's MazeGrid"""
        x, y = currentCell.x, currentCell.y
        # init list to return
        walls = []
        if y > 0:  # Ensure the top wall exists and is within bounds
            walls.append(((x, y), (x, y - 1)))
        # Right 
        if x < self.cols - 1:  # Ensure the right wall exists and is within bounds
            walls.append(((x, y), (x + 1, y)))
        # Bottom 
        if y < self.rows - 1:  # Ensure the bottom wall exists and is within bounds
            walls.append(((x, y), (x, y + 1)))
        # Left 
        if x > 0:  # Ensure the left wall exists and is within bounds
            walls.append(((x, y), (x - 1, y)))
        return walls
    
    # -- MAIN LOOP --
    def generate(self, fpsSpeed: int= 60, generator: str="dfs", preload: bool = False, log_data: bool= False) -> None:
        """
        Run the main loop and display the maze

        Parameters
        ----------
        fpsSpeed : int
            The first parameter, an integer.
        generator : str
            Generation algorithms to be included:
            - "wilson": iterative depth-first search
            - "kruksal": iterative Kruskal's algorithm
            - "prim": iterative Prim's algorithm
            - "wilson": Wilson's algorithm
        Returns
        -------
        None
        """
        if preload:
            self.preload_display(fpsSpeed=fpsSpeed, generatorName=generator, log_data=log_data)
        else:
            self.iterative_display(fpsSpeed=fpsSpeed, generatorName=generator, log_data=log_data)
    
    def preload_display(self, fpsSpeed: int, generatorName: "str", log_data: bool= False) -> None:
        """
        Main call to preload the maze then display

        Args:
            fpsSpeed (int): 
            generator (str):
        """
        if generatorName == "kruskal":
        # Generate the list of walls
            self.generateListofWalls()
            self.iterativeKruskal_preload()
        elif generatorName == "prim":
            self.iterativePrim_preload(self.current)
        elif generatorName == "wilson":
            self.init_Wilson()
            self.Wilson()

        running = True
        paused = False
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
                        stepMode = not stepMode 
                        if stepMode:
                            print("Step mode enabled. Press S to step through the program.")
                        else:
                            print("Step mode disabled. Resuming normal execution.")
                    elif event.key == pygame.K_UP:  # Increase speed
                        fpsSpeed += 5

                    elif event.key == pygame.K_DOWN:  # Decrease speed
                        fpsSpeed = max(5, fpsSpeed - 5)  # Ensure FPS doesn't go below 5

            if paused and not stepMode:
                continue # end this iteration
            # If in step mode, wait for the user to press the step key
            if stepMode:
                continue

            # Fill the screen with the background color
            self.screen.fill(self.backgroundColor)
            # Generate maze with different algorithms. TODO: create a parameter/argument to choose the type of algorithm to generate the maze
            # self.iterativeDFS() # iterative depth-first search (recursive backtracking)
            # As the layout of the maze is still being changed within the generateMaze() function
            # self.iterativeKruskal()

            # Update the maze's grids' Cell objects 
            for x in range(self.cols):
                for y in range(self.rows): 
                    self.MazeGrid[x][y].DrawCell(self.screen)

            # DEBUG:
            # Add a blinking effect to a specific cell (e.g., the starting cell)
            row, col = 0, 0
            self.blinkSpecifiedCell(self.screen, self.MazeGrid[col][row])

            # Update the display
            pygame.display.update()
            # Control the frame rate
            self.clock.tick(fpsSpeed)
            if log_data:
                # Logging info stuff- not that it is necessary but is good to know when working with data-intensive applications
                print("Time passed in pygame's Clock: ",self.clock.get_time())
                print("Current Frame per Second: ", self.clock.get_fps())
        pygame.quit()

    def iterative_display(self, fpsSpeed: int= 60, generatorName: str="dfs", log_data:bool = False) -> None:
        """
        Display method for iterative algorithms and concurrently display the maze generation procedure

        Args:
            fpsSpeed (int): 
            generator (str):
        """
        if generatorName == "kruskal":
            self.generateListofWalls()
        elif generatorName == "prim":
            # Iinitialize the Prim's algorithm
            # Mark the cell as visited so that we don't have to revisit it 
            self.current.visited = True
            # Initialize the wall list with the walls of the starting cell
            self.walls = self.retrieveWallsasXY_Tuple(self.current)
        elif generatorName == "wilson":
            self.init_Wilson()

        running = True
        paused = False
        stepMode = False
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
                        self.iterativeWilson() 
                    elif event.key == pygame.K_UP:  # Increase speed
                        fpsSpeed += 5
                    elif event.key == pygame.K_DOWN:  # Decrease speed
                        fpsSpeed = max(5, fpsSpeed - 5)  # Ensure FPS doesn't go below 5

            if paused and not stepMode:
                continue # end this iteration
            # If in step mode, wait for the user to press the step key
            if stepMode:
                continue
            # Fill the screen with the background color
            self.screen.fill(self.backgroundColor)
            if generatorName == "dfs":
                self.iterativeDFS()
            elif generatorName == "kruskal":
                self.iterativeKruskal()
            elif generatorName == "prim":
                if self.walls:
                    self.iterativePrim()
                else:
                    print("Maze generation complete!")
            elif generatorName == "wilson":
                self.iterativeWilson()
            # Generate maze with different algorithms. TODO: create a parameter/argument to choose the type of algorithm to generate the maze
            # self.iterativeDFS() # iterative depth-first search (recursive backtracking)
            # As the layout of the maze is still being changed within the generateMaze() function
            # self.iterativeKruskal()

            # Update the maze's grids' Cell objects 
            for x in range(self.cols):
                for y in range(self.rows): 
                    self.MazeGrid[x][y].DrawCell(self.screen)
            # DEBUG:
            # Add a blinking effect to a specific cell (e.g., the starting cell)
            self.blinkSpecifiedCell(self.screen, self.MazeGrid[self.startingX][self.startingY])

            # Update the display
            pygame.display.update()
            # Control the frame rate
            self.clock.tick(fpsSpeed)
            if log_data:
                # Logging info stuff- not that it is necessary but is good to know when working with data-intensive applications
                print("Time passed in pygame's Clock: ",self.clock.get_time())
                print("Current Frame per Second: ", self.clock.get_fps())
        pygame.quit()

    def save2file(self, filename: str) -> None:
        """
        Save the maze structure to a file. Example: `maze.save_to_file("saved_maze.json")`
        Args:
            filename (str): The name of the file to save the maze to.
        """
        maze_data = {
            "cols": self.cols,
            "rows": self.rows,
            "cellSize": self.cellSize,
            "walls": [
                [[cell.walls[0], cell.walls[1], cell.walls[2], cell.walls[3]] for cell in row]
                for row in self.MazeGrid
            ],
        }
        with open(filename, "w") as file:
            json.dump(maze_data, file)
        print(f"Maze saved to {filename}")

    def load_file(self, filename: str) -> None:
        """
        Load the maze structure from a file. Example: `loaded_maze.load_from_file("saved_maze.json")`
        Args:
            filename (str): The name of the file to load the maze from.
        """
        with open(filename, "r") as file:
            maze_data = json.load(file)
        self.cols = maze_data["cols"]
        self.rows = maze_data["rows"]
        self.cellSize = maze_data["cellSize"]
        # Reconstruct the MazeGrid
        self.MazeGrid = [
            [
                Cell(x, y, self.cellSize, walls=maze_data["walls"][x][y])
                for y in range(self.rows)
            ]
            for x in range(self.cols)
        ]
        print(f"Maze loaded from {filename}")

class Cell:
    "Representing a cell in the maze"
    def __init__(self, x: int, y:int, size: int):
        # x, y representing the indices of the cells in the maze.grid attribute (a 2-D array)
        self.x = x
        self.y = y
        self.size = size # use the size to compute the real coordinate
        self.pygameCoordinate = (self.x * self.size, self.y * self.size)
        # List of walls, returned with booleans to determine if there is a wall or not. Intialized with walls on four sides
        self.walls = [True, True, True, True] # Top, Right, Bottom, Left
        # This attribute will be used for maze solving algorithm for later. Mark all cells as unvisited initally
        self.visited = False
        # Iterative randomized Kruskal's algorithm's set
        self.cellSet = None
        self.Color: tuple = BLACK

    def DrawCell(self, screen: pygame.Surface, flash: bool= False):
        """
        Draw the cell and its wall
        
        Args:
        screen (pygame.Surface): The Pygame surface to draw on.
        cellColor (tuple): The color of the cell.
        flash (bool): Whether to flash the cell with a different color.
        """
        # using these attributes to draw them on the pygame Surface
        x = self.x * self.size
        y = self.y * self.size

        # # FIXME: If flashing, alternate the color
        # if flash:
        #     cellColor = self.Color if pygame.time.get_ticks() // 500 % 2 == 0 else BLACK

        # Checking if this cell has been visited or not
        """
        if self.visited: #NOTE: I think this condition is not necessary since we are going to draw on the cell anyways
            # Rect(left, top, width, height) -> Rect
            pygame.draw.rect(surface=screen, color=self.Color, rect=(x, y, self.size, self.size), width=WALL_WIDTH)
        """
        pygame.draw.rect(surface=screen, color=self.Color, rect=(x, y, self.size, self.size))
        # Drawing the walls
        if self.walls[0]:
            pygame.draw.line(surface=screen, color=GREEN, start_pos=(x, y), end_pos=(x + self.size, y), width=WALL_WIDTH)
        if self.walls[1]:
            pygame.draw.line(surface=screen, color=GREEN, start_pos=(x + self.size, y), end_pos=(x + self.size, y + self.size), width=WALL_WIDTH)
        if self.walls[2]:
            pygame.draw.line(surface=screen, color=GREEN, start_pos=(x + self.size, y + self.size), end_pos=(x, y + self.size), width=WALL_WIDTH)
        if self.walls[3]:
            pygame.draw.line(surface=screen, color=GREEN, start_pos=(x, y + self.size), end_pos=(x, y), width=WALL_WIDTH)
        
    def checkNeighbors(self, grid: List["Cell"], return_all: bool = False, includeVisited: bool = False) -> Union[List["Cell"], "Cell", None]:
        """Find neighboring cells
        Parameters
        ----------
        grid : List["Cell"]
            Grid of the mazes containing all the cells
        return_all : bool
            Default = False, to return all of the neighbors or not
        includeVisited: bool (default: False__)
            To include visited neighbors as well
        Returns
        -------
        None
        """
        neighbors = []
        # Case 1: if we include all the visited nodes as well
        if includeVisited:
            if self.x > 0:
                neighbors.append(grid[self.x - 1][self.y])
            if self.x < len(grid) - 1:
                neighbors.append(grid[self.x + 1][self.y])
            if self.y > 0:
                neighbors.append(grid[self.x][self.y - 1])
            if self.y < len(grid[0]) - 1:
                neighbors.append(grid[self.x][self.y + 1])
            if neighbors:
                if not return_all:
                    return random.choice(neighbors)
                else:
                    return neighbors
            return None 
        else:
            if self.x > 0 and not grid[self.x - 1][self.y].visited:
                neighbors.append(grid[self.x - 1][self.y])
            if self.x < len(grid) - 1 and not grid[self.x + 1][self.y].visited:
                neighbors.append(grid[self.x + 1][self.y])
            if self.y > 0 and not grid[self.x][self.y - 1].visited:
                neighbors.append(grid[self.x][self.y - 1])
            if self.y < len(grid[0]) - 1 and not grid[self.x][self.y + 1].visited:
                neighbors.append(grid[self.x][self.y + 1])
            if neighbors:
                if not return_all:
                    return random.choice(neighbors)
                else:
                    return neighbors
            return None 
            
# Boiler plate code to test things
if __name__ == "__main__":
    test_maze_disjoint_set()
    randomCell = Cell(5, 6, 20)
    # print(randomCell.retrieveWalls())