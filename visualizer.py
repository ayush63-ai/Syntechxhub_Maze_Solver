"""
visualizer.py — Pygame Real-Time Visualization Engine
======================================================
Renders the A* search process with:
  • Dark-themed professional UI
  • Color-coded cells: open set, closed set, path, walls, start, goal
  • Animated step-by-step search progression
  • Legend panel, stats bar, and status messages
  • Interactive controls (speed slider, pause/play, restart)
"""

import pygame
import sys
import time
import random
from astar import astar
from maze import PRESETS, MazeGenerator

# ─── Colour Palette ──────────────────────────────────────────────────────────
BG_DARK        = (13,  17,  23)
PANEL_BG       = (22,  27,  34)
BORDER_COLOR   = (48,  54,  61)

WALL_COLOR     = (48,  54,  61)
FREE_COLOR     = (33,  38,  45)
START_COLOR    = (63, 185, 80)      # green
GOAL_COLOR     = (248, 81,  73)     # red
OPEN_COLOR     = (56, 139, 253)     # blue
CLOSED_COLOR   = (110, 64, 170)     # purple
PATH_COLOR     = (255, 215, 0)      # gold
CURRENT_COLOR  = (255, 165, 0)      # orange

TEXT_PRIMARY   = (230, 237, 243)
TEXT_SECONDARY = (139, 148, 158)
TEXT_ACCENT    = (88, 166, 255)

# ─── Layout Constants ────────────────────────────────────────────────────────
SIDEBAR_W  = 280
TOPBAR_H   = 60
BOTBAR_H   = 50
CELL_MIN   = 6
CELL_MAX   = 60
FPS        = 60


