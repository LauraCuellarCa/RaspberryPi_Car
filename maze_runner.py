#!/usr/bin/env python3
# maze_runner.py - Main execution module for maze navigation system
# This module serves as the entry point for the maze solving system, handling
# command-line arguments, initialization, and the main execution flow of the
# maze navigation process.

import argparse
import sys
from maze_navigator import MazeNavigator
from maze_config import START_POSITION, EXIT_POSITION
from maze_calibration import (
    load_calibration_settings,
    save_calibration_settings,
    calibrate_forward_movement
)
from motor import Ordinary_Car  # Add motor import

def main():
    """
    Main execution function for the maze navigation system.
    Handles command-line arguments, system initialization, and maze solving process.
    """
    # Set up command-line argument parser
    argument_parser = argparse.ArgumentParser(
        description='Maze Navigation System Runner'
    )
    argument_parser.add_argument(
        '--calibrate',
        action='store_true',
        help='Execute the system calibration procedure'
    )
    parsed_arguments = argument_parser.parse_args()

    # Initialize motor controller
    motor_controller = Ordinary_Car()

    # Execute calibration if requested
    if parsed_arguments.calibrate:
        print("Initiating system calibration procedure...")
        calibrate_forward_movement(motor_controller)
        return

    # Initialize the maze navigation system
    maze_navigator = MazeNavigator()
    
    try:
        # Attempt to solve the maze
        navigation_path = maze_navigator.solve_maze(START_POSITION, EXIT_POSITION)
        
        if navigation_path:
            print("Maze navigation completed successfully!")
            print(f"Navigation path: {navigation_path}")
        else:
            print("No valid path found through the maze.")
            
    except KeyboardInterrupt:
        print("\nMaze navigation interrupted by user command")
    except Exception as error:
        print(f"Error during maze navigation: {error}")
    finally:
        # Ensure proper cleanup of system resources
        maze_navigator.cleanup()
        motor_controller.close()

if __name__ == "__main__":
    main() 