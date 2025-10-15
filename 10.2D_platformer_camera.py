import random
import math
from raylib import *
from pyray import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40          # Size of one tile in pixels
GRAVITY = 1800.0        # Downward acceleration (pixels/s/s)
JUMP_VELOCITY = -750.0  # Initial upward velocity on jump (Increased magnitude for higher jump)
PLAYER_SPEED = 300.0    # Horizontal movement speed
PLAYER_WIDTH = TILE_SIZE * 0.8
PLAYER_HEIGHT = TILE_SIZE * 0.9

# --- Expanded Level Tilemap Definition (50x16 tiles = 2000px wide) ---
# 0: Air (Empty)
# 1: Solid Ground
LEVEL = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
TILE_ROWS = len(LEVEL)
TILE_COLS = len(LEVEL[0])

# --- World Dimensions ---
WORLD_WIDTH = TILE_COLS * TILE_SIZE    # 50 * 40 = 2000
WORLD_HEIGHT = TILE_ROWS * TILE_SIZE   # 16 * 40 = 640


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
        if self.is_grounded:
            self.vy = 0.0
            
        # 2. Handle Input (Jump)
        if (IsKeyPressed(KEY_SPACE) or IsKeyPressed(KEY_UP)) and self.is_grounded:
            self.vy = JUMP_VELOCITY
            # is_grounded will be reset to False below

        # 3. Apply Gravity
        self.vy += GRAVITY * delta_time
        if self.vy > 1000:
            self.vy = 1000

        # --- Refactored Grounding Logic: Reset grounded state at start of frame update ---
        self.is_grounded = False

        # 4. Apply Movement (Separated for X and Y collision checks)
        
        # Apply X movement
        self.x += self.vx * delta_time
        self.handle_tile_collision(level, 'X')
        
        # Apply Y movement
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, 'Y')
        
        # --- Safety Clamp to World Bounds (Now uses WORLD_WIDTH) ---
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        # Player falling below world is a death condition (not implemented yet)
        
    def handle_tile_collision(self, level, axis):
        """
        Performs Axis-Aligned Bounding Box (AABB) collision checks against solid tiles 
        and resolves the collision by clamping position and zeroing velocity.
        """
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
                    
                    if CheckCollisionRecs(player_rect, tile_rect):
                        
                        if axis == 'X':
                            # Horizontal collision resolution
                            if self.vx > 0: # Moving Right
                                self.x = tile_rect[0] - self.width
                            elif self.vx < 0: # Moving Left
                                self.x = tile_rect[0] + TILE_SIZE
                            self.vx = 0.0 # Stop horizontal movement
                            
                        elif axis == 'Y':
                            # Vertical collision resolution
                            if self.vy >= 0: # Falling or standing still (Hitting Ground)
                                self.y = tile_rect[1] - self.height
                                self.is_grounded = True # Set True on confirmed floor collision
                            elif self.vy < 0: # Jumping (Hitting Ceiling)
                                self.y = tile_rect[1] + TILE_SIZE
                                
                            self.vy = 0.0 # Stop vertical movement
                            
                        # Update the player's rect after resolution
                        player_rect = self.get_rect()
                        px, py, pw, ph = player_rect


    def draw(self):
        """Draws the player at their world coordinates."""
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


def update_camera(camera, player, world_width, world_height, screen_width, screen_height):
    """Centers the camera on the player and clamps the camera's target to the world bounds."""
    
    # 1. Center the camera on the player's position
    camera.target.x = player.x + player.width / 2
    camera.target.y = player.y + player.height / 2

    # 2. Clamping the X position
    min_x = screen_width / 2
    max_x = world_width - screen_width / 2
    
    # Clamp the camera target (center point) to ensure the screen doesn't show outside the world
    if camera.target.x < min_x:
        camera.target.x = min_x
    if camera.target.x > max_x:
        camera.target.x = max_x

    # 3. Clamping the Y position
    min_y = screen_height / 2
    max_y = world_height - screen_height / 2
    
    if camera.target.y < min_y:
        camera.target.y = min_y
    if camera.target.y > max_y:
        camera.target.y = max_y
    
    # 4. Set the offset (the point on the screen where the target is drawn - center of screen)
    camera.offset.x = screen_width / 2
    camera.offset.y = screen_height / 2


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib 2D Platformer Clone (Camera Scrolling)".encode('utf-8'))
    SetTargetFPS(60)

    # Game State Variables
    player = Player(TILE_SIZE * 2, TILE_SIZE * 2) 
    game_state = "PLAYING" 
    
    # --- Camera Initialization ---
    camera = Camera2D()
    camera.target = Vector2(player.x, player.y) # World position the camera is looking at
    camera.offset = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2) # Screen position the target is drawn at (center)
    camera.rotation = 0.0
    camera.zoom = 1.0

    # --- Game Loop ---
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        
        # --- Update ---
        if game_state == "PLAYING":
            player.update(delta_time, LEVEL)
            update_camera(camera, player, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
            
        # --- Draw ---
        BeginDrawing()
        ClearBackground(SKYBLUE) 
        
        # Start the 2D camera mode. All drawing commands that follow will be relative to the camera's view.
        BeginMode2D(camera)
        
        # 1. Draw the Level
        draw_level(LEVEL)
            
        # 2. Draw Player (Drawn at world coordinates, the camera handles the translation)
        player.draw()
        
        # End the 2D camera mode
        EndMode2D()
        
        # 3. Draw HUD/Debug Info (Drawn on screen, outside of BeginMode2D)
        debug_text = f"Grounded: {player.is_grounded} | VX: {player.vx:.2f} | World Pos: ({player.x:.0f}, {player.y:.0f})".encode('utf-8')
        DrawText(debug_text, 10, 10, 20, BLACK)

        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
