
import random
from raylib import *
from pyray import *
import math

# --- Game Constants ---
BLOCK_SIZE = 40
TITLE = b"Python Raylib Sokoban"
TARGET_FPS = 60
MAX_HISTORY = 50 # Max moves to store for undo

# Map Element Colors
COLOR_WALL = Color(100, 100, 100, 255)    # Gray
COLOR_FLOOR = Color(40, 40, 50, 255)      # Dark Blue-Gray
COLOR_TARGET = Color(20, 20, 30, 255)     # Very Dark Target Circle (drawn on floor)
COLOR_PLAYER = Color(255, 165, 0, 255)    # Orange
COLOR_BOX_OFF = Color(139, 69, 19, 255)   # Brown (Box off target)
COLOR_BOX_ON = Color(0, 255, 0, 255)      # Green (Box on target)

# Level Map Definitions (using symbols for easy layout)
# #: Wall, ' ': Floor, .: Target, @: Player, $: Box
LEVELS = [
    # Level 1 (Verified Solvable) - 10x6
    [
        "##########",
        "#  #     #",
        "# $# $ $ #",
        "#  # . . #",
        "# @. $ . #",
        "##########",
    ],
    # Level 2 (Corrected: 4 Boxes, 4 Targets) - 8x7
    [
        "########",
        "#@.$  .#",
        "# $    #",
        "# . $  #", # Target added here to match 4 boxes
        "## #   #",
        "#  . $ #",
        "########",
    ],
    # Level 3 (Simplified Beginner: 4 Boxes, 4 Targets) - 9x8
    [
        "#########",
        "#@      #", 
        "# $ # $ #", 
        "# . # . #", 
        "#       #",
        "# $ # $ #",
        "# . # . #", 
        "#########",
    ]
]
TOTAL_LEVELS = len(LEVELS)

# --- Game Class ---

