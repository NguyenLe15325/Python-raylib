import random
import math
from raylib import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCROLL_SPEED = 200.0  # Speed of the starfield scroll (pixels/s)
PLAYER_SPEED = 300.0
PLAYER_RADIUS = 20
PLAYER_FIRE_RATE = 0.2
PLAYER_BULLET_SPEED = 800.0

ENEMY_SPEED = 150.0
ENEMY_FIRE_RATE_MIN = 3.0
ENEMY_FIRE_RATE_MAX = 6.0
ENEMY_BULLET_SPEED = 400.0

WAVE_TIMER_INTERVAL = 5.0 # Time between enemy waves

# --- Game Object Classes ---

class Star:
    """Represents a single star in the scrolling background."""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.uniform(1, 3)
        self.color = GRAY if self.size < 2 else WHITE
        
    def update(self, delta_time):
        # Move star downward, simulating upward flight
        self.y += SCROLL_SPEED * delta_time * (self.size / 2) # Faster scroll for bigger stars (parallax effect)
        
        # Reset star to the top if it goes off-screen
        if self.y > SCREEN_HEIGHT:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = 0

    def draw(self):
        DrawCircle(int(self.x), int(self.y), int(self.size), self.color)


class Entity:
    """Base class for Ship, Bullet, and Enemy to handle movement and lifespan checks."""
    def __init__(self, x, y, vx, vy, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.is_active = True

    def update(self, delta_time):
        if not self.is_active:
            return
            
        # Apply velocity to position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

        # Check if entity is off-screen (for cleanup)
        if self.x < -100 or self.x > SCREEN_WIDTH + 100 or \
           self.y < -100 or self.y > SCREEN_HEIGHT + 100:
            self.is_active = False

class PlayerShip(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 0.0, 0.0, PLAYER_RADIUS)
        self.can_fire_timer = 0.0
        self.lives = 3
        
    def update(self, delta_time):
        # Handle player input and set velocity
        self.vx = 0.0
        self.vy = 0.0
        
        if IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A):
            self.vx = -PLAYER_SPEED
        if IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D):
            self.vx = PLAYER_SPEED
        if IsKeyDown(KEY_UP) or IsKeyDown(KEY_W):
            self.vy = -PLAYER_SPEED
        if IsKeyDown(KEY_DOWN) or IsKeyDown(KEY_S):
            self.vy = PLAYER_SPEED

        super().update(delta_time)
        
        # Clamp position to screen bounds
        self.x = max(self.radius, min(self.x, SCREEN_WIDTH - self.radius))
        self.y = max(SCREEN_HEIGHT - 100 - self.radius, min(self.y, SCREEN_HEIGHT - self.radius))
        
        # Update fire timer
        if self.can_fire_timer > 0:
            self.can_fire_timer -= delta_time

    def fire_bullet(self):
        if self.can_fire_timer <= 0:
            # Bullet fires straight up
            start_x = self.x
            start_y = self.y - self.radius - 5
            
            self.can_fire_timer = PLAYER_FIRE_RATE
            # Player bullet always moves up (-Y direction)
            return PlayerBullet(start_x, start_y, 0, -PLAYER_BULLET_SPEED) 

    def draw(self):
        # Draw the ship as a blue triangle pointing up
        p1 = (self.x, self.y - self.radius)
        p2 = (self.x - self.radius, self.y + self.radius / 2)
        p3 = (self.x + self.radius, self.y + self.radius / 2)
        DrawTriangle(p1, p2, p3, BLUE)
        # Add a light blue cockpit/canopy
        DrawCircle(int(self.x), int(self.y), 5, SKYBLUE)
        
class PlayerBullet(Entity):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy, 4)
        
    def draw(self):
        if self.is_active:
            DrawCircle(int(self.x), int(self.y), self.radius, LIME)

