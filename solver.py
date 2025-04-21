# Maze-solver algorithms: Depth-First Search, Breadth-First Search, A* Search, Dijkstra's Algorithm, etc.
from Maze import MazeMap, Cell
from enum import Enum
import random
from collections import deque
from typing import List, Tuple, Union
from settings import Colors
import heapq

# using enum.Enum to define the symbolic names for the fixed set of constants or values 
class Direction(Enum):
    UP = (0, -1)    # Move up (decrease y)
    RIGHT = (1, 0)  # Move right (increase x)
    DOWN = (0, 1)   # Move down (increase y)
    LEFT = (-1, 0)  # Move left (decrease x)

# Define the opposite direction of the mouse
OPPOSITE_DIRECTION = {Direction.UP: Direction.DOWN,
                    Direction.DOWN: Direction.UP,
                    Direction.LEFT: Direction.RIGHT,
                    Direction.RIGHT: Direction.LEFT,
                    }

ADJACENT_DIRECTION = {Direction.UP: [Direction.LEFT, Direction.RIGHT],
                      Direction.DOWN: [Direction.LEFT, Direction.RIGHT],
                      Direction.LEFT: [Direction.UP, Direction.DOWN],
                      Direction.RIGHT: [Direction.UP, Direction.DOWN]}

# Parameter settings
NUM_TRAILING_CELLS = 5
TRAILING_COLORS = [Colors.DARK_RED, Colors.FIREBRICK, Colors.CRIMSON, Colors.RED, Colors.LIGHT_RED]

