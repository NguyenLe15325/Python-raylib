from raylib import *

# --- 1. Game Entity Class ---

class Ball:
    """
    Represents a simple bouncing ball in the game, handling its 
    position, movement, and drawing.
    """
    def __init__(self, x, y, radius, speed_x, speed_y, color):
        # Data/Attributes
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color

    def update(self, screen_width, screen_height):
        """Updates the ball's position and handles screen edge collisions."""
        
        # Update position based on current speed
        # Using GetFrameTime() helps achieve frame-rate independent movement
        delta_time = GetFrameTime()
        self.x += self.speed_x * delta_time
        self.y += self.speed_y * delta_time

        # Behavior: Check for screen edges and bounce
        
        # Horizontal bounce
        if self.x + self.radius >= screen_width or self.x - self.radius <= 0:
            self.speed_x *= -1  # Reverse direction
            # Keep ball within bounds to prevent sticking
            if self.x - self.radius <= 0:
                self.x = self.radius
            elif self.x + self.radius >= screen_width:
                self.x = screen_width - self.radius
            
        # Vertical bounce
        if self.y + self.radius >= screen_height or self.y - self.radius <= 0:
            self.speed_y *= -1  # Reverse direction
            # Keep ball within bounds to prevent sticking
            if self.y - self.radius <= 0:
                self.y = self.radius
            elif self.y + self.radius >= screen_height:
                self.y = screen_height - self.radius
            
    def draw(self):
        """Draws the ball on the screen."""
        # DrawCircle requires integer coordinates
        DrawCircle(int(self.x), int(self.y), self.radius, self.color)


# --- 2. Main Game Setup and Loop ---

# Screen Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
# The title MUST be a byte string (b"...") for InitWindow to avoid the TypeError
TITLE = b"Raylib OOP Bouncing Ball Single File" 
FPS = 60

def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(FPS)

    # Instantiate our Ball object (Note: speed is higher to account for delta_time)
    my_ball = Ball(
        x=SCREEN_WIDTH / 2,
        y=SCREEN_HEIGHT / 2,
        radius=25,
        speed_x=200, # pixels per second
        speed_y=150, # pixels per second
        color=GOLD
    )

    # --- Main Game Loop ---
    while not WindowShouldClose():
        
        # --- 1. Update (Logic) ---
        # Delegate the update logic to the Ball object
        my_ball.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- 2. Draw ---
        BeginDrawing()
        
        ClearBackground(RAYWHITE)
        
        # Delegate the drawing to the Ball object
        my_ball.draw()
        
        DrawText(
            b"OOP Raylib Example: Press ESC to close.", # Text must also be a byte string
            10, 
            10, 
            20, 
            DARKGRAY
        )

        # Show current FPS for debugging
        DrawFPS(SCREEN_WIDTH - 90, 10)

        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == '__main__':
    main()