class EnemyShip(Entity):
    def __init__(self, x, y, size, pattern='straight'):
        super().__init__(x, y, 0, ENEMY_SPEED, size)
        self.base_y = y # Used for sine wave calculation
        self.radius = size
        self.pattern = pattern
        self.wave_time = 0.0 # Tracks time within the current wave (used for patterns)
        self.fire_timer = random.uniform(ENEMY_FIRE_RATE_MIN, ENEMY_FIRE_RATE_MAX)
        self.points = 100
        
    def update(self, delta_time):
        self.wave_time += delta_time
        
        if self.pattern == 'straight':
            # Straight down movement (vy is set in init)
            pass
        elif self.pattern == 'sine':
            # Sine wave movement: oscillate VX based on time
            # VX = amplitude * sin(frequency * time)
            amplitude = 150.0
            frequency = 3.0 # How many full waves per second
            self.vx = amplitude * math.sin(frequency * self.wave_time)
        
        super().update(delta_time)
        
        # Update fire timer
        self.fire_timer -= delta_time

    def shoot(self):
        if self.fire_timer <= 0:
            self.fire_timer = random.uniform(ENEMY_FIRE_RATE_MIN, ENEMY_FIRE_RATE_MAX)
            # Enemy bullet always moves down (+Y direction)
            return EnemyBullet(self.x, self.y + self.radius + 5, 0, ENEMY_BULLET_SPEED)
        return None

    def draw(self):
        if self.is_active:
            # Draw as a red/purple circle for distinction
            DrawCircle(int(self.x), int(self.y), self.radius, RED)
            # Simple wing line
            DrawLine(int(self.x - self.radius), int(self.y), int(self.x + self.radius), int(self.y), PURPLE)
            

class EnemyBullet(Entity):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy, 3)
        
    def draw(self):
        if self.is_active:
            DrawCircle(int(self.x), int(self.y), self.radius, ORANGE)


# --- Game Management Functions ---

