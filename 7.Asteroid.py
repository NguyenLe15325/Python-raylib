import random
import math
from raylib import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SHIP_SIZE = 15          # Distance from center to vertex
ROTATION_SPEED = 200.0  # Degrees per second
THRUST_ACCEL = 150.0    # Acceleration rate (pixels/s/s)
MAX_SPEED = 400.0       # Max velocity for the ship
BULLET_SPEED = 600.0
FIRE_RATE = 0.2         # Seconds between shots

# Asteroid Sizes (Radius and points)
ASTEROID_SIZES = {
    3: (50, 20),  # Large: (radius, points)
    2: (30, 50),  # Medium
    1: (15, 100)  # Small
}

# --- Game Object Classes ---

class Entity:
    """Base class for Ship, Bullet, and Asteroid to handle common movement and screen wrapping."""
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_active = True

    def update(self, delta_time):
        if not self.is_active:
            return
            
        # Apply velocity to position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

        # Screen Wrapping
        if self.x > SCREEN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = SCREEN_WIDTH
            
        if self.y > SCREEN_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = SCREEN_HEIGHT

class Ship(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 0.0, 0.0)
        self.rotation = 90.0 # Facing UP initially (90 degrees in Raylib's system)
        self.thrusting = False
        self.radius = SHIP_SIZE
        self.can_fire_timer = 0.0
        self.lives = 3

    def update(self, delta_time):
        super().update(delta_time)
        
        # --- 1. Rotation ---
        if IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A):
            self.rotation -= ROTATION_SPEED * delta_time
        if IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D):
            self.rotation += ROTATION_SPEED * delta_time
            
        # Normalize rotation (keep it between 0 and 360)
        self.rotation %= 360.0

        # --- 2. Thrust (Acceleration) ---
        self.thrusting = False
        if IsKeyDown(KEY_UP) or IsKeyDown(KEY_W):
            self.thrusting = True
            
            # Convert rotation degree to radians for trig functions (math.cos/sin)
            # Ship rotation is 90 degrees UP (0 is right, 90 is up)
            # We need to offset by -90 if we want 0 to be right: (self.rotation - 90)
            # However, Raylib's DrawTriangle function doesn't use this standard.
            # Let's use the standard unit circle where 0 is right and grow counter-clockwise.
            # Since the ship points forward at 90 deg, we use (self.rotation - 90) to align with standard math.
            
            angle_rad = math.radians(self.rotation - 90)
            
            # Calculate thrust components
            thrust_x = THRUST_ACCEL * math.cos(angle_rad) * delta_time
            thrust_y = THRUST_ACCEL * math.sin(angle_rad) * delta_time
            
            self.vx += thrust_x
            self.vy += thrust_y

        # --- 3. Deceleration / Friction (Optional, but makes it easier to control) ---
        if not self.thrusting:
            self.vx *= (1.0 - 0.5 * delta_time) # 50% deceleration per second
            self.vy *= (1.0 - 0.5 * delta_time)
            
        # Clamp velocity to max speed
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > MAX_SPEED:
            scale = MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        # Update fire timer
        if self.can_fire_timer > 0:
            self.can_fire_timer -= delta_time

    def fire_bullet(self):
        if self.can_fire_timer <= 0:
            # Calculate bullet direction based on ship rotation
            angle_rad = math.radians(self.rotation - 90)
            
            # Start position: slightly ahead of the ship's nose
            start_x = self.x + (SHIP_SIZE + 5) * math.cos(angle_rad)
            start_y = self.y + (SHIP_SIZE + 5) * math.sin(angle_rad)
            
            # Bullet velocity vector
            bv_x = BULLET_SPEED * math.cos(angle_rad)
            bv_y = BULLET_SPEED * math.sin(angle_rad)
            
            self.can_fire_timer = FIRE_RATE
            return Bullet(start_x, start_y, bv_x + self.vx, bv_y + self.vy) # Add ship's velocity

    def draw(self):
        # Raylib DrawPolyEx works well for triangles with rotation
        # Draw a simple triangle centered at (self.x, self.y) with size=SHIP_SIZE and rotation=self.rotation
        
        # Use a classic triangle outline for the Asteroids look
        DrawPolyLinesEx((self.x, self.y), 3, SHIP_SIZE, self.rotation, 2, WHITE)
        
        # Draw the engine flame if thrusting
        if self.thrusting:
            # Flame position is behind the ship
            angle_rad = math.radians(self.rotation - 90 + 180) # Opposite direction
            flame_x = self.x + (SHIP_SIZE - 5) * math.cos(angle_rad)
            flame_y = self.y + (SHIP_SIZE - 5) * math.sin(angle_rad)
            DrawCircle(int(flame_x), int(flame_y), 3, RED)


