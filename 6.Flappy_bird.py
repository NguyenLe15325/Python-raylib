import random
from raylib import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 1800.0          # Downward acceleration (pixels/s/s)
FLAP_VELOCITY = -500.0    # Initial upward velocity on flap (pixels/s)
PIPE_SPEED = 250.0        # Horizontal speed of pipes (pixels/s)
PIPE_WIDTH = 70
PIPE_GAP_HEIGHT = 180
PIPE_SPAWN_INTERVAL = 1.6 # Time between pipe spawns (seconds)
BIRD_RADIUS = 20

# --- Game Object Classes ---

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BIRD_RADIUS
        self.velocity_y = 0.0
        self.color = YELLOW
        self.is_alive = True

    def draw(self):
        DrawCircle(int(self.x), int(self.y), self.radius, self.color)
        # Simple eye
        DrawCircle(int(self.x + 5), int(self.y - 5), 4, BLACK)

    def update(self, delta_time):
        if not self.is_alive:
            return

        # 1. Apply Gravity: Gravity accelerates velocity
        self.velocity_y += GRAVITY * delta_time
        
        # 2. Apply Velocity: Velocity moves position
        self.y += self.velocity_y * delta_time

        # Clamp max fall speed (optional, prevents ball from falling infinitely fast)
        if self.velocity_y > 1000:
            self.velocity_y = 1000

        # Keep bird within top boundary
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.velocity_y = 0

    def flap(self):
        self.velocity_y = FLAP_VELOCITY

    def check_floor_collision(self, screen_height):
        if self.y + self.radius >= screen_height:
            self.y = screen_height - self.radius
            self.is_alive = False
            return True
        return False


