"""
astar.py — Core A* Search Algorithm Engine
==========================================
Implements the A* pathfinding algorithm using:
  - Manhattan distance heuristic
  - heapq-based priority queue (min-heap) for O(log n) extraction
  - Open set / Closed set tracking for visualization
  - Shortest path reconstruction via parent map

Author: AI Maze Solver Project
"""

import heapq
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  Node: represents a cell in the grid
# ─────────────────────────────────────────────
@dataclass(order=True)
class Node:
    f: float                         # f = g + h  (priority key)
    g: float = field(compare=False)  # cost from start
    h: float = field(compare=False)  # heuristic to goal
    position: tuple = field(compare=False)  # (row, col)
    parent: Optional["Node"] = field(default=None, compare=False)

    def __hash__(self):
        return hash(self.position)

    def __eq__(self, other):
        return self.position == other.position


# ─────────────────────────────────────────────
#  Heuristic: Manhattan Distance
# ─────────────────────────────────────────────
def manhattan(a: tuple, b: tuple) -> float:
    """
    Manhattan distance heuristic — admissible for 4-directional grids.
    h(n) = |x1 - x2| + |y1 - y2|
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ─────────────────────────────────────────────
#  A* Search
# ─────────────────────────────────────────────
def astar(grid: list[list[int]], start: tuple, goal: tuple):
    """
    A* Search Algorithm.

    Parameters
    ----------
    grid  : 2D list — 0 = free, 1 = obstacle
    start : (row, col) of start cell
    goal  : (row, col) of goal cell

    Yields (step-by-step for animation)
    ------
    dict with keys:
        open_set   : set of positions currently in open list
        closed_set : set of positions already visited
        current    : position being evaluated
        path       : list of positions (final path, only on last yield)
        found      : bool — True when goal is reached
        impossible : bool — True when no path exists
    """
    rows = len(grid)
    cols = len(grid[0])

    # Validate start / goal
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        yield {"open_set": set(), "closed_set": set(), "current": None,
               "path": [], "found": False, "impossible": True}
        return

    # ── Initialise ──────────────────────────────────────
    start_node = Node(f=manhattan(start, goal), g=0,
                      h=manhattan(start, goal), position=start)

    # heapq entry: (f, counter, node) — counter breaks f ties deterministically
    counter = 0
    open_heap: list = []
    heapq.heappush(open_heap, (start_node.f, counter, start_node))

    # Position → best Node seen so far (for duplicate detection)
    open_dict: dict[tuple, Node] = {start: start_node}
    closed_set: set = set()

    # 4-directional neighbours (up, down, left, right)
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # ── Main loop ───────────────────────────────────────
    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        # Skip stale heap entries
        if current.position in closed_set:
            continue

        closed_set.add(current.position)
        open_set_positions = set(open_dict.keys()) - closed_set

        # ── Goal reached ────────────────────────────────
        if current.position == goal:
            path = _reconstruct_path(current)
            yield {
                "open_set": open_set_positions,
                "closed_set": closed_set.copy(),
                "current": current.position,
                "path": path,
                "found": True,
                "impossible": False,
            }
            return

        # ── Yield current state for animation ───────────
        yield {
            "open_set": open_set_positions,
            "closed_set": closed_set.copy(),
            "current": current.position,
            "path": [],
            "found": False,
            "impossible": False,
        }

        # ── Expand neighbours ───────────────────────────
        for dr, dc in DIRECTIONS:
            nr, nc = current.position[0] + dr, current.position[1] + dc

            # Boundary & obstacle check
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if grid[nr][nc] == 1:
                continue
            if (nr, nc) in closed_set:
                continue

            g_new = current.g + 1
            h_new = manhattan((nr, nc), goal)
            f_new = g_new + h_new
            neighbour = Node(f=f_new, g=g_new, h=h_new,
                             position=(nr, nc), parent=current)

            # Only push if better than known path
            if (nr, nc) not in open_dict or open_dict[(nr, nc)].g > g_new:
                open_dict[(nr, nc)] = neighbour
                counter += 1
                heapq.heappush(open_heap, (f_new, counter, neighbour))

    # ── No path found ───────────────────────────────────
    yield {
        "open_set": set(),
        "closed_set": closed_set.copy(),
        "current": None,
        "path": [],
        "found": False,
        "impossible": True,
    }


# ─────────────────────────────────────────────
#  Path reconstruction
# ─────────────────────────────────────────────
def _reconstruct_path(node: Node) -> list[tuple]:
    """Walk the parent chain from goal → start, then reverse."""
    path = []
    current = node
    while current:
        path.append(current.position)
        current = current.parent
    return path[::-1]