class Mouse:
    def __init__(self, maze: "MazeMap", x: int=0, y:int=0):
        """
        Initialize the solver with a reference to the MazeMap class
        """
        self.x = x; self.y = y; # Starting position indices
        self.maze: "MazeMap" = maze # reference to the MazeMap instance to access the maze grid # NOTE to self: the referenced maze has yet to be updated when initialized
                                    # TODO: maybe add an update function for whenever a maze is updated
        self.currentCell :"Cell"= self.maze.MazeGrid[self.x][self.y] 
        # For visual effects
        self.trailingCells :List["Cell"] = deque([self.maze.MazeGrid[0][0]]*5)
        # print(self.trailingCells)
        # We assume the end of the maze is bottom right
        self.endX = self.maze.cols - 1
        self.endY = self.maze.rows - 1
        self.direction = None # indicate the current direction that the mouse is going
        # Attributes marking the end of the maze-solving algorithm
        self.MazeSolved = False
        self.finalPath: List[tuple[int]] = [] # Final path which will be used to draw the final appropriate path
        # Depth First search data structure 
        self.stack = [(self.x, self.y)] # include the original starting position
        self.visited = set() 
        self.parent = dict() # Dictionary to store the parent of each cell
        # Breadth First search
        self.queue = deque([(self.x, self.y)]) # double-ended queue for first in first out
        # Dead-end filling
        self.dead_ends: List[Tuple[int]] = [] 
        self.deadEnd = None
        self.fillingaDeadEnd = False # A state to signify if the program is still filling in a deadEnd
        # Dijsktra's algorithm
        self.distances = None
        self.pq = [] # A priority used for retrieving the smallest distance
        # We will use the visited set
        # A star data structure attribute
        self.open_list = None
        self.closed_list = None

    # ----------------------------------------------------------------------------------
    # VISUAL STUFF FOR THE SOLVER
    def markCell(self, x:int, y:int, color= Colors.DARK_ORANGE.value):
        """Mark the current Cell as visited by giving it a color"""
        self.maze.MazeGrid[x][y].Color = color

    def resetallCells_toBlack(self):
        pass

    def updateTrailsofMouse(self):
        "Update the visual trailing colors on the running Mouse"
        if len(self.trailingCells) == NUM_TRAILING_CELLS:
            tailingCell : "Cell" = self.trailingCells.pop()
            # Mark the tail or the last one popped out as a mark of the cell, which is LIGHT_ORANGE
            self.markCell(tailingCell.x, tailingCell.y)
        # Add the latest Cell
        self.trailingCells.appendleft(self.currentCell)
    
        for i in range(len(self.trailingCells)):
            self.trailingCells[i].Color = TRAILING_COLORS[i].value

    def reconstructPath(self) -> None:
        """Utility function: Reconstruct the path from the start to the goal using a hashmap"""
        path = []
        current = (self.endX, self.endY)
        while current in self.parent: # Backtrack from the goal to the path
            path.append(current)
            current = self.parent[current] # Retrieve the parent of this p
        path.append((0, 0))
        path.reverse() # Reverse to get it from goal to start
        print(f"Final path: {'->'.join(map(str, path))}") # Convert each tuple in the path into a string,, then use join to join the string representations of the coordinates
        # with '->' as the separator
        self.finalPath = path
    
    def highlightFinalPath(self):
        "Draw the final path, or mark it as a neon green color"
        for cell in self.finalPath:
            self.maze.MazeGrid[cell[0]][cell[1]].Color = Colors.NEON_GREEN.value

    def resetMazeColor(self):
        self.maze.resetGrids2BLACK()

    def findNeighbors(self, currentCell: "Cell") -> Union[Tuple[int], List[Tuple[int]]]:
        """Find neighbors that have yet to be visited in the solver"""
        available_directions = []
        neighborCells = []

        # Referring to the order of the wall position: Top, Right, Bottom, Left
        if not currentCell.walls[0]:  # No wall at the top
            available_directions.append(Direction.UP)
        if not currentCell.walls[1]:  # No wall on the right
            available_directions.append(Direction.RIGHT)
        if not currentCell.walls[2]:  # No wall at the bottom
            available_directions.append(Direction.DOWN)
        if not currentCell.walls[3]:  # No wall on the left
            available_directions.append(Direction.LEFT)
        
        print("Available directions given the wall presence: {}".format(available_directions))
        # Return the neighboring Cells
        for direction in available_directions:
            dx, dy = direction.value # Retrieve the value of the direction
            
            if (currentCell.x+dx, currentCell.y+dy) not in self.visited:
                neighborCells.append((currentCell.x+dx, currentCell.y+dy))
        # # Return a single Cell if only one neighbor exists, otherwise return the list
        # if len(neighborCells) == 1:
        #     return neighborCells[0]
        return neighborCells
    
    def checkJunction(self, x:int, y:int):
        """Checking if the current Cell is a junction"""
        currCell = self.maze.MazeGrid[x][y]
        # Basically checking the there are 1 or 2 walls -> 3-way/4-way
        if sum(currCell.walls) <= 1:
            return True  
        else:
            return False 
        # open_neighbors = 4 - sum(currCell.walls)  # Count open neighbors
        # return open_neighbors > 2  # A junction has more than 2 open neighbors

    # ----------------------------------------------------------------------------------
    def RandomMouse(self):
        "Random Mouse algorithm: unintelligent robot that moves randomly, does not require any memory of the maze"
        print("Self.x is {}, self.y is {} \n end-X is {}, end-Y is {}".format(self.x, self.y, self.endX, self.endY))
        # While we have yet to reach the desired goal
        if self.x != self.endX or self.y != self.endY: # Took me 15 minutes staring at the condition until I realize what was wrong, and -> or
            print("--------------------------------------\nStill solving...")
            # Check the current grid cell to see what path there is
            self.currentCell = self.maze.MazeGrid[self.x][self.y]
            # Debug
            print(f"Current cell is {self.currentCell.x} | {self.currentCell.y}")
            print("Current states of the walls: top -> right -> bottom -> left is: {}".format(self.currentCell.walls))
            # Check with the current direction that th
            # See if there are availiability for four directions
            # NOTE, might be DEPRECATED: adding an extra memory might not be too much, but we can do better by just inferring if there is not a wall
            # meaning there is a path to the Cell, then we retrieve the corresponding dx, dy
            available_directions = []
            # Referring to the order of the wall position: Top, Right, Bottom, Left
            if not self.currentCell.walls[0]:  # No wall at the top
                available_directions.append(Direction.UP)
            if not self.currentCell.walls[1]:  # No wall on the right
                available_directions.append(Direction.RIGHT)
            if not self.currentCell.walls[2]:  # No wall at the bottom
                available_directions.append(Direction.DOWN)
            if not self.currentCell.walls[3]:  # No wall on the left
                available_directions.append(Direction.LEFT)
            
            print("Available directions given the wall presence: {}".format(available_directions))
            # Prioritize continuing in either the current direction or the adjacent directions, only return when necessary
            # Exclude the opposite direction unless it's the only option
            if self.direction:
                currOppositeDirection = OPPOSITE_DIRECTION.get(self.direction)
                filtered_directions = [d for d in available_directions if d != currOppositeDirection]
                
                # If there are other directions, use them; otherwise, use the opposite direction
                if filtered_directions:
                    available_directions = filtered_directions
                else:
                    print(f"No other options available. Falling back to opposite direction: {currOppositeDirection}")
            # Randomly select one of the remaining openings
            if available_directions:
                # Randomly select one of the openings
                self.direction = random.choice(available_directions)
                dx, dy = self.direction.value # Retrieve the value of the direction
                if (self.x + dx, self.y + dy) not in self.visited:
                    self.parent[(self.x+dx, self.y+dy)] = (self.x, self.y)
                self.x += dx
                self.y += dy
                print(f"Continued {self.direction.name} to ({self.x}, {self.y})")
                return # End this iteration
        else:
            self.MazeSolved = True
            print("Reached goal at x={}| y={}".format(self.endX, self.endY))
    
    # FIXME: wall following does not work right, check again the theory and constraints of the wall follower
    def rightHand(self):
        """Right-Hand Rule of Wall Following - Depth-first in-order tree traversal"""
        # NOTE: from the perspective of the mouse, starting from the top down, 
        # the right-hand rule is actually the left-hand rule for the mouse
        # As we rotate the maze 180 degree
        if self.x != self.endX or self.y != self.endY:
            self.currentCell = self.maze.MazeGrid[self.x][self.y]
            print(f"Current cell: ({self.currentCell.x}, {self.currentCell.y})")
            print(f"Wall states (top, right, bottom, left): {self.currentCell.walls}")

            if (self.x, self.y) not in self.visited:
                self.visited.add((self.x, self.y))
                print("Marking cell ({}, {}) as visited".format(self.x, self.y))
            # Determine the direction to move based on the right-hand rule
            if self.direction is None:
                self.direction = Direction.RIGHT  # Default starting direction

            # Priority: Right -> Forward -> Left -> Backward
            directions_priority = [
                (self.direction, "Right"),  # Right-hand direction
                (ADJACENT_DIRECTION[self.direction][0], "Forward"),  # Forward direction
                (ADJACENT_DIRECTION[self.direction][1], "Left"),  # Left-hand direction
                (OPPOSITE_DIRECTION[self.direction], "Backward")  # Opposite direction
            ]

            # Try to move to an unvisited cell #NOTE: added this for prioritization of unvisited cells
            for direction, label in directions_priority:
                dx, dy = direction.value
                next_x, next_y = self.x + dx, self.y + dy

                # Check if the direction is valid (no wall, within bounds, and unvisited)
                if 0 <= next_x < self.maze.cols and 0 <= next_y < self.maze.rows:
                    if not self.currentCell.walls[list(Direction).index(direction)] and (next_x, next_y) not in self.visited:
                        print(f"Moving {label} to unvisited cell ({next_x}, {next_y})")
                        self.direction = direction
                        self.x, self.y = next_x, next_y
                        return  # Move to the next cell
            
            # If all neighbors are visited, backtrack again to the priority of directions
            for direction, label in directions_priority:
                dx, dy = direction.value
                next_x, next_y = self.x + dx, self.y + dy

                # Check if the direction is valid (no wall and within bounds)
                if 0 <= next_x < self.maze.cols and 0 <= next_y < self.maze.rows:
                    if not self.currentCell.walls[list(Direction).index(direction)]:
                        print(f"Moving {label} to ({next_x}, {next_y})")
                        self.direction = direction
                        self.x, self.y = next_x, next_y
                        return  # Move to the next cell

            print("No valid moves found. Stuck!")
        else:
            print(f"Goal reached at ({self.endX}, {self.endY})")

    # ----------------------------------------------------------------------------------
    # Depth-first traversal - DFS method of finding a maze
    def depthFirstSearch(self):
        """Depth-First Search (DFS) algorithm for maze solving."""
        # Stack to keep track of the path
        while self.stack:
            # Get the current position
            self.x, self.y = self.stack.pop()
            self.currentCell = self.maze.MazeGrid[self.x][self.y]

            # Mark the current cell as visited
            self.visited.add((self.x, self.y))
            print(f"Visiting cell: ({self.x}, {self.y})")

            # Check if the goal is reached
            if self.x == self.endX and self.y == self.endY:
                print(f"Goal reached at ({self.x}, {self.y})")
                self.MazeSolved = True
                self.finalPath = self.reconstructPath()

            # Get all possible directions from the current cell
            neighbors = []
            if not self.currentCell.walls[0] and (self.x, self.y - 1) not in self.visited:  # Top
                neighbors.append((self.x, self.y - 1))
            if not self.currentCell.walls[1] and (self.x + 1, self.y) not in self.visited:  # Right
                neighbors.append((self.x + 1, self.y))
            if not self.currentCell.walls[2] and (self.x, self.y + 1) not in self.visited:  # Bottom
                neighbors.append((self.x, self.y + 1))
            if not self.currentCell.walls[3] and (self.x - 1, self.y) not in self.visited:  # Left
                neighbors.append((self.x - 1, self.y))

            print(f"Neighbors to visit: {neighbors}")

            # Add neighbors to the stack
            for neighbor in neighbors:
                if neighbor not in self.visited:
                    self.stack.append(neighbor)
                    self.parent[neighbor] = (self.x, self.y)

        print("No path to the goal was found.")

    def depthFirstSearch_optimized(self) -> List[tuple]:
        """TESTING: Optimized Depth-First Search (DFS) with path reconstruction embedded in the stack."""
        stack = [(self.x, self.y, [(self.x, self.y)])]  # Stack stores (x, y, path)
        visited = set()

        while stack:
            # Get the current position and path
            self.x, self.y, path = stack.pop()
            self.currentCell = self.maze.MazeGrid[self.x][self.y]

            # Mark the current cell as visited
            visited.add((self.x, self.y))
            print(f"Visiting cell: ({self.x}, {self.y})")

            # Check if the goal is reached
            if self.x == self.endX and self.y == self.endY:
                print(f"Goal reached at ({self.x}, {self.y})")
                self.finalPath = path  # Store the final path
                return path

            # Get all possible directions from the current cell
            neighbors = []
            if not self.currentCell.walls[0] and (self.x, self.y - 1) not in visited:  # Top
                neighbors.append((self.x, self.y - 1))
            if not self.currentCell.walls[1] and (self.x + 1, self.y) not in visited:  # Right
                neighbors.append((self.x + 1, self.y))
            if not self.currentCell.walls[2] and (self.x, self.y + 1) not in visited:  # Bottom
                neighbors.append((self.x, self.y + 1))
            if not self.currentCell.walls[3] and (self.x - 1, self.y) not in visited:  # Left
                neighbors.append((self.x - 1, self.y))

            print(f"Neighbors to visit: {neighbors}")

            # Add neighbors to the stack with the updated path
            for neighbor in neighbors:
                stack.append((neighbor[0], neighbor[1], path + [neighbor]))

        print("No path to the goal was found.")
        return []  # Return an empty path if no solution is found
    
    def depthFirstSearch_iter(self)-> bool:
        """Concurrently update the maze solving procedure of depth-first-search"""
        if self.x == self.endX and self.y == self.endY:
            print(f"Goal Reached at ({self.x}, {self.y})!")
            self.MazeSolved = True
            self.reconstructPath()
        else:
            # Continue with the pathfinding
            if self.stack:
                # Get the current position
                self.x, self.y = self.stack.pop()
                self.currentCell = self.maze.MazeGrid[self.x][self.y]
                # Mark as visited
                self.visited.add((self.x, self.y)); print(f"Visiting cell: ({self.x}, {self.y})")

                # Get all possible directions from the current cell
                neighbors = []
                if not self.currentCell.walls[0] and (self.x, self.y - 1) not in self.visited:  # Top
                    neighbors.append((self.x, self.y - 1))
                if not self.currentCell.walls[1] and (self.x + 1, self.y) not in self.visited:  # Right
                    neighbors.append((self.x + 1, self.y))
                if not self.currentCell.walls[2] and (self.x, self.y + 1) not in self.visited:  # Bottom
                    neighbors.append((self.x, self.y + 1))
                if not self.currentCell.walls[3] and (self.x - 1, self.y) not in self.visited:  # Left
                    neighbors.append((self.x - 1, self.y))

                print(f"Neighbors to visit: {neighbors}")
                # Add neighbors to the stack
                for neighbor in neighbors:
                    if neighbor not in self.visited:
                        self.stack.append(neighbor)
                        self.parent[neighbor] = (self.x, self.y)
            else:
                print("No path to the goal was found...")
    
    def Tremaux(self):
        pass

    def Pledge(self):
        pass

    # ----------------------------------------------------------------------------------
    # FIXME: algorithm not really working ...
    def findDeadEnds(self):
        for row in self.maze.MazeGrid:
            for cell in row:
                if sum(cell.walls) >= 3:
                    self.dead_ends.append((cell.x, cell.y))
                    self.visited.add((cell.x, cell.y))
                    # Visual marking on the maze so that we know that it is marked as a dead-ends
                    self.markCell(x=cell.x, y=cell.y, color=Colors.MAGENTA.value)
    
    def fillinPath(self):
        """Filling in the path of the current deadEnd until we reach a junction - or meeting a cell which has more than 2 neighbors, not
        regarding the visited cells, which we will mark
        """
        print("Currently running fillinPath()...\n")
        # if not self.checkJunction(*self.deadEnd):
        #     self.visited.add(self.deadEnd) # if the neighbor of this current cell does not open to a junction, mark as visited
        #     self.markCell(*self.deadEnd, color=Colors.MAGENTA.value) # Marked for visuals
        #     neighbor = self.findNeighbors(self.maze.MazeGrid[self.deadEnd[0]][self.deadEnd[1]]) # Since we know that the current cell is not a junction
        #     # We can use findNeighbors to return the neighboring cell that disregard visited cells
        #     self.deadEnd = neighbor[0] # Extract the cell object out from the array and assign this new current de
        # Checking if the returned array is of a single cell or not with the current deadend we are at
        if len(self.findNeighbors(self.maze.MazeGrid[self.deadEnd[0]][self.deadEnd[1]])) == 1:
            self.visited.add(self.deadEnd) # if the neighbor of this current cell does not open to a junction, mark as visited
            self.markCell(*self.deadEnd, color=Colors.MAGENTA.value) # Marked for visuals
            neighbor = self.findNeighbors(self.maze.MazeGrid[self.deadEnd[0]][self.deadEnd[1]])
            if neighbor[0] == (self.endX, self.endY):
                self.fillingaDeadEnd = False
                return
            self.deadEnd = neighbor[0] # Extract the cell object out from the array and assign this new current deadEnd
        else: # Finish filling a dead end since junction met
            self.fillingaDeadEnd = False
            
    def deadEndFilling_rec(self):
        # First off, find all of the dead-ends in the maze
        self.findDeadEnds()
        # # Test `findNeighbors()`
        # currCellNeighbors = self.findNeighbors(self.maze.MazeGrid[4][5])
        # for neighborCellx, neighborCelly in currCellNeighbors:
        #     self.markCell(neighborCellx, neighborCelly, color=Colors.CRIMSON.value)
        while self.dead_ends:
            # Pick a new random deadEnds
            self.deadEnd = random.choice(self.dead_ends)
            # Debug
            print(f"Choosing a random dead-end at x: {self.deadEnd[0]}| y: {self.deadEnd[1]}")
            self.dead_ends.remove(self.deadEnd)
            self.visited.add(self.deadEnd) # Add to the list of visited nodes
            self.fillinPath()
    
    def deadEndFilling_iter(self):
        "Iterative version"
        # NOTE: first off, invoke `self.findDeadEnds()` first to find all the current dead ends
        # Checking if there are still dead_ends to be made or the program is currently filling a dead end
        if self.fillingaDeadEnd:
            # Then calling fillinPath() to check if the current deadEnd can be extended further until we reach a junction
            self.fillinPath()
        # If program finishes filling a current dead end
        else:
            if self.dead_ends: # Check if there are still dead ends to be filled in, choose a new one
                self.deadEnd = random.choice(self.dead_ends)
                print(f"Choosing a random dead-end at x: {self.deadEnd[0]}| y: {self.deadEnd[1]}")
                self.dead_ends.remove(self.deadEnd) 
                self.visited.add(self.deadEnd) 
                self.fillingaDeadEnd = True
            else:
                # TODO: adding solving path for the remaining
                pass
    def deadEndFilling_iter_beta(self):
        """Iterative version of dead-end filling."""
        # If currently filling a dead end
        if self.fillingaDeadEnd:
            # Continue filling the current dead end until a junction is reached
            if not self.checkJunction(*self.deadEnd):
                self.visited.add(self.deadEnd)  # Mark the current cell as visited
                self.markCell(*self.deadEnd, color=Colors.MAGENTA.value)  # Mark for visuals
                neighbors = self.findNeighbors(self.maze.MazeGrid[self.deadEnd[0]][self.deadEnd[1]])

                if len(neighbors) == 1:  # Dead-end should have exactly one neighbor
                    self.deadEnd = neighbors[0]# Move to the next cell
                    self.visited.add(self.deadEnd)
                else:
                    print(f"Error: Dead-end at ({self.deadEnd[0]}, {self.deadEnd[1]}) has multiple neighbors!")
            else:
                # Finish filling the current dead end since a junction is reached
                print(f"Finished filling dead-end at x: {self.deadEnd[0]} | y: {self.deadEnd[1]}")
                self.fillingaDeadEnd = False
        else:
            # If not currently filling a dead end, select a new one
            if self.dead_ends:
                self.deadEnd = random.choice(self.dead_ends)  # Pick a random dead end
                print(f"Choosing a random dead-end at x: {self.deadEnd[0]} | y: {self.deadEnd[1]}")
                self.dead_ends.remove(self.deadEnd)  # Remove it from the list of dead ends
                self.visited.add(self.deadEnd)  # Mark it as visited
                self.fillingaDeadEnd = True  # Start filling this dead end
            else:
                # No more dead ends to process
                print("All dead ends have been filled.")
    # ----------------------------------------------------------------------------------
    # Shortest Path &  Pathfinding Algorithms, graph-based algorithms
    def breadthFirstSearch(self) -> List:
        """Graph-based implementation: Breadth-first search for maze solving."""
        # queue (FIFO) to keep track of the path
        queue = deque([(self.x, self.y)]) # syntax for initializing a nonempty deque: queue=deque([1, 2])
        visited = set()  # Keep track of visited cells
        parent = dict() # Dictionary to store the parent of each cell
        print("Breadth-first search chosen, now running the solver...")

        while queue:
            # Get the current position
            self.x, self.y = queue.pop()
            self.currentCell = self.maze.MazeGrid[self.x][self.y]

            # Mark the current cell as visited
            visited.add((self.x, self.y))
            print(f"Visiting cell: ({self.x}, {self.y})")

            # Check if the goal is reached
            if self.x == self.endX and self.y == self.endY:
                print(f"Goal reached at ({self.x}, {self.y})")
                self.finalPath = self.reconstructPath()
                self.MazeSolved = True

            # Get all possible directions from the current cell
            # NOTE: the order of the directions added: Top -> Right -> Bottom -> Left
            neighbors = []
            if not self.currentCell.walls[0] and (self.x, self.y - 1) not in visited:  # Top
                neighbors.append((self.x, self.y - 1))
            if not self.currentCell.walls[1] and (self.x + 1, self.y) not in visited:  # Right
                neighbors.append((self.x + 1, self.y))
            if not self.currentCell.walls[2] and (self.x, self.y + 1) not in visited:  # Bottom
                neighbors.append((self.x, self.y + 1))
            if not self.currentCell.walls[3] and (self.x - 1, self.y) not in visited:  # Left
                neighbors.append((self.x - 1, self.y))

            print(f"Neighbors to visit: {neighbors}")

            # Add neighbors to the stack
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.appendleft(neighbor)
                    parent[neighbor] = (self.x, self.y)

        print("No path to the goal was found.")
        return []

    def breadthFirstSearch_iter(self)-> None:
        """Concurrently update the maze solving procedure of depth-first-search"""
        """Graph-based implementation: Breadth-first search for maze solving."""
        print("Breadth-first search chosen, now running the solver...")
        if self.x == self.endX and self.y == self.endY:
            print(f"Goal Reached at ({self.x}, {self.y})!")
            self.reconstructPath()
            self.MazeSolved = True
        else:
            if self.queue:
                # Get the current position
                self.x, self.y = self.queue.pop()
                self.currentCell = self.maze.MazeGrid[self.x][self.y]

                # Mark the current cell as visited
                self.visited.add((self.x, self.y))
                print(f"Visiting cell: ({self.x}, {self.y})")

                # Get all possible directions from the current cell
                # NOTE: the order of the directions added: Top -> Right -> Bottom -> Left
                neighbors = []
                if not self.currentCell.walls[0] and (self.x, self.y - 1) not in self.visited:  # Top
                    neighbors.append((self.x, self.y - 1))
                if not self.currentCell.walls[1] and (self.x + 1, self.y) not in self.visited:  # Right
                    neighbors.append((self.x + 1, self.y))
                if not self.currentCell.walls[2] and (self.x, self.y + 1) not in self.visited:  # Bottom
                    neighbors.append((self.x, self.y + 1))
                if not self.currentCell.walls[3] and (self.x - 1, self.y) not in self.visited:  # Left
                    neighbors.append((self.x - 1, self.y))

                print(f"Neighbors to visit: {neighbors}")

                # Add neighbors to the stack
                for neighbor in neighbors:
                    if neighbor not in self.visited:
                        self.queue.appendleft(neighbor)
                        self.parent[neighbor] = (self.x, self.y) # Mark that neighbor cell's parent as the current cell's xy-coordinate
            else:
                print("No path to the goal was found.")
            self.MazeSolved = False

    # ----------------------------------------------------------------------------------
    def Dijsktra(self):
        # Given that the weights between vertices are uniform, meaning that they have the same weight
        self.distances = [[float('inf') for _ in range(self.maze.cols)] for _ in range(self.maze.rows)]    
        self.distances[self.x][self.y] = 0 # starting vertex should be 0
        # Alternative data structure: self.distaces = {(self.x, self.y):0}

        # Dictionary to store the parent of each cell for path reconstruction
        parent = {}

        # Initialize a min priority queue heap
        pq = [(0, (self.x, self.y))]

        while pq:
            # Get the current vertex with the minimum distance
            curr_dist, (curr_x, curr_y) = heapq.heappop(pq)
            self.currentCell = self.maze.MazeGrid[curr_x][curr_y]

            # If the goal is reached, reconstruct the path and terminate the loop
            if (curr_x, curr_y) == (self.endX, self.endY):
                print(f"Goal reached at ({curr_x}, {curr_y}) with distance {curr_dist}")
                self.parent = parent
                self.reconstructPath()
                self.MazeSolved = True
                return
            
            # Mark the current cell as visited
            self.visited.add((curr_x, curr_y))
            print(f"Debug Check: Visiting Cell: ({curr_x}, {curr_y}) with distance {curr_dist}")
            
            # Get all possible neighbors
            neighbors = []
            if not self.currentCell.walls[0]:  # Top
                neighbors.append((curr_x, curr_y - 1))
            if not self.currentCell.walls[1]:  # Right
                neighbors.append((curr_x + 1, curr_y))
            if not self.currentCell.walls[2]:  # Bottom
                neighbors.append((curr_x, curr_y + 1))
            if not self.currentCell.walls[3]:  # Left
                neighbors.append((curr_x - 1, curr_y))

            # Process each neighbor
            for neighbor_x, neighbor_y in neighbors:
                if (neighbor_x, neighbor_y) not in self.visited:
                    # Calculate the tentative distance
                    tentative_distance = curr_dist + 1  # Cost of moving to a neighbor is 1

                    # If the tentative distance is smaller, update it
                    if self.distances[neighbor_x][neighbor_y] == float("inf") or tentative_distance < self.distances[neighbor_x][neighbor_y]:
                        self.distances[neighbor_x][neighbor_y] = tentative_distance
                        parent[(neighbor_x, neighbor_y)] = (curr_x, curr_y)
                        heapq.heappush(pq, (tentative_distance, (neighbor_x, neighbor_y)))

    def dijkstra_init(self):
        # Given that the weights between vertices are uniform, meaning that they have the same weight
        self.distances = [[float('inf') for _ in range(self.maze.cols)] for _ in range(self.maze.rows)]    
        self.distances[self.x][self.y] = 0 # starting vertex should be 0
        # Alternative data structure: self.distaces = {(self.x, self.y):0}

        # Dictionary to store the parent of each cell for path reconstruction
        self.parent = {}

        # Initialize a min priority queue heap
        self.pq = [(0, (self.x, self.y))]

    def dijkstra_iter(self):
        if self.pq:
            # Get the current vertex with the minimum distance
            curr_dist, (curr_x, curr_y) = heapq.heappop(self.pq)
            self.currentCell = self.maze.MazeGrid[curr_x][curr_y]

            # If the goal is reached, reconstruct the path and terminate the loop
            if (curr_x, curr_y) == (self.endX, self.endY):
                print(f"Goal reached at ({curr_x}, {curr_y}) with distance {curr_dist}")
                self.reconstructPath()
                self.MazeSolved = True
                return
            
            # Mark the current cell as visited
            # Since we use a min heap, we always make sure our current cell is having the smallest distance before marking it as visited

            self.visited.add((curr_x, curr_y))
            print(f"Debug Check: Visiting Cell: ({curr_x}, {curr_y}) with distance {curr_dist}")
            
            # Get all possible neighbors
            neighbors = []
            if not self.currentCell.walls[0]:  # Top
                neighbors.append((curr_x, curr_y - 1))
            if not self.currentCell.walls[1]:  # Right
                neighbors.append((curr_x + 1, curr_y))
            if not self.currentCell.walls[2]:  # Bottom
                neighbors.append((curr_x, curr_y + 1))
            if not self.currentCell.walls[3]:  # Left
                neighbors.append((curr_x - 1, curr_y))
            # TEST: shuffle to see the random behavior
            random.shuffle(neighbors)
            # Process each neighbor
            for neighbor_x, neighbor_y in neighbors:
                if (neighbor_x, neighbor_y) not in self.visited:
                    # Calculate the tentative distance
                    tentative_distance = curr_dist + 1  # Cost of moving to a neighbor is 1, uniform cost

                    # If the tentative distance is smaller than the previously assigned distance to that neighbor cell, update it
                    if self.distances[neighbor_x][neighbor_y] == float("inf") or tentative_distance < self.distances[neighbor_x][neighbor_y]:
                        self.distances[neighbor_x][neighbor_y] = tentative_distance
                        self.parent[(neighbor_x, neighbor_y)] = (curr_x, curr_y)
                        heapq.heappush(self.pq, (tentative_distance, (neighbor_x, neighbor_y)))

    # ----------------------------------------------------------------------------------
    def calculate_h_value(self, curr_x, curr_y):
        "Approximation heuristics to calculate h for the A-star search"
        return abs(curr_x - self.endX) + abs(curr_y - self.endY)

    def trace_path(self):
        path = []
        x, y = self.endX, self.endY
        # Trace the path from destination to source using parent cells, while the parent of the cell is not itself
        while not (self.maze.MazeGrid[x][y].parent_x == x and self.maze.MazeGrid[x][y].parent_y==y):
            path.append((x, y))
            # Update the next parent
            x = self.maze.MazeGrid[x][y].parent_x
            y = self.maze.MazeGrid[x][y].parent_y
        # Add the source cell to the path
        path.append((x, y))
        path.reverse() # Reverse direction back from source -> destination
        print(f"Final Path: {'->'.join(map(str, path))}")
        self.finalPath = path

    def Astar_search(self):
        """A* Search - pathfinding algorithm"""
        # Check if the source and destination are valid

        # Check if the source and destination are unblocked (in this maze, we make all the cells accessible, so we don't have to worry about that)
        
        # Check if we are already at the destination
        
        # Initialize the closed list (ALTERNATIVELY, use the self.visited() set data structure)
        closed_list = [[False for _ in range(self.maze.cols)] for _ in range(self.maze.rows)]
        # Initialize the details of each Cell
        "I had the Cells object initialized for the Maze map to contain the necessary attributes to run this A* algorithm as well, so no need for additional objects"
        # Intialize starting cell's details
        self.maze.MazeGrid[self.x][self.y].f = 0
        self.maze.MazeGrid[self.x][self.y].g = 0
        self.maze.MazeGrid[self.x][self.y].h = 0
        self.maze.MazeGrid[self.x][self.y].parent_x = self.x
        self.maze.MazeGrid[self.x][self.y].parent_y = self.y

        # Initialize the open list (Cells to be visited) with the starting cell
        open_list = []
        heapq.heappush(open_list, (0.0, self.x, self.y)) # (f(n), x-coordinate, y-coordinate)
        # Flag for whenever the destination is found : self.MazeSolved = False
        while open_list:
            # Pop the cell with the smallest f value from the open list
            p, curr_x, curr_y = heapq.heappop(open_list)

            # Mark the cell as visited
            self.currentCell = self.maze.MazeGrid[curr_x][curr_y]
            closed_list[curr_x][curr_y] = True
            # Alternatively
            self.visited.add((curr_x, curr_y))

            # For each direction, check the successor (or children node)
            # Get all possible neighbors
            neighbors = []
            if not self.currentCell.walls[0]:  # Top
                neighbors.append((curr_x, curr_y - 1))
            if not self.currentCell.walls[1]:  # Right
                neighbors.append((curr_x + 1, curr_y))
            if not self.currentCell.walls[2]:  # Bottom
                neighbors.append((curr_x, curr_y + 1))
            if not self.currentCell.walls[3]:  # Left
                neighbors.append((curr_x - 1, curr_y))
            # Check for each neighbor
            for neighborx, neighbory in neighbors:
                # Not visited
                if (neighborx, neighbory) not in self.visited:
                    # if this successor/neighbor in the destination
                    if neighborx == self.endX and neighbory == self.endY:
                        # Set the parent of the new destination cell
                        self.maze.MazeGrid[neighborx][neighbory].parent_x = curr_x
                        self.maze.MazeGrid[neighborx][neighbory].parent_y = curr_y
                        # Trace and print the path from source to destination
                        self.trace_path()
                        self.MazeSolved = True
                        return
                    else:
                        # Calculate the new f, g, and h value for each Cell
                        g_new = self.maze.MazeGrid[curr_x][curr_y].g + 1.0
                        h_new = self.calculate_h_value(neighborx, neighbory)
                        f_new = g_new + h_new

                        # If the cell is not in the open list or the new value f is smaller 
                        if self.maze.MazeGrid[neighborx][neighbory].f == float('inf') or self.maze.MazeGrid[neighborx][neighbory].f > f_new:
                            # Add the cell to the open list
                            heapq.heappush(open_list, (f_new, neighborx, neighbory))
                            # Update the cell details
                            self.maze.MazeGrid[neighborx][neighbory].f = f_new
                            self.maze.MazeGrid[neighborx][neighbory].g = g_new
                            self.maze.MazeGrid[neighborx][neighbory].h = h_new
                            self.maze.MazeGrid[neighborx][neighbory].parent_x = curr_x
                            self.maze.MazeGrid[neighborx][neighbory].parent_y = curr_y
                
        
        if not self.MazeSolved:
            print("Failed to find the destination cell")
    
    def astar_init(self):
        # Initialize the closed list (ALTERNATIVELY, use the self.visited() set data structure)
        self.closed_list = [[False for _ in range(self.maze.cols)] for _ in range(self.maze.rows)]
        # Initialize the details of each Cell
        "I had the Cells object initialized for the Maze map to contain the necessary attributes to run this A* algorithm as well, so no need for additional objects"
        # Intialize starting cell's details
        self.maze.MazeGrid[self.x][self.y].f = 0
        self.maze.MazeGrid[self.x][self.y].g = 0
        self.maze.MazeGrid[self.x][self.y].h = 0
        self.maze.MazeGrid[self.x][self.y].parent_x = self.x
        self.maze.MazeGrid[self.x][self.y].parent_y = self.y

        # Initialize the open list (Cells to be visited) with the starting cell
        self.open_list = []
        heapq.heappush(self.open_list, (0.0, self.x, self.y)) # (f(n), x-coordinate, y-coordinate)
        
    def astar_iter(self):
        """A* Search - pathfinding algorithm"""
        if self.open_list:
            # Pop the cell with the smallest f value from the open list
            f_value, curr_x, curr_y = heapq.heappop(self.open_list)

            # Mark the cell as visited and make it as current cell for our current iteration update on the trailing mouse
            self.currentCell = self.maze.MazeGrid[curr_x][curr_y]
            self.closed_list[curr_x][curr_y] = True
            # Alternatively
            self.visited.add((curr_x, curr_y))

            # For each direction, check the successor (or children node)
            # Get all possible neighbors
            neighbors = []
            if not self.currentCell.walls[0]:  # Top
                neighbors.append((curr_x, curr_y - 1))
            if not self.currentCell.walls[1]:  # Right
                neighbors.append((curr_x + 1, curr_y))
            if not self.currentCell.walls[2]:  # Bottom
                neighbors.append((curr_x, curr_y + 1))
            if not self.currentCell.walls[3]:  # Left
                neighbors.append((curr_x - 1, curr_y))
            # Check for each neighbor
            for neighborx, neighbory in neighbors:
                # Not visited
                if (neighborx, neighbory) not in self.visited:
                    # if this successor/neighbor in the destination
                    if neighborx == self.endX and neighbory == self.endY:
                        # Set the parent of the new destination cell
                        self.maze.MazeGrid[neighborx][neighbory].parent_x = curr_x
                        self.maze.MazeGrid[neighborx][neighbory].parent_y = curr_y
                        # Trace and print the path from source to destination
                        self.trace_path()
                        self.MazeSolved = True
                        return
                    else:
                        # Calculate the new f, g, and h value for each Cell
                        g_new = self.maze.MazeGrid[curr_x][curr_y].g + 1.0
                        h_new = self.calculate_h_value(neighborx, neighbory)
                        f_new = g_new + h_new

                        # If the cell is not in the open list or the new value f is smaller 
                        if self.maze.MazeGrid[neighborx][neighbory].f == float('inf') or self.maze.MazeGrid[neighborx][neighbory].f > f_new:
                            # Add the cell to the open list
                            heapq.heappush(self.open_list, (f_new, neighborx, neighbory))
                            # Update the cell details
                            self.maze.MazeGrid[neighborx][neighbory].f = f_new
                            self.maze.MazeGrid[neighborx][neighbory].g = g_new
                            self.maze.MazeGrid[neighborx][neighbory].h = h_new
                            self.maze.MazeGrid[neighborx][neighbory].parent_x = curr_x
                            self.maze.MazeGrid[neighborx][neighbory].parent_y = curr_y

# TEST DRIVER
if __name__ == "__main__":

    distances = [[float('inf') * 5] for _ in range(6)]
    distances_right = [[float('inf') for _ in range(5)] for _ in range(6)]    
    print(distances)
    print(distances_right)
    maat = [[0]*5 for _ in range(6)]
    print(maat)