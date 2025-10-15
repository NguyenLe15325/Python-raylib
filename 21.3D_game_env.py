import pyray
import math

# --- Configuration Constants ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# World constants
GRAVITY = -20.0 # Acceleration due to gravity (m/s^2)
PLAYER_SPEED = 10.0 # Horizontal movement speed
JUMP_VELOCITY = 10.0 # Initial vertical velocity for a jump
# TP: Initial offset for third-person camera
THIRD_PERSON_OFFSET = pyray.Vector3(-10.0, 10.0, -10.0) 
MOUSE_SENSITIVITY = 0.005 # Sensitivity for camera rotation (Mouse Look)

# Player model size
PLAYER_SIZE = 2.0 
PLAYER_HALF_SIZE = PLAYER_SIZE / 2.0

# Static Obstacles (Position, Size, Color)
# These are defined as (center_position, dimensions, color)
OBSTACLES = [
    # Blue Cube (Short platform)
    (pyray.Vector3(15.0, 1.5, -5.0), pyray.Vector3(3.0, 3.0, 3.0), pyray.BLUE), 
    # Orange Cube (Tall tower)
    (pyray.Vector3(-10.0, 4.0, 20.0), pyray.Vector3(8.0, 8.0, 8.0), pyray.ORANGE),
    # Green Cube (Medium Block)
    (pyray.Vector3(-20.0, 2.5, -20.0), pyray.Vector3(5.0, 5.0, 5.0), pyray.GREEN),
]

class Player:
    """Represents the player-controlled character."""
    def __init__(self, position):
        self.position = position
        self.velocity_y = 0.0 # Vertical velocity for jumping/gravity
        self.is_grounded = True
        self.yaw = 0.0 # Horizontal rotation around the Y axis (driven by mouse look)
        self.pitch = 0.0 # Pitch rotation (unused here, managed by camera_pitch in main)

    def update_movement(self, dt, camera):
        """
        Handles user input for movement. Movement is relative to the player's yaw
        which is driven by the camera/mouse look for a consistent feel.
        """
        
        # Calculate base movement vectors based on player's yaw
        # Sine for X, Cosine for Z (Standard math coordinates to Pyray/raylib)
        forward_x = -math.sin(self.yaw)
        forward_z = math.cos(self.yaw)
        
        # Right vector (perpendicular to forward)
        right_x = math.cos(self.yaw)
        right_z = math.sin(self.yaw)
        
        move_direction = pyray.Vector3(0.0, 0.0, 0.0)
        
        # --- Handle Movement (WASD) ---
        if pyray.is_key_down(pyray.KEY_W):
            move_direction.x += forward_x
            move_direction.z += forward_z
        if pyray.is_key_down(pyray.KEY_S):
            move_direction.x -= forward_x
            move_direction.z -= forward_z
        if pyray.is_key_down(pyray.KEY_D):
            # FIX: Reversing A/D movement again as requested by the user. D (Right strafe) now uses -Right vector.
            move_direction.x -= right_x
            move_direction.z -= right_z
        if pyray.is_key_down(pyray.KEY_A):
            # FIX: Reversing A/D movement again as requested. A (Left strafe) now uses +Right vector.
            move_direction.x += right_x
            move_direction.z += right_z
            
        # Normalize combined movement direction and apply speed
        if pyray.vector3_length_sqr(move_direction) > 0.0001:
            move_direction = pyray.vector3_normalize(move_direction)
            movement = pyray.vector3_scale(move_direction, PLAYER_SPEED * dt)
            
            # Apply horizontal movement
            self.position = pyray.vector3_add(self.position, movement)
            
        # --- Handle Jump (Space) ---
        if pyray.is_key_pressed(pyray.KEY_SPACE) and self.is_grounded:
            self.velocity_y = JUMP_VELOCITY
            self.is_grounded = False

    def update_physics(self, dt):
        """Applies gravity."""
        
        # Apply gravity
        self.velocity_y += GRAVITY * dt
        
        # Update vertical position
        self.position.y += self.velocity_y * dt

