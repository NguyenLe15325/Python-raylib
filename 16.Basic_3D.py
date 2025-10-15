from raylib import *
from pyray import *
import math # Needed for trigonometry in manual camera movement

# --- Game Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TITLE = b"Basic 3D Explorer"

# Global cube configuration
CUBE_POSITION = Vector3(0.0, 2.5, 0.0) # Position the cube 2.5 units above the grid (Y is up)
CUBE_SIZE = 5.0

def update_camera_manual(camera, delta_time):
    """
    Manually updates the camera position based on WASD/QE input, 
    bypassing potentially problematic 'UpdateCamera' binding wrappers.
    This simulates a basic first-person camera movement.
    """
    move_speed = 15.0 * delta_time # Units per second (adjusted for smoother speed)
    
    # 1. Calculate the forward and right vectors based on the current view
    forward = Vector3Subtract(camera.target, camera.position)
    forward.y = 0.0 # Keep movement in the XZ plane for standard FPS navigation
    forward = Vector3Normalize(forward)
    
    right = Vector3CrossProduct(forward, camera.up)
    right = Vector3Normalize(right)
    
    # 2. Determine the movement vector based on key input
    movement_vector = Vector3(0.0, 0.0, 0.0)
    
    if IsKeyDown(KEY_W):
        movement_vector = Vector3Add(movement_vector, Vector3Scale(forward, move_speed))
    if IsKeyDown(KEY_S):
        movement_vector = Vector3Subtract(movement_vector, Vector3Scale(forward, move_speed))
    if IsKeyDown(KEY_D):
        movement_vector = Vector3Add(movement_vector, Vector3Scale(right, move_speed))
    if IsKeyDown(KEY_A):
        movement_vector = Vector3Subtract(movement_vector, Vector3Scale(right, move_speed))
        
    # Vertical movement (Q/E)
    if IsKeyDown(KEY_E):
        movement_vector.y += move_speed
    if IsKeyDown(KEY_Q):
        movement_vector.y -= move_speed

    # 3. Apply movement to both position and target
    camera.position = Vector3Add(camera.position, movement_vector)
    camera.target = Vector3Add(camera.target, movement_vector)
    
    # 4. Handle simple mouse look (Pitch and Yaw)
    if IsKeyDown(KEY_LEFT_ALT) or IsMouseButtonDown(MOUSE_BUTTON_RIGHT):
        mouse_delta = GetMouseDelta()
        rotation_speed = 0.05 # Sensitivity
        
        # Yaw (Horizontal Rotation) - Rotate around the UP (Y) axis
        camera.position = Vector3RotateByAxisAngle(camera.position, camera.up, -mouse_delta.x * rotation_speed)
        
        # Pitch (Vertical Rotation) - Rotate around the RIGHT vector
        # NOTE: This is complex and often leads to gimbal lock or issues. 
        # For simplicity, we stick to position update, as the target is already moving with position.
        
        # A simple fix for target is to reset it relative to the position after rotation
        if abs(mouse_delta.x) > 0.1:
            # We only need to adjust the target relative to the position after rotation
            # For simplicity, we just look forward from the new position
            camera.target = Vector3Add(camera.position, forward)


def main():
    # --- Initialization ---
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    SetTargetFPS(60)

    # Define the camera parameters (Perspective Projection)
    camera = Camera3D()
    camera.position = Vector3(20.0, 10.0, 20.0)  # Camera position (x, y, z)
    camera.target = Vector3(0.0, 0.0, 0.0)      # Where the camera looks
    camera.up = Vector3(0.0, 1.0, 0.0)          # Camera up vector (always Y)
    camera.fovy = 45.0                          # Field-of-view in Y direction (degrees)
    camera.projection = CAMERA_PERSPECTIVE      # Projection type
    
    # --- Game Loop ---
    while not WindowShouldClose():
        # --- Update ---
        delta_time = GetFrameTime()

        # Manual camera update now handles movement
        update_camera_manual(camera, delta_time)
        
        # Calculate rotation angle based on time (20 degrees per second)
        rotation_angle = GetTime() * 20.0
        
        # --- Draw ---
        BeginDrawing()

        ClearBackground(Color(20, 20, 30, 255)) # Dark background for space

        # Start 3D drawing mode
        BeginMode3D(camera)

        # 1. Draw a massive grid on the XZ plane (Y=0) to represent the ground
        DrawGrid(30, 1.0) # 30x30 grid, 1.0 unit spacing
        
        # --- ROTATING CUBE LOGIC ---
        # 2. Draw a central object (a cube) with rotation using matrix transformations.
        rlPushMatrix() # Save the current transformation matrix (Camera matrix)
        
        # Apply Translation: Move the drawing origin to the cube's desired position
        rlTranslatef(CUBE_POSITION.x, CUBE_POSITION.y, CUBE_POSITION.z) 
        
        # Apply Rotation: Rotate the drawing origin around the Y-axis
        rlRotatef(rotation_angle, 0.0, 1.0, 0.0) 
        
        # Draw the cube centered at the *new, rotated origin* (0, 0, 0)
        DrawCube(Vector3(0.0, 0.0, 0.0), CUBE_SIZE, CUBE_SIZE, CUBE_SIZE, RED)
        DrawCubeWires(Vector3(0.0, 0.0, 0.0), CUBE_SIZE, CUBE_SIZE, CUBE_SIZE, MAROON) # Outline

        rlPopMatrix() # Restore the previous transformation matrix (undoes the translate/rotate)
        # ---------------------------

        # 3. Draw a small reference sphere (unaffected by the cube's matrix transformations)
        DrawSphere(Vector3(10.0, 1.0, 10.0), 1.0, BLUE)

        # Stop 3D drawing mode
        EndMode3D()

        # --- Draw HUD (2D overlay) ---
        DrawText(b"Controls: WASD/QE to move (Manual Control Active)", 10, 10, 20, RAYWHITE)
        DrawText(b"Cube is rotating using matrix transformations.", 10, 35, 20, GRAY)
        
        # Display current camera position
        pos_text = f"Pos: ({camera.position.x:.2f}, {camera.position.y:.2f}, {camera.position.z:.2f})".encode('utf-8')
        DrawText(pos_text, 10, SCREEN_HEIGHT - 30, 20, LIGHTGRAY)
        
        EndDrawing()

    # --- De-Initialization ---
    CloseWindow()

if __name__ == "__main__":
    main()
