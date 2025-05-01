#!/usr/bin/env python3
# maze_config.py - Configuration parameters for maze navigation system
# This module defines all the physical and operational constants used throughout
# the maze navigation system, including maze dimensions, movement parameters,
# sensor configurations, and competition rules.

# Physical maze dimensions and layout
CELL_SIZE_CENTIMETERS = 33.2          # Size of one grid cell in centimeters
MAZE_COLUMNS = 10                     # Number of columns in the maze
MAZE_ROWS = 5                         # Number of rows in the maze
WALL_THICKNESS_CENTIMETERS = 2.0      # Thickness of maze walls in centimeters

# Maze navigation points
START_POSITION = (0, MAZE_ROWS-1)     # Starting position (0,4) – marked with red arrow
EXIT_POSITION = (MAZE_COLUMNS-1, 0)   # Exit position (9,0) – marked with green arrow

# Direction vectors for navigation
# Direction indices: North(0), East(1), South(2), West(3)
X_AXIS_MOVEMENT = [0, 1, 0, -1]       # X-axis movement for each direction
Y_AXIS_MOVEMENT = [1, 0, -1, 0]       # Y-axis movement for each direction

# Motor control parameters
MAXIMUM_MOTOR_SPEED = 3000            # Maximum allowed motor speed
MINIMUM_MOTOR_SPEED = 500             # Minimum allowed motor speed
MOTOR_ACCELERATION = 100              # Speed change per step

# Line sensor configuration
NUMBER_OF_SENSORS = 5                 # Total number of line sensors
SENSOR_SPACING_CENTIMETERS = 2.5      # Distance between adjacent sensors in cm
SENSOR_READING_DELAY = 0.01           # Delay between consecutive sensor readings

# Navigation control parameters
TURN_ANGLE_TOLERANCE = 0.1            # Maximum allowed error in degrees for turns
POSITION_ERROR_TOLERANCE = 1.0        # Maximum allowed position error in cm
WALL_DETECTION_DISTANCE = 20          # Distance threshold for wall detection in cm

# System logging and debugging
ENABLE_DEBUG_OUTPUT = False           # Enable detailed debug information
ENABLE_MOVEMENT_LOGGING = True        # Log all movement operations
MOVEMENT_LOG_FILE = "maze_navigation.log"  # File path for movement logging

# Competition parameters
MAXIMUM_ALLOWED_TIME = 300            # Maximum time allowed for maze completion in seconds
MAXIMUM_ALLOWED_MOVES = 1000          # Maximum number of moves allowed
WALL_COLLISION_PENALTY = 10           # Penalty time in seconds for wall collision 