def check_and_resolve_collisions(player):
    """
    Checks for AABB collision between the player and the ground (y=0) and all obstacles,
    and resolves the position to prevent intersection.
    """
    
    # Reset grounded status before checking collisions
    player.is_grounded = False
    
    # --- 1. Ground Collision (Floor at y=0) ---
    min_y = PLAYER_HALF_SIZE 
    if player.position.y <= min_y:
        player.position.y = min_y
        player.velocity_y = 0.0 
        player.is_grounded = True
        
    # Simple bounds check to keep the player near the center (optional)
    world_limit = 50.0
    player.position.x = max(-world_limit, min(world_limit, player.position.x))
    player.position.z = max(-world_limit, min(world_limit, player.position.z))

    # --- 2. Obstacle Collisions (AABB vs AABB) ---
    player_min = pyray.vector3_subtract(player.position, pyray.Vector3(PLAYER_HALF_SIZE, PLAYER_HALF_SIZE, PLAYER_HALF_SIZE))
    player_max = pyray.vector3_add(player.position, pyray.Vector3(PLAYER_HALF_SIZE, PLAYER_HALF_SIZE, PLAYER_HALF_SIZE))

    for obs_pos, obs_size, _ in OBSTACLES:
        obs_half_size = pyray.vector3_scale(obs_size, 0.5)
        
        obs_min = pyray.vector3_subtract(obs_pos, obs_half_size)
        obs_max = pyray.vector3_add(obs_pos, obs_half_size)

        # Check for non-overlap
        overlap_x = player_max.x > obs_min.x and player_min.x < obs_max.x
        overlap_y = player_max.y > obs_min.y and player_min.y < obs_max.y
        overlap_z = player_max.z > obs_min.z and player_min.z < obs_max.z
        
        if overlap_x and overlap_y and overlap_z:
            # Collision occurred: Calculate penetration and resolve
            
            # Penetration depths along each axis
            dx1 = obs_max.x - player_min.x
            dx2 = player_max.x - obs_min.x
            penetration_x = min(dx1, dx2)
            
            dy1 = obs_max.y - player_min.y
            dy2 = player_max.y - obs_min.y
            penetration_y = min(dy1, dy2)
            
            dz1 = obs_max.z - player_min.z
            dz2 = player_max.z - obs_min.z
            penetration_z = min(dz1, dz2)
            
            # Find the minimum penetration depth (axis of least resistance)
            min_penetration = min(penetration_x, penetration_y, penetration_z)
            
            # Calculate direction vector (from player center to obstacle center)
            delta_x = obs_pos.x - player.position.x
            delta_y = obs_pos.y - player.position.y
            delta_z = obs_pos.z - player.position.z

            # Response: Resolve along the axis with minimum penetration
            # FIX: Use center delta to reliably determine push direction
            if min_penetration == penetration_y:
                # Vertical collision (Most critical for landing/ceiling)
                if delta_y < 0: 
                    # Obstacle center is below player center (i.e., player is landing on it)
                    player.position.y += penetration_y # Push UP
                    player.is_grounded = True
                    player.velocity_y = 0.0
                else: 
                    # Obstacle center is above player center (i.e., player hit ceiling)
                    player.position.y -= penetration_y # Push DOWN
                    player.velocity_y = 0.0
                    
            elif min_penetration == penetration_x:
                # Horizontal X-axis collision
                if delta_x < 0: 
                    # Obstacle center is LEFT of player center, push player RIGHT (+X)
                    player.position.x += penetration_x
                else: 
                    # Obstacle center is RIGHT of player center, push player LEFT (-X)
                    player.position.x -= penetration_x
                    
            elif min_penetration == penetration_z:
                # Horizontal Z-axis collision
                if delta_z < 0: 
                    # Obstacle center is BEHIND player center, push player FORWARD (+Z)
                    player.position.z += penetration_z
                else: 
                    # Obstacle center is IN FRONT of player center, push player BACKWARD (-Z)
                    player.position.z -= penetration_z

def update_camera(camera, player, dt, camera_mode, camera_pitch):
    """
    Updates the camera position and rotation based on the current mode (THIRD or FIRST).
    Updates player.yaw based on mouse input.
    Returns the updated camera_pitch.
    """
    
    # --- 1. Mouse Rotation (Applies to both modes) ---
    mouse_delta = pyray.get_mouse_delta()
    
    # Update player yaw (horizontal rotation) based on mouse X movement
    player.yaw += mouse_delta.x * MOUSE_SENSITIVITY
    
    # Update camera pitch (vertical rotation) based on mouse Y movement
    camera_pitch -= mouse_delta.y * MOUSE_SENSITIVITY
    # Clamp pitch to prevent flipping the camera
    camera_pitch = max(-math.pi / 2.0, min(math.pi / 2.0, camera_pitch))

    # --- 2. Camera Positioning and Target Setting ---
    
    # Calculate the look vector based on the player's yaw and pitch
    target_dir_x = -math.sin(player.yaw) * math.cos(camera_pitch)
    target_dir_y = math.sin(camera_pitch)
    target_dir_z = math.cos(player.yaw) * math.cos(camera_pitch)
    look_vector = pyray.vector3_normalize(pyray.Vector3(target_dir_x, target_dir_y, target_dir_z))

    if camera_mode == 'THIRD':
        # --- THIRD PERSON CAMERA LOGIC ---
        
        # The camera offset is scaled backwards along the look vector
        # The 12.0 determines how far back the camera sits
        camera.position = pyray.vector3_subtract(
            pyray.Vector3(player.position.x, player.position.y + PLAYER_HALF_SIZE * 0.5, player.position.z), 
            pyray.vector3_scale(look_vector, 12.0)
        )
        # Add a bit of lift to the position for a better TP angle
        camera.position.y += 5.0

        camera.target = player.position # Always look at the player

    elif camera_mode == 'FIRST':
        # --- FIRST PERSON CAMERA LOGIC ---
        
        # Position: Eye level of the player
        camera.position = pyray.Vector3(
            player.position.x, 
            player.position.y + PLAYER_HALF_SIZE * 0.5, # Slightly above player center
            player.position.z
        )
        
        # Target: Point one unit in front of the camera along the look vector
        camera.target = pyray.vector3_add(camera.position, look_vector)
        
    return camera_pitch

