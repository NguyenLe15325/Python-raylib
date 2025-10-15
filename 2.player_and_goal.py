# This code is structured to work with the unique installation where 
# the standard 'raylib' and 'pyray' packages coexist and are both required.

# We keep both imports as requested, allowing the code to function in your environment.
from raylib import *
from pyray import *

# --- 1. Game Entity Classes ---

class Player:
    """Represents the user-controlled object."""
    def __init__(self, x, y, size, speed, color):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color 
        self.score = 0
        
    def update(self, screen_width, screen_height):
        """Handle input and update player position."""
        
        # Functions are typically from the 'raylib' import
        delta_time = GetFrameTime() 
        movement = self.speed * delta_time

        if IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D):
            self.x += movement
        if IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A):
            self.x -= movement
        if IsKeyDown(KEY_UP) or IsKeyDown(KEY_W):
            self.y -= movement
        if IsKeyDown(KEY_DOWN) or IsKeyDown(KEY_S):
            self.y += movement
            
        # Keep player within screen bounds
        self.x = max(self.size / 2, min(self.x, screen_width - self.size / 2))
        self.y = max(self.size / 2, min(self.y, screen_height - self.size / 2))

    def draw(self):
        """Draws the player circle."""
        DrawCircle(int(self.x), int(self.y), int(self.size / 2), self.color)
        
    def get_rec(self):
        """Returns the bounding box (Rectangle) for collision checks."""
        # Rectangle structure is resolved by one of the imports
        return Rectangle(
            self.x - self.size / 2, 
            self.y - self.size / 2, 
            self.size, 
            self.size
        )

class Goal:
    """Represents the objective the player must reach."""
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        
    def draw(self):
        """Draws the goal square."""
        DrawRectangle(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
            self.color
        )
        
    def get_rec(self):
        """Returns the bounding box (Rectangle) for collision checks."""
        # Rectangle structure is resolved by one of the imports
        return Rectangle(
            self.x - self.size / 2, 
            self.y - self.size / 2, 
            self.size, 
            self.size
        )

    def reposition_randomly(self, screen_width, screen_height):
        """Move the goal to a new random location on the screen."""
        SetRandomSeed(GetTime()) # Seed the random number generator
        self.x = GetRandomValue(self.size, screen_width - self.size)
        self.y = GetRandomValue(self.size, screen_height - self.size)


# --- 2. Main Game Setup and Loop ---

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
TITLE = b"Raylib OOP Interactive Game" 
FPS = 60

def main():
    # Initialization using PascalCase functions
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE) 
    SetTargetFPS(FPS)

    player = Player(
        x=50, 
        y=SCREEN_HEIGHT / 2, 
        size=40, 
        speed=300, 
        color=BLUE # Constants are all caps
    )
    
    goal = Goal(
        x=SCREEN_WIDTH - 50, 
        y=SCREEN_HEIGHT / 2, 
        size=50, 
        color=GREEN
    )

    while not WindowShouldClose():
        
        # 1. Update (Logic)
        player.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Check for collision
        if CheckCollisionRecs(player.get_rec(), goal.get_rec()):
            goal.reposition_randomly(SCREEN_WIDTH, SCREEN_HEIGHT)
            player.score += 1
            # Structure constructor
            player.color = Color(255, 100, 0, 255) 
        else:
            player.color = BLUE

        # 2. Draw
        BeginDrawing()
        
        ClearBackground(RAYWHITE)
        
        goal.draw()
        player.draw()
        
        score_text = b"Score: " + str(player.score).encode('utf-8')
        DrawText(score_text, 10, 10, 30, DARKGRAY)
        DrawText(b"Use WASD or Arrows to move!", 10, SCREEN_HEIGHT - 30, 20, MAROON)

        DrawFPS(SCREEN_WIDTH - 90, 10)

        EndDrawing()

    CloseWindow()

if __name__ == '__main__':
    main()
