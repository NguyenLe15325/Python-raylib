import random
import math
from raylib import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40          # Size of one tile in pixels
GRAVITY = 1800.0        # Downward acceleration (pixels/s/s)
JUMP_VELOCITY = -750.0  # Initial upward velocity on jump (Increased magnitude for higher jump)
PLAYER_SPEED = 300.0    # Horizontal movement speed
PLAYER_WIDTH = TILE_SIZE * 0.8
PLAYER_HEIGHT = TILE_SIZE * 0.9

# --- Level Tilemap Definition ---
# 0: Air (Empty)
# 1: Solid Ground
LEVEL = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
TILE_ROWS = len(LEVEL)
TILE_COLS = len(LEVEL[0])


# --- Game Object Classes ---

class Player:
    def __init__(self, x, y):
        # Position (center for simple drawing, top-left for collision)
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        
        # Physics
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False

    def get_rect(self):
        """Returns the player's collision bounding box (top-left, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def update(self, delta_time, level):
        # 1. Handle Input (Horizontal Movement)
        self.vx = 0.0
        if IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A):
            self.vx = -PLAYER_SPEED
        if IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D):
            self.vx = PLAYER_SPEED

        # --- FIX: Velocity Zeroing for Stability ---
        # If the player is grounded, force vertical velocity to zero 
        # to prevent accumulation of residual forces and eliminate flicker.
        if self.is_grounded:
            self.vy = 0.0
            
        # 2. Handle Input (Jump)
        if (IsKeyPressed(KEY_SPACE) or IsKeyPressed(KEY_UP)) and self.is_grounded:
            self.vy = JUMP_VELOCITY
            # is_grounded will be reset to False below

        # 3. Apply Gravity
        # Now we apply gravity universally, allowing it to start the fall immediately after a jump
        self.vy += GRAVITY * delta_time
        # Clamp terminal velocity to prevent massive speeds
        if self.vy > 1000:
            self.vy = 1000

        # --- Refactored Grounding Logic: Reset grounded state at start of frame update ---
        # Assume not grounded, forcing the Y collision check to confirm landing.
        self.is_grounded = False

        # 4. Apply Movement (Separated for X and Y collision checks)
        
        # Apply X movement
        self.x += self.vx * delta_time
        self.handle_tile_collision(level, 'X')
        
        # Apply Y movement
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, 'Y')
        
        # --- Safety Clamp to World Bounds (Optional) ---
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
    def handle_tile_collision(self, level, axis):
        """
        Performs Axis-Aligned Bounding Box (AABB) collision checks against solid tiles 
        and resolves the collision by clamping position and zeroing velocity.
        """
        # The grounded reset logic was moved to Player.update.

        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
        
        # Determine the range of tiles the player potentially overlaps
        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        # Iterate over all potentially intersecting tiles
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                
                # Check for bounds
                if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                    continue
                
                # Check if the tile is solid (value 1)
                if level[row][col] == 1:
                    tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    # Use Raylib's CheckCollisionRecs for simple intersection detection
                    if CheckCollisionRecs(player_rect, tile_rect):
                        
                        if axis == 'X':
                            # Horizontal collision resolution
                            if self.vx > 0: # Moving Right
                                # Clamp player's right edge to tile's left edge
                                self.x = tile_rect[0] - self.width
                            elif self.vx < 0: # Moving Left
                                # Clamp player's left edge to tile's right edge
                                self.x = tile_rect[0] + TILE_SIZE
                            self.vx = 0.0 # Stop horizontal movement upon collision
                            
                        elif axis == 'Y':
                            # Vertical collision resolution
                            # FIX: Check for falling OR standing still (vy >= 0) to ensure grounding is set.
                            if self.vy >= 0: # Falling or standing still (Hitting Ground)
                                # Clamp player's bottom edge to tile's top edge
                                self.y = tile_rect[1] - self.height
                                self.is_grounded = True # Set True on confirmed floor collision
                            elif self.vy < 0: # Jumping (Hitting Ceiling)
                                # Clamp player's top edge to tile's bottom edge
                                self.y = tile_rect[1] + TILE_SIZE
                                
                            self.vy = 0.0 # Stop vertical movement upon collision
                            
                        # Update the player's rect after resolution to ensure accurate subsequent checks
                        player_rect = self.get_rect()
                        px, py, pw, ph = player_rect


    def draw(self):
        # Draw the player as a yellow rectangle
        DrawRectangle(int(self.x), int(self.y), int(self.width), int(self.height), GOLD)
        # Indicate state with color
        if self.is_grounded:
             DrawRectangleLines(int(self.x), int(self.y), int(self.width), int(self.height), WHITE)
        else:
             DrawRectangleLines(int(self.x), int(self.y), int(self.width), int(self.height), GRAY)


def draw_level(level):
    """Draws the tiles of the level map."""
    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            tile_value = level[row][col]
            if tile_value == 1:
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                
                # Draw solid block
                DrawRectangle(x, y, TILE_SIZE, TILE_SIZE, DARKGRAY)
                # Draw edge lines for clarity
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, BLACK)


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib 2D Platformer Clone".encode('utf-8'))
    SetTargetFPS(60)

    # Game State Variables
    # Start player at the top left, adjusting for tile size
    player = Player(TILE_SIZE * 2, TILE_SIZE * 2) 
    game_state = "PLAYING" # Simple state for this example

    # --- Game Loop ---
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        
        # --- Update ---
        if game_state == "PLAYING":
            player.update(delta_time, LEVEL)
            
        # --- Draw ---
        BeginDrawing()
        ClearBackground(SKYBLUE) 
        
        # 1. Draw the Level
        draw_level(LEVEL)
            
        # 2. Draw Player
        player.draw()
        
        # 3. Draw HUD/Debug Info
        debug_text = f"Grounded: {player.is_grounded} | VY: {player.vy:.2f}".encode('utf-8')
        DrawText(debug_text, 10, 10, 20, BLACK)


        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
