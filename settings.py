from enum import Enum

# GAME HYPERPARAMETERS
FPS_RATE = 60
MAZE_WIDTH = 800
MAZE_HEIGHT = 800

# COLOR SETTINGS FOR SELECTION
class Colors(Enum):
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

    # Shades of Red (Sorted from darkest to lightest)
    DARK_RED = (139, 0, 0)
    FIREBRICK = (178, 34, 34)
    CRIMSON = (220, 20, 60)
    RED = (255, 0, 0)
    LIGHT_RED = (255, 102, 102)

    # Shades of Orange
    LIGHT_ORANGE = (255, 200, 102)
    DARK_ORANGE = (255, 140, 0)
    CORAL = (255, 127, 80)
    ORANGE_RED = (255, 69, 0)
    
    NEON_GREEN = (57, 255, 20)

class GameState(Enum):
    GENERATING = 1
    SOLVING = 2
    PAUSED = 3
    RESUMED = 4
    SAVING = 5
    LOADING = 6
    IDLE = 7  # Default state when nothing is happening
    RESET = 8

if __name__ == "__main__":
    print(Colors.LIGHT_ORANGE.value)