# AI Maze Solver — A* Search Algorithm 🧩

<p align="center">
 I uploaded a video name Ai-Maze-Solver.mp4 check that for demo
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Algorithm-A*_Search-gold" />
  <img src="https://img.shields.io/badge/Visualization-Pygame-green" />
  <img src="https://img.shields.io/badge/Heuristic-Manhattan-purple" />
  <img src="https://img.shields.io/badge/Status-Production_Ready-brightgreen" />
</p>

---

## 🚀 Overview

A **professional, internship-showcase-ready** implementation of the **A\* Search Algorithm** with real-time visualization using **Pygame**.

The project demonstrates:
- A\* pathfinding with a **Manhattan distance heuristic**
- **Real-time animation** of Open Set (frontier), Closed Set (visited), and shortest path
- **Interactive maze editing** — click to toggle walls
- **Multiple preset mazes** + procedurally generated random mazes
- **Impossible path detection** with clear UI feedback
- **Optimized performance** via `heapq`-based priority queue

---

## ✨ Features

| Feature | Details |
|---|---|
| Grid System | Configurable 2D grid, 4-directional movement |
| A\* Algorithm | f(n) = g(n) + h(n) with Manhattan heuristic |
| Priority Queue | Python `heapq` for O(log n) node extraction |
| Visualization | Pygame real-time animation at configurable speed |
| Open Set | Shown in **blue** — nodes queued for exploration |
| Closed Set | Shown in **purple** — nodes already visited |
| Shortest Path | Shown in **gold** — reconstructed via parent chain |
| Impossible Path | Detected and displayed with red error message |
| Maze Presets | 4 hand-crafted + random DFS-generated mazes |
| Interactive Edit | Left-click = toggle wall; right-click = erase |
| Speed Control | ↑/↓ keys to change animation speed (1–500 sps) |

---

## 📂 Project Structure

```
AI-Maze-Solver/
│
├── main.py          # Entry point — launches Pygame UI or demo mode
├── astar.py         # Core A* algorithm (generator-based, step-by-step)
├── maze.py          # Preset mazes + random DFS maze generator
├── visualizer.py    # Pygame UI, rendering, animation, sidebar
├── demo.py          # Headless terminal demo (no display needed)
├── exporter.py      # Matplotlib PNG exporter for examples/
│
├── requirements.txt
├── README.md
└── examples/        # Auto-generated output images
    ├── Simple_10x10.png
    ├── Winding_15x15.png
    ├── Impossible_Path.png
    ├── Open_Field_12x12.png
    └── Random_10x10.png
```

---

## ⚙️ Installation

### Prerequisites
- Python **3.11+**
- pip

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AI-Maze-Solver.git
cd AI-Maze-Solver

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### Interactive Pygame Visualizer (recommended)
```bash
python main.py
```

### Headless Terminal Demo (no display required)
```bash
python main.py --demo
```

### Export Example PNGs to `examples/`
```bash
python main.py --export
```

---

## 🎮 Controls

| Key / Action | Effect |
|---|---|
| `SPACE` | Pause / Resume animation |
| `R` | Restart search on current maze |
| `←` / `→` | Cycle through maze presets |
| `↑` / `↓` | Increase / Decrease animation speed |
| `Left Click` | Toggle wall on a cell (resets search) |
| `Right Click` | Erase wall from a cell (resets search) |
| Sidebar buttons | Click preset name to load it |

---

## 🧠 Algorithm Details

### A\* Search

```
f(n) = g(n) + h(n)
```

| Term | Meaning |
|---|---|
| `g(n)` | Actual cost from **start** to node `n` |
| `h(n)` | Heuristic estimate from `n` to **goal** (Manhattan distance) |
| `f(n)` | Total estimated cost of the cheapest path through `n` |

### Manhattan Heuristic
```python
h(a, b) = |a.row - b.row| + |a.col - b.col|
```
Admissible (never over-estimates) for 4-directional grids → **guarantees optimal path**.

### Priority Queue (heapq)
Nodes are stored in a **min-heap** ordered by `f`. Each extraction is `O(log n)`,
making the algorithm efficient even for large grids.

### Step-by-step Generator
`astar()` is implemented as a **Python generator** — it `yield`s intermediate states
after each node expansion, enabling frame-by-frame animation without threading.

---

## 🎨 Colour Scheme

| Colour | Meaning |
|---|---|
| 🟢 Green | Start cell |
| 🔴 Red | Goal cell |
| 🔵 Blue | Open Set (frontier) |
| 🟣 Purple | Closed Set (visited) |
| 🟡 Gold | Shortest path |
| 🟠 Orange | Currently evaluated node |
| ⬛ Dark grey | Wall / obstacle |
| ⬜ Charcoal | Free cell |

---

## 📸 Example Outputs

| Maze | Result |
|---|---|
| Simple 10×10 | ![Simple](examples/Simple_10x10.png) |
| Winding 15×15 | ![Winding](examples/Winding_15x15.png) |
| Impossible Path | ![Impossible](examples/Impossible_Path.png) |
| Open Field | ![Open](examples/Open_Field_12x12.png) |

---

## 🏗️ Architecture

```
main.py
  └── visualizer.py  (Pygame UI + event loop)
        ├── astar.py  (A* generator engine)
        └── maze.py   (grid data & random generator)
  └── demo.py         (terminal runner)
        └── astar.py
  └── exporter.py     (matplotlib PNG export)
        └── astar.py + maze.py
```

---

## 📋 Requirements

```
matplotlib>=3.7.0
numpy>=1.24.0
pygame>=2.5.0
```

---

## 👨‍💻 Author

Built as a professional internship showcase project demonstrating:
- Algorithm design (A\* with admissible heuristic)
- Software engineering (clean modules, generators, type hints)
- Interactive visualization (Pygame real-time rendering)
- Python best practices (docstrings, comments, project structure)

---

## 📄 License

MIT License — free to use, modify, and distribute.
