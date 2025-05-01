# Raspberry Pi Car - Maze Solver (RasCar)

This project implements an autonomous maze-solving car using a Raspberry Pi. The car is designed to navigate through a physical maze, using sensors to detect walls and line following to maintain its position. The system combines line following capabilities with an A* pathfinding algorithm to efficiently solve mazes.

## Project Overview

The RasCar is a Raspberry Pi-powered autonomous vehicle designed for line following and maze-solving competitions. The system combines hardware components with sophisticated software algorithms to achieve autonomous navigation.

### Hardware Components
- Raspberry Pi (main controller)
- Motor drivers and wheels
- Servos for sensor positioning
- Ultrasonic sensors for wall detection
- Color sensor for line following
- Chassis and power system

### Software Architecture
- Line following logic with real-time trajectory adjustment
- Collision detection and avoidance system
- A* pathfinding algorithm with Manhattan Distance heuristic
- Dynamic maze mapping and exploration
- Real-time sensor data processing

## Key Components

### Main Files
- `maze_runner.py`: The main execution script that coordinates the maze solving process
- `maze_navigator.py`: Core navigation logic and maze solving algorithms
- `maze_config.py`: Configuration parameters for maze dimensions, movement settings, and sensor configurations
- `maze_calibration.py`: Tools for calibrating the car's movement and sensor readings

### Maze Specifications
- Grid size: 10x5 cells
- Cell size: 33.2 cm
- Wall thickness: 2.0 cm
- Start position: (0,4) - marked with red arrow
- Exit position: (9,0) - marked with green arrow

## Features

### Navigation Capabilities
- Autonomous maze solving using A* algorithm
- Line following with real-time trajectory adjustment
- Multi-directional wall detection (front, left, right)
- Dynamic maze mapping and exploration
- Real-time path optimization

### Sensor Integration
- Ultrasonic sensor scanning in three directions
- Color sensor calibration for line detection
- Real-time sensor data processing
- Collision avoidance system

### Movement Control
- Precise movement calibration
- Four-directional movement control
- Speed and acceleration management
- Turn radius optimization

## Usage

### Running the Maze Solver
```bash
python3 maze_runner.py
```

### Calibration
Before running the maze solver, it's recommended to calibrate the car:
```bash
python3 maze_runner.py --calibrate
```

The calibration process includes:
- Movement timing calibration
- Sensor threshold adjustment
- Line following calibration
- Turn radius optimization

## Implementation Details

### Navigation Strategy
1. Initial exploration phase to map the maze
2. Dynamic grid representation (10×5) for efficient storage
3. A* pathfinding with Manhattan Distance heuristic
4. Real-time wall detection and path adjustment
5. Backtracking for complete maze exploration

### Sensor Configuration
- Ultrasonic sensor sampling rate optimization
- Color sensor threshold calibration
- Multi-angle scanning for wall detection
- Real-time sensor data processing

## Requirements
- Raspberry Pi (compatible model)
- Line following sensors
- Motor controllers
- Ultrasonic sensors
- Servo motors
- Python 3.x
- Required Python packages (list dependencies here)

## Known Challenges and Solutions
- Hardware integration and stability
- Sensor calibration and threshold optimization
- Real-time path planning with noisy sensor data
- Movement precision and timing calibration
