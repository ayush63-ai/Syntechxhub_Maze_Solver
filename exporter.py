"""
exporter.py — Matplotlib Static Export
========================================
Generates high-quality PNG images of solved mazes
using matplotlib and saves them to examples/.

Used for README screenshots and GitHub showcase.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # headless backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap

from astar import astar
from maze import PRESETS, MazeGenerator


# ── Colour map indices ────────────────────────────────────────
IDX_FREE    = 0
IDX_WALL    = 1
IDX_OPEN    = 2
IDX_CLOSED  = 3
IDX_PATH    = 4
IDX_START   = 5
IDX_GOAL    = 6
IDX_CURRENT = 7

CMAP = ListedColormap([
    "#1a1f27",   # free
    "#30363d",   # wall
    "#388bfd",   # open
    "#6e40aa",   # closed
    "#ffd700",   # path
    "#3fb950",   # start
    "#f85149",   # goal
    "#ff8c00",   # current
])


def _solve_full(grid, start, goal):
    """Run A* fully and collect all intermediate states."""
    states = []
    for s in astar(grid, start, goal):
        states.append(s)
    return states


def _build_image(grid, start, goal, state):
    """Build a numpy 2D array with colour indices."""
    rows = len(grid); cols = len(grid[0])
    img = np.full((rows, cols), IDX_FREE, dtype=int)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                img[r][c] = IDX_WALL

    for pos in state["closed_set"]:
        img[pos[0]][pos[1]] = IDX_CLOSED
    for pos in state["open_set"]:
        img[pos[0]][pos[1]] = IDX_OPEN
    for pos in state["path"]:
        img[pos[0]][pos[1]] = IDX_PATH
    if state["current"]:
        img[state["current"][0]][state["current"][1]] = IDX_CURRENT

    img[start[0]][start[1]] = IDX_START
    img[goal[0]][goal[1]]   = IDX_GOAL
    return img


def export_examples(out_dir: str = "examples"):
    os.makedirs(out_dir, exist_ok=True)

    all_mazes = dict(PRESETS)
    mg = MazeGenerator(rows=10, cols=10, seed=7)
    all_mazes["Random 10×10"] = mg.generate()

    for name, data in all_mazes.items():
        grid  = [row[:] for row in data["grid"]]
        start = data["start"]
        goal  = data["goal"]

        states = _solve_full(grid, start, goal)
        final_state = states[-1]

        img = _build_image(grid, start, goal, final_state)

        fig, ax = plt.subplots(figsize=(10, 8), facecolor="#0d1117")
        ax.set_facecolor("#0d1117")

        ax.imshow(img, cmap=CMAP, vmin=0, vmax=7, interpolation="nearest")

        # Grid lines
        rows = len(grid); cols = len(grid[0])
        ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
        ax.grid(which="minor", color="#1a1f27", linewidth=0.5)
        ax.tick_params(which="minor", length=0)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")

        # Title
        if final_state["found"]:
            status = f"✔ Path Found — {len(final_state['path'])} steps"
            tcol = "#3fb950"
        elif final_state["impossible"]:
            status = "✘ No Path Exists"
            tcol = "#f85149"
        else:
            status = "Search Complete"
            tcol = "#888"

        ax.set_title(
            f"A* Maze Solver  |  {name}\n{status}  |  Nodes Visited: {len(final_state['closed_set'])}",
            color=tcol, fontsize=13, pad=12, fontweight="bold"
        )

        # Legend
        patches = [
            mpatches.Patch(color="#3fb950", label="Start"),
            mpatches.Patch(color="#f85149", label="Goal"),
            mpatches.Patch(color="#ffd700", label="Shortest Path"),
            mpatches.Patch(color="#388bfd", label="Open Set"),
            mpatches.Patch(color="#6e40aa", label="Closed Set"),
            mpatches.Patch(color="#30363d", label="Wall"),
        ]
        ax.legend(handles=patches, loc="upper right", framealpha=0.8,
                  facecolor="#1a1f27", edgecolor="#30363d",
                  labelcolor="#e6edf3", fontsize=9)

        safe_name = name.replace(" ", "_").replace("×", "x").replace("/", "-")
        out_path = os.path.join(out_dir, f"{safe_name}.png")
        plt.tight_layout()
        plt.savefig(out_path, dpi=150, bbox_inches="tight",
                    facecolor="#0d1117")
        plt.close(fig)
        print(f"  Exported -> {out_path}")

    print(f"\n[OK]  {len(all_mazes)} example images saved to '{out_dir}/'")


if __name__ == "__main__":
    export_examples()
