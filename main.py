import pygame
import random
import sys
import time
import math  # Added for distance calculations
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
money = 0  # Starting with no money - player needs to earn it
fence_placement_mode = False  # Track if we're placing the fence
fence_first_point = None  # Track first point of fence placement

# Create initial store items
store_items.append(StoreItem("sprinkler", 50, 20, 100, duration=30))  # $1.00, lasts 30 seconds
store_items.append(StoreItem("gnome", 150, 20, 150, duration=45))     # $1.50, lasts 45 seconds
store_items.append(StoreItem("shoes", 250, 20, 250))                  # $2.50, permanent effect
store_items.append(StoreItem("fence", 350, 20, 200))                  # $2.00, permanent electric fence

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
            
            # Handle fence placement mode
            if fence_placement_mode:
                # If we don't have the first point yet, set it
                if fence_first_point is None:
                    fence_first_point = (mouse_x, mouse_y)
                    # Display some feedback to the user
                    print("First fence point placed! Click again to place the second point.")
                else:
                    # We already have the first point, so this is the second click
                    for item in store_items:
                        if item.name == "fence" and item.active and not item.fence_active:
                            item.fence_start = fence_first_point
                            item.fence_end = (mouse_x, mouse_y)
                            item.fence_active = True
                            fence_placement_mode = False
                            fence_first_point = None
                            print("Electric fence placed!")
                            break
                    
            # Regular clicking (when not in fence placement mode)
            else:            
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
                # Get current mouse position for checking
                mouse_x, mouse_y = event.pos
                
                if isinstance(dragging_item, Snail):
                    # Check if snail is now in tank
                    if TANK_RECT.collidepoint(mouse_x, mouse_y):
                        dragging_item.in_garden = False
                    else:
                        dragging_item.in_garden = True
                        # Make sure snail is below store area
                        if dragging_item.y < STORE_RECT.height:
                            dragging_item.y = STORE_RECT.height
                        
                elif isinstance(dragging_item, Lettuce):
                    # Check if lettuce is now in tank
                    if TANK_RECT.collidepoint(mouse_x, mouse_y):
                        dragging_item.in_garden = False
                    else:
                        dragging_item.in_garden = True
                        # Make sure lettuce is below store area
                        if dragging_item.y < STORE_RECT.height:
                            dragging_item.y = STORE_RECT.height
                
                elif isinstance(dragging_item, StoreItem):
                    # Check if store item was dragged out of store - use mouse position
                    if dragging_item.in_store and mouse_y > STORE_RECT.height:
                        # Check if enough money
                        if money >= dragging_item.price:
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
                            
                            # Handle fence placement mode
                            elif dragging_item.name == "fence":
                                # Enter fence placement mode
                                fence_placement_mode = True
                                print("Click to place the first end of the electric fence!")
                            
                            # Create a new item in the store with slight position offset to avoid stacking
                            x_pos = 50 if dragging_item.name == "sprinkler" else (
                                   150 if dragging_item.name == "gnome" else (
                                   250 if dragging_item.name == "shoes" else 350))
                            
                            new_item = StoreItem(dragging_item.name, 
                                             x_pos, 
                                             20, 
                                             dragging_item.price,
                                             dragging_item.duration)
                            store_items.append(new_item)
                        else:
                            # Not enough money, return item to store
                            x_pos = 50 if dragging_item.name == "sprinkler" else (
                                   150 if dragging_item.name == "gnome" else (
                                   250 if dragging_item.name == "shoes" else 350))
                            dragging_item.x = x_pos
                            dragging_item.y = 20
                    else:
                        # Item was dragged but not placed correctly, return to store
                        if dragging_item.in_store:
                            x_pos = 50 if dragging_item.name == "sprinkler" else (
                                   150 if dragging_item.name == "gnome" else (
                                   250 if dragging_item.name == "shoes" else 350))
                            dragging_item.x = x_pos
                            dragging_item.y = 20
                
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
            # Remove the lettuce directly - no need to turn brown
            lettuces.remove(lettuce)
    
    # Check for snails eating lettuce - but now with a distance check
    for snail in snails:
        for lettuce in lettuces[:]:  # Create a copy to safely remove items
            # Calculate actual distance between snail and lettuce (center to center)
            snail_center_x = snail.x + snail.width // 2
            snail_center_y = snail.y + snail.height // 2
            lettuce_center_x = lettuce.x + lettuce.width // 2
            lettuce_center_y = lettuce.y + lettuce.height // 2
            
            distance = math.sqrt((snail_center_x - lettuce_center_x)**2 + 
                                (snail_center_y - lettuce_center_y)**2)
            
            # Only eat if very close (within 20 pixels of centers)
            if distance < 20:
                if lettuce.in_garden and snail.in_garden:
                    # In garden, one bite still ruins the lettuce
                    lettuce.bad = True
                elif not lettuce.in_garden and not snail.in_garden:
                    # In tank, bites are slower now - only take 0.02 bite at a time instead of 0.05
                    lettuce.bites += 0.02
                    # Reset snail hunger when eating
                    snail.hunger = 0
                    snail.escape_timer = 0
                    
                    # Give money for feeding snails in the tank
                    if random.random() < 0.05:  # 5% chance per bite to get money
                        # Reward based on lettuce type
                        if lettuce.lettuce_type == "green":
                            reward = random.randint(5, 10)  # 5-10 cents
                        elif lettuce.lettuce_type == "yellow":
                            reward = random.randint(10, 15)  # 10-15 cents
                        elif lettuce.lettuce_type == "red":
                            reward = random.randint(15, 20)  # 15-20 cents
                        elif lettuce.lettuce_type == "purple":
                            reward = random.randint(20, 25)  # 20-25 cents
                        
                        money += reward
                        # Show a little message about earning money
                        print(f"A snail ate some {lettuce.lettuce_type} lettuce! You earned ${reward/100:.2f}")
                    
                    # Remove lettuce when it reaches its max bites (based on color type)
                    if lettuce.bites >= lettuce.max_bites:
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
    
    # Draw first point of fence placement if in fence placement mode
    if fence_placement_mode and fence_first_point:
        pygame.draw.circle(screen, ELECTRIC_YELLOW, fence_first_point, 5)
        # Draw a line from first point to current mouse position
        pygame.draw.line(screen, ELECTRIC_YELLOW, fence_first_point, (mouse_x, mouse_y), 2)
    
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
    
    # Draw game objectives
    small_font = pygame.font.SysFont(None, 24)
    objective1 = small_font.render("Grow Lettuce: Get money after 10 seconds", True, BLACK)
    objective2 = small_font.render("Feed Snails: Get money for snails eating in tank", True, BLACK)
    
    screen.blit(objective1, (SCREEN_WIDTH - 380, 160))
    screen.blit(objective2, (SCREEN_WIDTH - 380, 185))
    
    # Draw store items
    for item in store_items:
        item.draw(screen)
    
    # Draw game objects
    for lettuce in lettuces:
        lettuce.draw(screen)
        
    for snail in snails:
        snail.draw(screen)
    
    # If in fence placement mode, show instructional text
    if fence_placement_mode:
        instruction_font = pygame.font.SysFont(None, 24)
        if fence_first_point is None:
            instruction_text = instruction_font.render("Click to place the first end of the fence!", True, BLACK)
        else:
            instruction_text = instruction_font.render("Now click to place the second end of the fence!", True, BLACK)
        screen.blit(instruction_text, (SCREEN_WIDTH//2 - 150, 70))
        
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()