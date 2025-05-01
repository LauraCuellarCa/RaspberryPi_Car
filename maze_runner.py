#!/usr/bin/env python3
# maze_runner.py - Main executor for maze solving operations

import argparse
import sys
from maze_navigator import MazeNavigator
from maze_config import START_CELL, EXIT_CELL
from maze_calibration import load_calibration, save_calibration, calibrate_straight_movement

def main():
    parser = argparse.ArgumentParser(description='Maze Solver Runner')
    parser.add_argument('--calibrate', action='store_true', help='Run calibration procedure')
    args = parser.parse_args()

    # Run calibration if requested
    if args.calibrate:
        print("Running calibration...")
        calibrate_straight_movement()
        return

    # Initialize maze navigator
    navigator = MazeNavigator()
    
    try:
        # Solve the maze
        path = navigator.solve_maze(START_CELL, EXIT_CELL)
        if path:
            print("Maze solved successfully!")
            print(f"Path: {path}")
        else:
            print("No solution found for the maze.")
            
    except KeyboardInterrupt:
        print("\nMaze solving interrupted by user")
    except Exception as e:
        print(f"Error during maze solving: {e}")
    finally:
        navigator.cleanup()

if __name__ == "__main__":
    main() 