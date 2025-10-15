import math
from raylib import *
from pyray import *

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = b"Python Raylib 2-Player Gun Fight"
TARGET_FPS = 60

# Physics Constants
GRAVITY = 900.0        # Downward acceleration (pixels/s/s)
JUMP_VELOCITY = -500.0 # Initial upward velocity on jump
PLAYER_SPEED = 250.0   # Player horizontal movement speed
BULLET_SPEED = 600.0   # Bullet travel speed

# Gameplay Constants
MAX_HEALTH = 3
INVULN_TIME = 1.0       # Time (seconds) the player is immune after being hit
SHOT_COOLDOWN = 0.3     # Time (seconds) between shots

# Game States
STATE_PLAYING = 0
STATE_GAME_OVER = 1

# --- Game Object Classes ---

class Platform:
    """A static, solid rectangle for players and bullets to collide with."""
    def __init__(self, x, y, w, h, color):
        self.rect = Rectangle(x, y, w, h)
        self.color = color

    def draw(self):
        DrawRectangleRec(self.rect, self.color)
        DrawRectangleLinesEx(self.rect, 2, BLACK)
    
    def get_rect(self):
        return self.rect


class Bullet:
    """A projectile shot by a player."""
    def __init__(self, x, y, direction, color, owner):
        self.rect = Rectangle(x, y, 15, 5)
        self.vx = direction * BULLET_SPEED
        self.color = color
        self.owner = owner # Reference to the Player object that shot this bullet
        self.is_alive = True

    def update(self, dt, platforms, players):
        if not self.is_alive: return

        # 1. Apply Movement
        self.rect.x += self.vx * dt

        # 2. Check Screen/Platform Collision
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH:
            self.is_alive = False
            return
        
        for platform in platforms:
            if CheckCollisionRecs(self.rect, platform.get_rect()):
                self.is_alive = False
                return

        # 3. Check Player Collision
        for target in players:
            # Check if it hit the other player (and not its owner)
            if target != self.owner and target.health > 0 and CheckCollisionRecs(self.rect, target.get_rect()):
                target.take_damage()
                self.is_alive = False
                return

    def draw(self):
        if self.is_alive:
            DrawRectangleRec(self.rect, self.color)