class SokobanGame:
    """Manages the Sokoban game state, map, and logic."""
    def __init__(self, level_index):
        # State variables for multi-level tracking
        self.current_level_index = level_index
        self.is_game_over = False   # True when ALL levels are completed
        self.level_complete = False # True when current level is solved
        self.moves = 0
        self.state_history = [] 

        # Load the layout based on the index
        level_layout = LEVELS[level_index]
        self.level_layout = level_layout
        self.grid_rows = len(level_layout)
        self.grid_cols = len(level_layout[0])
        
        # Calculate screen dimensions based on map size
        self.screen_width = self.grid_cols * BLOCK_SIZE
        self.screen_height = self.grid_rows * BLOCK_SIZE + 50 # +50 for HUD/instructions
        
        self.static_grid = []
        self.player_pos = (0, 0)
        self.box_positions = []
        self.target_positions = []
        
        self._load_level(level_layout)
        self._save_state()

    def _load_level(self, layout):
        """Parses the character layout into internal data structures."""
        self.static_grid = []
        self.box_positions = []
        self.target_positions = []
        
        for r, row_str in enumerate(layout):
            row_data = []
            for c, char in enumerate(row_str):
                pos = (r, c)
                
                # Determine static element
                if char == '#':
                    row_data.append(1) # Wall
                elif char == '.' or char == '+' or char == '*':
                    row_data.append(3) # Target
                    self.target_positions.append(pos)
                else:
                    row_data.append(0) # Floor
                    
                # Determine dynamic element
                if char == '@' or char == '+':
                    self.player_pos = pos
                elif char == '$' or char == '*':
                    self.box_positions.append(pos)
                    
            self.static_grid.append(row_data)

    def _save_state(self):
        """Saves the current game state to the history stack."""
        if len(self.state_history) >= MAX_HISTORY:
            self.state_history.pop(0) # Remove oldest state
            
        # Store a deep copy of the box positions list
        current_state = (self.player_pos, list(self.box_positions))
        self.state_history.append(current_state)
        
    def undo_move(self):
        """Restores the game state from the history stack."""
        if len(self.state_history) > 1:
            self.state_history.pop() # Remove current state
            last_state = self.state_history[-1]
            self.player_pos, self.box_positions = last_state
            self.moves -= 1 # Decrement move count
            
            # Ensure box_positions is a fresh list copy
            self.box_positions = list(self.box_positions) 
            
    def _advance_level(self):
        """Loads the next level or signals game completion."""
        next_index = self.current_level_index + 1
        
        if next_index < TOTAL_LEVELS:
            # Load next level
            global game
            # Re-initialize the global game object with the next level index
            game = SokobanGame(next_index) 
        else:
            # All levels completed (True game over / win)
            self.is_game_over = True
            self.level_complete = False 
            
    def move_player(self, dr, dc):
        """Attempts to move the player and push boxes."""
        if self.level_complete or self.is_game_over: return # Prevent movement when solved
        
        r, c = self.player_pos
        new_r, new_c = r + dr, c + dc
        
        # 1. Check if the new position is a Wall
        if self.static_grid[new_r][new_c] == 1:
            return

        # 2. Check if the new position has a Box
        if (new_r, new_c) in self.box_positions:
            # Calculate the position *behind* the box
            push_r, push_c = new_r + dr, new_c + dc
            
            # Check if the space behind the box is free (not wall and not another box)
            if self.static_grid[push_r][push_c] == 1 or (push_r, push_c) in self.box_positions:
                # Cannot push the box
                return
            else:
                # Move the Box: Replace old box position with new one in the list
                box_idx = self.box_positions.index((new_r, new_c))
                self.box_positions[box_idx] = (push_r, push_c)
                
        # 3. Finalize Player Movement
        self.player_pos = (new_r, new_c)
        self.moves += 1
        self._save_state()
        
        # 4. Check Win Condition after a move
        if self.check_win():
            self.level_complete = True # Set level complete flag
        
    def check_win(self):
        """Returns True if all boxes are on target squares."""
        if not self.target_positions:
            return False
            
        return all(box_pos in self.target_positions for box_pos in self.box_positions)

    def update(self, dt):
        """Handles player input."""
        
        # Logic for level transition or final restart
        if self.level_complete or self.is_game_over:
            if IsKeyPressed(KEY_ENTER):
                if self.is_game_over:
                    # Restart entire game (Level 1)
                    global game
                    game = SokobanGame(0)
                else:
                    # Advance to next level
                    self._advance_level()
            return

        dr, dc = 0, 0
        if IsKeyPressed(KEY_RIGHT) or IsKeyPressed(KEY_D):
            dc = 1
        elif IsKeyPressed(KEY_LEFT) or IsKeyPressed(KEY_A):
            dc = -1
        elif IsKeyPressed(KEY_UP) or IsKeyPressed(KEY_W):
            dr = -1
        elif IsKeyPressed(KEY_DOWN) or IsKeyPressed(KEY_S):
            dr = 1
        
        # Undo logic
        if IsKeyPressed(KEY_Z):
            self.undo_move()
            
        if dr != 0 or dc != 0:
            self.move_player(dr, dc)
            
    def draw(self):
        """Draws the game board and all elements."""
        
        # Draw the Grid and Static Elements
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                x = c * BLOCK_SIZE
                y = r * BLOCK_SIZE
                
                cell_type = self.static_grid[r][c]
                
                # Draw Floor
                DrawRectangle(x, y, BLOCK_SIZE, BLOCK_SIZE, COLOR_FLOOR)
                
                # Draw Wall
                if cell_type == 1:
                    DrawRectangle(x, y, BLOCK_SIZE, BLOCK_SIZE, COLOR_WALL)
                    
                # Draw Target (as a subtle circle on the floor)
                elif cell_type == 3:
                    DrawCircle(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2, BLOCK_SIZE // 3, COLOR_TARGET)
                    
        # Draw Boxes
        for r_box, c_box in self.box_positions:
            x = c_box * BLOCK_SIZE
            y = r_box * BLOCK_SIZE
            
            # Check if box is on a target
            on_target = self.static_grid[r_box][c_box] == 3
            
            color = COLOR_BOX_ON if on_target else COLOR_BOX_OFF
            
            # Draw the box rectangle
            DrawRectangle(x + 2, y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4, color)
            DrawRectangleLines(x, y, BLOCK_SIZE, BLOCK_SIZE, BLACK)

        # Draw Player
        r_p, c_p = self.player_pos
        x_p = c_p * BLOCK_SIZE
        y_p = r_p * BLOCK_SIZE
        
        DrawCircle(x_p + BLOCK_SIZE // 2, y_p + BLOCK_SIZE // 2, BLOCK_SIZE // 2 - 5, COLOR_PLAYER)
        
        # Draw HUD/Instructions
        hud_y = self.grid_rows * BLOCK_SIZE
        
        DrawRectangle(0, hud_y, self.screen_width, 50, Color(30, 30, 30, 255))
        
        # Display current level
        DrawText(b"LEVEL:", 10, hud_y + 15, 20, RAYWHITE)
        DrawText(f"{self.current_level_index + 1} / {TOTAL_LEVELS}".encode('utf-8'), 100, hud_y + 15, 20, LIME)

        # Display moves
        DrawText(b"MOVES:", 200, hud_y + 15, 20, RAYWHITE)
        DrawText(f"{self.moves}".encode('utf-8'), 300, hud_y + 15, 20, YELLOW)

        DrawText(b"Controls: Arrows/WASD | Undo: Z | Next: Enter", 400, hud_y + 15, 18, RAYWHITE)

        # Draw Win/Completion Screen
        if self.level_complete or self.is_game_over:
            DrawRectangle(0, 0, self.screen_width, self.screen_height, Fade(BLACK, 0.8))
            
            # Determine the correct message based on state
            if self.is_game_over:
                win_text = b"ALL LEVELS CONQUERED!"
                restart_text = b"Press ENTER to Restart from Level 1"
            else:
                win_text = b"LEVEL CLEARED!"
                restart_text = b"Press ENTER for Next Level"
            
            # Win Text
            text_w = MeasureText(win_text, 40)
            DrawText(win_text, int(self.screen_width/2 - text_w/2), int(self.screen_height/2 - 60), 40, GREEN)
            
            # Moves Text
            moves_text = f"Total Moves: {self.moves}".encode('utf-8')
            text_w = MeasureText(moves_text, 25)
            DrawText(moves_text, int(self.screen_width/2 - text_w/2), int(self.screen_height/2), 25, RAYWHITE)
            
            # Restart/Next Level Text
            text_w = MeasureText(restart_text, 20)
            DrawText(restart_text, int(self.screen_width/2 - text_w/2), int(self.screen_height/2 + 40), 20, RAYWHITE)


# --- Main Function ---
game = None

def main():
    global game
    
    # Initialize the game instance with the first level index (0)
    game = SokobanGame(0)
    
    InitWindow(game.screen_width, game.screen_height, TITLE)
    SetTargetFPS(TARGET_FPS)
    
    while not WindowShouldClose():
        dt = GetFrameTime()
        
        # --- Update ---
        game.update(dt)
            
        # --- Draw ---
        BeginDrawing()
        ClearBackground(DARKGRAY) 
        
        game.draw()
        
        EndDrawing()

    CloseWindow()

if __name__ == "__main__":
    main()
