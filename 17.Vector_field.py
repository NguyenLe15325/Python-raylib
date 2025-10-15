from raylib import *
from pyray import *
import math

# --- CONSTANTS ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TITLE = b"Interactive Vector Field Simulation"

# Simulation Constants
GRID_SIZE = 25          # Spacing between drawn vector arrows
PARTICLE_COUNT = 2500   # Number of particles following the field
FIELD_STRENGTH = 1.5    # How quickly particles accelerate towards the field vector
PARTICLE_DECAY = 0.99   # Damping factor for particle speed (friction)
TRAIL_LENGTH = 0.9      # 1.0 = no trail, 0.9 = long trail fade

# Colors
BACKGROUND_COLOR = Color(20, 20, 30, 255)
PARTICLE_COLOR = Color(100, 255, 255, 255) # Cyan/Light Blue
# UPDATED: Fully opaque and brighter light blue-gray for maximum visibility
FIELD_COLOR = Color(150, 150, 200, 255) 

# --- Particle Class ---
class Particle:
    """A particle that follows the field vectors."""
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.color = PARTICLE_COLOR
        
    def reset(self):
        # Place particle randomly within the screen bounds
        self.position = Vector2(GetRandomValue(0, SCREEN_WIDTH), GetRandomValue(0, SCREEN_HEIGHT))
        self.velocity = Vector2(0.0, 0.0)
        
    def update(self, field_vector, dt):
        
        # 1. Apply field force to velocity
        field_force = Vector2Scale(field_vector, FIELD_STRENGTH)
        self.velocity = Vector2Add(self.velocity, field_force)
        
        # 2. Dampen velocity (friction/drag)
        self.velocity = Vector2Scale(self.velocity, PARTICLE_DECAY)
        
        # 3. Limit maximum speed for stability
        max_speed = 5.0 
        if Vector2LengthSqr(self.velocity) > max_speed * max_speed:
            self.velocity = Vector2Scale(Vector2Normalize(self.velocity), max_speed)
        
        # 4. Update position (Velocity * Time, simplified since dt is small)
        self.position = Vector2Add(self.position, self.velocity)
        
        # 5. Handle screen boundaries (wrap around)
        if self.position.x < 0: self.position.x = SCREEN_WIDTH
        if self.position.x > SCREEN_WIDTH: self.position.x = 0
        if self.position.y < 0: self.position.y = SCREEN_HEIGHT
        if self.position.y > SCREEN_HEIGHT: self.position.y = 0

    def draw(self):
        DrawPixelV(self.position, self.color)

# --- Field Logic ---

def get_field_vector(x, y, time):
    """
    Calculates the vector at position (x, y) based on a simple, dynamic function.
    """
    # Normalize coordinates to a smaller range
    scaled_x = x / 100.0
    scaled_y = y / 100.0
    
    # Calculate a complex angle based on position and time
    angle_offset = math.atan2(scaled_y - (SCREEN_HEIGHT/200.0), scaled_x - (SCREEN_WIDTH/200.0))
    angle = scaled_x * 0.5 + scaled_y * 0.3 + time * 0.2 + angle_offset * 0.1
    
    # Use sine and cosine of the calculated angle for the vector components
    vx = math.cos(angle) 
    vy = math.sin(angle)
    
    # --- Mouse Interaction (Repeller) ---
    mouse_pos = GetMousePosition()
    if IsMouseButtonDown(MOUSE_BUTTON_LEFT):
        mouse_force = Vector2Subtract(mouse_pos, Vector2(x, y))
        dist_sq = Vector2LengthSqr(mouse_force)
        
        if dist_sq < 200 * 200: # Check interaction radius
            if dist_sq < 100: dist_sq = 100 # Clamp minimum distance to prevent huge forces
            
            # Inverse square repulsion force
            mouse_repulsion_scale = -1000.0 / dist_sq
            mouse_force = Vector2Scale(Vector2Normalize(mouse_force), mouse_repulsion_scale)
            
            vx += mouse_force.x
            vy += mouse_force.y

    return Vector2(vx, vy)


# --- Main Application ---

def main():
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(60)

    # Explicitly define mouse constant for linter safety
    MOUSE_BUTTON_LEFT = 0 
    
    # Initialize Particles
    particles = []
    for _ in range(PARTICLE_COUNT):
        x = GetRandomValue(0, SCREEN_WIDTH)
        y = GetRandomValue(0, SCREEN_HEIGHT)
        particles.append(Particle(x, y))
    
    current_time = 0.0

    while not WindowShouldClose():
        dt = GetFrameTime()
        current_time += dt

        # --- Update Particles ---
        for p in particles:
            field_vec = get_field_vector(p.position.x, p.position.y, current_time)
            p.update(field_vec, dt)

        # --- Draw ---
        BeginDrawing()
        
        # Clear background with a partial fade to create particle trails
        DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(
            BACKGROUND_COLOR.r, 
            BACKGROUND_COLOR.g, 
            BACKGROUND_COLOR.b, 
            int(255 * (1.0 - TRAIL_LENGTH)) # Apply alpha based on TRAIL_LENGTH
        )) 
        
        # --- Draw Vector Field Grid ---
        # This section ensures the field is drawn every single frame
        for i in range(0, SCREEN_WIDTH, GRID_SIZE):
            for j in range(0, SCREEN_HEIGHT, GRID_SIZE):
                
                start = Vector2(i, j)
                field_vec = get_field_vector(i, j, current_time)
                
                # Normalize and scale vector for drawing length
                field_len = Vector2Length(field_vec)
                if field_len > 0:
                    field_vec = Vector2Scale(field_vec, GRID_SIZE * 0.3 / field_len) 
                
                end = Vector2Add(start, field_vec)
                
                DrawLineV(start, end, FIELD_COLOR)
                DrawCircleV(end, 2, FIELD_COLOR) # Simple dot/arrow head

        # --- Draw Particles ---
        for p in particles:
            p.draw()
            
        DrawFPS(10, 10)
        DrawText(b"LEFT CLICK: Repel Particles", 10, 40, 20, GRAY)

        EndDrawing()

    CloseWindow()

if __name__ == "__main__":
    main()
