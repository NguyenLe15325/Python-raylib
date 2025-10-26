# 🎮 Python-raylib

<div align="center">

![Python](https://img.shields.io/badge/python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Raylib](https://img.shields.io/badge/raylib-powered-red?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Games](https://img.shields.io/badge/demos-20+-orange?style=for-the-badge)

**Game demo collection using [raylib](https://www.raylib.com/) in Python**

*Explore game loops • 2D/3D graphics • Physics simulation • Interactive demos*

</div>

---

## 🚀 Project Overview

This repository presents a variety of small games and graphics demos written in Python using the **raylib** library. It's ideal for exploring game-loop structure, 2D/3D graphics, physics simulation, and interactive demos.

Whether you're learning game development or experimenting with new ideas, these demos provide hands-on examples of core concepts in action.

> **Note:** Demo code in this repository was generated with assistance from Google Gemini and Claude AI, and refined through experimentation.

---

## 📂 Contents

Each file demonstrates a different concept. Example files include:

<table>
<tr>
<td width="50%">

### 🎯 Basic Demos
- `1.ball.py` — Simple bouncing ball demo
- `3.Pong.py` — Classic Pong game logic
- `4.Pong_2player.py` — Two-player Pong variant

### 🎮 Platformers & 2D
- `10.2D_platformer_camera.py` — 2D platformer with camera control
- And more 2D game mechanics...

</td>
<td width="50%">

### 🌐 3D Graphics
- `16.Basic_3D.py` — Introductory 3D scene
- 3D rendering and camera demos

### ⚛️ Physics Simulations
- `19.Physics_playground.py` — Basic physics sandbox
- `20.Physics_simulation.py` — Advanced physics demos

</td>
</tr>
</table>

*See the full list of 20+ demos in the repository!*

---

## 🧩 Why Use raylib + Python?

<table>
<tr>
<td align="center" width="25%">
<img src="https://raw.githubusercontent.com/raysan5/raylib/master/logo/raylib_logo_animation.gif" width="80" alt="raylib"/>
<br><strong>Simple API</strong>
<br>Easy-to-use interface for graphics, input, and sound
</td>
<td align="center" width="25%">
📚<br><strong>Educational</strong>
<br>Perfect for learning game loops, rendering, and physics
</td>
<td align="center" width="25%">
🖥️<br><strong>Cross-platform</strong>
<br>Works on Windows, macOS, and Linux
</td>
<td align="center" width="25%">
⚡<br><strong>Rapid Prototyping</strong>
<br>Mix Python simplicity with real-time graphics
</td>
</tr>
</table>

---

## 🛠 Getting Started

### Prerequisites

- **Python 3.x** installed on your system
- **raylib Python binding** — Install via pip:

```bash
pip install raylib-py
```

> **Note:** If you use a different binding or version (e.g., `raylib-python-cffi`), adjust the import statements accordingly.

### Running a Demo

1. **Clone this repository:**
   ```bash
   git clone https://github.com/NguyenLe15325/Python-raylib.git
   cd Python-raylib
   ```

2. **Run one of the demos:**
   ```bash
   python 3.Pong.py
   ```

3. **Explore, modify, and experiment!**
   - Change colors, speeds, or physics parameters
   - Add new features or mechanics
   - Build your own game using these as templates

---

## 🎯 Suggested Learning Path

Follow this progression to get the most out of these demos:

**1. 🟢 Start with basics** (`1.ball.py`)  
↓ *Understand the game loop and rendering*

**2. 🟡 Add input** (`3.Pong.py`, `4.Pong_2player.py`)  
↓ *Progress to input-driven games*

**3. 🟠 Explore platformers** (`10.2D_platformer_camera.py`)  
↓ *Learn camera control and advanced 2D mechanics*

**4. 🔴 Try 3D** (`16.Basic_3D.py`)  
↓ *Dive into 3D scenes and rendering*

**5. 🟣 Physics** (`19.Physics_playground.py`, `20.Physics_simulation.py`)  
↓ *Experiment with physics simulations*

**6. ⚫ Build your own!**  
*Extend a demo: add new mechanics, change assets, or create something original!*

---

## 💡 Demo Highlights

### 🏓 Classic Pong (`3.Pong.py`)
Experience the fundamentals of collision detection, scoring systems, and AI opponents.

### 🎮 2D Platformer (`10.2D_platformer_camera.py`)
Learn about character movement, gravity, jumping mechanics, and dynamic camera following.

### 🌍 3D Basics (`16.Basic_3D.py`)
Explore 3D rendering, camera positioning, and basic 3D object manipulation.

### ⚛️ Physics Playground (`19.Physics_playground.py`)
Experiment with gravity, collisions, forces, and realistic object interactions.

---

## ⭐ Featured Project: 3D Physics Simulation

<div align="center">

### 🚀 `20.Physics_simulation.py` - Interactive 3D Physics Engine

*The crown jewel of this collection - a fully interactive 3D physics sandbox!*

<img src="assets/Physics_simulation.gif" alt="Physics Simulation Demo" loop="infinite" />

</div>

#### 🎯 What Makes It Special

This demo showcases a complete 3D physics simulation environment where you can interact with multiple spherical objects in real-time. It's not just a demonstration—it's a fully playable physics sandbox that responds to your every action!

#### ✨ Key Features

- **🕹️ Free Camera Movement** — Navigate through 3D space with WASD controls and mouse look
- **🤲 Object Interaction** — Hold and throw spheres with realistic physics
- **⚡ Real-time Physics** — Watch objects bounce, collide, and interact with gravity
- **🎨 Multiple Objects** — Experiment with spheres of different sizes, masses, and colors
- **🔧 Highly Configurable** — Tweak physics parameters to create your own simulation

#### 🎮 Controls

| Input | Action |
|-------|--------|
| `W` `A` `S` `D` | Move camera forward/left/back/right |
| `Space` / `Left Shift` | Move camera up/down |
| `Mouse` | Look around (first-person view) |
| `Left Click` | Grab/hold sphere |
| `Mouse Scroll` | Adjust grabbed object's distance from camera |
| `Release Click` | Throw sphere (velocity based on mouse movement) |
| `ESC` | Exit simulation |

#### ⚙️ Configurable Parameters

The simulation is designed to be tweaked! Here are some parameters you can adjust:

```python
# Screen Settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Physics Constants
GRAVITY_ACCEL = Vector3(0.0, -9.81, 0.0)  # Earth-like gravity
BOUNDS_SIZE = 15.0                         # Simulation cube size
FRICTION_FACTOR = 0.85                     # Bounce elasticity (0-1)
THROW_FACTOR = 0.5                         # Throw strength multiplier

# Camera Settings
CAM_SPEED = 15.0                          # Movement speed
CAM_SENSITIVITY = 0.15                    # Mouse sensitivity
CAMERA_BOUNDS_SIZE = 18.0                 # Camera movement limits
```

#### 🎨 Customize Your Spheres

Create your own physics objects with different properties:

```python
spheres = [
    # Small and light - bounces easily
    Sphere(Vector3(-5.0, 5.0, 0.0), radius=0.7, mass=0.5, color=SKYBLUE),
    
    # Medium size - balanced behavior
    Sphere(Vector3(5.0, 10.0, 0.0), radius=1.5, mass=3.0, color=LIME),
    
    # Tiny and floaty - fun to throw
    Sphere(Vector3(0.0, 15.0, 5.0), radius=0.5, mass=0.2, color=YELLOW),
    
    # Large and heavy - powerful collisions
    Sphere(Vector3(-10.0, 10.0, -5.0), radius=2.0, mass=5.0, color=MAGENTA)
]
```

#### 🔬 What You'll Learn

- **3D Camera Systems** — First-person camera with constraints and smooth movement
- **Vector Physics** — Velocity, acceleration, and force calculations in 3D
- **Collision Detection** — Sphere-to-sphere and sphere-to-boundary collisions
- **Realistic Interactions** — Momentum transfer, friction, and energy conservation
- **Input Handling** — Mouse picking and drag-to-throw mechanics
- **Performance Optimization** — Efficient physics updates at 60 FPS

#### 💡 Experiment Ideas

Try these modifications to learn more:

1. **Adjust gravity** — What happens in low gravity? Or with reversed gravity?
2. **Change elasticity** — Make everything super bouncy or completely inelastic
3. **Add more spheres** — How many objects can the simulation handle?
4. **Modify masses** — Create very heavy or very light objects and observe interactions
5. **Change bounds** — Make the simulation space larger or smaller
6. **Add spin** — Implement rotational physics for even more realism

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You're free to use, modify, and distribute this code for personal or commercial projects.

---

## 🤝 Acknowledgements

<div align="center">

**[raylib](https://www.raylib.com/)** — Amazing lightweight graphics/game library by [Ramon Santamaria](https://github.com/raysan5)

**The open-source Python community** — For bindings, examples, and endless inspiration

**[Google Gemini](https://gemini.google.com/)** & **[Claude AI](https://claude.ai/)** — AI assistance in generating and refining demo code

</div>

---

## 🎓 Additional Resources

### 📚 Official Documentation
- [Raylib Official Website](https://www.raylib.com/)
- [Raylib Cheatsheet](https://www.raylib.com/cheatsheet/cheatsheet.html)
- [Raylib Examples](https://www.raylib.com/examples.html)
- [Python Raylib Documentation](https://electronstudio.github.io/raylib-python-cffi/)

### 🎥 Video Tutorials
- [The ultimate introduction to Raylib [2D & 3D game dev]](https://www.youtube.com/watch?v=UoAsDlUwjy0&t=422s)
- [Getting Started with Raylib](https://www.youtube.com/results?search_query=raylib+python+tutorial)
- [Game Development Tutorials](https://www.youtube.com/results?search_query=raylib+game+development)

---

## 📧 Contact & Links

<div align="center">

**Nguyen Le** • [@NguyenLe15325](https://github.com/NguyenLe15325)

[🌟 Star this repo](https://github.com/NguyenLe15325/Python-raylib) • [🐛 Report Bug](https://github.com/NguyenLe15325/Python-raylib/issues) • [💡 Request Feature](https://github.com/NguyenLe15325/Python-raylib/issues)

</div>

---

<div align="center">

### 🎮 Have fun exploring game development with Python & raylib!

*Made with ❤️ and Python*

⭐ **If you find this helpful, consider starring the repository!** ⭐

</div>