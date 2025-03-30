# Maze-solver algorithms: Depth-First Search, Breadth-First Search, A* Search, Dijkstra's Algorithm, etc.
from Maze import MazeMap
from enum import Enum
import random

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
class Mouse:
    def __init__(self, maze: "MazeMap", x: int=0, y:int=0):
        """
        Initialize the solver with a reference to the MazeMap class
        """
        self.x = x; self.y = y; # Starting position indices, also used to mark the solver location in the maze
        self.maze: "MazeMap" = maze # reference to the MazeMap instance to access the maze grid
        # We assume the end of the maze is bottom right
        self.endX = self.maze.cols - 1
        self.endY = self.maze.rows - 1
        self.direction = None # indicate the current direction that the mouse is going

    def RandomMouse(self):
        "Random Mouse algorithm: unintelligent robot that moves randomly, does not require any memory of the maze"
        print("Self.x is {}, self.y is {} \n end-X is {}, end-Y is {}".format(self.x, self.y, self.endX, self.endY))
        if self.x != self.endX and self.y != self.endY:
            print("Still solving....")
            # Check the current grid cell to see what path there is
            currentCell = self.maze.MazeGrid[self.x][self.y]

            # Check with the current direction that th
            # See if there are availiability for four directions
            available_directions = []
            # Referring to the order of the wall position: Top, Right, Bottom, Left
            if not currentCell.walls[0]:  # No wall at the top
                available_directions.append(Direction.UP)
            if not currentCell.walls[1]:  # No wall on the right
                available_directions.append(Direction.RIGHT)
            if not currentCell.walls[2]:  # No wall at the bottom
                available_directions.append(Direction.DOWN)
            if not currentCell.walls[3]:  # No wall on the left
                available_directions.append(Direction.LEFT)
            
            # Prioritize continuing in the current direction if valid (the path is open onwards)
            if self.direction:
                if self.direction in available_directions:
                    dx, dy = self.direction.value # Retrieve the value of the direction
                    self.x += dx
                    self.y += dy
                    print(f"Continued {self.direction.name} to ({self.x}, {self.y})")
                    return # End this iteration
                
                # Determine what are the opposite and the adjacent directions
                currOppositeDirection = OPPOSITE_DIRECTION.get(self.direction)
                currAdjacentDirections = ADJACENT_DIRECTION.get(self.direction)

                # Choose a new random direction
                if currAdjacentDirections in available_directions:
                    self.direction = random.choice(currAdjacentDirections)
                    dx, dy = self.direction.value
                    self.x += dx
                    self.y += dy
                    print(f"Moved {self.direction.name} to ({self.x}, {self.y})")
                    return
                else:
                    self.direction = currOppositeDirection
                    dx, dy = self.direction.value
                    self.x += dx
                    self.y += dy
                    print(f"Moved {self.direction.name} to ({self.x}, {self.y})")
                    return
            else:
                self.direction = random.choice(available_directions)
                dx, dy = self.direction.value
                self.x += dx; self.y += dy
                print(f"Moved {self.direction.name} to ({self.x}, {self.y})")
                return