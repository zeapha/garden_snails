import pygame

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
GREEN = (100, 200, 100)
LIME_GREEN = (50, 255, 50)  # Brighter green for lettuce
BROWN = (139, 69, 19)
BLUE = (100, 100, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
DARK_BROWN = (90, 40, 10)  # Darker brown for snail boots
YELLOW = (220, 220, 50)    # Yellow for yellow lettuce
RED = (220, 60, 60)        # Red for red lettuce
PURPLE = (180, 60, 220)    # Purple for purple lettuce
ELECTRIC_YELLOW = (255, 255, 0)  # Bright yellow for electric fence

# Game areas
GARDEN_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
TANK_RECT = pygame.Rect(SCREEN_WIDTH - SCREEN_WIDTH//4, SCREEN_HEIGHT - SCREEN_HEIGHT//4, 
                        SCREEN_WIDTH//4, SCREEN_HEIGHT//4)
STORE_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, 100)  # Store at the top of the screen