import pyray as rl
from pyray import Vector3, Color
import math
import random

# Physics object class
class PhysicsObject:
    def __init__(self, pos, vel, obj_type, size, color):
        self.pos = Vector3(pos.x, pos.y, pos.z)
        self.vel = Vector3(vel.x, vel.y, vel.z)
        self.type = obj_type  # 'sphere' or 'box'
        self.size = size
        self.color = color
        self.mass = size ** 3 if obj_type == 'box' else (4/3) * math.pi * (size ** 3)
        self.restitution = 0.7  # Bounciness
        
    def update(self, dt, gravity):
        # Apply gravity
        self.vel.y += gravity * dt
        
        # Update position
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt
        self.pos.z += self.vel.z * dt
        
        # Ground collision
        if self.type == 'sphere':
            if self.pos.y - self.size <= 0:
                self.pos.y = self.size
                self.vel.y = -self.vel.y * self.restitution
                self.vel.x *= 0.98  # Friction
                self.vel.z *= 0.98
        else:  # box
            if self.pos.y - self.size/2 <= 0:
                self.pos.y = self.size/2
                self.vel.y = -self.vel.y * self.restitution
                self.vel.x *= 0.98
                self.vel.z *= 0.98
        
        # Wall collisions (arena bounds)
        arena_size = 15
        if self.type == 'sphere':
            r = self.size
        else:
            r = self.size / 2
            
        if abs(self.pos.x) + r > arena_size:
            self.pos.x = arena_size * (1 if self.pos.x > 0 else -1) - r * (1 if self.pos.x > 0 else -1)
            self.vel.x = -self.vel.x * self.restitution
            
        if abs(self.pos.z) + r > arena_size:
            self.pos.z = arena_size * (1 if self.pos.z > 0 else -1) - r * (1 if self.pos.z > 0 else -1)
            self.vel.z = -self.vel.z * self.restitution
    
    def draw(self):
        if self.type == 'sphere':
            rl.draw_sphere(self.pos, self.size, self.color)
            rl.draw_sphere_wires(self.pos, self.size, 8, 8, rl.BLACK)
        else:  # box
            rl.draw_cube(self.pos, self.size, self.size, self.size, self.color)
            rl.draw_cube_wires(self.pos, self.size, self.size, self.size, rl.BLACK)

# Check collision between two spheres
def check_sphere_collision(obj1, obj2):
    if obj1.type != 'sphere' or obj2.type != 'sphere':
        return False
    
    dx = obj2.pos.x - obj1.pos.x
    dy = obj2.pos.y - obj1.pos.y
    dz = obj2.pos.z - obj1.pos.z
    dist_sq = dx*dx + dy*dy + dz*dz
    min_dist = obj1.size + obj2.size
    
    return dist_sq < min_dist * min_dist

def resolve_collision(obj1, obj2):
    # Calculate collision normal
    dx = obj2.pos.x - obj1.pos.x
    dy = obj2.pos.y - obj1.pos.y
    dz = obj2.pos.z - obj1.pos.z
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    if dist < 0.001:
        return
    
    # Normalize
    nx = dx / dist
    ny = dy / dist
    nz = dz / dist
    
    # Separate objects
    overlap = (obj1.size + obj2.size) - dist
    obj1.pos.x -= nx * overlap * 0.5
    obj1.pos.y -= ny * overlap * 0.5
    obj1.pos.z -= nz * overlap * 0.5
    obj2.pos.x += nx * overlap * 0.5
    obj2.pos.y += ny * overlap * 0.5
    obj2.pos.z += nz * overlap * 0.5
    
    # Calculate relative velocity
    dvx = obj2.vel.x - obj1.vel.x
    dvy = obj2.vel.y - obj1.vel.y
    dvz = obj2.vel.z - obj1.vel.z
    
    # Velocity along normal
    vel_along_normal = dvx * nx + dvy * ny + dvz * nz
    
    if vel_along_normal > 0:
        return
    
    # Calculate impulse
    e = min(obj1.restitution, obj2.restitution)
    j = -(1 + e) * vel_along_normal
    j /= (1/obj1.mass + 1/obj2.mass)
    
    # Apply impulse
    impulse_x = j * nx
    impulse_y = j * ny
    impulse_z = j * nz
    
    obj1.vel.x -= impulse_x / obj1.mass
    obj1.vel.y -= impulse_y / obj1.mass
    obj1.vel.z -= impulse_z / obj1.mass
    
    obj2.vel.x += impulse_x / obj2.mass
    obj2.vel.y += impulse_y / obj2.mass
    obj2.vel.z += impulse_z / obj2.mass

# Initialize window
rl.init_window(1200, 800, "3D Physics Playground")
rl.set_target_fps(60)