def spawn_wave(current_wave, enemies):
    """Spawns a new wave of enemies."""
    
    if current_wave == 1:
        # Wave 1: 5 straight-moving enemies
        for i in range(5):
            x_pos = SCREEN_WIDTH / 6 * (i + 1)
            y_pos = -random.uniform(50, 150) # Start slightly off-screen
            enemies.append(EnemyShip(x_pos, y_pos, 15, 'straight'))
        print("Wave 1 spawned: Straight line.")
        
    elif current_wave == 2:
        # Wave 2: 3 enemies with sine wave pattern
        for i in range(3):
            x_pos = SCREEN_WIDTH / 4 * (i + 1)
            y_pos = -random.uniform(50, 150) 
            enemies.append(EnemyShip(x_pos, y_pos, 20, 'sine'))
        print("Wave 2 spawned: Sine pattern.")
    
    # You can add more complex waves here later!


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib Vertical Shooter (Shmup)".encode('utf-8'))
    SetTargetFPS(60)

    # Game State Variables
    ship = PlayerShip(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50)
    stars = [Star() for _ in range(100)] # 100 stars for the background
    
    player_bullets = []
    enemies = []
    enemy_bullets = []
    
    game_state = "READY" # READY, PLAYING, GAME_OVER, WIN
    
    score = 0
    wave_timer = WAVE_TIMER_INTERVAL
    current_wave = 0

    # --- Game Loop ---
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        
        # --- Update ---
        if game_state == "READY":
            if IsKeyPressed(KEY_SPACE) or IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                game_state = "PLAYING"
                current_wave = 1
                wave_timer = 1.0 # Give a moment before first wave
            
        elif game_state == "PLAYING":
            
            # 1. Background Scroll
            for star in stars:
                star.update(delta_time)
                
            # 2. Wave Management
            if not enemies:
                wave_timer -= delta_time
                if wave_timer <= 0:
                    spawn_wave(current_wave, enemies)
                    current_wave += 1
                    wave_timer = WAVE_TIMER_INTERVAL # Reset for next wave
                    
            # 3. Player Input & Update
            ship.update(delta_time)
            
            if (IsKeyPressed(KEY_SPACE) or IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) and ship.is_active:
                new_bullet = ship.fire_bullet()
                if new_bullet:
                    player_bullets.append(new_bullet)

            # 4. Enemy Update & Shooting
            new_enemy_bullets = []
            for enemy in enemies:
                enemy.update(delta_time)
                e_bullet = enemy.shoot()
                if e_bullet:
                    new_enemy_bullets.append(e_bullet)
            enemy_bullets.extend(new_enemy_bullets)
            
            # 5. Bullet Updates
            for bullet in player_bullets:
                bullet.update(delta_time)
            for bullet in enemy_bullets:
                bullet.update(delta_time)
                
            # --- Collision Detection ---
            
            # a. Player Bullet vs Enemy
            for p_bullet in player_bullets:
                if not p_bullet.is_active: continue
                
                for enemy in enemies:
                    if not enemy.is_active: continue
                    
                    if CheckCollisionCircles((p_bullet.x, p_bullet.y), p_bullet.radius, (enemy.x, enemy.y), enemy.radius):
                        p_bullet.is_active = False # Destroy player bullet
                        enemy.is_active = False # Destroy enemy
                        score += enemy.points
                        break # Bullet can only hit one entity
                        
            # b. Player vs Enemy Ship
            if ship.is_active:
                for enemy in enemies:
                    if enemy.is_active:
                        if CheckCollisionCircles((ship.x, ship.y), ship.radius, (enemy.x, enemy.y), enemy.radius):
                            ship.lives -= 1
                            enemy.is_active = False # Destroy enemy
                            if ship.lives <= 0:
                                ship.is_active = False
                                game_state = "GAME_OVER"
                                
            # c. Player vs Enemy Bullet
            if ship.is_active:
                for e_bullet in enemy_bullets:
                    if e_bullet.is_active:
                        if CheckCollisionCircles((ship.x, ship.y), ship.radius, (e_bullet.x, e_bullet.y), e_bullet.radius):
                            ship.lives -= 1
                            e_bullet.is_active = False # Destroy enemy bullet
                            if ship.lives <= 0:
                                ship.is_active = False
                                game_state = "GAME_OVER"


            # --- Clean up inactive entities ---
            player_bullets = [b for b in player_bullets if b.is_active]
            enemies = [e for e in enemies if e.is_active]
            enemy_bullets = [b for b in enemy_bullets if b.is_active]
            
            # Note: No explicit WIN condition (waves are infinite or until you run out of waves)
            # If current_wave > 2, you could add more waves or transition to a WIN state if no more waves exist.
            
        # --- Draw ---
        BeginDrawing()
        ClearBackground(BLACK) 
        
        # 1. Draw Stars (Background)
        for star in stars:
            star.draw()
            
        # 2. Draw Enemy Bullets
        for bullet in enemy_bullets:
            bullet.draw()
            
        # 3. Draw Enemies
        for enemy in enemies:
            enemy.draw()
            
        # 4. Draw Player Bullets
        for bullet in player_bullets:
            bullet.draw()
            
        # 5. Draw Ship (if active)
        if ship.is_active:
            ship.draw()
        
        # 6. Draw HUD
        score_text = f"Score: {score}".encode('utf-8')
        lives_text = f"Lives: {ship.lives}".encode('utf-8')
        wave_text = f"Wave: {current_wave}".encode('utf-8')

        DrawText(score_text, 10, 10, 20, WHITE)
        DrawText(lives_text, SCREEN_WIDTH - MeasureText(lives_text, 20) - 10, 10, 20, WHITE)
        DrawText(wave_text, 10, 40, 20, YELLOW)


        # Draw Game State Messages
        if game_state == "READY":
            message_1 = "VERTICAL SHOOTER".encode('utf-8')
            message_2 = "WASD/Arrows to Move | SPACE/Click to Shoot".encode('utf-8')
            
            DrawText(message_1, SCREEN_WIDTH // 2 - MeasureText(message_1, 60) // 2, 
                     SCREEN_HEIGHT // 2 - 80, 60, LIME)
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

        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
