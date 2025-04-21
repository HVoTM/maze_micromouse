import pygame
import sys

# Initialize pygame
pygame.init()

# # Create two windows
# window1 = pygame.display.set_mode((400, 400), pygame.NOFRAME)
# pygame.display.set_caption("Window 1")
# window2 = pygame.display.set_mode((400, 400), pygame.NOFRAME)
# pygame.display.set_caption("Window 2")

# # Main loop
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Draw content for window 1
#     window1.fill((255, 0, 0))  # Red background
#     pygame.draw.circle(window1, (255, 255, 255), (200, 200), 50)

#     # Draw content for window 2
#     window2.fill((0, 0, 255))  # Blue background
#     pygame.draw.rect(window2, (255, 255, 255), (150, 150, 100, 100))

#     # Update both windows
#     pygame.display.update()

# # Quit pygame
# pygame.quit()
# sys.exit()

import pygame
import multiprocessing

def create_window(color, caption):
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption(caption)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(color)
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    # Create two processes for two windows
    process1 = multiprocessing.Process(target=create_window, args=((255, 0, 0), "Window 1"))
    process2 = multiprocessing.Process(target=create_window, args=((0, 0, 255), "Window 2"))

    # Start the processes
    process1.start()
    process2.start()

    # Wait for both processes to finish
    process1.join()
    process2.join()