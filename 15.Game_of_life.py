import random
from raylib import *
from pyray import *

# --- Simulation Constants ---
TITLE = b"Conway's Game of Life"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
CELL_SIZE = 10
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = (SCREEN_HEIGHT - 50) // CELL_SIZE # Reserve 50px for the HUD
SIM_SPEED_DELAY = 0.1 # Seconds between generations (10 generations per second)

# Raylib Mouse Button Constants (Defined explicitly to prevent Linter warnings)
MOUSE_LEFT_BUTTON = 0
MOUSE_RIGHT_BUTTON = 1

# --- Colors ---
COLOR_BACKGROUND = Color(30, 30, 40, 255) # Dark Blue-Gray
COLOR_LIVE = Color(144, 238, 144, 255)    # Light Green
COLOR_DEAD = Color(40, 40, 50, 255)       # Very Dark Gray
COLOR_GRID_LINES = Color(50, 50, 60, 255) # Slightly darker for grid
COLOR_HUD = Color(20, 20, 30, 255)        # Black-Blue

# --- Game State ---
grid = []
is_paused = True
time_since_last_update = 0.0
generation_count = 0

# --- Helper Functions ---

def init_grid():
    """Initializes the grid with all dead cells."""
    global grid, generation_count, is_paused
    grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    generation_count = 0
    is_paused = True

def randomize_grid(density=0.2):
    """Fills the grid randomly based on density (0.0 to 1.0)."""
    global grid, generation_count, is_paused
    init_grid()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if random.random() < density:
                grid[r][c] = 1 # Live cell
    generation_count = 0
    is_paused = True

def count_neighbors(r, c):
    """Counts the number of live neighbors for a cell at (r, c)."""
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            # Skip the cell itself
            if dr == 0 and dc == 0:
                continue
            
            nr, nc = r + dr, c + dc
            
            # Use toroidal (wrapping) boundaries
            nr = nr % GRID_ROWS
            nc = nc % GRID_COLS
            
            # Check if the neighbor is alive
            if grid[nr][nc] == 1:
                count += 1
    return count

def update_generation():
    """Calculates the next generation based on the four rules."""
    global grid, generation_count
    
    # Create a new grid for the next state to avoid using intermediate results
    new_grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            neighbors = count_neighbors(r, c)
            current_state = grid[r][c]
            
            # Conway's Rules
            if current_state == 1:
                # Rule 1 & 3: Survival or Death by under/overpopulation
                if neighbors == 2 or neighbors == 3:
                    new_grid[r][c] = 1 # Survives
                else:
                    new_grid[r][c] = 0 # Dies
            else:
                # Rule 4: Reproduction (Birth)
                if neighbors == 3:
                    new_grid[r][c] = 1 # Becomes live
                else:
                    new_grid[r][c] = 0 # Stays dead
                    
    grid = new_grid
    generation_count += 1

def handle_manual_drawing():
    """Allows user to toggle cell state with the mouse."""
    if not is_paused:
        return

    mouse_x, mouse_y = GetMouseX(), GetMouseY()
    
    # Check if mouse is within the grid area
    if 0 <= mouse_x < GRID_COLS * CELL_SIZE and 0 <= mouse_y < GRID_ROWS * CELL_SIZE:
        c = mouse_x // CELL_SIZE
        r = mouse_y // CELL_SIZE
        
        # Left click to set cell to live, right click to kill
        if IsMouseButtonDown(MOUSE_LEFT_BUTTON):
            grid[r][c] = 1
        elif IsMouseButtonDown(MOUSE_RIGHT_BUTTON):
            grid[r][c] = 0

# --- Main Functions ---

def update(dt):
    """Handles time and input updates."""
    global is_paused, time_since_last_update
    
    # Toggle Pause/Start
    if IsKeyPressed(KEY_SPACE):
        is_paused = not is_paused
        
    # Reset Grid to empty
    if IsKeyPressed(KEY_R):
        init_grid()
        
    # Randomize Grid
    if IsKeyPressed(KEY_A):
        randomize_grid()

    # Manual Drawing
    handle_manual_drawing()
        
    # Run the simulation if not paused
    if not is_paused:
        time_since_last_update += dt
        if time_since_last_update >= SIM_SPEED_DELAY:
            update_generation()
            time_since_last_update = 0.0

def draw():
    """Draws the grid, cells, and HUD."""
    
    # 1. Draw Grid Lines and Cells
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            
            color = COLOR_LIVE if grid[r][c] == 1 else COLOR_DEAD
            
            DrawRectangle(x, y, CELL_SIZE, CELL_SIZE, color)
            
            # Draw thin grid lines
            DrawRectangleLines(x, y, CELL_SIZE, CELL_SIZE, COLOR_GRID_LINES)
            
    # 2. Draw HUD
    hud_y = GRID_ROWS * CELL_SIZE
    DrawRectangle(0, hud_y, SCREEN_WIDTH, 50, COLOR_HUD)

    status_text = b""
    if is_paused:
        status_text = b"[PAUSED] - Edit Grid or Press SPACE to Start"
    else:
        status_text = b"[RUNNING] - Press SPACE to Pause"

    DrawText(status_text, 10, hud_y + 10, 20, RAYWHITE)
    
    gen_text = f"Generation: {generation_count}".encode('utf-8')
    DrawText(gen_text, 10, hud_y + 30, 15, RAYWHITE)
    
    controls_text = b"R: Reset | A: Randomize | L-Click: Draw | R-Click: Erase"
    controls_w = MeasureText(controls_text, 15)
    
    # Draw controls centered on the right side
    DrawText(controls_text, SCREEN_WIDTH - controls_w - 10, hud_y + 20, 15, RAYWHITE)


def main():
    """Main game loop and initialization."""
    
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(60) # Main loop runs at 60 FPS, but simulation update is slower
    
    # Initialize the grid with a random pattern for immediate testing
    randomize_grid(density=0.3) 
    
    while not WindowShouldClose():
        dt = GetFrameTime()
        
        # --- Update ---
        update(dt)
            
        # --- Draw ---
        BeginDrawing()
        ClearBackground(COLOR_BACKGROUND) 
        
        draw()
        
        EndDrawing()

    CloseWindow()

if __name__ == "__main__":
    main()
