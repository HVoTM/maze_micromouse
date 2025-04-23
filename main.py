import pygame
import sys
import random
import Maze
import time
import solver
from settings import Colors, GameState
from app import mainMazeProgram
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

def checkObjectAttributes(object):
    print("Checking {}'s attributes:".format(object.__class__.__name__))
    print(vars(object))

# --- Driver Code ---
if __name__ == "__main__":
    # New maze new mouse who dis?
    new_maze = Maze.MazeMap(mazeWidth=800, mazeHeight=800, cellSize=20 ,startX=0, startY=0)
    new_mouse = solver.Mouse(maze=new_maze) # referencing the maze to the mouse for solving
    # --------------------------------------------------------------------
    
    # Testing main program
    mainMazeProgram(new_maze, new_mouse, fpsSpeed=60, generatorName='dfs', solver='bfs')
    # --------------------------------------------------------------------
   