class Bullet(Entity):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy)
        self.radius = 2
        self.lifetime = 2.0 # Bullet disappears after 2 seconds

    def update(self, delta_time):
        super().update(delta_time)
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.is_active = False

    def draw(self):
        if self.is_active:
            DrawCircle(int(self.x), int(self.y), self.radius, YELLOW)


class Asteroid(Entity):
    def __init__(self, x, y, vx, vy, size_level):
        super().__init__(x, y, vx, vy)
        self.size_level = size_level # 3=Large, 2=Medium, 1=Small
        self.radius, self.points = ASTEROID_SIZES[size_level]
        self.color = GRAY
        
    def draw(self):
        if self.is_active:
            # Draw a simple circle for the asteroid, larger for bigger ones
            DrawCircleLines(int(self.x), int(self.y), self.radius, self.color)
            DrawCircle(int(self.x), int(self.y), 2, self.color) # Center dot for visibility

    @staticmethod
    def create_small_asteroids(asteroid):
        """Creates 2-3 smaller asteroids when a larger one is destroyed."""
        new_asteroids = []
        if asteroid.size_level > 1:
            new_size = asteroid.size_level - 1
            
            # Spawn 2 new asteroids with randomized velocity
            for _ in range(2):
                # Random angle and speed
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(50, 200)
                
                new_vx = speed * math.cos(angle)
                new_vy = speed * math.sin(angle)
                
                # Spawn slightly offset from parent position
                new_asteroids.append(Asteroid(asteroid.x + random.randint(-5, 5), 
                                              asteroid.y + random.randint(-5, 5), 
                                              new_vx, new_vy, new_size))
        return new_asteroids


