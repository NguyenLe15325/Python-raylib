import random
from raylib import *

# --- Game Object Classes ---

class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        # Speeds are now defined as PIXELS PER SECOND
        self.speed_x = speed_x 
        self.speed_y = speed_y

    def draw(self):
        DrawCircle(int(self.x), int(self.y), self.radius, WHITE)

    def update(self, screen_width, screen_height, player_paddle, cpu_paddle, delta_time):
        # Movement: Multiply speed (pixels/sec) by delta_time (sec) to get distance (pixels)
        self.x += self.speed_x * delta_time
        self.y += self.speed_y * delta_time

        # Wall Collision (Top/Bottom)
        if self.y + self.radius >= screen_height or self.y - self.radius <= 0:
            self.speed_y *= -1

        # Paddle Collision (Player & CPU)
        if CheckCollisionCircleRec((self.x, self.y), self.radius, player_paddle.get_rect()) or \
           CheckCollisionCircleRec((self.x, self.y), self.radius, cpu_paddle.get_rect()):
            self.speed_x *= -1
            # Optional: Add slight speed boost on hit (e.g., 10%)
            self.speed_x *= 1.1 

    def reset_ball(self, screen_width, screen_height):
        self.x = screen_width // 2
        self.y = screen_height // 2
        # Use initial speed values
        initial_speed = 300 # Pixels per second
        self.speed_x = random.choice([-initial_speed, initial_speed])
        self.speed_y = random.choice([-initial_speed, initial_speed])


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Speed is defined as PIXELS PER SECOND
        self.speed = speed

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


class PlayerPaddle(Paddle):
    def update(self, screen_height, delta_time):
        # Movement is controlled by speed * delta_time
        if IsKeyDown(KEY_UP) or IsKeyDown(KEY_W):
            self.y -= self.speed * delta_time
        if IsKeyDown(KEY_DOWN) or IsKeyDown(KEY_S):
            self.y += self.speed * delta_time
        
        self.clamp_movement(screen_height)


class CpuPaddle(Paddle):
    def update(self, screen_height, ball, delta_time):
        center_y = self.y + self.height // 2
        
        # Simple AI: Move towards the ball's Y position
        if center_y < ball.y:
            # Calculate distance to move, clamped by max speed * delta_time
            move_amount = min(self.speed * delta_time, ball.y - center_y)
            self.y += move_amount
            
        elif center_y > ball.y:
            # Calculate distance to move, clamped by max speed * delta_time
            move_amount = min(self.speed * delta_time, center_y - ball.y)
            self.y -= move_amount
            
        self.clamp_movement(screen_height)


# --- Main Game Logic ---

def main():
    # --- Initialization ---
    screen_width = 1000
    screen_height = 600
    target_fps = 60
    
    # Use .encode('utf-8') for C-style string compatibility
    InitWindow(screen_width, screen_height, "Raylib Pong".encode('utf-8'))
    SetTargetFPS(target_fps)

    # Paddle and Ball Speeds (PIXELS PER SECOND)
    ball_initial_speed = 300  
    paddle_speed = 400
    
    # Paddle dimensions
    paddle_width = 15
    paddle_height = 90
    
    # Create Game Objects
    player_paddle = PlayerPaddle(20, screen_height // 2 - paddle_height // 2, 
                                 paddle_width, paddle_height, paddle_speed)
    
    cpu_paddle = CpuPaddle(screen_width - 20 - paddle_width, screen_height // 2 - paddle_height // 2, 
                           paddle_width, paddle_height, paddle_speed)
                           
    ball = Ball(screen_width // 2, screen_height // 2, 10, ball_initial_speed, ball_initial_speed)
    ball.reset_ball(screen_width, screen_height) # Set random initial direction

    player_score = 0
    cpu_score = 0

    # --- Game Loop ---
    while not WindowShouldClose():
        # Get the time elapsed since the last frame (our delta_time)
        delta_time = GetFrameTime()
        
        # --- Update (Game Logic) ---
        player_paddle.update(screen_height, delta_time)
        cpu_paddle.update(screen_height, ball, delta_time)
        ball.update(screen_width, screen_height, player_paddle, cpu_paddle, delta_time)

        # Scoring Logic
        if ball.x + ball.radius >= screen_width:
            player_score += 1
            ball.reset_ball(screen_width, screen_height)
            
        if ball.x - ball.radius <= 0:
            cpu_score += 1
            ball.reset_ball(screen_width, screen_height)

        # --- Draw (Rendering) ---
        BeginDrawing()

        ClearBackground(BLACK) 
        
        # Draw center line
        DrawLine(screen_width // 2, 0, screen_width // 2, screen_height, WHITE)
        
        # Draw Objects
        player_paddle.draw()
        cpu_paddle.draw()
        ball.draw()
        
        # Draw Score (Ensure text is encoded to bytes)
        score_text = f"{player_score}  |  {cpu_score}"
        score_text_bytes = score_text.encode('utf-8')
        
        text_width = MeasureText(score_text_bytes, 40)
        
        DrawText(score_text_bytes, 
                 screen_width // 2 - text_width // 2, 
                 20, 40, WHITE)

        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()