# Raspberry Pi Car - Maze Solver

This project implements an autonomous maze-solving car using a Raspberry Pi. The car is designed to navigate through a physical maze, using sensors to detect walls and line following to maintain its position.

## Project Overview

The system consists of several key components:
- A Raspberry Pi-based car with line following sensors
- Maze navigation algorithms
- Calibration tools for precise movement
- Configuration management for maze parameters

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
- Autonomous maze solving
- Line following capabilities
- Wall detection and avoidance
- Precise movement calibration
- Configurable navigation parameters
- Debug logging and monitoring

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

## Configuration
The `maze_config.py` file contains all configurable parameters:
- Movement speeds and acceleration
- Sensor configurations
- Navigation tolerances
- Debug settings
- Competition parameters

## Requirements
- Raspberry Pi (compatible model)
- Line following sensors
- Motor controllers
- Python 3.x
- Required Python packages (list dependencies here)

## License
This project is licensed under the terms specified in the LICENSE.txt file.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments
- [Add any acknowledgments or references here]