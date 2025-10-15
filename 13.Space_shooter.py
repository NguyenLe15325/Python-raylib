import math
from raylib import *
from pyray import *
import random

# --- Game Constants ---

# Grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
GRID_OFFSET_X = 20 # Padding from left edge
GRID_OFFSET_Y = 20 # Padding from top edge

# Screen dimensions based on grid and side panel
SIDE_PANEL_WIDTH = 150
SCREEN_WIDTH = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + SIDE_PANEL_WIDTH + 20
SCREEN_HEIGHT = GRID_OFFSET_Y + GRID_HEIGHT * BLOCK_SIZE + 20
TITLE = b"Python Raylib Tetris Clone"
TARGET_FPS = 60

# Game Physics/Timing
DROP_TIME = 0.5         # Time (seconds) for gravity drop
SOFT_DROP_SPEED = 0.05  # Time (seconds) for soft drop (fast fall)
LINE_CLEAR_POINTS = [0, 100, 300, 500, 800] # Points for 0, 1, 2, 3, 4 lines

# Define the colors for the grid (using Raylib Colors)
# 0 is empty (Black), 1-7 map to the colors below
TETROMINO_COLORS = [
    BLACK, LIME, RED, PURPLE, ORANGE, BLUE, SKYBLUE, YELLOW 
]

