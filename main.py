"""
main.py — AI Maze Solver Entry Point
=====================================
Launch the interactive Pygame-based A* maze solver.

Usage
-----
    python main.py                  # Interactive Pygame visualizer
    python main.py --demo           # Run text-based demo (no display required)
    python main.py --export         # Export example screenshots to /examples
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="AI Maze Solver",
        description="A* Search Algorithm — Interactive Maze Solver with Real-Time Visualization",
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Run a headless text-based demo of A* on all presets"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export solved maze screenshots to the examples/ folder"
    )
    args = parser.parse_args()

    if args.demo:
        from demo import run_demo
        run_demo()
    elif args.export:
        from exporter import export_examples
        export_examples()
    else:
        # Launch interactive Pygame UI
        from visualizer import launch
        launch()


if __name__ == "__main__":
    main()