def draw_scene(camera, player, camera_mode):
    """Draws the 3D environment and the player."""
    
    pyray.begin_mode_3d(camera)

    # Draw the ground plane (y=0)
    pyray.draw_grid(100, 1.0)
    pyray.draw_plane(pyray.Vector3(0.0, 0.0, 0.0), pyray.Vector2(100.0, 100.0), pyray.Color(50, 50, 50, 255))

    # --- Draw the Player (Rotated Cube) ---
    # Only draw the player cube in Third-Person mode
    if camera_mode == 'THIRD':
        rotation_axis = pyray.Vector3(0.0, 1.0, 0.0)
        pyray.rl_push_matrix()
        
        pyray.rl_translatef(player.position.x, player.position.y, player.position.z)
        # Use player yaw for visual rotation
        pyray.rl_rotatef(player.yaw * (180.0 / math.pi), rotation_axis.x, rotation_axis.y, rotation_axis.z)
        
        pyray.draw_cube(pyray.Vector3(0.0, 0.0, 0.0), PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE, pyray.RED)
        pyray.draw_cube_wires(pyray.Vector3(0.0, 0.0, 0.0), PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE, pyray.DARKGRAY)
        
        pyray.rl_pop_matrix()
    
    # --- Draw Obstacles ---
    for obs_pos, obs_size, obs_color in OBSTACLES:
        # Draw Solid
        pyray.draw_cube(obs_pos, obs_size.x, obs_size.y, obs_size.z, obs_color)
        # Draw Wires (AABB visualizer)
        pyray.draw_cube_wires(obs_pos, obs_size.x, obs_size.y, obs_size.z, pyray.fade(obs_color, 0.5))

    pyray.end_mode_3d()


def main():
    """Main game loop."""
    pyray.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "3D Character Control Game")
    pyray.set_target_fps(FPS)
    
    # --- Setup Player ---
    player = Player(pyray.Vector3(0.0, PLAYER_HALF_SIZE, 0.0))

    # --- Setup Camera ---
    camera = pyray.Camera3D()
    camera.up = pyray.Vector3(0.0, 1.0, 0.0)
    camera.fovy = 60.0
    camera.projection = pyray.CAMERA_PERSPECTIVE
    
    # --- Camera State ---
    camera_mode = 'THIRD' # 'THIRD' or 'FIRST'
    camera_pitch = 0.0 # Vertical rotation in radians (common to both modes)

    # Lock cursor in the center of the screen for better FPS controls
    # pyray.set_mouse_cursor(pyray.MOUSE_CURSOR_HIDDEN) <-- REMOVED: Caused AttributeError
    pyray.disable_cursor()
    
    # Main game loop
    while not pyray.window_should_close():
        dt = pyray.get_frame_time()
        
        # --- Input Toggle ---
        if pyray.is_key_pressed(pyray.KEY_C):
            if camera_mode == 'THIRD':
                camera_mode = 'FIRST'
            else:
                camera_mode = 'THIRD'
                
        # --- Update ---
        player.update_movement(dt, camera)
        player.update_physics(dt)
        
        # Collision detection MUST run AFTER movement and physics updates
        check_and_resolve_collisions(player)
        
        # Update camera position and player rotation based on mouse input
        camera_pitch = update_camera(camera, player, dt, camera_mode, camera_pitch)

        # --- Draw ---
        pyray.begin_drawing()
        pyray.clear_background(pyray.BLACK)

        draw_scene(camera, player, camera_mode)

        # Draw UI instructions
        mode_color = pyray.YELLOW if camera_mode == 'FIRST' else pyray.GREEN
        pyray.draw_text(f"Camera Mode: {camera_mode} PERSON (Press C to switch)", 10, 10, 20, mode_color)
        pyray.draw_text("Controls:", 10, 40, 20, pyray.WHITE)
        pyray.draw_text(" - WASD: Move Character (Relative to view)", 10, 60, 20, pyray.BLUE)
        pyray.draw_text(" - SPACE: Jump", 10, 80, 20, pyray.BLUE)
        pyray.draw_text(" - MOUSE: Look Around (Cursor Locked)", 10, 100, 20, pyray.RED)
        pyray.draw_text(" - C: Toggle Camera Mode", 10, 120, 20, pyray.RED)
        pyray.draw_text(f"Grounded: {player.is_grounded}", WINDOW_WIDTH - 200, 10, 20, pyray.GREEN)

        pyray.end_drawing()

    # Re-enable cursor before closing
    pyray.enable_cursor()
    pyray.close_window()

if __name__ == "__main__":
    main()
