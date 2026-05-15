"""
demo.py — Headless Text-Based A* Demo
======================================
Runs A* on all preset mazes and prints:
  - Grid visualization (ASCII)
  - Path found / impossible
  - Steps, path length, time taken

No display or Pygame required.
"""

import time
from astar import astar
from maze import PRESETS, MazeGenerator

# ANSI colour codes for terminal output
RESET  = "\033[0m"
GREEN  = "\033[92m"
RED    = "\033[91m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"


def _solve(grid, start, goal):
    """Run A* to completion and return final state + timing."""
    t0 = time.perf_counter()
    state = {}
    for state in astar(grid, start, goal):
        pass
    elapsed = time.perf_counter() - t0
    return state, elapsed


def _render_ascii(grid, start, goal, path, open_set, closed_set):
    """Render the maze as a coloured ASCII grid."""
    path_set   = set(path)
    rows = len(grid)
    cols = len(grid[0])
    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            pos = (r, c)
            if grid[r][c] == 1:
                ch = f"{DIM}██{RESET}"
            elif pos == start:
                ch = f"{GREEN}{BOLD} S{RESET}"
            elif pos == goal:
                ch = f"{RED}{BOLD} G{RESET}"
            elif pos in path_set:
                ch = f"{YELLOW} *{RESET}"
            elif pos in open_set:
                ch = f"{BLUE} o{RESET}"
            elif pos in closed_set:
                ch = f"{PURPLE} x{RESET}"
            else:
                ch = f"{DIM} .{RESET}"
            row_chars.append(ch)
        lines.append("".join(row_chars))
    return "\n".join(lines)


def run_demo():
    """Run the headless demo on all presets."""
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print("   AI MAZE SOLVER  —  A* Search Algorithm Demo")
    print(f"{'='*60}{RESET}\n")

    all_mazes = dict(PRESETS)
    # Add one random maze
    mg = MazeGenerator(rows=8, cols=8, seed=42)
    all_mazes["Random 8×8 (seed=42)"] = mg.generate()

    for name, data in all_mazes.items():
        grid  = [row[:] for row in data["grid"]]
        start = data["start"]
        goal  = data["goal"]

        print(f"{BOLD}{'─'*55}")
        print(f"  Maze: {CYAN}{name}{RESET}")
        print(f"  Grid: {len(grid)}×{len(grid[0])}   Start: {start}   Goal: {goal}")
        print(f"{'─'*55}{RESET}")

        state, elapsed = _solve(grid, start, goal)

        # Display ASCII maze
        ascii_art = _render_ascii(
            grid, start, goal,
            state["path"],
            state["open_set"],
            state["closed_set"],
        )
        print(ascii_art)
        print()

        if state["found"]:
            print(f"  {GREEN}✔  Path Found!{RESET}")
            print(f"     Path length : {YELLOW}{len(state['path'])} steps{RESET}")
        elif state["impossible"]:
            print(f"  {RED}✘  No path exists — maze is unsolvable!{RESET}")
        else:
            print(f"  {RED}✘  Search ended without result.{RESET}")

        print(f"     Nodes visited: {BLUE}{len(state['closed_set'])}{RESET}")
        print(f"     Time elapsed : {CYAN}{elapsed*1000:.3f} ms{RESET}")
        print()

    print(f"\n{BOLD}{CYAN}Legend:{RESET}")
    print(f"  {GREEN} S{RESET} = Start    {RED} G{RESET} = Goal    "
          f"{YELLOW} *{RESET} = Path    {BLUE} o{RESET} = Open Set    "
          f"{PURPLE} x{RESET} = Closed    {DIM}██{RESET} = Wall")
    print()
