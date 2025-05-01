#!/usr/bin/env python3
# maze_navigator.py - Maze navigation and path finding implementation

import time
import numpy as np
from maze_config import CELL_CM, COLS, ROWS, WALL_THICKCM, START_CELL, EXIT_CELL, DX, DY
from maze_calibration import load_calibration

class MazeNavigator:
    def __init__(self):
        """Initialize maze navigator with calibration data"""
        self.calib = load_calibration()
        self.initialize_hardware()
        self.current_pose = (0, 0, 0)  # (x, y, direction)
        self.visited = set()
        self.walls = set()
        
    def initialize_hardware(self):
        """Initialize required hardware components"""
        # Initialize motors, sensors, etc.
        self.motor_speed = self.calib["BASE_SPEED"]
        self.turn_speed = self.calib["TURN_SPEED"]
        
    def solve_maze(self, start, exit):
        """Find path from start to exit in the maze using A* algorithm"""
        self.current_pose = (start[0], start[1], 0)  # Start facing north
        self.visited = set()
        self.walls = set()
        
        # Implement A* path finding
        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, exit)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            if current == exit:
                return self.reconstruct_path(came_from, current)
                
            open_set.remove(current)
            self.visited.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in self.walls:
                    continue
                    
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, exit)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                        
        return None  # No path found
        
    def heuristic(self, a, b):
        """Calculate Manhattan distance between two points"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    def get_neighbors(self, pos):
        """Get valid neighboring cells"""
        neighbors = []
        for dx, dy in zip(DX, DY):
            new_x, new_y = pos[0] + dx, pos[1] + dy
            if 0 <= new_x < COLS and 0 <= new_y < ROWS:
                neighbors.append((new_x, new_y))
        return neighbors
        
    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from start to current position"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))
        
    def move_forward(self):
        """Move forward one cell"""
        duration = self.calib["SEC_PER_CELL"]
        # Move forward for duration
        PWM.setMotorModel(self.motor_speed, self.motor_speed, 
                         self.motor_speed, self.motor_speed)
        time.sleep(duration)
        PWM.setMotorModel(0, 0, 0, 0)
        
        # Update position
        x, y, direction = self.current_pose
        self.current_pose = (x + DX[direction], y + DY[direction], direction)
        
    def turn_left(self):
        """Turn 90 degrees left"""
        duration = self.calib["TURN_DURATION_90"]
        # Turn left for duration
        PWM.setMotorModel(-self.turn_speed, -self.turn_speed,
                         self.turn_speed, self.turn_speed)
        time.sleep(duration)
        PWM.setMotorModel(0, 0, 0, 0)
        
        # Update direction
        x, y, direction = self.current_pose
        self.current_pose = (x, y, (direction - 1) % 4)
        
    def turn_right(self):
        """Turn 90 degrees right"""
        duration = self.calib["TURN_DURATION_90"]
        # Turn right for duration
        PWM.setMotorModel(self.turn_speed, self.turn_speed,
                         -self.turn_speed, -self.turn_speed)
        time.sleep(duration)
        PWM.setMotorModel(0, 0, 0, 0)
        
        # Update direction
        x, y, direction = self.current_pose
        self.current_pose = (x, y, (direction + 1) % 4)
        
    def detect_wall(self):
        """Detect if there's a wall in front"""
        # Implement wall detection using sensors
        # For now, return False (no wall)
        return False
        
    def cleanup(self):
        """Clean up resources"""
        PWM.setMotorModel(0, 0, 0, 0)
        # Close any other connections 