class MazeSolverApp:
    """Main Pygame application for the AI Maze Solver."""

    def __init__(self, width: int = 1280, height: int = 760):
        pygame.init()
        pygame.display.set_caption("🧩  AI Maze Solver  —  A* Search Algorithm")

        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_title  = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_label  = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_small  = pygame.font.SysFont("Segoe UI", 12)
        self.font_big    = pygame.font.SysFont("Segoe UI", 30, bold=True)
        self.font_mono   = pygame.font.SysFont("Consolas", 13)

        # State
        self.preset_names  = list(PRESETS.keys()) + ["Random 10x10", "Random 15x15", "Random 20x20"]
        self.preset_idx    = 0
        self.speed         = 8       # steps per second (slow enough to watch)
        self.paused        = False
        self.auto_cycle    = True    # auto-advance to next maze after solve
        self.AUTO_DELAY    = 3.0     # seconds to wait before auto-cycling

        self._load_preset(self.preset_idx)

    # ─── Data Loading ─────────────────────────────────────────────────────────
    def _load_preset(self, idx: int):
        name = self.preset_names[idx]
        if name.startswith("Random"):
            # Use a new random seed each load so maze looks different every cycle
            size = int(name.split()[1].split("x")[0])
            seed = random.randint(0, 99999)
            mg   = MazeGenerator(rows=size // 2, cols=size // 2, seed=seed)
            data = mg.generate()
        else:
            data = PRESETS[name]

        self.grid  = [row[:] for row in data["grid"]]   # deep copy
        self.start = data["start"]
        self.goal  = data["goal"]
        self._reset_search()

    def _reset_search(self):
        self.gen          = astar(self.grid, self.start, self.goal)
        self.open_set     = set()
        self.closed_set   = set()
        self.current_pos  = None
        self.path         = []
        self.found        = False
        self.impossible   = False
        self.running      = True
        self.steps        = 0
        self.start_time   = time.time()
        self.elapsed      = 0.0
        self.done         = False
        self._step_accum  = 0.0
        self._done_timer  = 0.0    # countdown before auto-cycling to next maze

    # ─── Main Loop ────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0   # seconds since last frame
            self._handle_events()
            if self.done:
                # Count down then auto-cycle to next maze
                if self.auto_cycle and not self.paused:
                    self._done_timer += dt
                    if self._done_timer >= self.AUTO_DELAY:
                        self.preset_idx = (self.preset_idx + 1) % len(self.preset_names)
                        self._load_preset(self.preset_idx)
            elif not self.paused:
                self._advance(dt)
            self._draw()
            pygame.display.flip()

    # ─── Event Handling ───────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset_search()
                elif event.key == pygame.K_RIGHT:
                    self.preset_idx = (self.preset_idx + 1) % len(self.preset_names)
                    self._load_preset(self.preset_idx)
                elif event.key == pygame.K_LEFT:
                    self.preset_idx = (self.preset_idx - 1) % len(self.preset_names)
                    self._load_preset(self.preset_idx)
                elif event.key == pygame.K_UP:
                    self.speed = min(500, self.speed + 10)
                elif event.key == pygame.K_DOWN:
                    self.speed = max(1, self.speed - 10)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_mouse_click(event.pos, toggle=True)
                elif event.button == 3:
                    self._handle_mouse_click(event.pos, erase=True)

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    self._handle_mouse_click(event.pos, toggle=True)

            elif event.type == pygame.VIDEORESIZE:
                self.W, self.H = event.w, event.h
                self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)

    def _handle_mouse_click(self, pos, toggle=False, erase=False):
        """Toggle walls on the maze grid via mouse."""
        mx, my = pos
        maze_rect = self._maze_rect()
        if not maze_rect.collidepoint(mx, my):
            return
        rows = len(self.grid); cols = len(self.grid[0])
        cell_w = maze_rect.width  / cols
        cell_h = maze_rect.height / rows
        col = int((mx - maze_rect.x) / cell_w)
        row = int((my - maze_rect.y) / cell_h)
        if 0 <= row < rows and 0 <= col < cols:
            if (row, col) == self.start or (row, col) == self.goal:
                return
            if erase:
                self.grid[row][col] = 0
            else:
                self.grid[row][col] = 1 - self.grid[row][col]
            self._reset_search()

    # ─── Search Advancement ───────────────────────────────────────────────────
    def _advance(self, dt: float):
        if self.done:
            return
        self._step_accum += dt * self.speed
        steps_this_frame = int(self._step_accum)
        self._step_accum -= steps_this_frame

        for _ in range(steps_this_frame):
            try:
                state = next(self.gen)
                self.open_set    = state["open_set"]
                self.closed_set  = state["closed_set"]
                self.current_pos = state["current"]
                self.path        = state["path"]
                self.found       = state["found"]
                self.impossible  = state["impossible"]
                self.steps      += 1
                if state["found"] or state["impossible"]:
                    self.done    = True
                    self.elapsed = time.time() - self.start_time
                    break
            except StopIteration:
                self.done = True
                break

    # ─── Drawing ──────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BG_DARK)
        self._draw_topbar()
        self._draw_sidebar()
        self._draw_maze()
        self._draw_botbar()

    def _maze_rect(self) -> pygame.Rect:
        rows = len(self.grid); cols = len(self.grid[0])
        avail_w = self.W - SIDEBAR_W - 30
        avail_h = self.H - TOPBAR_H - BOTBAR_H - 20
        cell = max(CELL_MIN, min(CELL_MAX, avail_w // cols, avail_h // rows))
        maze_w = cell * cols
        maze_h = cell * rows
        x = 15 + (avail_w - maze_w) // 2
        y = TOPBAR_H + 10 + (avail_h - maze_h) // 2
        return pygame.Rect(x, y, maze_w, maze_h)

    def _draw_maze(self):
        rows = len(self.grid); cols = len(self.grid[0])
        rect = self._maze_rect()
        cell_w = rect.width  / cols
        cell_h = rect.height / rows

        path_set = set(self.path)

        for r in range(rows):
            for c in range(cols):
                x = int(rect.x + c * cell_w)
                y = int(rect.y + r * cell_h)
                w = max(1, int(cell_w) - 1)
                h = max(1, int(cell_h) - 1)
                cell_rect = pygame.Rect(x, y, w, h)
                pos = (r, c)

                if self.grid[r][c] == 1:
                    color = WALL_COLOR
                elif pos == self.start:
                    color = START_COLOR
                elif pos == self.goal:
                    color = GOAL_COLOR
                elif pos in path_set:
                    color = PATH_COLOR
                elif pos == self.current_pos:
                    color = CURRENT_COLOR
                elif pos in self.open_set:
                    color = OPEN_COLOR
                elif pos in self.closed_set:
                    color = CLOSED_COLOR
                else:
                    color = FREE_COLOR

                pygame.draw.rect(self.screen, color, cell_rect, border_radius=2)

                # Draw S / G labels for big cells
                if cell_w >= 20:
                    if pos == self.start:
                        self._blit_center("S", self.font_label, TEXT_PRIMARY, cell_rect)
                    elif pos == self.goal:
                        self._blit_center("G", self.font_label, TEXT_PRIMARY, cell_rect)

        # Maze border
        pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2, border_radius=4)

    def _draw_topbar(self):
        bar = pygame.Rect(0, 0, self.W, TOPBAR_H)
        pygame.draw.rect(self.screen, PANEL_BG, bar)
        pygame.draw.line(self.screen, BORDER_COLOR, (0, TOPBAR_H), (self.W, TOPBAR_H), 1)

        title = self.font_title.render("AI Maze Solver  -  A* Search Algorithm", True, TEXT_ACCENT)
        self.screen.blit(title, (20, (TOPBAR_H - title.get_height()) // 2))

        preset_name = self.preset_names[self.preset_idx]
        hint = self.font_small.render(
            f"Maze: {preset_name}   |   LEFT/RIGHT = change   |   UP/DOWN = speed ({self.speed} sps)   |   SPACE = pause   |   R = restart   |   Click = wall",
            True, TEXT_SECONDARY)
        self.screen.blit(hint, (self.W - hint.get_width() - 20, (TOPBAR_H - hint.get_height()) // 2))

    def _draw_botbar(self):
        y = self.H - BOTBAR_H
        bar = pygame.Rect(0, y, self.W, BOTBAR_H)
        pygame.draw.rect(self.screen, PANEL_BG, bar)
        pygame.draw.line(self.screen, BORDER_COLOR, (0, y), (self.W, y), 1)

        # Status message
        if self.impossible:
            remain = max(0.0, self.AUTO_DELAY - self._done_timer)
            status = f"No path exists — unsolvable!  Next maze in {remain:.1f}s"
            color  = (248, 81, 73)
        elif self.found:
            remain = max(0.0, self.AUTO_DELAY - self._done_timer)
            status = f"Path found!  Length: {len(self.path)} steps   |   Next maze in {remain:.1f}s  (SPACE to pause)"
            color  = START_COLOR
        elif self.paused:
            status = "Paused  —  press SPACE to resume"
            color  = TEXT_SECONDARY
        else:
            status = "Searching..."
            color  = OPEN_COLOR

        surf = self.font_label.render(status, True, color)
        self.screen.blit(surf, (20, y + (BOTBAR_H - surf.get_height()) // 2))

        # Stats
        stats = f"Steps: {self.steps:,}   |   Open: {len(self.open_set):,}   |   Closed: {len(self.closed_set):,}   |   Speed: {self.speed} sps (up/down)"
        if self.done:
            stats += f"   |   Solved in {self.elapsed*1000:.1f} ms"
        ssurf = self.font_small.render(stats, True, TEXT_SECONDARY)
        self.screen.blit(ssurf, (self.W - SIDEBAR_W - ssurf.get_width() - 30, y + (BOTBAR_H - ssurf.get_height()) // 2))

    def _draw_sidebar(self):
        x = self.W - SIDEBAR_W
        panel = pygame.Rect(x, 0, SIDEBAR_W, self.H)
        pygame.draw.rect(self.screen, PANEL_BG, panel)
        pygame.draw.line(self.screen, BORDER_COLOR, (x, 0), (x, self.H), 1)

        cy = TOPBAR_H + 20

        # ── Title ──
        t = self.font_label.render("LEGEND", True, TEXT_ACCENT)
        self.screen.blit(t, (x + 20, cy)); cy += t.get_height() + 12

        # Legend items
        items = [
            (START_COLOR,   "Start Cell (S)"),
            (GOAL_COLOR,    "Goal Cell (G)"),
            (OPEN_COLOR,    "Open Set (frontier)"),
            (CLOSED_COLOR,  "Closed Set (visited)"),
            (CURRENT_COLOR, "Current Node"),
            (PATH_COLOR,    "Shortest Path"),
            (WALL_COLOR,    "Wall / Obstacle"),
            (FREE_COLOR,    "Free Cell"),
        ]
        for color, label in items:
            pygame.draw.rect(self.screen, color, (x + 20, cy, 18, 18), border_radius=3)
            lbl = self.font_small.render(label, True, TEXT_PRIMARY)
            self.screen.blit(lbl, (x + 46, cy + 1))
            cy += 26

        cy += 16
        # ── Divider ──
        pygame.draw.line(self.screen, BORDER_COLOR, (x + 20, cy), (x + SIDEBAR_W - 20, cy), 1)
        cy += 16

        # ── Stats ──
        t2 = self.font_label.render("STATISTICS", True, TEXT_ACCENT)
        self.screen.blit(t2, (x + 20, cy)); cy += t2.get_height() + 10

        rows = len(self.grid); cols = len(self.grid[0])
        walls = sum(cell for row in self.grid for cell in row)
        free  = rows * cols - walls

        stat_items = [
            ("Grid Size",       f"{rows} × {cols}"),
            ("Free Cells",      f"{free:,}"),
            ("Wall Cells",      f"{walls:,}"),
            ("Steps Taken",     f"{self.steps:,}"),
            ("Open Set Size",   f"{len(self.open_set):,}"),
            ("Closed Set Size", f"{len(self.closed_set):,}"),
            ("Path Length",     f"{len(self.path):,}" if self.path else "—"),
            ("Search Speed",    f"{self.speed} sps"),
            ("Elapsed",         f"{self.elapsed*1000:.1f} ms" if self.done else "…"),
        ]
        for key, val in stat_items:
            k = self.font_small.render(key, True, TEXT_SECONDARY)
            v = self.font_mono.render(val, True, TEXT_PRIMARY)
            self.screen.blit(k, (x + 20, cy))
            self.screen.blit(v, (x + SIDEBAR_W - v.get_width() - 20, cy))
            cy += 20

        cy += 16
        pygame.draw.line(self.screen, BORDER_COLOR, (x + 20, cy), (x + SIDEBAR_W - 20, cy), 1)
        cy += 16

        # ── How it works ──
        t3 = self.font_label.render("HOW A* WORKS", True, TEXT_ACCENT)
        self.screen.blit(t3, (x + 20, cy)); cy += t3.get_height() + 8

        lines = [
            "f(n) = g(n) + h(n)",
            "g(n) = cost from start",
            "h(n) = Manhattan distance",
            "Priority queue (heapq)",
            "Always expands lowest f",
        ]
        for line in lines:
            s = self.font_mono.render(line, True, TEXT_SECONDARY)
            self.screen.blit(s, (x + 20, cy)); cy += 18

        # ── Maze selector buttons ──
        cy += 16
        pygame.draw.line(self.screen, BORDER_COLOR, (x + 20, cy), (x + SIDEBAR_W - 20, cy), 1)
        cy += 16
        t4 = self.font_label.render("MAZE PRESETS", True, TEXT_ACCENT)
        self.screen.blit(t4, (x + 20, cy)); cy += t4.get_height() + 10

        for i, name in enumerate(self.preset_names):
            btn_rect = pygame.Rect(x + 20, cy, SIDEBAR_W - 40, 24)
            color = TEXT_ACCENT if i == self.preset_idx else BORDER_COLOR
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=4,
                             width=0 if i == self.preset_idx else 1)
            txt_color = BG_DARK if i == self.preset_idx else TEXT_SECONDARY
            lbl = self.font_small.render(name, True, txt_color)
            self.screen.blit(lbl, (btn_rect.x + 8, btn_rect.y + 4))

            # Click detection
            mx, my = pygame.mouse.get_pos()
            if btn_rect.collidepoint(mx, my):
                if pygame.mouse.get_pressed()[0]:
                    if i != self.preset_idx:
                        self.preset_idx = i
                        self._load_preset(i)

            cy += 28

    # ─── Utility ──────────────────────────────────────────────────────────────
    def _blit_center(self, text: str, font, color, rect: pygame.Rect):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
def launch():
    app = MazeSolverApp()
    app.run()


if __name__ == "__main__":
    launch()
