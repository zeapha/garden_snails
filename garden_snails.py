# Create initial store items
store_items.append(StoreItem("sprinkler", 50, 20, 100, duration=30))  # $1.00, lasts 30 seconds
store_items.append(StoreItem("gnome", 150, 20, 200, duration=45))  # $2.00, lasts 45 seconds
store_items.append(StoreItem("shoes", 250, 20, 300))  # $3.00, permanent effectclass StoreItem:
    def __init__(self, name, x, y, price, duration=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.price = price  # in cents
        self.dragging = False
        self.in_store = True
        self.active = False
        self.duration = duration  # None means permanent
        self.timer = 0
        self.effect_radius = 100  # For items that affect an area
        
    def draw(self):
        # Draw different items based on name
        if self.name == "sprinkler":
            # Draw a blue sprinkler
            pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, BLUE, (self.x + self.width//2, self.y + self.height//2), 20)
            # Draw water drops
            if self.active:
                for i in range(8):
                    angle = i * (math.pi / 4)
                    drop_x = self.x + self.width//2 + int(25 * math.cos(angle))
                    drop_y = self.y + self.height//2 + int(25 * math.sin(angle))
                    pygame.draw.circle(screen, BLUE, (drop_x, drop_y), 5)
                # Draw effect radius
                pygame.draw.circle(screen, BLUE, (self.x + self.width//2, self.y + self.height//2), 
                                 self.effect_radius, 1)
            
        elif self.name == "gnome":
            # Draw a garden gnome
            pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height))
            # Hat
            pygame.draw.polygon(screen, (255, 0, 0), [
                (self.x + self.width//2, self.y + 10),
                (self.x + self.width//2 - 15, self.y + 30),
                (self.x + self.width//2 + 15, self.y + 30)
            ])
            # Face
            pygame.draw.circle(screen, (255, 200, 150), (self.x + self.width//2, self.y + 35), 10)
            # Body
            pygame.draw.rect(screen, BLUE, (self.x + self.width//2 - 10, self.y + 45, 20, 15))
            
            # Draw effect radius if active
            if self.active:
                pygame.draw.circle(screen, (255, 0, 0), (self.x + self.width//2, self.y + self.height//2), 
                                 self.effect_radius, 1)
            
        elif self.name == "shoes":
            # Draw snail shoes
            pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height))
            # Draw a pair of tiny boots
            boot_y = self.y + 20
            # Left boot
            pygame.draw.rect(screen, BROWN, (self.x + 10, boot_y, 15, 25))
            pygame.draw.rect(screen, BROWN, (self.x + 10, boot_y + 15, 20, 10))
            # Right boot
            pygame.draw.rect(screen, BROWN, (self.x + 35, boot_y, 15, 25))
            pygame.draw.rect(screen, BROWN, (self.x + 35, boot_y + 15, 20, 10))
            
        # Draw price tag if in store
        if self.in_store:
            price_text = f"${self.price/100:.2f}"
            font = pygame.font.SysFont(None, 24)
            text = font.render(price_text, True, BLACK)
            screen.blit(text, (self.x + 5, self.y + self.height + 5))
            
        # Draw timer for temporary items
        if self.active and self.duration is not None:
            time_left = int(self.duration - self.timer)
            if time_left > 0:
                time_text = f"{time_left}s"
                font = pygame.font.SysFont(None, 20)
                text = font.render(time_text, True, BLACK)
                screen.blit(text, (self.x, self.y - 15))
            
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Update timer for active temporary items
        if self.active and self.duration is not None:
            self.timer += 0.016  # Approximately 1/60th of a second
            if self.timer >= self.duration:
                self.active = False
                self.timer = 0
                
import pygame
import random
import sys
import math
import time

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
LIGHT_GRAY = (220, 220, 220)

# Game areas - tank is now 1/8th of screen in lower right
GARDEN_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
TANK_RECT = pygame.Rect(SCREEN_WIDTH - SCREEN_WIDTH//4, SCREEN_HEIGHT - SCREEN_HEIGHT//4, 
                        SCREEN_WIDTH//4, SCREEN_HEIGHT//4)
STORE_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, 100)  # Store at the top of the screen

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
        
        # Give each snail a random base speed between 0.15 and 0.45
        self.base_speed = 0.3 * random.uniform(0.5, 1.5)
        self.speed = self.base_speed
        
        self.target_x = x
        self.target_y = y
        self.climbing = False
        self.climbing_timer = 0
        self.random_move_timer = 0
        self.has_shoes = False
        self.last_dx = 0
        self.last_dy = 0
        
    def draw(self):
        # Draw the snail - simplified but still looking good
        
        # Draw the shell
        shell_color = (180, 140, 100)
        shell_pattern = (120, 80, 60)
        pygame.draw.ellipse(screen, shell_color, (self.x, self.y, self.width, self.height))
        
        # Shell pattern - just two arcs, no random elements
        pygame.draw.arc(screen, shell_pattern, 
                      (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 
                      0, 3.14, 3)
        pygame.draw.arc(screen, shell_pattern, 
                      (self.x + 10, self.y + 10, self.width - 20, self.height - 20), 
                      0, 3.14, 3)
        
        # Draw the snail body (fixed position relative to shell)
        body_length = 20
        pygame.draw.ellipse(screen, BROWN, (self.x - body_length, self.y + self.height - 15, body_length + 10, 15))
        
        # Draw the snail head (fixed position)
        pygame.draw.ellipse(screen, BROWN, (self.x - body_length - 10, self.y + self.height - 18, 15, 10))
        
        # Draw the eye stalks (fixed position)
        stalk1_x = self.x - body_length - 5
        stalk1_y = self.y + self.height - 15
        stalk2_x = self.x - body_length
        stalk2_y = self.y + self.height - 15
        
        # Draw eye stalks
        pygame.draw.line(screen, BROWN, (stalk1_x, stalk1_y), 
                         (stalk1_x - 5, stalk1_y - 15), 2)
        pygame.draw.line(screen, BROWN, (stalk2_x, stalk2_y), 
                         (stalk2_x - 0, stalk2_y - 15), 2)
        
        # Draw the eyes
        pygame.draw.circle(screen, BLACK, (stalk1_x - 5, stalk1_y - 15), 2)
        pygame.draw.circle(screen, BLACK, (stalk2_x - 0, stalk2_y - 15), 2)
        
        # Draw shoes if the snail has them
        if self.has_shoes:
            # Left boot
            pygame.draw.rect(screen, (139, 69, 19), (self.x - body_length - 5, self.y + self.height, 10, 5))
            # Right boot
            pygame.draw.rect(screen, (139, 69, 19), (self.x - body_length + 5, self.y + self.height, 10, 5))
        
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
            # Increment random movement timer
            self.random_move_timer += 0.1
            
            # Decide whether to continue in last direction with high probability
            if self.last_dx != 0 or self.last_dy != 0:
                if random.random() < 0.8:  # 80% chance to continue in same direction
                    self.x += self.last_dx
                    self.y += self.last_dy
                    return  # Skip the rest of movement logic
            
            # MUCH more exaggerated random walk - higher chance of random movement
            if random.random() < 0.03 or self.random_move_timer > random.uniform(2, 6):
                # Set a random target with wider range
                if self.in_garden:
                    max_range = 200  # Much larger random movement range
                    valid_target = False
                    while not valid_target:
                        rand_x = self.x + random.uniform(-max_range, max_range)
                        rand_y = self.y + random.uniform(-max_range, max_range)
                        # Make sure target is within garden and not in tank or store
                        if (0 < rand_x < SCREEN_WIDTH - self.width and 
                            STORE_RECT.height < rand_y < SCREEN_HEIGHT - self.height and
                            not TANK_RECT.collidepoint(rand_x, rand_y)):
                            valid_target = True
                else:
                    # If in tank, stay within tank bounds
                    rand_x = random.uniform(TANK_RECT.x + 10, TANK_RECT.x + TANK_RECT.width - self.width - 10)
                    rand_y = random.uniform(TANK_RECT.y + 10, TANK_RECT.y + TANK_RECT.height - self.height - 10)
                
                self.target_x = rand_x
                self.target_y = rand_y
                self.random_move_timer = 0
            else:
                # Only sometimes go toward lettuce (less often than before)
                if random.random() < 0.7:  # 70% chance to target lettuce
                    closest_lettuce = self.find_closest_lettuce(lettuces)
                    
                    if closest_lettuce:
                        # Set target to the closest lettuce
                        self.target_x = closest_lettuce.x
                        self.target_y = closest_lettuce.y
            
            # Calculate direction to target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
            
            # Move speed depends on state
            current_speed = self.speed
            
            # Handle climbing behavior
            if not self.in_garden:
                # Check if near tank edge
                edge_distance = min(
                    abs(self.x - TANK_RECT.x),
                    abs(self.x - (TANK_RECT.x + TANK_RECT.width)),
                    abs(self.y - TANK_RECT.y),
                    abs(self.y - (TANK_RECT.y + TANK_RECT.height))
                )
                
                if edge_distance < 15:  # If close to edge
                    self.climbing = True
                    current_speed = self.speed * 0.2  # Slow down to 20% of normal speed
                else:
                    self.climbing = False
            else:
                self.climbing = False
            
            # Apply a larger random jitter to movement
            jitter_x = random.uniform(-0.3, 0.3)
            jitter_y = random.uniform(-0.3, 0.3)
            
            # Check for store items' effects
            for item in store_items:
                if item.active and not item.in_store:
                    # Sprinkler effect - slows snails in radius
                    if item.name == "sprinkler":
                        dist_to_item = math.sqrt((self.x - item.x)**2 + (self.y - item.y)**2)
                        if dist_to_item < item.effect_radius:
                            current_speed *= 0.5  # 50% speed in sprinkler area
                            
                    # Gnome effect - snails avoid radius, make it much stronger
                    elif item.name == "gnome":
                        dist_to_item = math.sqrt((self.x - item.x)**2 + (self.y - item.y)**2)
                        if dist_to_item < item.effect_radius * 1.2:  # Slightly larger avoidance radius
                            # Reverse direction away from gnome with strong force
                            dx = self.x - item.x
                            dy = self.y - item.y
                            distance = max(1, math.sqrt(dx*dx + dy*dy))
                            # Move at 3x normal speed away from gnome
                            self.x += (dx / distance) * current_speed * 3.0
                            self.y += (dy / distance) * current_speed * 3.0
                            
                            # Store the last movement for direction persistence
                            self.last_dx = (dx / distance) * current_speed * 3.0
                            self.last_dy = (dy / distance) * current_speed * 3.0
                            continue  # Skip normal movement
            
            # Move toward target with jitter
            move_dx = ((dx / distance) * current_speed) + jitter_x
            move_dy = ((dy / distance) * current_speed) + jitter_y
            
            self.x += move_dx
            self.y += move_dy
            
            # Store the last movement for direction persistence
            self.last_dx = move_dx
            self.last_dy = move_dy
            
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
        self.spawn_time = time.time()  # Track when the lettuce was created
        self.points_given = False  # Track if we've given points for this lettuce
        
    def draw(self):
        if self.bad:
            color = (150, 150, 0)  # Yellowish for bad lettuce
            edge_color = (130, 130, 0)
        else:
            color = LIME_GREEN  # Brighter green for good lettuce
            edge_color = (30, 180, 30)  # Darker green for edges
            
        # Main leaf shape
        leaf_width = self.width
        leaf_height = self.height
        
        # Draw the main leaf body
        pygame.draw.ellipse(screen, color, (self.x, self.y, leaf_width, leaf_height))
        
        # Draw a border around the leaf
        pygame.draw.ellipse(screen, edge_color, (self.x, self.y, leaf_width, leaf_height), 2)
        
        # Draw central vein (stem)
        stem_x = self.x + self.width // 2
        pygame.draw.line(screen, edge_color, 
                        (stem_x, self.y + self.height // 3),
                        (stem_x, self.y + self.height - 5), 2)
        
        # Draw a few side veins
        pygame.draw.line(screen, edge_color, 
                        (stem_x, self.y + self.height // 2),
                        (stem_x - 10, self.y + self.height // 3), 1)
        pygame.draw.line(screen, edge_color, 
                        (stem_x, self.y + self.height // 2),
                        (stem_x + 10, self.y + self.height // 3), 1)
        
        # Show bite marks if in tank and being eaten
        if not self.in_garden and self.bites > 0:
            num_bites = min(int(self.bites + 1), 5)
            bite_positions = [(10, 10), (30, 15), (15, 25), (35, 30), (25, 5)]
            
            for i in range(num_bites):
                if i < len(bite_positions):
                    bite_x = self.x + bite_positions[i][0]
                    bite_y = self.y + bite_positions[i][1]
                    bite_size = 6
                    pygame.draw.circle(screen, WHITE, (bite_x, bite_y), bite_size)
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

# Game variables
snails = []
lettuces = []
store_items = []
mouse_x, mouse_y = 0, 0
dragging_item = None
spawn_timer = 0
money = 500  # Starting money (raised to allow testing store items)

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
                                snail.speed *= 0.6  # Reduce speed to 60%
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
    
    # Check if an object is going out of bounds and adjust
    def keep_in_bounds(item):
        # Keep objects within the screen boundaries
        if item.x < 0:
            item.x = 0
        elif item.x > SCREEN_WIDTH - item.width:
            item.x = SCREEN_WIDTH - item.width
            
        if item.y < STORE_RECT.height:  # Keep below store area
            item.y = STORE_RECT.height
        elif item.y > SCREEN_HEIGHT - item.height:
            item.y = SCREEN_HEIGHT - item.height
            
        # Force store items to stay in store if they're marked as in_store
        if isinstance(item, StoreItem) and item.in_store:
            if item.y > STORE_RECT.height - 10:
                item.y = 20  # Reset to store height
            
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
    
    # Check for lettuce that's been in the garden for 10 seconds (earn money)
    current_time = time.time()
    for lettuce in lettuces[:]:  # Use copy to safely remove items
        if (lettuce.in_garden and not lettuce.bad and not lettuce.points_given and 
            current_time - lettuce.spawn_time > 10):
            # Award random amount between 10-25 cents
            points_earned = random.randint(10, 25)
            money += points_earned
            # Remove the lettuce after giving points
            lettuces.remove(lettuce)
    
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
        item.draw()
    
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