# The 7 Tetromino shapes and their rotations (4x4 grid flattened to a 16-element array)
# Index 0 is empty (background), 1-7 map to the colors in TETROMINO_COLORS
TETROMINOES = {
    'I': {'color_idx': 1, 'shapes': [ # Lime
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    ]},
    'Z': {'color_idx': 2, 'shapes': [ # Red
        [1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    ]},
    'T': {'color_idx': 3, 'shapes': [ # Purple
        [0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    ]},
    'L': {'color_idx': 4, 'shapes': [ # Orange
        [0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    ]},
    'J': {'color_idx': 5, 'shapes': [ # Blue
        [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
    ]},
    'S': {'color_idx': 6, 'shapes': [ # SkyBlue
        [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    ]},
    'O': {'color_idx': 7, 'shapes': [ # Yellow
        [0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]},
}

# --- Game Class ---

class Piece:
    """Represents a falling Tetromino piece."""
    def __init__(self, key):
        self.key = key
        self.data = TETROMINOES[key]
        self.color_idx = self.data['color_idx']
        self.shape_list = self.data['shapes']
        self.rotation = 0
        
        # Start position (top center)
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0

    def get_shape(self):
        """Returns the current 16-element shape array for the current rotation."""
        return self.shape_list[self.rotation]

    def rotate(self, direction):
        """Changes the rotation index."""
        num_rotations = len(self.shape_list)
        self.rotation = (self.rotation + direction) % num_rotations

    def draw(self, offset_x, offset_y, block_size):
        """Draws the piece on the grid."""
        shape = self.get_shape()
        for i in range(16):
            if shape[i] == 1:
                row = i // 4
                col = i % 4
                DrawRectangle(
                    offset_x + (self.x + col) * block_size,
                    offset_y + (self.y + row) * block_size,
                    block_size, block_size,
                    TETROMINO_COLORS[self.color_idx]
                )
                DrawRectangleLines(
                    offset_x + (self.x + col) * block_size,
                    offset_y + (self.y + row) * block_size,
                    block_size, block_size,
                    BLACK
                )

class Game:
    """The main Tetris game logic manager."""
    def __init__(self):
        # Game grid: 2D list storing the color index (0 for empty)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.is_game_over = False
        
        self.current_piece = self._get_new_piece()
        self.next_piece = self._get_new_piece()
        
        self.drop_timer = 0.0
        self.drop_interval = DROP_TIME # Starts at base drop time
        self.hard_drop_locking = False # Flag for hard drop to prevent instant lock

    def _get_new_piece(self):
        """Generates a new, random piece."""
        key = random.choice(list(TETROMINOES.keys()))
        return Piece(key)

    def _is_valid_position(self, piece, new_x, new_y, new_rotation):
        """Checks if a piece's position/rotation is valid (no collisions)."""
        piece.rotation = new_rotation
        shape = piece.get_shape()
        
        for i in range(16):
            if shape[i] == 1:
                row = piece.y + i // 4
                col = i % 4
                
                # Use prospective position
                test_row = new_y + i // 4
                test_col = new_x + i % 4
                
                # Check boundaries
                if test_col < 0 or test_col >= GRID_WIDTH or test_row >= GRID_HEIGHT:
                    return False
                
                # Check for collision with settled blocks (ignore above grid)
                if test_row >= 0 and self.grid[test_row][test_col] != 0:
                    return False
        
        return True

    def _lock_piece(self):
        """Locks the current piece into the grid."""
        shape = self.current_piece.get_shape()
        color_idx = self.current_piece.color_idx
        
        for i in range(16):
            if shape[i] == 1:
                row = self.current_piece.y + i // 4
                col = self.current_piece.x + i % 4
                
                # Check for game over condition (piece locked in non-visible area)
                if row < 0: 
                    self.is_game_over = True
                    return

                # Place block on grid
                self.grid[row][col] = color_idx
        
        self._check_and_clear_lines()
        self._spawn_next_piece()

    def _spawn_next_piece(self):
        """Moves next piece to current and generates a new next piece."""
        self.current_piece = self.next_piece
        self.next_piece = self._get_new_piece()
        self.hard_drop_locking = False
        
        # Check for immediate game over upon spawn
        if not self._is_valid_position(self.current_piece, self.current_piece.x, self.current_piece.y, self.current_piece.rotation):
            self.is_game_over = True

    def _check_and_clear_lines(self):
        """Checks for and clears any completed lines, awarding points."""
        cleared_count = 0
        new_grid = []
        
        for row in self.grid:
            if 0 in row:
                new_grid.append(row)
            else:
                cleared_count += 1
        
        # Pad the top with new empty rows
        for _ in range(cleared_count):
            new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
        self.grid = new_grid
        self.lines_cleared += cleared_count
        
        # Award points
        if cleared_count > 0:
            self.score += LINE_CLEAR_POINTS[cleared_count]
            # Simple speed increase (e.g., increase speed every 10 lines)
            self.drop_interval = DROP_TIME * (0.9 ** (self.lines_cleared // 10))

    def move(self, dx, dy):
        """Attempts to move the piece by (dx, dy). Returns True if successful."""
        new_x = self.current_piece.x + dx
        new_y = self.current_piece.y + dy
        
        if self._is_valid_position(self.current_piece, new_x, new_y, self.current_piece.rotation):
            self.current_piece.x = new_x
            self.current_piece.y = new_y
            return True
        return False

    def rotate(self, direction):
        """Attempts to rotate the piece."""
        original_rotation = self.current_piece.rotation
        new_rotation = (original_rotation + direction) % len(self.current_piece.shape_list)
        
        # Simple Wall Kick Test (try moving sideways if rotation hits wall)
        if self._is_valid_position(self.current_piece, self.current_piece.x, self.current_piece.y, new_rotation):
            self.current_piece.rotation = new_rotation
            return True
        # Try kick right
        elif self._is_valid_position(self.current_piece, self.current_piece.x + 1, self.current_piece.y, new_rotation):
            self.current_piece.x += 1
            self.current_piece.rotation = new_rotation
            return True
        # Try kick left
        elif self._is_valid_position(self.current_piece, self.current_piece.x - 1, self.current_piece.y, new_rotation):
            self.current_piece.x -= 1
            self.current_piece.rotation = new_rotation
            return True
        
        # Reset rotation if all kicks fail (piece.rotation was temporarily set in _is_valid_position)
        self.current_piece.rotation = original_rotation 
        return False

    def hard_drop(self):
        """Instantly drops the piece and locks it."""
        if self.is_game_over: return
        
        # Find the drop distance
        drop_y = self.current_piece.y
        while self.move(0, 1):
            drop_y = self.current_piece.y
            
        # The piece has moved to the lowest possible valid y position
        self.current_piece.y = drop_y
        self.hard_drop_locking = True
        self._lock_piece()

    def update(self, dt):
        """Updates the game state."""
        if self.is_game_over: return

        # Handle input
        if IsKeyPressed(KEY_LEFT) or IsKeyPressed(KEY_A):
            self.move(-1, 0)
        if IsKeyPressed(KEY_RIGHT) or IsKeyPressed(KEY_D):
            self.move(1, 0)
            
        # Hard Drop
        if IsKeyPressed(KEY_SPACE):
            self.hard_drop()
            return # Don't process soft drop/gravity if hard drop occurred

        # Rotation
        if IsKeyPressed(KEY_UP) or IsKeyPressed(KEY_W) or IsKeyPressed(KEY_X):
            self.rotate(1) # Clockwise
        if IsKeyPressed(KEY_Z) or IsKeyPressed(KEY_LEFT_CONTROL):
            self.rotate(-1) # Counter-clockwise

        # Gravity / Soft Drop
        self.drop_timer += dt
        
        current_interval = self.drop_interval
        # If soft drop is held, decrease the effective drop interval
        if IsKeyDown(KEY_DOWN) or IsKeyDown(KEY_S):
            current_interval = SOFT_DROP_SPEED
            
        if self.drop_timer >= current_interval:
            self.drop_timer = 0.0
            
            # If the move down fails, the piece must lock
            if not self.move(0, 1):
                # Lock immediately if not a hard drop (hard drop already locked it)
                if not self.hard_drop_locking:
                    self._lock_piece()

    def draw(self):
        """Draws the grid, pieces, and HUD."""
        
        # Draw the main game area background
        grid_rect = Rectangle(GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE)
        DrawRectangleRec(grid_rect, Color(30, 41, 59, 255)) # Dark background
        DrawRectangleLinesEx(grid_rect, 4, LIGHTGRAY)
        
        # 1. Draw Settled Blocks
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                color_idx = self.grid[r][c]
                if color_idx != 0:
                    x = GRID_OFFSET_X + c * BLOCK_SIZE
                    y = GRID_OFFSET_Y + r * BLOCK_SIZE
                    DrawRectangle(x, y, BLOCK_SIZE, BLOCK_SIZE, TETROMINO_COLORS[color_idx])
                    DrawRectangleLines(x, y, BLOCK_SIZE, BLOCK_SIZE, BLACK)

        # 2. Draw Current Falling Piece
        if not self.is_game_over:
            self.current_piece.draw(GRID_OFFSET_X, GRID_OFFSET_Y, BLOCK_SIZE)

        # 3. Draw HUD (Score, Lines, Next Piece)
        hud_x = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 20
        DrawText(b"SCORE", hud_x, 40, 20, RAYWHITE)
        DrawText(f"{self.score}".encode('utf-8'), hud_x, 65, 30, YELLOW)

        DrawText(b"LINES", hud_x, 110, 20, RAYWHITE)
        DrawText(f"{self.lines_cleared}".encode('utf-8'), hud_x, 135, 30, LIME)

        DrawText(b"NEXT", hud_x, 190, 20, RAYWHITE)
        
        # Define offsets for the Next Piece display area outside the if block (FIXED NameError)
        next_x_offset = hud_x + 30
        next_y_offset = 220
        
        # Draw Next Piece
        if self.next_piece:
            # Fix: Ensure the block size passed for the small 'next' piece is an integer.
            self.next_piece.draw(next_x_offset, next_y_offset, int(BLOCK_SIZE / 1.5))
            
        # Draw Instructions
        DrawText(b"Controls:", 10, SCREEN_HEIGHT - 35, 15, WHITE)
        DrawText(b"L/R: A/D", 10, SCREEN_HEIGHT - 20, 15, WHITE)
        DrawText(b"Rotate: W/Up", 90, SCREEN_HEIGHT - 35, 15, WHITE)
        DrawText(b"Soft Drop: S/Down", 90, SCREEN_HEIGHT - 20, 15, WHITE)
        DrawText(b"Hard Drop: SPACE", 230, SCREEN_HEIGHT - 20, 15, RED)

        # 4. Draw Game Over Screen
        if self.is_game_over:
            DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Fade(BLACK, 0.8))
            
            game_over_text = b"GAME OVER"
            restart_text = b"Press ENTER to Restart"
            
            text_w = MeasureText(game_over_text, 60)
            DrawText(game_over_text, int(SCREEN_WIDTH/2 - text_w/2), int(SCREEN_HEIGHT/2 - 60), 60, RED)
            
            text_w = MeasureText(restart_text, 25)
            DrawText(restart_text, int(SCREEN_WIDTH/2 - text_w/2), int(SCREEN_HEIGHT/2 + 20), 25, RAYWHITE)


# --- Main Function ---
game = None

def main():
    global game
    
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(TARGET_FPS)
    
    game = Game()

    while not WindowShouldClose():
        dt = GetFrameTime()
        
        # --- Update ---
        if not game.is_game_over:
            game.update(dt)
        elif IsKeyPressed(KEY_ENTER):
            game = Game() # Reset game
            
        # --- Draw ---
        BeginDrawing()
        ClearBackground(DARKGRAY) 
        
        game.draw()
        
        EndDrawing()

    CloseWindow()

if __name__ == "__main__":
    main()
