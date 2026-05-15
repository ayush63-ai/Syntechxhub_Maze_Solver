"""
maze.py — Maze Generator & Preset Library
==========================================
Provides:
  - MazeGenerator: random maze creation via Recursive Backtracker DFS
  - PRESETS: hand-crafted example mazes for demo / showcase

Grid convention:
  0 = free cell
  1 = wall / obstacle
"""

import random


# ─────────────────────────────────────────────
#  Preset Mazes
# ─────────────────────────────────────────────
PRESETS = {
    "Simple 10×10": {
        "grid": [
            [0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,0,1,1,1,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,0,1,1,1,1,0,1,0],
            [0,0,0,1,0,0,1,0,0,0],
            [0,1,0,1,0,1,1,1,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,0,1,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
        ],
        "start": (0, 0),
        "goal":  (9, 9),
    },
    "Winding 15×15": {
        "grid": [
            [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
            [1,1,1,1,0,1,0,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,1,0,0,0,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,0,1,0],
            [0,1,0,0,0,0,0,0,0,0,0,1,0,1,0],
            [0,1,0,1,1,1,1,1,1,1,0,1,0,1,0],
            [0,1,0,1,0,0,0,0,0,1,0,1,0,0,0],
            [0,1,0,1,0,1,1,1,0,1,0,1,1,1,0],
            [0,1,0,1,0,1,0,0,0,1,0,0,0,1,0],
            [0,1,0,1,0,1,0,1,1,1,1,1,0,1,0],
            [0,1,0,0,0,1,0,0,0,0,0,1,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,0,1,0,1,0],
            [0,0,0,0,0,0,0,0,0,1,0,0,0,1,0],
            [1,1,1,1,1,1,1,1,0,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ],
        "start": (0, 0),
        "goal":  (14, 14),
    },
    "Impossible Path": {
        "grid": [
            [0,0,0,0,0],
            [0,1,1,1,0],
            [0,1,0,1,0],
            [0,1,1,1,0],
            [0,0,0,0,0],
        ],
        "start": (0, 0),
        "goal":  (2, 2),   # Surrounded by walls
    },
    "Open Field 12×12": {
        "grid": [[0]*12 for _ in range(12)],
        "start": (0, 0),
        "goal":  (11, 11),
    },
}


# ─────────────────────────────────────────────
#  Random Maze Generator
# ─────────────────────────────────────────────
class MazeGenerator:
    """
    Generates a random perfect maze using Recursive Backtracker (DFS).

    Works on a logical grid of 'cells'; walls exist between cells.
    The physical grid size is (2*rows+1) x (2*cols+1).
    """

    def __init__(self, rows: int = 10, cols: int = 10, seed: int | None = None):
        self.rows = rows
        self.cols = cols
        self.rng  = random.Random(seed)

    def generate(self) -> dict:
        """Return dict with keys: grid, start, goal."""
        r, c = self.rows, self.cols
        # Physical grid: all walls initially
        grid = [[1] * (2 * c + 1) for _ in range(2 * r + 1)]

        # Carve starting cell
        visited = [[False] * c for _ in range(r)]
        self._dfs(grid, visited, 0, 0)

        # Ensure start and goal cells are open
        grid[1][1] = 0
        grid[2 * r - 1][2 * c - 1] = 0

        return {
            "grid":  grid,
            "start": (1, 1),
            "goal":  (2 * r - 1, 2 * c - 1),
        }

    # ── Private helpers ──────────────────────────────────
    def _dfs(self, grid, visited, row, col):
        visited[row][col] = True
        # Physical coordinate
        pr, pc = 2 * row + 1, 2 * col + 1
        grid[pr][pc] = 0

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.rng.shuffle(directions)

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not visited[nr][nc]:
                # Carve wall between current and neighbour
                grid[pr + dr][pc + dc] = 0
                self._dfs(grid, visited, nr, nc)