class Player:
    """A controllable character with physics and health."""
    def __init__(self, x, y, controls, color, bullet_color):
        self.start_pos = Vector2(x, y)
        self.rect = Rectangle(x, y, 32, 60)
        
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        
        self.controls = controls
        self.color = color
        self.bullet_color = bullet_color
        
        self.health = MAX_HEALTH
        self.invuln_timer = 0.0
        self.last_shot_time = 0.0
        self.facing_direction = 1 # 1: right, -1: left

    def get_rect(self):
        return self.rect

    def update(self, dt, platforms, bullets_list):
        if self.health <= 0: return
        
        current_time = GetTime()

        # 1. Update Invulnerability timer
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            if self.invuln_timer < 0:
                self.invuln_timer = 0.0

        # 2. Handle Input (Movement)
        self.vx = 0.0
        if IsKeyDown(self.controls['left']):
            self.vx = -PLAYER_SPEED
            self.facing_direction = -1
        if IsKeyDown(self.controls['right']):
            self.vx = PLAYER_SPEED
            self.facing_direction = 1
        
        # 3. Handle Input (Jump)
        if IsKeyPressed(self.controls['jump']) and self.is_grounded:
            self.vy = JUMP_VELOCITY
        
        # 4. Handle Input (Shoot)
        if IsKeyPressed(self.controls['shoot']) and current_time > self.last_shot_time + SHOT_COOLDOWN:
            self.shoot(bullets_list, current_time)

        # 5. Apply Gravity
        self.vy += GRAVITY * dt
        self.vy = min(self.vy, 1000) # Terminal velocity

        self.is_grounded = False

        # 6. X Movement and Collision
        self.rect.x += self.vx * dt
        self._handle_collision(platforms, 'X')

        # 7. Y Movement and Collision
        self.rect.y += self.vy * dt
        self._handle_collision(platforms, 'Y')
        
        # Clamp to screen edges
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))

        # Check for death by falling
        if self.rect.y > SCREEN_HEIGHT + 100:
            self.reset_position()
            self.take_damage() # Fall damage

    def _handle_collision(self, platforms, axis):
        """Resolves collision against all platforms."""
        for platform in platforms:
            if CheckCollisionRecs(self.rect, platform.get_rect()):
                
                if axis == 'X':
                    if self.vx > 0: # Moving Right
                        self.rect.x = platform.rect.x - self.rect.width
                    elif self.vx < 0: # Moving Left
                        self.rect.x = platform.rect.x + platform.rect.width
                    self.vx = 0.0
                
                elif axis == 'Y':
                    if self.vy >= 0: # Falling (Hitting Ground)
                        self.rect.y = platform.rect.y - self.rect.height
                        self.is_grounded = True
                    elif self.vy < 0: # Jumping (Hitting Ceiling)
                        self.rect.y = platform.rect.y + platform.rect.height
                    self.vy = 0.0
    
    def shoot(self, bullets_list, current_time):
        """Creates a new bullet instance."""
        bullet_x = self.rect.x + self.rect.width / 2 + (self.facing_direction * (self.rect.width / 2 + 5))
        bullet_y = self.rect.y + self.rect.height / 2 - 2
        
        new_bullet = Bullet(bullet_x, bullet_y, self.facing_direction, self.bullet_color, self)
        bullets_list.append(new_bullet)
        self.last_shot_time = current_time

    def take_damage(self):
        """Reduces health and initiates invulnerability."""
        global game_state, winner
        
        if self.invuln_timer <= 0 and self.health > 0:
            self.health -= 1
            self.invuln_timer = INVULN_TIME
            self.reset_position()

            if self.health <= 0:
                game_state = STATE_GAME_OVER
                # Set the winner to the OTHER player
                if self == players[0]:
                    winner = players[1]
                else:
                    winner = players[0]
            
    def reset_position(self):
        """Teleports player back to start point."""
        self.rect.x = self.start_pos.x
        self.rect.y = self.start_pos.y
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False

    def draw(self):
        """Draws the player, flickering if invulnerable."""
        if self.health <= 0: return

        # Flicker effect: only draw on alternating 0.1s intervals when invulnerable
        draw_player = True
        if self.invuln_timer > 0:
            if int(GetTime() * 10) % 2 != 0: 
                draw_player = False

        if draw_player:
            DrawRectangleRec(self.rect, self.color)
            DrawRectangleLinesEx(self.rect, 3, self.bullet_color)
            
            # Simple aiming indicator (Draw cone in direction of fire)
            center_x = self.rect.x + self.rect.width / 2
            center_y = self.rect.y + self.rect.height / 2
            
            if self.facing_direction == 1: # Right
                DrawTriangle(Vector2(center_x, center_y), Vector2(center_x + 10, center_y - 10), Vector2(center_x + 10, center_y + 10), self.bullet_color)
            else: # Left
                DrawTriangle(Vector2(center_x, center_y), Vector2(center_x - 10, center_y - 10), Vector2(center_x - 10, center_y + 10), self.bullet_color)


# --- Game Setup Functions ---

def setup_level():
    """Defines the arena platforms."""
    platforms_list = []
    
    # 1. Floor
    platforms_list.append(Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, RAYWHITE))
    
    # 2. Side Platforms
    platforms_list.append(Platform(SCREEN_WIDTH / 4 - 80, SCREEN_HEIGHT - 120, 160, 20, RAYWHITE))
    platforms_list.append(Platform(SCREEN_WIDTH * 3 / 4 - 80, SCREEN_HEIGHT - 120, 160, 20, RAYWHITE))
    
    # 3. Center Platform
    platforms_list.append(Platform(SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT - 240, 240, 20, RAYWHITE))
    
    # 4. High Platforms
    platforms_list.append(Platform(20, SCREEN_HEIGHT - 350, 100, 20, RAYWHITE))
    platforms_list.append(Platform(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 350, 100, 20, RAYWHITE))
    
    return platforms_list