# Setup camera
camera = rl.Camera3D(
    Vector3(25, 15, 25),
    Vector3(0, 2, 0),
    Vector3(0, 1, 0),
    45,
    rl.CAMERA_PERSPECTIVE
)

# Physics settings
gravity = -20.0
objects = []

# Add initial objects
for i in range(5):
    pos = Vector3(random.uniform(-8, 8), random.uniform(5, 15), random.uniform(-8, 8))
    vel = Vector3(random.uniform(-3, 3), 0, random.uniform(-3, 3))
    size = random.uniform(0.4, 0.8)
    color = Color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255), 255)
    objects.append(PhysicsObject(pos, vel, 'sphere', size, color))

# UI state
show_vectors = False
paused = False

# Main game loop
while not rl.window_should_close():
    dt = rl.get_frame_time()
    if paused:
        dt = 0
    
    # Camera controls
    rl.update_camera(camera, rl.CAMERA_ORBITAL)
    
    # Input handling
    if rl.is_key_pressed(rl.KEY_SPACE):
        paused = not paused
    
    if rl.is_key_pressed(rl.KEY_V):
        show_vectors = not show_vectors
    
    if rl.is_key_pressed(rl.KEY_C):
        objects.clear()
    
    # Spawn sphere
    if rl.is_key_pressed(rl.KEY_B):
        pos = Vector3(random.uniform(-5, 5), 12, random.uniform(-5, 5))
        vel = Vector3(random.uniform(-2, 2), 0, random.uniform(-2, 2))
        size = random.uniform(0.4, 0.9)
        color = Color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255), 255)
        objects.append(PhysicsObject(pos, vel, 'sphere', size, color))
    
    # Spawn box
    if rl.is_key_pressed(rl.KEY_N):
        pos = Vector3(random.uniform(-5, 5), 12, random.uniform(-5, 5))
        vel = Vector3(0, 0, 0)
        size = random.uniform(0.8, 1.5)
        color = Color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255), 255)
        objects.append(PhysicsObject(pos, vel, 'box', size, color))
    
    # Update physics
    for obj in objects:
        obj.update(dt, gravity)
    
    # Check collisions (only for spheres)
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            if check_sphere_collision(objects[i], objects[j]):
                resolve_collision(objects[i], objects[j])
    
    # Drawing
    rl.begin_drawing()
    rl.clear_background(rl.RAYWHITE)
    
    rl.begin_mode_3d(camera)
    
    # Draw ground grid
    rl.draw_grid(30, 1.0)
    
    # Draw arena walls (wireframe only)
    arena_size = 15
    rl.draw_cube_wires(Vector3(0, 5, arena_size), 30, 10, 0.1, rl.BLUE)
    rl.draw_cube_wires(Vector3(0, 5, -arena_size), 30, 10, 0.1, rl.BLUE)
    rl.draw_cube_wires(Vector3(arena_size, 5, 0), 0.1, 10, 30, rl.BLUE)
    rl.draw_cube_wires(Vector3(-arena_size, 5, 0), 0.1, 10, 30, rl.BLUE)
    
    # Draw objects
    for obj in objects:
        obj.draw()
        
        # Draw velocity vectors
        if show_vectors:
            end_pos = Vector3(
                obj.pos.x + obj.vel.x * 0.2,
                obj.pos.y + obj.vel.y * 0.2,
                obj.pos.z + obj.vel.z * 0.2
            )
            rl.draw_line_3d(obj.pos, end_pos, rl.RED)
            rl.draw_sphere(end_pos, 0.1, rl.RED)
    
    rl.end_mode_3d()
    
    # UI
    rl.draw_rectangle(10, 10, 320, 160, Color(0, 0, 0, 150))
    rl.draw_text("3D PHYSICS PLAYGROUND", 20, 20, 20, rl.WHITE)
    rl.draw_text(f"Objects: {len(objects)}", 20, 50, 16, rl.WHITE)
    rl.draw_text("B - Spawn Ball", 20, 75, 14, rl.LIGHTGRAY)
    rl.draw_text("N - Spawn Box", 20, 95, 14, rl.LIGHTGRAY)
    rl.draw_text("V - Toggle Vectors", 20, 115, 14, rl.LIGHTGRAY)
    rl.draw_text("C - Clear All", 20, 135, 14, rl.LIGHTGRAY)
    rl.draw_text("SPACE - Pause", 20, 155, 14, rl.LIGHTGRAY)
    
    status = "PAUSED" if paused else "RUNNING"
    rl.draw_text(status, 1100, 20, 20, rl.YELLOW if paused else rl.GREEN)
    
    rl.draw_fps(1100, 760)
    
    rl.end_drawing()

rl.close_window()