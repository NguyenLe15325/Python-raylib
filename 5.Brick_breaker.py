import random
from raylib import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_SPEED = 500  # Pixels per second
BALL_SPEED = 450    # Pixels per second
PADDLE_HEIGHT = 20
PADDLE_WIDTH = 100

# --- Game Object Classes ---

class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.active = True

    def draw(self):
        DrawCircle(int(self.x), int(self.y), self.radius, WHITE)

    def update(self, delta_time):
        if not self.active:
            return

        # Movement: Speed * delta_time
        self.x += self.speed_x * delta_time
        self.y += self.speed_y * delta_time

        # Wall Collision (Left/Right)
        if self.x + self.radius >= SCREEN_WIDTH or self.x - self.radius <= 0:
            self.speed_x *= -1
            
        # Wall Collision (Top)
        if self.y - self.radius <= 0:
            self.speed_y *= -1
            
        # Wall Collision (Bottom - Game Over Zone)
        if self.y + self.radius >= SCREEN_HEIGHT:
            self.active = False # Signal game over

    def check_paddle_collision(self, paddle):
        # Raylib CheckCollisionCircleRec uses a tuple for the rectangle
        if CheckCollisionCircleRec((self.x, self.y), self.radius, paddle.get_rect()):
            # Only bounce if moving downwards (prevents sticky bug on side hit)
            if self.speed_y > 0:
                self.speed_y *= -1
                
                # Simple angle adjustment based on hit position
                hit_pos_x = self.x - (paddle.x + PADDLE_WIDTH / 2)
                self.speed_x = hit_pos_x * 5 # Factor to control angle (higher value = steeper angle)


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def draw(self):
        DrawRectangle(int(self.x), int(self.y), self.width, self.height, GREEN)

    def get_rect(self):
        # Used for collision checks
        return (int(self.x), int(self.y), self.width, self.height)

    def update(self, delta_time):
        # Movement
        if IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A):
            self.x -= self.speed * delta_time
        if IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D):
            self.x += self.speed * delta_time
        
        # Clamp Movement
        if self.x <= 0:
            self.x = 0
        if self.x + self.width >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width


class Brick:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.active = True

    def draw(self):
        if self.active:
            DrawRectangle(int(self.x), int(self.y), self.width, self.height, self.color)
            DrawRectangleLines(int(self.x), int(self.y), self.width, self.height, BLACK) # Outline

    def get_rect(self):
        return (int(self.x), int(self.y), self.width, self.height)


def create_bricks(rows, cols, offset_x, offset_y, brick_width, brick_height):
    """Generates the grid of bricks."""
    bricks = []
    colors = [RED, ORANGE, YELLOW, GREEN, SKYBLUE, BLUE]
    
    for r in range(rows):
        for c in range(cols):
            x = offset_x + c * (brick_width + 5)
            y = offset_y + r * (brick_height + 5)
            color = colors[r % len(colors)]
            
            # Ensure brick is within screen bounds
            if x + brick_width <= SCREEN_WIDTH and y + brick_height <= SCREEN_HEIGHT / 2:
                 bricks.append(Brick(x, y, brick_width, brick_height, color))
    return bricks


def check_brick_collision(ball, bricks):
    """Handles collision between the ball and all active bricks."""
    bricks_hit = []
    
    for brick in bricks:
        if brick.active:
            if CheckCollisionCircleRec((ball.x, ball.y), ball.radius, brick.get_rect()):
                brick.active = False
                bricks_hit.append(brick)
                
                # --- Collision Bounce Logic ---
                # This simple logic reverses Y speed, assuming the bounce is vertical
                # For more complex collision, you would determine if the hit was vertical or horizontal.
                ball.speed_y *= -1 
                
                # Slightly increase ball speed for difficulty progression
                ball.speed_x *= 1.01 
                ball.speed_y *= 1.01 
                
                return True # Stop after hitting one brick per frame

    return False


# --- Main Game Loop ---
def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib Brick Breaker".encode('utf-8'))
    SetTargetFPS(60)

    # Game Objects Setup
    paddle = Paddle(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, 
                    SCREEN_HEIGHT - PADDLE_HEIGHT - 30, 
                    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED)
    
    ball = Ball(SCREEN_WIDTH // 2, paddle.y - 30, 10, 
                random.choice([-BALL_SPEED, BALL_SPEED]), -BALL_SPEED)
    
    # Brick Layout
    BRICK_ROWS = 5
    BRICK_COLS = 10
    BRICK_W = 70
    BRICK_H = 20
    BRICKS_OFFSET_X = 50
    BRICKS_OFFSET_Y = 50
    bricks = create_bricks(BRICK_ROWS, BRICK_COLS, BRICKS_OFFSET_X, BRICKS_OFFSET_Y, BRICK_W, BRICK_H)
    
    game_state = "READY" # READY, PLAYING, GAME_OVER, WIN

    # --- Game Loop ---
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        
        # --- Update ---
        if game_state == "READY":
            if IsKeyPressed(KEY_SPACE):
                game_state = "PLAYING"
            # Keep ball centered on paddle
            ball.x = paddle.x + PADDLE_WIDTH // 2
            
        elif game_state == "PLAYING":
            paddle.update(delta_time)
            ball.update(delta_time)
            
            ball.check_paddle_collision(paddle)
            check_brick_collision(ball, bricks)
            
            # Check for Game Over (ball fell off bottom)
            if not ball.active:
                game_state = "GAME_OVER"

            # Check for Win Condition (all bricks destroyed)
            if all(not brick.active for brick in bricks):
                game_state = "WIN"

        elif game_state == "GAME_OVER" or game_state == "WIN":
            if IsKeyPressed(KEY_ENTER):
                # Reset game state and objects
                main()
                break # Exit current loop to restart main()


        # --- Draw ---
        BeginDrawing()
        ClearBackground(BLACK)
        
        # Draw all objects
        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()
        
        # Draw game state messages
        if game_state == "READY":
            message = "Press SPACE to Start".encode('utf-8')
            DrawText(message, SCREEN_WIDTH // 2 - MeasureText(message, 40) // 2, 
                     SCREEN_HEIGHT // 2, 40, WHITE)

        elif game_state == "GAME_OVER":
            message = "GAME OVER (Press ENTER to Restart)".encode('utf-8')
            DrawText(message, SCREEN_WIDTH // 2 - MeasureText(message, 40) // 2, 
                     SCREEN_HEIGHT // 2, 40, RED)

        elif game_state == "WIN":
            message = "YOU WIN! (Press ENTER to Restart)".encode('utf-8')
            DrawText(message, SCREEN_WIDTH // 2 - MeasureText(message, 40) // 2, 
                     SCREEN_HEIGHT // 2, 40, GOLD)
        
        # Instructions
        DrawText("Controls: A/D or Left/Right".encode('utf-8'), 10, SCREEN_HEIGHT - 25, 15, GRAY)
        
        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
