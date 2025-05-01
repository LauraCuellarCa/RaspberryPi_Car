#!/usr/bin/env python3
# maze_config.py - Maze configuration and constants

# Physical dimensions
CELL_CM      = 33.2          # Size of one grid cell in centimeters
COLS, ROWS   = 10, 5         # Maze dimensions (width × height)
WALL_THICKCM = 2.0           # Wall thickness in centimeters

# Start and exit positions
START_CELL   = (0, ROWS-1)   # Starting position (0,4) – marked with red arrow
EXIT_CELL    = (COLS-1, 0)   # Exit position (9,0) – marked with green arrow

# Direction vectors for navigation
# Index mapping: North(0), East(1), South(2), West(3)
DX = [0, 1, 0, -1]  # X-axis movement for each direction
DY = [1, 0, -1, 0]  # Y-axis movement for each direction

# Movement constraints
MAX_SPEED = 3000    # Maximum motor speed
MIN_SPEED = 500     # Minimum motor speed
ACCELERATION = 100  # Speed change per step

# Sensor configuration
NUM_SENSORS = 5     # Number of line sensors
SENSOR_SPACING = 2.5  # Distance between sensors in cm
SENSOR_READ_DELAY = 0.01  # Delay between sensor readings

# Navigation parameters
TURN_PRECISION = 0.1  # Allowed error in degrees for turns
POSITION_TOLERANCE = 1.0  # Allowed position error in cm
WALL_DETECTION_THRESHOLD = 20  # Distance in cm to detect walls

# Debug settings
DEBUG_MODE = False  # Enable debug output
LOG_MOVEMENTS = True  # Log all movements to file
LOG_FILE = "maze_navigation.log"  # File to log movements

# Competition settings
MAX_TIME = 300  # Maximum time allowed in seconds
MAX_MOVES = 1000  # Maximum number of moves allowed
PENALTY_TIME = 10  # Penalty time in seconds for wall collision 