def init_game():
    """Initializes player and global state."""
    global platforms, players, bullets, game_state, winner
    
    # Controls definition (Raylib key codes)
    P1_CONTROLS = {'jump': KEY_W, 'left': KEY_A, 'right': KEY_D, 'shoot': KEY_Q}
    P2_CONTROLS = {'jump': KEY_UP, 'left': KEY_LEFT, 'right': KEY_RIGHT, 'shoot': KEY_P}
    
    # Player Instantiation
    p1 = Player(SCREEN_WIDTH * 0.25 - 16, SCREEN_HEIGHT / 2, P1_CONTROLS, RED, ORANGE)
    p2 = Player(SCREEN_WIDTH * 0.75 - 16, SCREEN_HEIGHT / 2, P2_CONTROLS, BLUE, SKYBLUE)
    
    players = [p1, p2]
    platforms = setup_level()
    bullets = []
    game_state = STATE_PLAYING
    winner = None

def reset_game():
    """Resets the game state for a new round."""
    global players, bullets, game_state, winner
    
    for p in players:
        p.health = MAX_HEALTH
        p.reset_position()
        p.invuln_timer = 0.0
        p.last_shot_time = 0.0
        
    bullets = []
    game_state = STATE_PLAYING
    winner = None


# --- Drawing Functions ---

def draw_hud():
    """Draws player health and instructions."""
    p1_health_text = f"P1 Health: {players[0].health}".encode('utf-8')
    p2_health_text = f"P2 Health: {players[1].health}".encode('utf-8')
    
    # P1 HUD (Left)
    DrawText(p1_health_text, 10, 10, 25, players[0].color)
    DrawText(b"W/A/D | Q (Shoot)", 10, 35, 18, WHITE)

    # P2 HUD (Right)
    p2_text_width = MeasureText(p2_health_text, 25)
    p2_controls_width = MeasureText(b"ARROWS | P (Shoot)", 18)
    DrawText(p2_health_text, SCREEN_WIDTH - p2_text_width - 10, 10, 25, players[1].color)
    DrawText(b"ARROWS | P (Shoot)", SCREEN_WIDTH - p2_controls_width - 10, 35, 18, WHITE)


def draw_game_over():
    """Draws the game over screen."""
    if winner:
        winner_text = f"{'PLAYER 1' if winner == players[0] else 'PLAYER 2'} WINS!".encode('utf-8')
    else:
        winner_text = b"GAME OVER"
        
    restart_text = b"Press ENTER or SPACE to restart"
    
    # Draw transparent overlay
    DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Fade(BLACK, 0.7))
    
    # Winner text
    font_size = 60
    text_w = MeasureText(winner_text, font_size)
    DrawText(winner_text, int(SCREEN_WIDTH/2 - text_w/2), int(SCREEN_HEIGHT/2 - 40), font_size, YELLOW)
    
    # Restart text
    font_size = 30
    text_w = MeasureText(restart_text, font_size)
    DrawText(restart_text, int(SCREEN_WIDTH/2 - text_w/2), int(SCREEN_HEIGHT/2 + 20), font_size, WHITE)


# --- Main Function ---

# Global variables to manage game state
players = []
platforms = []
bullets = []
game_state = STATE_PLAYING
winner = None

def main():
    global game_state, players, bullets, winner

    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(TARGET_FPS)
    
    init_game()

    while not WindowShouldClose():
        dt = GetFrameTime()
        
        # --- Update ---
        if game_state == STATE_PLAYING:
            
            # Update Players
            for p in players:
                p.update(dt, platforms, bullets)
            
            # Update Bullets (filtered list comprehension)
            for b in bullets:
                b.update(dt, platforms, players)
            bullets = [b for b in bullets if b.is_alive]
            
        elif game_state == STATE_GAME_OVER:
            if IsKeyPressed(KEY_ENTER) or IsKeyPressed(KEY_SPACE):
                reset_game()

        # --- Draw ---
        BeginDrawing()
        ClearBackground(Color(30, 41, 59, 255)) # Dark slate background

        # Draw Platforms
        for p in platforms:
            p.draw()

        # Draw Players
        for p in players:
            p.draw()
            
        # Draw Bullets
        for b in bullets:
            b.draw()
        
        # Draw HUD (always visible)
        draw_hud()
        
        # Draw Game Over Overlay
        if game_state == STATE_GAME_OVER:
            draw_game_over()
        
        EndDrawing()

    CloseWindow()

if __name__ == "__main__":
    main()
