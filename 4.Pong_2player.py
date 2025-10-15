import random
from raylib import *

# --- Game Object Classes ---

class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        # Speeds are defined as PIXELS PER SECOND
        self.speed_x = speed_x 
        self.speed_y = speed_y

    def draw(self):
        DrawCircle(int(self.x), int(self.y), self.radius, WHITE)

    def update(self, screen_width, screen_height, player1_paddle, player2_paddle, delta_time):
        # Movement: Multiply speed (pixels/sec) by delta_time (sec) to get distance (pixels)
        self.x += self.speed_x * delta_time
        self.y += self.speed_y * delta_time

        # Wall Collision (Top/Bottom)
        if self.y + self.radius >= screen_height or self.y - self.radius <= 0:
            self.speed_y *= -1

        # Paddle Collision (Player 1 & Player 2)
        if CheckCollisionCircleRec((self.x, self.y), self.radius, player1_paddle.get_rect()) or \
           CheckCollisionCircleRec((self.x, self.y), self.radius, player2_paddle.get_rect()):
            self.speed_x *= -1
            # Add slight speed boost on hit (10%)
            self.speed_x *= 1.1 

    def reset_ball(self, screen_width, screen_height, initial_speed):
        self.x = screen_width // 2
        self.y = screen_height // 2
        # Use initial speed values
        self.speed_x = random.choice([-initial_speed, initial_speed])
        self.speed_y = random.choice([-initial_speed, initial_speed])


class Paddle:
    def __init__(self, x, y, width, height, speed, up_key, down_key):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Speed is defined as PIXELS PER SECOND
        self.speed = speed 
        self.up_key = up_key
        self.down_key = down_key

    def draw(self):
        DrawRectangle(int(self.x), int(self.y), self.width, self.height, WHITE)

    def get_rect(self):
        # Raylib expects an integer tuple for the Rectangle check
        return (int(self.x), int(self.y), self.width, self.height)

    def clamp_movement(self, screen_height):
        # Keep paddle within screen bounds
        if self.y <= 0:
            self.y = 0
        if self.y + self.height >= screen_height:
            self.y = screen_height - self.height

    def update(self, screen_height, delta_time):
        # Movement is controlled by speed * delta_time using instance-specific keys
        if IsKeyDown(self.up_key):
            self.y -= self.speed * delta_time
        if IsKeyDown(self.down_key):
            self.y += self.speed * delta_time
        
        self.clamp_movement(screen_height)


# --- Main Game Logic ---

def main():
    # --- Initialization ---
    screen_width = 1000
    screen_height = 600
    target_fps = 60
    
    # Use .encode('utf-8') for C-style string compatibility
    InitWindow(screen_width, screen_height, "2-Player Raylib Pong".encode('utf-8'))
    SetTargetFPS(target_fps)

    # Player 1 controls (Left Paddle)
    P1_UP = KEY_W
    P1_DOWN = KEY_S
    
    # Player 2 controls (Right Paddle)
    P2_UP = KEY_UP
    P2_DOWN = KEY_DOWN

    # Game speeds (PIXELS PER SECOND)
    ball_initial_speed = 350  # Slightly faster for more fun
    paddle_speed = 500
    
    # Paddle dimensions
    paddle_width = 15
    paddle_height = 90
    
    # Create Game Objects
    player1_paddle = Paddle(20, screen_height // 2 - paddle_height // 2, 
                            paddle_width, paddle_height, paddle_speed, P1_UP, P1_DOWN)
    
    player2_paddle = Paddle(screen_width - 20 - paddle_width, screen_height // 2 - paddle_height // 2, 
                            paddle_width, paddle_height, paddle_speed, P2_UP, P2_DOWN)
                           
    # Ball initialization
    ball = Ball(screen_width // 2, screen_height // 2, 10, ball_initial_speed, ball_initial_speed)
    ball.reset_ball(screen_width, screen_height, ball_initial_speed) 

    player1_score = 0
    player2_score = 0

    # --- Game Loop ---
    while not WindowShouldClose():
        # Get the time elapsed since the last frame (our delta_time)
        delta_time = GetFrameTime()
        
        # --- Update (Game Logic) ---
        player1_paddle.update(screen_height, delta_time)
        player2_paddle.update(screen_height, delta_time)
        
        ball.update(screen_width, screen_height, player1_paddle, player2_paddle, delta_time)

        # Scoring Logic (Player 2 scores if ball passes Player 1, vice versa)
        if ball.x + ball.radius >= screen_width:
            player1_score += 1
            ball.reset_ball(screen_width, screen_height, ball_initial_speed)
            
        if ball.x - ball.radius <= 0:
            player2_score += 1
            ball.reset_ball(screen_width, screen_height, ball_initial_speed)

        # --- Draw (Rendering) ---
        BeginDrawing()

        ClearBackground(BLACK) 
        
        # Draw center line
        DrawLine(screen_width // 2, 0, screen_width // 2, screen_height, WHITE)
        
        # Draw Objects
        player1_paddle.draw()
        player2_paddle.draw()
        ball.draw()
        
        # Draw Score (Ensure text is encoded to bytes for Raylib functions)
        score_text = f"{player1_score}  |  {player2_score}"
        score_text_bytes = score_text.encode('utf-8')
        
        text_width = MeasureText(score_text_bytes, 40)
        
        DrawText(score_text_bytes, 
                 screen_width // 2 - text_width // 2, 
                 20, 40, WHITE)

        # Draw Player Instructions - FIX: Encode strings to bytes
        DrawText("P1: W/S".encode('utf-8'), 50, 560, 20, GRAY)
        DrawText("P2: Up/Down".encode('utf-8'), 800, 560, 20, GRAY)

        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
