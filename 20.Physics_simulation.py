import pyray as pr
import math

# --- Configuration Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Physics constants
GRAVITY_ACCEL = pr.Vector3(0.0, -9.81, 0.0) # Gravity (m/s^2)
BOUNDS_SIZE = 15.0 # Size of the simulation cube (from center to wall)
FRICTION_FACTOR = 0.85 # Damping for all collisions (elasticity)
THROW_FACTOR = 0.5 # Multiplier for the flick/throw impulse

# Camera Movement constants
CAM_SPEED = 15.0
CAM_SENSITIVITY = 0.15
CAMERA_BOUNDS_SIZE = 18.0 # Maximum distance from origin the camera can travel (slightly larger than BOUNDS_SIZE)
CAM_PITCH_LIMIT_DOT = 0.995 # Dot product limit for pitch (prevents looking exactly up/down, approx 5 degrees from vertical)

# --- Utility Functions for Vector Math ---
def vector3_scale(v, scalar):
    return pr.Vector3(v.x * scalar, v.y * scalar, v.z * scalar)

def vector3_add(v1, v2):
    return pr.Vector3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)

def vector3_subtract(v1, v2):
    return pr.Vector3(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def vector3_length(v):
    return math.sqrt(v.x*v.x + v.y*v.y + v.z*v.z)

def vector3_normalize(v):
    length = vector3_length(v)
    if length == 0.0:
        return pr.Vector3(0.0, 0.0, 0.0)
    return pr.Vector3(v.x / length, v.y / length, v.z / length)

def vector3_dot_product(v1, v2):
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

def vector3_cross_product(v1, v2):
    return pr.Vector3(
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    )

# --- Collision Resolution (Simplified Elastic Collision) ---
def resolve_sphere_collision(s1, s2):
    """
    Handles collision between two spheres, resolving penetration and applying impulse.
    Assumes constant mass for simplicity in penetration resolution.
    """
    
    # Vector from s1 to s2
    n = vector3_subtract(s2.position, s1.position)
    dist = vector3_length(n)
    
    sum_radii = s1.radius + s2.radius
    
    # Check for collision
    if dist < sum_radii:
        # 1. Resolve penetration (Separate the spheres)
        overlap = sum_radii - dist
        
        if dist == 0: 
            # Handle perfect overlap (set arbitrary normal)
            n = pr.Vector3(1.0, 0.0, 0.0) 
        else:
            n = vector3_normalize(n)
            
        # Separate them by half the overlap along the normal vector
        s1.position = vector3_subtract(s1.position, vector3_scale(n, overlap * 0.5))
        s2.position = vector3_add(s2.position, vector3_scale(n, overlap * 0.5))
        
        # 2. Resolve velocity (Impulse/Momentum)
        
        # Relative velocity
        v_rel = vector3_subtract(s1.velocity, s2.velocity)
        
        # Relative velocity along the normal (projection)
        v_n = vector3_dot_product(v_rel, n)
        
        # If objects are moving away from each other, ignore (prevents jitter)
        if v_n < 0:
            # Calculate impulse magnitude (using 1D elastic collision formula)
            # e = FRICTION_FACTOR (Coefficient of Restitution)
            # m1 = s1.mass, m2 = s2.mass
            impulse_magnitude = -(1.0 + FRICTION_FACTOR) * v_n / (1.0/s1.mass + 1.0/s2.mass)
            
            # Change in velocity
            impulse = vector3_scale(n, impulse_magnitude)
            
            # Apply impulse
            s1.velocity = vector3_add(s1.velocity, vector3_scale(impulse, 1.0/s1.mass))
            s2.velocity = vector3_subtract(s2.velocity, vector3_scale(impulse, 1.0/s2.mass))


# --- Manual Ray/Sphere Intersection Utility (Replaces pyray's check_collision_ray_sphere) ---
def ray_sphere_intersection(ray, sphere_position, sphere_radius):
    """Calculates ray-sphere intersection using vector math."""
    # E = Ray Origin - Sphere Center
    e_vec = vector3_subtract(ray.position, sphere_position)
    
    # a = Rd . Rd (Rd is ray direction)
    a = vector3_dot_product(ray.direction, ray.direction) 
    
    # b = 2 * (Rd . E)
    b = 2.0 * vector3_dot_product(ray.direction, e_vec)
    
    # c = (E . E) - r^2
    c = vector3_dot_product(e_vec, e_vec) - (sphere_radius * sphere_radius)
    
    # Discriminant
    discriminant = b*b - 4.0*a*c
    
    # No intersection
    if discriminant < 0.0:
        return False, 0.0, pr.Vector3(0.0, 0.0, 0.0) # Hit, distance, hit_point
    
    # Find the smallest positive t (closest intersection point)
    sqrt_d = math.sqrt(discriminant)
    
    t1 = (-b - sqrt_d) / (2.0 * a)
    t2 = (-b + sqrt_d) / (2.0 * a)
    
    t = 0.0
    
    # Get the smallest positive time t
    if t1 > 0.001:
        t = t1
        if t2 > 0.001 and t2 < t1:
            t = t2
    elif t2 > 0.001:
        t = t2
    else:
        # Intersection is behind the ray origin
        return False, 0.0, pr.Vector3(0.0, 0.0, 0.0)
        
    # Calculate intersection point P = R0 + t * Rd
    hit_point = vector3_add(ray.position, vector3_scale(ray.direction, t))
    
    return True, t, hit_point

# --- Sphere Physics Object ---
class Sphere:
    def __init__(self, position, radius, mass, color):
        self.position = position
        self.velocity = pr.Vector3(0.0, 0.0, 0.0)
        self.radius = radius
        self.mass = mass
        self.color = color
        self.original_color = color # Store the initial color here!
        self.wire_color = pr.BLACK # NEW: Current wireframe color
        self.original_wire_color = pr.BLACK # NEW: Store original wireframe color (always black initially)
        self.is_held = False

    def update(self, dt):
        if not self.is_held:
            # 1. Apply gravity (acceleration)
            self.velocity = vector3_add(self.velocity, vector3_scale(GRAVITY_ACCEL, dt))

            # 2. Update position
            self.position = vector3_add(self.position, vector3_scale(self.velocity, dt))

            # 3. Check and resolve collision with the bounding box
            self.check_bounds()

    def check_bounds(self):
        min_bound = -BOUNDS_SIZE
        max_bound = BOUNDS_SIZE
        
        # X-axis collision
        if self.position.x + self.radius > max_bound:
            self.position.x = max_bound - self.radius
            self.velocity.x *= -FRICTION_FACTOR
        elif self.position.x - self.radius < min_bound:
            self.position.x = min_bound + self.radius
            self.velocity.x *= -FRICTION_FACTOR

        # Y-axis collision (floor/ceiling)
        if self.position.y + self.radius > max_bound:
            self.position.y = max_bound - self.radius
            self.velocity.y *= -FRICTION_FACTOR
        elif self.position.y - self.radius < min_bound:
            self.position.y = min_bound + self.radius
            self.velocity.y *= -FRICTION_FACTOR
            if abs(self.velocity.y) < 0.5: # Simple resting check
                self.velocity.y = 0.0

        # Z-axis collision
        if self.position.z + self.radius > max_bound:
            self.position.z = max_bound - self.radius
            self.velocity.z *= -FRICTION_FACTOR
        elif self.position.z - self.radius < min_bound:
            self.position.z = min_bound + self.radius
            self.velocity.z *= -FRICTION_FACTOR

    def draw(self):
        pr.draw_sphere(self.position, self.radius, self.color)
        # Use the stored wire_color, which will be GOLD when held
        pr.draw_sphere_wires(self.position, self.radius, 10, 10, self.wire_color) 

# --- Camera Movement Helper ---
def update_camera_manual(camera, dt):
    forward = vector3_normalize(vector3_subtract(camera.target, camera.position))
    right = vector3_normalize(vector3_cross_product(forward, camera.up))
    
    movement = pr.Vector3(0.0, 0.0, 0.0)
    speed = CAM_SPEED * dt

    # Horizontal movement (WASD)
    if pr.is_key_down(pr.KEY_W):
        movement = vector3_add(movement, vector3_scale(forward, speed))
    if pr.is_key_down(pr.KEY_S):
        movement = vector3_add(movement, vector3_scale(forward, -speed))
    if pr.is_key_down(pr.KEY_A):
        movement = vector3_add(movement, vector3_scale(right, -speed))
    if pr.is_key_down(pr.KEY_D):
        movement = vector3_add(movement, vector3_scale(right, speed))

    # Vertical movement (SPACE/SHIFT)
    if pr.is_key_down(pr.KEY_SPACE):
        movement = vector3_add(movement, vector3_scale(camera.up, speed))
    if pr.is_key_down(pr.KEY_LEFT_SHIFT) or pr.is_key_down(pr.KEY_RIGHT_SHIFT):
        movement = vector3_add(movement, vector3_scale(camera.up, -speed))

    # Calculate desired new position and clamp it
    new_position = vector3_add(camera.position, movement)

    min_cam_pos = -CAMERA_BOUNDS_SIZE
    max_cam_pos = CAMERA_BOUNDS_SIZE

    new_position.x = max(min_cam_pos, min(max_cam_pos, new_position.x))
    new_position.y = max(min_cam_pos, min(max_cam_pos, new_position.y))
    new_position.z = max(min_cam_pos, min(max_cam_pos, new_position.z))
    
    actual_movement = vector3_subtract(new_position, camera.position)

    # Apply the constrained movement
    camera.position = new_position
    camera.target = vector3_add(camera.target, actual_movement)
    
    # Rotation (Mouse Look)
    mouse_delta = pr.get_mouse_delta()
    
    if mouse_delta.x != 0 or mouse_delta.y != 0:
        yaw = -mouse_delta.x * CAM_SENSITIVITY
        pitch = -mouse_delta.y * CAM_SENSITIVITY
        
        # 1. Start with current forward vector
        forward = vector3_normalize(vector3_subtract(camera.target, camera.position))
        
        # 2. Apply Yaw Rotation (Always safe)
        rotation_matrix_yaw = pr.matrix_rotate(camera.up, yaw * pr.DEG2RAD)
        yawed_forward = pr.vector3_transform(forward, rotation_matrix_yaw)
        
        # 3. Calculate Right vector from Yaw result
        right = vector3_normalize(vector3_cross_product(yawed_forward, camera.up))
        
        # 4. Apply Pitch Rotation
        rotation_matrix_pitch = pr.matrix_rotate(right, pitch * pr.DEG2RAD)
        proposed_forward = pr.vector3_transform(yawed_forward, rotation_matrix_pitch)
        
        # 5. --- Pitch Clamping Check (Fixes Gimbal Lock) ---
        # The dot product of proposed_forward and camera.up (0, 1, 0) gives the cosine of the angle.
        # If abs(dot_product) approaches 1.0, the camera is looking straight up or down.
        dot_up = vector3_dot_product(proposed_forward, camera.up)
        
        if abs(dot_up) < CAM_PITCH_LIMIT_DOT:
            # If the pitch is within limits, accept the proposed rotation
            new_forward = proposed_forward
        else:
            # If the pitch goes out of bounds, only accept the yaw rotation
            # This effectively stops the pitch change at the limit.
            new_forward = yawed_forward
        
        # Update camera target with the constrained forward vector
        camera.target = vector3_add(camera.position, new_forward)
    
    return camera

# --- Main Game Loop ---
def main():
    pr.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Raylib 3D Physics: Sphere Gravity & Throw")
    pr.set_target_fps(FPS)

    # Initialize Camera
    camera = pr.Camera3D()
    camera.position = pr.Vector3(0.0, 5.0, 20.0) # Camera position
    camera.target = pr.Vector3(0.0, 0.0, 0.0)    # Camera looking at point
    camera.up = pr.Vector3(0.0, 1.0, 0.0)       # Camera up vector
    camera.fovy = 60.0                          # Camera field-of-view Y
    camera.projection = pr.CAMERA_PERSPECTIVE   # Camera projection type

    # Initialize Multiple Spheres (The section you can play around with!)
    spheres = [
        # Sphere 1: Small and light
        Sphere(pr.Vector3(-5.0, 5.0, 0.0), 0.7, 0.5, pr.SKYBLUE), 
        # Sphere 2: Medium size, medium mass
        Sphere(pr.Vector3(5.0, 10.0, 0.0), 1.5, 3.0, pr.LIME),
        # Sphere 3: Very small, very light
        Sphere(pr.Vector3(0.0, 15.0, 5.0), 0.5, 0.2, pr.YELLOW),
        # Sphere 4: Large and heavy
        Sphere(pr.Vector3(-10.0, 10.0, -5.0), 2.0, 5.0, pr.MAGENTA)
    ]
    
    # State for Grabbing/Throwing
    held_sphere = None
    held_distance = 0.0
    last_target_pos = pr.Vector3(0.0, 0.0, 0.0)
    
    # Hide the mouse cursor
    pr.disable_cursor()

    while not pr.window_should_close():
        dt = pr.get_frame_time()
        
        # ------------------------------------------------
        # 1. Update Camera and Sphere Movement
        # ------------------------------------------------
        
        # Update camera (WASD, Mouse Look)
        camera = update_camera_manual(camera, dt)
        
        # Update sphere physics and check inter-sphere collisions
        for i, s1 in enumerate(spheres):
            # Update individual sphere physics (gravity, bounds)
            s1.update(dt) 
            
            # Check collisions with all subsequent spheres (to avoid double checks)
            for j in range(i + 1, len(spheres)):
                s2 = spheres[j]
                # Only check collision if neither sphere is being held
                if not s1.is_held and not s2.is_held:
                    resolve_sphere_collision(s1, s2) 

        # ------------------------------------------------
        # 2. Mouse Interaction (Grab, Scroll, Throw)
        # ------------------------------------------------
        
        # Check for grab
        if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT) and held_sphere is None:
            # 1. Create Ray
            ray = None
            try:
                ray = pr.get_mouse_ray(pr.get_mouse_position(), camera)
            except AttributeError:
                try:
                    ray = pr.GetMouseRay(pr.get_mouse_position(), camera)
                except AttributeError:
                    # Reliable Fallback: Use a ray pointing straight out from the camera center (crosshair)
                    ray = pr.Ray()
                    ray.position = camera.position
                    ray.direction = vector3_normalize(vector3_subtract(camera.target, camera.position))
                    
            # 2. Check Collision against all spheres
            if ray is not None:
                closest_hit = float('inf')
                best_sphere = None
                
                # Iterate through all spheres to find the closest hit
                for current_sphere in spheres:
                    hit, distance, hit_point = ray_sphere_intersection(ray, current_sphere.position, current_sphere.radius)
                    
                    if hit and distance < closest_hit:
                        closest_hit = distance
                        best_sphere = current_sphere

                if best_sphere is not None:
                    held_sphere = best_sphere
                    held_sphere.is_held = True
                    held_distance = closest_hit
                    last_target_pos = held_sphere.position
                    # Set the color to RAYWHITE (White) as a visual cue when held
                    held_sphere.color = pr.RAYWHITE 
                    # Set the wireframe color to GOLD for a glowing effect
                    held_sphere.wire_color = pr.GOLD

        # Handle holding and distance scroll
        if held_sphere is not None and pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT):
            
            # Mouse Scroll to change distance
            scroll_delta = pr.get_mouse_wheel_move()
            held_distance -= scroll_delta * 0.5 # Scroll wheel changes distance
            held_distance = max(1.0, min(50.0, held_distance)) # Clamp distance

            # Calculate the target position in front of the camera
            forward = vector3_normalize(vector3_subtract(camera.target, camera.position))
            target_pos = vector3_add(camera.position, vector3_scale(forward, held_distance))
            
            # --- Clamp the target position to keep the sphere inside the bounding box ---
            min_pos = -BOUNDS_SIZE + held_sphere.radius
            max_pos = BOUNDS_SIZE - held_sphere.radius

            target_pos.x = max(min_pos, min(max_pos, target_pos.x))
            target_pos.y = max(min_pos, min(max_pos, target_pos.y))
            target_pos.z = max(min_pos, min(max_pos, target_pos.z))
            # ---------------------------------------------------------------------------------

            # Calculate the velocity of the target point (for throwing impulse)
            target_velocity = vector3_scale(vector3_subtract(target_pos, last_target_pos), 1.0 / dt)

            # Move the held sphere and stop its physics
            held_sphere.position = target_pos
            held_sphere.velocity = pr.Vector3(0, 0, 0)
            
            # Update for next frame's velocity calculation
            last_target_pos = target_pos

        # Handle release and throw
        if held_sphere is not None and pr.is_mouse_button_released(pr.MOUSE_BUTTON_LEFT):
            # Apply throwing impulse (using the target's last velocity)
            held_sphere.velocity = vector3_scale(target_velocity, THROW_FACTOR)
            held_sphere.is_held = False
            # Restore the sphere's original color upon release
            held_sphere.color = held_sphere.original_color 
            # Restore the sphere's original wire color
            held_sphere.wire_color = held_sphere.original_wire_color
            
            held_sphere = None
            last_target_pos = pr.Vector3(0.0, 0.0, 0.0) # Reset

        # ------------------------------------------------
        # 3. Drawing
        # ------------------------------------------------

        pr.begin_drawing()
        pr.clear_background(pr.DARKGRAY)

        pr.begin_mode_3d(camera)
        
        # Draw the Bounding Box (Simulation Volume)
        pr.draw_cube_wires(pr.Vector3(0, 0, 0), BOUNDS_SIZE * 2, BOUNDS_SIZE * 2, BOUNDS_SIZE * 2, pr.RAYWHITE)
        
        # Draw the ground plane at the bottom boundary for better visualization
        floor_position = pr.Vector3(0.0, -BOUNDS_SIZE, 0.0)
        floor_size = BOUNDS_SIZE * 2
        pr.draw_plane(floor_position, pr.Vector2(floor_size, floor_size), pr.DARKGREEN)
        
        # Draw all Spheres
        for s in spheres:
            s.draw()
        
        pr.end_mode_3d()

        # ------------------------------------------------
        # 4. Draw UI and Instructions
        # ------------------------------------------------
        
        # --- Draw Center Cursor (Crosshair) ---
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        crosshair_size = 10
        crosshair_thickness = 1
        
        # Horizontal line
        pr.draw_rectangle(center_x - crosshair_size, center_y - crosshair_thickness, 
                          crosshair_size * 2, crosshair_thickness * 2, pr.RAYWHITE)
        # Vertical line
        pr.draw_rectangle(center_x - crosshair_thickness, center_y - crosshair_size, 
                          crosshair_thickness * 2, crosshair_size * 2, pr.RAYWHITE)
        # Center dot
        pr.draw_rectangle(center_x - 1, center_y - 1, 2, 2, pr.RED)
        # -------------------------------------------
        
        pr.draw_rectangle(10, 10, 350, 130, pr.fade(pr.BLACK, 0.7))
        pr.draw_text("3D Physics Sandbox (Multi-Sphere)", 20, 20, 20, pr.YELLOW)
        pr.draw_line(20, 45, 340, 45, pr.GRAY)

        pr.draw_text("Movement:", 20, 60, 16, pr.WHITE)
        pr.draw_text("WASD: Move | SPACE: Up | SHIFT: Down", 30, 80, 14, pr.LIME)
        pr.draw_text("Mouse: Look", 30, 95, 14, pr.LIME)
        
        pr.draw_text("Interaction:", 20, 110, 16, pr.WHITE)
        pr.draw_text("LMB Click/Hold: Grab | Scroll: Change Distance", 30, 130, 14, pr.LIME)

        # Status text for holding (still red, as this is an alert status)
        if held_sphere is not None:
             pr.draw_text("SPHERE HELD (Throw by flicking mouse/releasing LMB)", 
                          SCREEN_WIDTH - 500, SCREEN_HEIGHT - 30, 18, pr.RED)

        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()
