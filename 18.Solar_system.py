from raylib import *
from pyray import *
import math

# --- CONSTANTS ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TITLE = b"Hierarchical 3D Solar System Simulator"
TARGET_FPS = 60

# Orbital Parameters (in degrees per second)
EARTH_ORBIT_SPEED = 10.0  # Speed of Earth around the Sun
EARTH_AXIAL_SPEED = 150.0 # Speed of Earth spinning on its axis
MOON_ORBIT_SPEED = 150.0  # Speed of Moon around the Earth
MOON_AXIAL_SPEED = 300.0  # Speed of Moon spinning on its axis

# Distances (relative units)
EARTH_ORBIT_RADIUS = 20.0
MOON_ORBIT_RADIUS = 5.0

# Sizes
SUN_RADIUS = 4.0
EARTH_RADIUS = 1.5
MOON_RADIUS = 0.5

# --- Custom Camera Control (To avoid binding issues) ---

def update_manual_camera(camera, dt):
    """
    Manually updates camera position based on WASD keys.
    This replaces the problematic UpdateCamera function.
    """
    move_speed = 10.0 * dt

    # Forward/Backward
    if IsKeyDown(KEY_W):
        camera.position.x += camera.target.x * move_speed
        camera.position.z += camera.target.z * move_speed
    if IsKeyDown(KEY_S):
        camera.position.x -= camera.target.x * move_speed
        camera.position.z -= camera.target.z * move_speed

    # Strafe Left/Right (simplified perpendicular movement)
    if IsKeyDown(KEY_A):
        camera.position.x -= camera.target.z * move_speed
        camera.position.z += camera.target.x * move_speed
    if IsKeyDown(KEY_D):
        camera.position.x += camera.target.z * move_speed
        camera.position.z -= camera.target.x * move_speed
        
    # Up/Down
    if IsKeyDown(KEY_Q):
        camera.position.y += move_speed
    if IsKeyDown(KEY_E):
        camera.position.y -= move_speed

    # Rotation (Manual mouse look is complex without raymath, using simple key rotation)
    rotation_speed = 0.05
    if IsKeyDown(KEY_LEFT):
        camera.target.x = camera.target.x * math.cos(rotation_speed) - camera.target.z * math.sin(rotation_speed)
        camera.target.z = camera.target.x * math.sin(rotation_speed) + camera.target.z * math.cos(rotation_speed)
    if IsKeyDown(KEY_RIGHT):
        camera.target.x = camera.target.x * math.cos(-rotation_speed) - camera.target.z * math.sin(-rotation_speed)
        camera.target.z = camera.target.x * math.sin(-rotation_speed) + camera.target.z * math.cos(-rotation_speed)


# --- Core Draw Logic ---

def draw_solar_system(total_time):
    """
    Renders the Sun, Earth, and Moon using hierarchical transformations.
    """
    
    # 1. DRAW THE SUN (Origin of the entire system)
    
    # The Sun is at the center (0, 0, 0)
    DrawSphere(Vector3(0, 0, 0), SUN_RADIUS, YELLOW)
    
    # --- EARTH SYSTEM ---
    
    # Use the transformation stack to manage the Earth's orbit
    rlPushMatrix()
    
    # Rotation 1: Orbit around the Sun (Y-axis rotation)
    earth_orbit_angle = total_time * EARTH_ORBIT_SPEED
    rlRotatef(earth_orbit_angle, 0, 1, 0)
    
    # Translation 1: Move out to the Earth's orbital distance
    rlTranslatef(EARTH_ORBIT_RADIUS, 0, 0)
    
    # Save the Earth's current position to use as the Moon's origin
    rlPushMatrix()
    
    # Rotation 2: Earth's axial rotation (spinning on its own axis)
    earth_axial_angle = total_time * EARTH_AXIAL_SPEED
    rlRotatef(earth_axial_angle, 0, 1, 0) 
    
    # Draw the Earth
    DrawSphere(Vector3(0, 0, 0), EARTH_RADIUS, BLUE) 
    
    # --- MOON SYSTEM ---
    
    # Rotation 3: Moon's orbit around the Earth
    moon_orbit_angle = total_time * MOON_ORBIT_SPEED
    rlRotatef(moon_orbit_angle, 0, 1, 0)
    
    # Translation 2: Move out to the Moon's orbital distance (relative to Earth's center)
    rlTranslatef(MOON_ORBIT_RADIUS, 0, 0)

    # Rotation 4: Moon's axial rotation
    moon_axial_angle = total_time * MOON_AXIAL_SPEED
    rlRotatef(moon_axial_angle, 0, 1, 0)
    
    # Draw the Moon
    DrawSphere(Vector3(0, 0, 0), MOON_RADIUS, GRAY)
    
    # Restore the transformation state before Moon's orbit (to finish Earth's drawing)
    rlPopMatrix() 
    
    # Restore the transformation state before Earth's orbit (to return to Sun's center)
    rlPopMatrix() 

# --- Main Program ---

def main():
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(TARGET_FPS)
    
    # Camera setup
    camera = Camera3D()
    camera.position = Vector3(50.0, 50.0, 50.0) # Position in 3D space
    camera.target = Vector3(0.0, 0.0, 0.0)      # Point the camera at the origin (the Sun)
    camera.up = Vector3(0.0, 1.0, 0.0)          # Up vector (standard Y-up)
    camera.fovy = 60.0                          # Field of view
    camera.projection = CAMERA_PERSPECTIVE
    
    total_time = 0.0

    while not WindowShouldClose():
        dt = GetFrameTime()
        total_time += dt

        # Manual Camera Update
        update_manual_camera(camera, dt)

        BeginDrawing()
        
        ClearBackground(Color(10, 10, 25, 255)) # Deep space background
        
        BeginMode3D(camera)
        
        # Draw a grid plane for reference
        DrawGrid(100, 10.0) 
        
        # Draw the entire solar system simulation
        draw_solar_system(total_time)
        
        EndMode3D()

        # Draw HUD
        DrawFPS(10, 10)
        DrawText(b"3D Solar System Simulator", 10, 40, 20, WHITE)
        DrawText(b"Controls: WASD/QE to Move, Arrow Keys to Rotate", 10, 70, 20, GRAY)

        EndDrawing()

    CloseWindow()

if __name__ == "__main__":
    main()