class Pipe:
    def __init__(self, x, gap_center_y, width, gap_height):
        self.x = x
        self.width = width
        self.gap_height = gap_height
        self.gap_center_y = gap_center_y
        self.scored = False

        # Top pipe starts at 0 and ends right before the gap
        self.top_pipe_height = self.gap_center_y - (self.gap_height / 2)
        
        # Bottom pipe starts after the gap and extends to the floor
        self.bottom_pipe_y = self.gap_center_y + (self.gap_height / 2)
        self.bottom_pipe_height = SCREEN_HEIGHT - self.bottom_pipe_y

    def draw(self):
        # Top Pipe
        DrawRectangle(int(self.x), 0, self.width, int(self.top_pipe_height), DARKGREEN)
        # Bottom Pipe
        DrawRectangle(int(self.x), int(self.bottom_pipe_y), self.width, int(self.bottom_pipe_height), DARKGREEN)
        # Outline (for better look)
        DrawRectangleLines(int(self.x), 0, self.width, int(self.top_pipe_height), BLACK)
        DrawRectangleLines(int(self.x), int(self.bottom_pipe_y), self.width, int(self.bottom_pipe_height), BLACK)

    def update(self, delta_time):
        # Move pipe to the left
        self.x -= PIPE_SPEED * delta_time

    def get_rects(self):
        # Returns the collision rectangles for the top and bottom pipe
        return [
            # Top Rect (x, y, width, height)
            (self.x, 0, self.width, self.top_pipe_height),
            # Bottom Rect (x, y, width, height)
            (self.x, self.bottom_pipe_y, self.width, self.bottom_pipe_height)
        ]

    def check_collision(self, bird):
        rects = self.get_rects()
        for rect in rects:
            if CheckCollisionCircleRec((bird.x, bird.y), bird.radius, rect):
                return True
        return False


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib Flappy Bird".encode('utf-8'))
    SetTargetFPS(60)
    
    # Game State Variables
    bird = Bird(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2)
    pipes = []
    game_state = "READY" # READY, PLAYING, GAME_OVER
    pipe_timer = PIPE_SPAWN_INTERVAL
    score = 0

    # --- Game Loop ---
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        
        # --- Update ---
        if game_state == "READY":
            # Start game on space or click
            if IsKeyPressed(KEY_SPACE) or IsMouseButtonPressed(MOUSE_BUTTON_LEFT): # Updated constant
                bird.flap()
                game_state = "PLAYING"
            
        elif game_state == "PLAYING":
            # Check for jump input WHILE playing
            if IsKeyPressed(KEY_SPACE) or IsMouseButtonPressed(MOUSE_BUTTON_LEFT): # Updated constant
                bird.flap()
                
            bird.update(delta_time)
            
            # --- Pipe Management and Spawning ---
            pipe_timer -= delta_time
            if pipe_timer <= 0:
                # Spawn a new pipe: gap center must be far from top/bottom
                min_gap_y = PIPE_GAP_HEIGHT
                max_gap_y = SCREEN_HEIGHT - PIPE_GAP_HEIGHT
                new_gap_y = random.uniform(min_gap_y, max_gap_y)
                
                pipes.append(Pipe(SCREEN_WIDTH, new_gap_y, PIPE_WIDTH, PIPE_GAP_HEIGHT))
                pipe_timer = PIPE_SPAWN_INTERVAL # Reset timer

            # Update pipes and check collisions
            pipes_to_remove = []
            for pipe in pipes:
                pipe.update(delta_time)

                # Check collision with bird
                if pipe.check_collision(bird):
                    bird.is_alive = False

                # Scoring: Check if bird passed the pipe's X position
                if not pipe.scored and pipe.x + PIPE_WIDTH < bird.x - bird.radius:
                    score += 1
                    pipe.scored = True
                
                # Check if pipe is off-screen
                if pipe.x + PIPE_WIDTH < 0:
                    pipes_to_remove.append(pipe)
            
            # Remove off-screen pipes
            for pipe in pipes_to_remove:
                pipes.remove(pipe)

            # Check for ground collision
            if bird.check_floor_collision(SCREEN_HEIGHT) or not bird.is_alive:
                game_state = "GAME_OVER"
        
        elif game_state == "GAME_OVER":
            if IsKeyPressed(KEY_ENTER) or IsKeyPressed(KEY_SPACE):
                # --- FIX: Instead of calling main() recursively, reset state variables ---
                
                # 1. Reset bird position and status
                bird.x = SCREEN_WIDTH / 4
                bird.y = SCREEN_HEIGHT / 2
                bird.velocity_y = 0.0
                bird.is_alive = True
                
                # 2. Clear pipes and reset timers/score
                pipes.clear()
                pipe_timer = PIPE_SPAWN_INTERVAL
                score = 0
                
                # 3. Go back to ready state
                game_state = "READY"
                # Removed 'break' and recursive 'main()' call
                


        # --- Draw ---
        BeginDrawing()
        ClearBackground(SKYBLUE)
        
        # Draw Pipes
        for pipe in pipes:
            pipe.draw()
            
        # Draw Ground (always draw last before bird to look layered)
        DrawRectangle(0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30, BROWN)
        
        # Draw Bird
        bird.draw()
        
        # Draw Score
        score_text = f"Score: {score}"
        score_text_bytes = score_text.encode('utf-8')
        DrawText(score_text_bytes, 10, 10, 30, WHITE)

        # Draw Game State Messages
        if game_state == "READY":
            message = "Press SPACE or Click to Start".encode('utf-8')
            DrawText(message, SCREEN_WIDTH // 2 - MeasureText(message, 40) // 2, 
                     SCREEN_HEIGHT // 2, 40, WHITE)
        elif game_state == "GAME_OVER":
            message_1 = "GAME OVER".encode('utf-8')
            message_2 = f"Final Score: {score}".encode('utf-8')
            message_3 = "Press ENTER to Restart".encode('utf-8')
            
            DrawText(message_1, SCREEN_WIDTH // 2 - MeasureText(message_1, 60) // 2, 
                     SCREEN_HEIGHT // 2 - 80, 60, RED)
            DrawText(message_2, SCREEN_WIDTH // 2 - MeasureText(message_2, 40) // 2, 
                     SCREEN_HEIGHT // 2 + 10, 40, WHITE)
            DrawText(message_3, SCREEN_WIDTH // 2 - MeasureText(message_3, 20) // 2, 
                     SCREEN_HEIGHT // 2 + 70, 20, GRAY)


        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
