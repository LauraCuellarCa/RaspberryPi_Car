#!/usr/bin/env python3
# maze_navigator.py - Core navigation and path finding implementation
# This module implements the A* path finding algorithm and provides the core
# functionality for autonomous maze navigation, including movement control,
# wall detection, and path reconstruction.

import time
import numpy as np
from maze_config import (
    CELL_SIZE_CENTIMETERS,
    MAZE_COLUMNS,
    MAZE_ROWS,
    WALL_THICKNESS_CENTIMETERS,
    START_POSITION,
    EXIT_POSITION,
    X_AXIS_MOVEMENT,
    Y_AXIS_MOVEMENT
)
from maze_calibration import load_calibration_settings

class MazeNavigator:
    """
    Main navigation class that handles maze exploration and path finding.
    Implements the A* algorithm for optimal path finding and provides
    methods for physical movement control and wall detection.
    """
    
    def __init__(self):
        """
        Initialize the maze navigation system with calibration data
        and set up initial state variables.
        """
        self.calibration_data = load_calibration_settings()
        self.initialize_hardware_components()
        self.current_position = (0, 0, 0)  # (x, y, direction)
        self.visited_cells = set()
        self.detected_walls = set()
        
    def initialize_hardware_components(self):
        """
        Initialize all required hardware components including motors and sensors.
        Sets up initial motor speeds based on calibration data.
        """
        # Initialize motors, sensors, and other hardware components
        self.forward_motor_speed = self.calibration_data["base_motor_speed"]
        self.turn_motor_speed = self.calibration_data["turn_motor_speed"]
        
    def solve_maze(self, start_position, exit_position):
        """
        Find an optimal path through the maze using the A* algorithm.
        
        Args:
            start_position (tuple): Starting coordinates (x, y)
            exit_position (tuple): Exit coordinates (x, y)
            
        Returns:
            list: Sequence of coordinates representing the path from start to exit,
                  or None if no path is found
        """
        self.current_position = (start_position[0], start_position[1], 0)  # Start facing north
        self.visited_cells = set()
        self.detected_walls = set()
        
        # Initialize A* algorithm data structures
        open_cells = {start_position}
        path_predecessors = {}
        movement_costs = {start_position: 0}
        estimated_costs = {start_position: self.calculate_heuristic(start_position, exit_position)}
        
        while open_cells:
            current_cell = min(open_cells, key=lambda x: estimated_costs.get(x, float('inf')))
            if current_cell == exit_position:
                return self.reconstruct_navigation_path(path_predecessors, current_cell)
                
            open_cells.remove(current_cell)
            self.visited_cells.add(current_cell)
            
            for neighbor in self.get_adjacent_cells(current_cell):
                if neighbor in self.detected_walls:
                    continue
                    
                tentative_cost = movement_costs[current_cell] + 1
                if neighbor not in movement_costs or tentative_cost < movement_costs[neighbor]:
                    path_predecessors[neighbor] = current_cell
                    movement_costs[neighbor] = tentative_cost
                    estimated_costs[neighbor] = tentative_cost + self.calculate_heuristic(neighbor, exit_position)
                    if neighbor not in open_cells:
                        open_cells.add(neighbor)
                        
        return None  # No valid path found
        
    def calculate_heuristic(self, current_cell, target_cell):
        """
        Calculate the Manhattan distance between two cells as the heuristic
        for the A* algorithm.
        
        Args:
            current_cell (tuple): Current position coordinates
            target_cell (tuple): Target position coordinates
            
        Returns:
            int: Manhattan distance between the cells
        """
        return abs(current_cell[0] - target_cell[0]) + abs(current_cell[1] - target_cell[1])
        
    def get_adjacent_cells(self, position):
        """
        Get all valid neighboring cells from the current position.
        
        Args:
            position (tuple): Current position coordinates
            
        Returns:
            list: List of valid neighboring cell coordinates
        """
        adjacent_cells = []
        for x_offset, y_offset in zip(X_AXIS_MOVEMENT, Y_AXIS_MOVEMENT):
            new_x = position[0] + x_offset
            new_y = position[1] + y_offset
            if 0 <= new_x < MAZE_COLUMNS and 0 <= new_y < MAZE_ROWS:
                adjacent_cells.append((new_x, new_y))
        return adjacent_cells
        
    def reconstruct_navigation_path(self, path_predecessors, final_position):
        """
        Reconstruct the complete path from start to final position.
        
        Args:
            path_predecessors (dict): Dictionary mapping each cell to its predecessor
            final_position (tuple): Final position coordinates
            
        Returns:
            list: Complete path from start to final position
        """
        path = [final_position]
        current = final_position
        while current in path_predecessors:
            current = path_predecessors[current]
            path.append(current)
        return list(reversed(path))
        
    def move_forward(self):
        """
        Move the robot forward by one cell.
        Updates the current position after movement.
        """
        movement_duration = self.calibration_data["seconds_per_cell"]
        # Execute forward movement
        PWM.setMotorModel(
            self.forward_motor_speed,
            self.forward_motor_speed,
            self.forward_motor_speed,
            self.forward_motor_speed
        )
        time.sleep(movement_duration)
        PWM.setMotorModel(0, 0, 0, 0)
        
        # Update position coordinates
        x, y, direction = self.current_position
        self.current_position = (
            x + X_AXIS_MOVEMENT[direction],
            y + Y_AXIS_MOVEMENT[direction],
            direction
        )
        
    def turn_left(self):
        """
        Execute a 90-degree left turn.
        Updates the current direction after the turn.
        """
        turn_duration = self.calibration_data["turn_duration_90_degrees"]
        # Execute left turn
        PWM.setMotorModel(
            -self.turn_motor_speed,
            -self.turn_motor_speed,
            self.turn_motor_speed,
            self.turn_motor_speed
        )
        time.sleep(turn_duration)
        PWM.setMotorModel(0, 0, 0, 0)
        
        # Update direction
        x, y, direction = self.current_position
        self.current_position = (x, y, (direction - 1) % 4)
        
    def turn_right(self):
        """
        Execute a 90-degree right turn.
        Updates the current direction after the turn.
        """
        turn_duration = self.calibration_data["turn_duration_90_degrees"]
        # Execute right turn
        PWM.setMotorModel(
            self.turn_motor_speed,
            self.turn_motor_speed,
            -self.turn_motor_speed,
            -self.turn_motor_speed
        )
        time.sleep(turn_duration)
        PWM.setMotorModel(0, 0, 0, 0)
        
        # Update direction
        x, y, direction = self.current_position
        self.current_position = (x, y, (direction + 1) % 4)
        
    def detect_wall(self):
        """
        Detect if there is a wall in front of the robot.
        
        Returns:
            bool: True if a wall is detected, False otherwise
        """
        # Implement wall detection using sensors
        # For now, return False (no wall)
        return False
        
    def cleanup(self):
        """
        Clean up system resources and ensure motors are stopped.
        """
        PWM.setMotorModel(0, 0, 0, 0)
        # Close any other hardware connections 