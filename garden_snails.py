import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Garden Snails Game")

# Colors
WHITE = (255, 255, 255)
GREEN = (100, 200, 100)
LIME_GREEN = (50, 255, 50)  # Brighter green for lettuce
BROWN = (139, 69, 19)
BLUE = (100, 100, 255)
BLACK = (0, 0, 0)

# Game areas - tank is now 1/8th of screen in lower right
GARDEN_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
TANK_RECT = pygame.Rect(SCREEN_WIDTH - SCREEN_WIDTH//4, SCREEN_HEIGHT - SCREEN_HEIGHT//4, 
                        SCREEN_WIDTH//4, SCREEN_HEIGHT//4)

# Game classes
class Snail:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.dragging = False
        self.in_garden = True
        self.hunger = 0
        self.escape_timer = 0
        self.speed = 0.3  # Slow movement speed
        self.target_x = x
        self.target_y = y
        
    def draw(self):
        # Draw the snail body (shell)
        pygame.draw.ellipse(screen, (180, 140, 100), (self.x, self.y, self.width, self.height))
        # Draw shell pattern
        pygame.draw.arc(screen, (120, 80, 60), (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 0, 3.14, 3)
        
        # Draw the snail body
        pygame.draw.ellipse(screen, BROWN, (self.x - 15, self.y + self.height - 15, 30, 15))
        
        # Draw the snail head
        pygame.draw.ellipse(screen, BROWN, (self.x - 20, self.y + self.height - 20, 15, 10))
        
        # Draw the eyes on stalks
        pygame.draw.line(screen, BROWN, (self.x - 15, self.y + self.height - 15), 
                         (self.x - 20, self.y + self.height - 25), 2)
        pygame.draw.line(screen, BROWN, (self.x - 10, self.y + self.height - 15), 
                         (self.x - 5, self.y + self.height - 25), 2)
        pygame.draw.circle(screen, BLACK, (self.x - 20, self.y + self.height - 25), 2)
        pygame.draw.circle(screen, BLACK, (self.x - 5, self.y + self.height - 25), 2)
        
    def find_closest_lettuce(self, lettuces):
        closest_lettuce = None
        min_distance = float('inf')
        
        # First try to find lettuce in the same area
        for lettuce in lettuces:
            if lettuce.in_garden == self.in_garden:
                distance = math.sqrt((self.x - lettuce.x)**2 + (self.y - lettuce.y)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_lettuce = lettuce
        
        # If no lettuce in the same area, look in the other area
        if closest_lettuce is None:
            for lettuce in lettuces:
                distance = math.sqrt((self.x - lettuce.x)**2 + (self.y - lettuce.y)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_lettuce = lettuce
        
        return closest_lettuce
        
    def update(self, lettuces):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Only move if not being dragged
        if not self.dragging:
            # Find closest lettuce
            closest_lettuce = self.find_closest_lettuce(lettuces)
            
            if closest_lettuce:
                # Set target to the closest lettuce
                self.target_x = closest_lettuce.x
                self.target_y = closest_lettuce.y
                
                # Calculate direction to target
                dx = self.target_x - self.x
                dy = self.target_y - self.y
                distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
                
                # Move slowly toward target
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            
        # If in tank, increase hunger and maybe try to escape
        if not self.in_garden:
            self.hunger += 0.01
            if self.hunger > 5:
                self.escape_timer += 0.02
                if self.escape_timer > 5 and random.random() < 0.01:
                    self.in_garden = True
                    self.x = TANK_RECT.x - 50  # Place just outside the tank
                    self.y = TANK_RECT.y
                    self.hunger = 0
                    self.escape_timer = 0
        
class Lettuce:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.dragging = False
        self.in_garden = True
        self.bites = 0
        self.bad = False
        
    def draw(self):
        if self.bad:
            color = (150, 150, 0)  # Yellowish for bad lettuce
        else:
            color = LIME_GREEN  # Brighter green for good lettuce
            
        # Draw the lettuce - now with a more leaf-like shape
        pygame.draw.ellipse(screen, color, (self.x, self.y, self.width, self.height))
        # Add some details to make it look more like a lettuce leaf
        pygame.draw.line(screen, (30, 200, 30), 
                        (self.x + self.width//2, self.y + self.height//2),
                        (self.x + self.width//2, self.y + self.height - 5), 3)
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
# Game variables
snails = []
lettuces = []
mouse_x, mouse_y = 0, 0
dragging_item = None
spawn_timer = 0

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Check if clicked on a snail
            for snail in snails:
                if snail.rect.collidepoint(mouse_x, mouse_y):
                    snail.dragging = True
                    dragging_item = snail
                    break
                    
            # If not dragging a snail, check if clicked on lettuce
            if not dragging_item:
                for lettuce in lettuces:
                    if lettuce.rect.collidepoint(mouse_x, mouse_y):
                        lettuce.dragging = True
                        dragging_item = lettuce
                        break
                
        elif event.type == pygame.MOUSEBUTTONUP:
            # Release any dragged item
            if dragging_item:
                if isinstance(dragging_item, Snail):
                    # Check if snail is now in tank
                    if TANK_RECT.collidepoint(dragging_item.x + dragging_item.width//2, 
                                             dragging_item.y + dragging_item.height//2):
                        dragging_item.in_garden = False
                    else:
                        dragging_item.in_garden = True
                        
                elif isinstance(dragging_item, Lettuce):
                    # Check if lettuce is now in tank
                    if TANK_RECT.collidepoint(dragging_item.x + dragging_item.width//2, 
                                             dragging_item.y + dragging_item.height//2):
                        dragging_item.in_garden = False
                    else:
                        dragging_item.in_garden = True
                
                dragging_item.dragging = False
                dragging_item = None
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            
            # Move the item being dragged
            if dragging_item:
                dragging_item.x = mouse_x - dragging_item.width // 2
                dragging_item.y = mouse_y - dragging_item.height // 2
    
    # Game logic
    
    # Spawn new snails and lettuce over time
    spawn_timer += 0.1
    if spawn_timer > 10:
        # Maybe spawn a new snail in the garden (avoiding the tank area)
        if random.random() < 0.3 and len(snails) < 10:
            valid_spawn = False
            while not valid_spawn:
                x = random.randint(10, SCREEN_WIDTH - 60)
                y = random.randint(10, SCREEN_HEIGHT - 50)
                # Make sure it's not in the tank
                if not TANK_RECT.collidepoint(x, y):
                    valid_spawn = True
            snails.append(Snail(x, y))
            
        # Maybe spawn new lettuce in the garden (avoiding the tank area)
        if random.random() < 0.5 and len(lettuces) < 8:
            valid_spawn = False
            while not valid_spawn:
                x = random.randint(10, SCREEN_WIDTH - 60)
                y = random.randint(10, SCREEN_HEIGHT - 50)
                # Make sure it's not in the tank
                if not TANK_RECT.collidepoint(x, y):
                    valid_spawn = True
            lettuces.append(Lettuce(x, y))
            
        spawn_timer = 0
    
    # Check for snails eating lettuce
    for snail in snails:
        for lettuce in lettuces[:]:  # Create a copy to safely remove items
            if snail.rect.colliderect(lettuce.rect):
                if lettuce.in_garden and snail.in_garden:
                    # In garden, one bite ruins the lettuce
                    lettuce.bad = True
                elif not lettuce.in_garden and not snail.in_garden:
                    # In tank, lettuce can take 5 bites
                    lettuce.bites += 0.05
                    # Reset snail hunger when eating
                    snail.hunger = 0
                    snail.escape_timer = 0
                    if lettuce.bites >= 5:
                        lettuces.remove(lettuce)
    
    # Update all game objects
    for snail in snails:
        snail.update(lettuces)
    
    for lettuce in lettuces[:]:  # Create a copy to safely remove items
        lettuce.update()
        # Remove bad lettuce from garden after a while
        if lettuce.bad and lettuce.in_garden:
            lettuce.bites += 0.01
            if lettuce.bites > 3:
                lettuces.remove(lettuce)
    
    # Drawing
    # Fill the background
    screen.fill(WHITE)
    
    # Draw the garden area (now the entire screen except tank)
    pygame.draw.rect(screen, GREEN, GARDEN_RECT)
    
    # Draw the tank area (lower right corner)
    pygame.draw.rect(screen, BLUE, TANK_RECT)
    
    # Draw a border around the tank
    pygame.draw.rect(screen, BLACK, TANK_RECT, 3)
    
    # Draw text
    font = pygame.font.SysFont(None, 36)
    garden_text = font.render("Garden", True, BLACK)
    tank_text = font.render("Snail Tank", True, BLACK)
    screen.blit(garden_text, (20, 10))
    screen.blit(tank_text, (TANK_RECT.x + 10, TANK_RECT.y + 10))
    
    # Draw game objects
    for lettuce in lettuces:
        lettuce.draw()
        
    for snail in snails:
        snail.draw()
        
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()