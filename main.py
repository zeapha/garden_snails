import pygame
import random
import sys
import time
from settings import *
from game_objects import StoreItem, Snail, Lettuce, keep_in_bounds

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Garden Snails Game")

# Game variables
snails = []
lettuces = []
store_items = []
mouse_x, mouse_y = 0, 0
dragging_item = None
spawn_timer = 0
money = 500  # Starting money (raised to allow testing store items)

# Create initial store items
store_items.append(StoreItem("sprinkler", 50, 20, 100, duration=30))  # $1.00, lasts 30 seconds
store_items.append(StoreItem("gnome", 150, 20, 150, duration=45))     # $1.50, lasts 45 seconds
store_items.append(StoreItem("shoes", 250, 20, 250))                  # $2.50, permanent effect

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
            
            # Check if clicked on a store item
            if STORE_RECT.collidepoint(mouse_x, mouse_y):
                for item in store_items:
                    if item.rect.collidepoint(mouse_x, mouse_y) and item.in_store:
                        # Check if enough money
                        if money >= item.price:
                            item.dragging = True
                            dragging_item = item
                            break
            else:
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
                            
                # If not dragging food or snail, check if clicked on placed store item
                if not dragging_item:
                    for item in store_items:
                        if not item.in_store and item.rect.collidepoint(mouse_x, mouse_y):
                            item.dragging = True
                            dragging_item = item
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
                
                elif isinstance(dragging_item, StoreItem):
                    # Check if store item was dragged out of store
                    if dragging_item.in_store and not STORE_RECT.collidepoint(dragging_item.x, dragging_item.y):
                        # Deduct money
                        money -= dragging_item.price
                        dragging_item.in_store = False
                        dragging_item.active = True
                        
                        # Apply special effects
                        if dragging_item.name == "shoes":
                            # Apply shoes to all snails
                            for snail in snails:
                                snail.speed = snail.base_speed * 0.6  # Reduce speed to 60%
                                snail.has_shoes = True  # Mark that this snail has shoes
                        
                        # Create a new item in the store with slight position offset to avoid stacking
                        x_pos = 50 if dragging_item.name == "sprinkler" else (150 if dragging_item.name == "gnome" else 250)
                        new_item = StoreItem(dragging_item.name, 
                                         x_pos, 
                                         20, 
                                         dragging_item.price,
                                         dragging_item.duration)
                        store_items.append(new_item)
                
                dragging_item.dragging = False
                dragging_item = None
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            
            # Move the item being dragged
            if dragging_item:
                dragging_item.x = mouse_x - dragging_item.width // 2
                dragging_item.y = mouse_y - dragging_item.height // 2
                # Make sure dragged items stay in bounds
                keep_in_bounds(dragging_item)
    
    # Game logic
    
    # Spawn new snails and lettuce over time
    spawn_timer += 0.1
    if spawn_timer > 10:
        # Maybe spawn a new snail in the garden (avoiding the tank area)
        if random.random() < 0.3 and len(snails) < 10:
            valid_spawn = False
            while not valid_spawn:
                x = random.randint(10, SCREEN_WIDTH - 60)
                y = random.randint(STORE_RECT.height + 10, SCREEN_HEIGHT - 50)
                # Make sure it's not in the tank
                if not TANK_RECT.collidepoint(x, y):
                    valid_spawn = True
            
            new_snail = Snail(x, y)
            
            # Apply shoes effect to new snails if activated
            for item in store_items:
                if item.name == "shoes" and item.active and not item.in_store:
                    new_snail.speed = new_snail.base_speed * 0.6
                    new_snail.has_shoes = True
                    
            snails.append(new_snail)
            
        # Maybe spawn new lettuce in the garden (avoiding the tank area)
        if random.random() < 0.5 and len(lettuces) < 8:
            valid_spawn = False
            while not valid_spawn:
                x = random.randint(10, SCREEN_WIDTH - 60)
                y = random.randint(STORE_RECT.height + 10, SCREEN_HEIGHT - 50)
                # Make sure it's not in the tank
                if not TANK_RECT.collidepoint(x, y):
                    valid_spawn = True
            lettuces.append(Lettuce(x, y))
            
        spawn_timer = 0
    
    # Check for lettuce that's been in the garden for 10 seconds (earn money)
    current_time = time.time()
    for lettuce in lettuces[:]:  # Use copy to safely remove items
        if (lettuce.in_garden and not lettuce.bad and not lettuce.points_given and 
            current_time - lettuce.spawn_time > 10):
            # Award random amount between 10-25 cents
            points_earned = random.randint(10, 25)
            money += points_earned
            lettuce.points_given = True
            # Mark for removal
            lettuce.bad = True
    
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
    
    # Update all game objects and keep them in bounds
    for snail in snails:
        snail.update(lettuces, store_items)
        keep_in_bounds(snail)  # Keep snails on screen
    
    for lettuce in lettuces[:]:  # Create a copy to safely remove items
        lettuce.update()
        keep_in_bounds(lettuce)  # Keep lettuce on screen
        # Remove bad lettuce from garden after a while
        if lettuce.bad and lettuce.in_garden:
            lettuce.bites += 0.01
            if lettuce.bites > 3:
                lettuces.remove(lettuce)
    
    # Update store items
    for item in store_items[:]:  # Use copy to safely remove items
        item.update()
        keep_in_bounds(item)  # Keep store items on screen
        
        # Remove temporary items that have expired but aren't in store
        if not item.active and not item.in_store and item.duration is not None:
            store_items.remove(item)
    
    # Drawing
    # Fill the background
    screen.fill(WHITE)
    
    # Draw the garden area (now the entire screen except tank)
    pygame.draw.rect(screen, GREEN, GARDEN_RECT)
    
    # Draw the tank area (lower right corner)
    pygame.draw.rect(screen, BLUE, TANK_RECT)
    
    # Draw the store area at the top
    pygame.draw.rect(screen, LIGHT_GRAY, STORE_RECT)
    pygame.draw.line(screen, BLACK, (0, STORE_RECT.height), (SCREEN_WIDTH, STORE_RECT.height), 3)
    
    # Draw a border around the tank
    pygame.draw.rect(screen, BLACK, TANK_RECT, 3)
    
    # Draw text
    font = pygame.font.SysFont(None, 36)
    garden_text = font.render("Garden", True, BLACK)
    tank_text = font.render("Snail Tank", True, BLACK)
    money_text = font.render(f"Money: ${money/100:.2f}", True, BLACK)
    store_text = font.render("Store", True, BLACK)
    
    screen.blit(garden_text, (20, 110))
    screen.blit(tank_text, (TANK_RECT.x + 10, TANK_RECT.y + 10))
    screen.blit(money_text, (SCREEN_WIDTH - 200, 110))
    screen.blit(store_text, (20, 10))
    
    # Draw store items
    for item in store_items:
        item.draw(screen)
    
    # Draw game objects
    for lettuce in lettuces:
        lettuce.draw(screen)
        
    for snail in snails:
        snail.draw(screen)
        
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()