import pygame
import random
import math
import time
from settings import *

class StoreItem:
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
        # For electric fence
        self.fence_start = None
        self.fence_end = None
        self.fence_active = False
        
    def draw(self, screen):
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
            pygame.draw.rect(screen, DARK_BROWN, (self.x + 10, boot_y, 15, 25))
            pygame.draw.rect(screen, DARK_BROWN, (self.x + 10, boot_y + 15, 20, 10))
            # Right boot
            pygame.draw.rect(screen, DARK_BROWN, (self.x + 35, boot_y, 15, 25))
            pygame.draw.rect(screen, DARK_BROWN, (self.x + 35, boot_y + 15, 20, 10))
        
        elif self.name == "fence":
            # Draw an electric fence icon
            pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height))
            # Draw a lightning bolt icon
            pygame.draw.polygon(screen, YELLOW, [
                (self.x + 30, self.y + 10),  # Top point
                (self.x + 15, self.y + 30),  # Middle left
                (self.x + 25, self.y + 30),  # Middle center
                (self.x + 10, self.y + 50),  # Bottom point
                (self.x + 25, self.y + 30),  # Middle center again
                (self.x + 35, self.y + 30),  # Middle right
            ])
            
            # Draw the actual fence if placed
            if self.fence_active and self.fence_start and self.fence_end:
                # Draw the fence line
                pygame.draw.line(screen, YELLOW, self.fence_start, self.fence_end, 5)
                
                # Draw little electric zaps along the fence
                fence_length = math.sqrt((self.fence_end[0] - self.fence_start[0])**2 + 
                                        (self.fence_end[1] - self.fence_start[1])**2)
                num_zaps = int(fence_length // 20)  # One zap every 20 pixels
                
                if num_zaps > 0:
                    dx = (self.fence_end[0] - self.fence_start[0]) / num_zaps
                    dy = (self.fence_end[1] - self.fence_start[1]) / num_zaps
                    
                    for i in range(num_zaps):
                        zap_x = self.fence_start[0] + dx * i
                        zap_y = self.fence_start[1] + dy * i
                        
                        # Draw a little lightning zap coming off the fence
                        if i % 2 == 0:  # Only on every other segment
                            # Get perpendicular direction
                            perp_dx = -dy / fence_length * 10
                            perp_dy = dx / fence_length * 10
                            
                            pygame.draw.line(screen, (255, 255, 0), 
                                           (zap_x, zap_y),
                                           (zap_x + perp_dx, zap_y + perp_dy), 2)
                            pygame.draw.line(screen, (255, 255, 0), 
                                           (zap_x + perp_dx, zap_y + perp_dy),
                                           (zap_x + perp_dx*0.5, zap_y + perp_dy*0.5 + 5), 2)
            
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
        
        # Give each snail a random base speed between 0.3 and 0.9 (doubled from before)
        self.base_speed = 0.6 * random.uniform(0.5, 1.5)
        self.speed = self.base_speed
        
        self.target_x = x
        self.target_y = y
        self.climbing = False
        self.climbing_timer = 0
        self.random_move_timer = 0
        self.has_shoes = False
        self.last_dx = 0
        self.last_dy = 0
        
    def draw(self, screen):
        # Draw the snail - simplified but still looking good
        
        # Draw the shell - changed to RED
        shell_color = (220, 60, 60)  # Bright red shell
        shell_pattern = (180, 30, 30)  # Darker red pattern
        pygame.draw.ellipse(screen, shell_color, (self.x, self.y, self.width, self.height))
        
        # Shell pattern - just two arcs, no random elements
        pygame.draw.arc(screen, shell_pattern, 
                      (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 
                      0, 3.14, 3)
        pygame.draw.arc(screen, shell_pattern, 
                      (self.x + 10, self.y + 10, self.width - 20, self.height - 20), 
                      0, 3.14, 3)
        
        # Draw the snail body (fixed position relative to shell) - changed to PINK
        pink_color = (255, 150, 200)  # Pink body color
        body_length = 20
        pygame.draw.ellipse(screen, pink_color, (self.x - body_length, self.y + self.height - 15, body_length + 10, 15))
        
        # Draw the snail head (fixed position) - also PINK
        pygame.draw.ellipse(screen, pink_color, (self.x - body_length - 10, self.y + self.height - 18, 15, 10))
        
        # Draw the eye stalks (fixed position) - also PINK
        stalk1_x = self.x - body_length - 5
        stalk1_y = self.y + self.height - 15
        stalk2_x = self.x - body_length
        stalk2_y = self.y + self.height - 15
        
        # Draw eye stalks - also PINK
        pygame.draw.line(screen, pink_color, (stalk1_x, stalk1_y), 
                         (stalk1_x - 5, stalk1_y - 15), 2)
        pygame.draw.line(screen, pink_color, (stalk2_x, stalk2_y), 
                         (stalk2_x - 0, stalk2_y - 15), 2)
        
        # Draw the eyes - keeping BLACK
        pygame.draw.circle(screen, BLACK, (stalk1_x - 5, stalk1_y - 15), 2)
        pygame.draw.circle(screen, BLACK, (stalk2_x - 0, stalk2_y - 15), 2)
        
        # Draw shoes if the snail has them
        if self.has_shoes:
            # Left boot
            pygame.draw.rect(screen, DARK_BROWN, (self.x - body_length - 5, self.y + self.height, 10, 5))
            # Right boot
            pygame.draw.rect(screen, DARK_BROWN, (self.x - body_length + 5, self.y + self.height, 10, 5))
        
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

    def check_fence_collision(self, store_items):
        # Check if snail is crossing an electric fence
        for item in store_items:
            if item.name == "fence" and item.fence_active and item.fence_start and item.fence_end:
                # Calculate the distance from snail to the fence line
                # using the formula for distance from point to line segment
                x1, y1 = item.fence_start
                x2, y2 = item.fence_end
                x3, y3 = self.x + self.width//2, self.y + self.height//2
                
                # Calculate the length of the fence line
                line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if line_length == 0:  # Avoid division by zero if fence points are the same
                    return False
                
                # Calculate the distance from point to line
                numerator = abs((y2-y1)*x3 - (x2-x1)*y3 + x2*y1 - y2*x1)
                distance = numerator / line_length
                
                # Check if point is actually within the line segment bounds
                # Project point onto line
                t = ((x3-x1)*(x2-x1) + (y3-y1)*(y2-y1)) / (line_length * line_length)
                
                # If projection is on the line segment and distance is small, consider it a collision
                if 0 <= t <= 1 and distance < 15:
                    return True
                    
        return False
        
    def update(self, lettuces, store_items):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Only move if not being dragged
        if not self.dragging:
            # Increment random movement timer
            self.random_move_timer += 0.1
            
            # Decide whether to continue in last direction with VERY high probability (80%)
            if self.last_dx != 0 or self.last_dy != 0:
                if random.random() < 0.8:  # 80% chance to continue in same direction
                    # First check if this movement would cross a fence
                    future_x = self.x + self.last_dx
                    future_y = self.y + self.last_dy
                    
                    # Check if future position would be out of bounds
                    if future_x < 0 or future_x > SCREEN_WIDTH - self.width or \
                       future_y < STORE_RECT.height or future_y > SCREEN_HEIGHT - self.height:
                        # Bounce off the edge with a new random direction
                        random_angle = random.uniform(0, 2 * math.pi)
                        self.last_dx = math.cos(random_angle) * self.speed
                        self.last_dy = math.sin(random_angle) * self.speed
                        return
                        
                    self.x = future_x
                    self.y = future_y
                    
                    # Check if we just crossed a fence
                    if self.check_fence_collision(store_items):
                        # Bounce back and change direction
                        self.x -= self.last_dx * 2
                        self.y -= self.last_dy * 2
                        self.last_dx = -self.last_dx
                        self.last_dy = -self.last_dy
                    
                    return  # Skip the rest of movement logic
            
            # Find closest lettuce more often, but with some randomness
            if random.random() < 0.8:  # 80% chance to go toward lettuce (increased from 70%)
                closest_lettuce = self.find_closest_lettuce(lettuces)
                
                if closest_lettuce:
                    # Set target to the closest lettuce
                    self.target_x = closest_lettuce.x
                    self.target_y = closest_lettuce.y
                    
                    # Add some randomness to the target position
                    self.target_x += random.uniform(-30, 30)
                    self.target_y += random.uniform(-30, 30)
            # Random walk less often
            elif random.random() < 0.1 or self.random_move_timer > random.uniform(5, 10):
                # Set a random target with smaller range (reduced from 200)
                if self.in_garden:
                    max_range = 100  # Smaller random movement range
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
                            
                    # Gnome effect - snails avoid radius, MUCH stronger effect
                    elif item.name == "gnome":
                        dist_to_item = math.sqrt((self.x - item.x)**2 + (self.y - item.y)**2)
                        if dist_to_item < item.effect_radius * 1.5:  # Larger avoidance radius
                            # Reverse direction away from gnome with stronger force
                            dx = self.x - item.x
                            dy = self.y - item.y
                            distance = max(1, math.sqrt(dx*dx + dy*dy))
                            # Move at 5x normal speed away from gnome (increased from 3x)
                            self.x += (dx / distance) * current_speed * 5.0
                            self.y += (dy / distance) * current_speed * 5.0
                            
                            # Store the last movement for direction persistence
                            self.last_dx = (dx / distance) * current_speed * 5.0
                            self.last_dy = (dy / distance) * current_speed * 5.0
                            return  # Skip normal movement
            
            # Move toward target with jitter
            move_dx = ((dx / distance) * current_speed) + jitter_x
            move_dy = ((dy / distance) * current_speed) + jitter_y
            
            # Check if this movement would cross a fence
            future_x = self.x + move_dx
            future_y = self.y + move_dy
            
            # Save original position to restore if fence crossed
            orig_x, orig_y = self.x, self.y
            
            # Move the snail
            self.x = future_x
            self.y = future_y
            
            # Check if we just crossed a fence
            if self.check_fence_collision(store_items):
                # Bounce back and generate new random direction
                self.x = orig_x
                self.y = orig_y
                
                # Choose a random new direction to go instead
                random_angle = random.uniform(0, 2 * math.pi)
                self.last_dx = math.cos(random_angle) * current_speed
                self.last_dy = math.sin(random_angle) * current_speed
            else:
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
        
        # Add different lettuce types with different colors and bite resistance
        self.lettuce_type = random.choice(["green", "yellow", "red", "purple"])
        
        # Set max bites based on type
        if self.lettuce_type == "green":
            self.max_bites = 5  # Regular green lettuce (unchanged)
        elif self.lettuce_type == "yellow":
            self.max_bites = 15  # Yellow can take 10 more bites
        elif self.lettuce_type == "red":
            self.max_bites = 25  # Red can take 20 more bites
        elif self.lettuce_type == "purple":
            self.max_bites = 35  # Purple can take 30 more bites
        
    def draw(self, screen):
        # Set color based on type
        if self.bad:
            color = (150, 150, 0)  # Yellowish for bad lettuce
            edge_color = (130, 130, 0)
        else:
            if self.lettuce_type == "green":
                color = LIME_GREEN
                edge_color = (30, 180, 30)
            elif self.lettuce_type == "yellow":
                color = (220, 220, 50)  # Bright yellow
                edge_color = (180, 180, 30)
            elif self.lettuce_type == "red":
                color = (220, 60, 60)  # Bright red
                edge_color = (180, 30, 30)
            elif self.lettuce_type == "purple":
                color = (180, 60, 220)  # Purple
                edge_color = (140, 30, 180)
            
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
            num_bites = min(int(self.bites + 1), self.max_bites)
            
            # More bite positions for more durable lettuce
            bite_positions = []
            for _ in range(min(40, self.max_bites)):  # Generate up to 40 positions
                bite_positions.append((
                    random.randint(5, self.width-5), 
                    random.randint(5, self.height-5)
                ))
            
            for i in range(num_bites):
                if i < len(bite_positions):
                    bite_x = self.x + bite_positions[i][0]
                    bite_y = self.y + bite_positions[i][1]
                    bite_size = 4
                    pygame.draw.circle(screen, WHITE, (bite_x, bite_y), bite_size)
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

# Function to keep objects within game boundaries
def keep_in_bounds(item):
    # Keep objects within the screen boundaries
    if item.x < 0:
        item.x = 0
    elif item.x > SCREEN_WIDTH - item.width:
        item.x = SCREEN_WIDTH - item.width
        
    # Keep below store area but not in tank if in garden
    if item.in_garden if hasattr(item, 'in_garden') else not item.in_store:
        if item.y < STORE_RECT.height:
            item.y = STORE_RECT.height
        elif item.y > SCREEN_HEIGHT - item.height:
            item.y = SCREEN_HEIGHT - item.height
            
    # Force store items to stay in store if they're marked as in_store
    if isinstance(item, StoreItem) and item.in_store:
        if item.y < 10:
            item.y = 20
        elif item.y > STORE_RECT.height - 20:
            item.y = 20