def spawn_initial_asteroids(num_asteroids, size_level):
    """Initializes a list of large asteroids."""
    asteroids = []
    
    for _ in range(num_asteroids):
        # Spawn near the edges (not near the center where the ship starts)
        edge = random.choice(["left", "right", "top", "bottom"])
        if edge == "left":
            x, y = random.uniform(-50, 0), random.uniform(0, SCREEN_HEIGHT)
        elif edge == "right":
            x, y = random.uniform(SCREEN_WIDTH, SCREEN_WIDTH + 50), random.uniform(0, SCREEN_HEIGHT)
        elif edge == "top":
            x, y = random.uniform(0, SCREEN_WIDTH), random.uniform(-50, 0)
        else: # bottom
            x, y = random.uniform(0, SCREEN_WIDTH), random.uniform(SCREEN_HEIGHT, SCREEN_HEIGHT + 50)
            
        # Give them random, controlled initial velocity
        vx = random.uniform(-100, 100)
        vy = random.uniform(-100, 100)
        
        asteroids.append(Asteroid(x, y, vx, vy, size_level))
        
    return asteroids


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib Asteroids Clone".encode('utf-8'))
    SetTargetFPS(60)

    # Game State Variables
    ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    bullets = []
    asteroids = spawn_initial_asteroids(4, 3) # 4 large asteroids to start
    game_state = "READY" # READY, PLAYING, GAME_OVER
    
    score = 0
    total_points = sum(ASTEROID_SIZES[s][1] for s in ASTEROID_SIZES) * 4 # Max possible score

    # --- Game Loop ---
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        
        # --- Update ---
        if game_state == "READY":
            if IsKeyPressed(KEY_SPACE) or IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                game_state = "PLAYING"
            
        elif game_state == "PLAYING":
            # Player Input
            ship.update(delta_time)
            
            if IsKeyPressed(KEY_SPACE) or IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                new_bullet = ship.fire_bullet()
                if new_bullet:
                    bullets.append(new_bullet)

            # Update Bullets
            for bullet in bullets:
                bullet.update(delta_time)

            # Update Asteroids
            for asteroid in asteroids:
                asteroid.update(delta_time)
                
            # --- Collision Detection ---
            
            # 1. Ship vs Asteroid
            if ship.is_active:
                for asteroid in asteroids:
                    if CheckCollisionCircles((ship.x, ship.y), ship.radius, (asteroid.x, asteroid.y), asteroid.radius):
                        ship.lives -= 1
                        if ship.lives <= 0:
                            ship.is_active = False # Final death
                            game_state = "GAME_OVER"
                        else:
                            # Simple respawn after hit
                            ship.x, ship.y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
                            ship.vx, ship.vy = 0.0, 0.0
                            # Destroy the impacting asteroid
                            asteroid.is_active = False
                            
            # 2. Bullet vs Asteroid
            newly_spawned_asteroids = []
            
            for bullet in bullets:
                if not bullet.is_active: continue
                
                for asteroid in asteroids:
                    if not asteroid.is_active: continue
                    
                    if CheckCollisionCircles((bullet.x, bullet.y), bullet.radius, (asteroid.x, asteroid.y), asteroid.radius):
                        bullet.is_active = False # Destroy bullet
                        asteroid.is_active = False # Destroy asteroid
                        score += ASTEROID_SIZES[asteroid.size_level][1] # Add score
                        
                        # Spawn smaller asteroids
                        newly_spawned_asteroids.extend(Asteroid.create_small_asteroids(asteroid))
                        break # Bullet can only hit one asteroid
            
            asteroids.extend(newly_spawned_asteroids)
            
            # --- Clean up inactive entities ---
            bullets = [b for b in bullets if b.is_active]
            asteroids = [a for a in asteroids if a.is_active]
            
            # Check for Win Condition (all asteroids destroyed)
            if not asteroids and ship.is_active:
                game_state = "WIN"


        elif game_state == "GAME_OVER" or game_state == "WIN":
            if IsKeyPressed(KEY_ENTER):
                # Soft reset the game state
                ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                bullets = []
                asteroids = spawn_initial_asteroids(4, 3) 
                score = 0
                game_state = "READY"


        # --- Draw ---
        BeginDrawing()
        ClearBackground(BLACK) 
        
        # Draw Ship (if active)
        if ship.is_active:
            ship.draw()
        
        # Draw Bullets
        for bullet in bullets:
            bullet.draw()
            
        # Draw Asteroids
        for asteroid in asteroids:
            asteroid.draw()
        
        # Draw HUD
        score_text = f"Score: {score}".encode('utf-8')
        lives_text = f"Lives: {ship.lives}".encode('utf-8')
        
        DrawText(score_text, 10, 10, 25, WHITE)
        DrawText(lives_text, SCREEN_WIDTH - MeasureText(lives_text, 25) - 10, 10, 25, WHITE)


        # Draw Game State Messages
        if game_state == "READY":
            message_1 = "ASTEROIDS".encode('utf-8')
            message_2 = "Press SPACE to Begin | UP/W to Thrust".encode('utf-8')
            
            DrawText(message_1, SCREEN_WIDTH // 2 - MeasureText(message_1, 60) // 2, 
                     SCREEN_HEIGHT // 2 - 80, 60, WHITE)
            DrawText(message_2, SCREEN_WIDTH // 2 - MeasureText(message_2, 20) // 2, 
                     SCREEN_HEIGHT // 2, 20, GRAY)

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
                     
        elif game_state == "WIN":
            message_1 = "WAVE CLEARED!".encode('utf-8')
            message_2 = f"Final Score: {score}".encode('utf-8')
            message_3 = "Press ENTER to Continue".encode('utf-8')
            
            DrawText(message_1, SCREEN_WIDTH // 2 - MeasureText(message_1, 60) // 2, 
                     SCREEN_HEIGHT // 2 - 80, 60, GOLD)
            DrawText(message_2, SCREEN_WIDTH // 2 - MeasureText(message_2, 40) // 2, 
                     SCREEN_HEIGHT // 2 + 10, 40, WHITE)
            DrawText(message_3, SCREEN_WIDTH // 2 - MeasureText(message_3, 20) // 2, 
                     SCREEN_HEIGHT // 2 + 70, 20, GRAY)


        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
