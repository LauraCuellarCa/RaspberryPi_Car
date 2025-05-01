#!/usr/bin/env python3
# maze_calibration.py - Maze navigation calibration and configuration

import json
import os
import time
from pathlib import Path

# Default calibration values for maze navigation
DEFAULT_CALIBRATION = {
    "SEC_PER_CELL": 0.5,      # Time to move one cell (seconds)
    "TURN_DURATION_90": 0.65, # Time for 90-degree turns (seconds)
    "BASE_SPEED": 2000,       # Base motor speed for straight movement
    "TURN_SPEED": 2500,       # Motor speed for turning
    "SENSOR_THRESHOLD": 1000, # Threshold for line detection
    "WALL_DISTANCE": 15.0,    # Distance to maintain from walls (cm)
    "LINE_FOLLOW_SPEED": 1500 # Speed for line following
}

def load_calibration(file_path="~/maze_solver/calibration.json"):
    """Load maze navigation calibration data from JSON file"""
    path = Path(os.path.expanduser(file_path))
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        else:
            # Create default calibration file if it doesn't exist
            save_calibration(DEFAULT_CALIBRATION, file_path)
            return DEFAULT_CALIBRATION
    except Exception as e:
        print(f"Error loading calibration: {e}")
        return DEFAULT_CALIBRATION

def save_calibration(data, file_path="~/maze_solver/calibration.json"):
    """Save maze navigation calibration data to JSON file"""
    path = Path(os.path.expanduser(file_path))
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Calibration saved to {path}")
        return True
    except Exception as e:
        print(f"Error saving calibration: {e}")
        return False

def calibrate_straight_movement(pwm, speed=2000):
    """Calibrate straight movement parameters for maze navigation"""
    print("\n=== Straight Movement Calibration ===")
    print("This will measure the time needed to move one cell")
    input("Press Enter when ready to start calibration...")
    
    # Load current calibration
    calib = load_calibration()
    
    # Measure time for straight movement
    start_time = time.time()
    pwm.setMotorModel(speed, speed, speed, speed)
    input("Press Enter when the car has moved one cell...")
    pwm.setMotorModel(0, 0, 0, 0)
    end_time = time.time()
    
    # Calculate and update calibration
    sec_per_cell = end_time - start_time
    calib["SEC_PER_CELL"] = sec_per_cell
    
    # Save updated calibration
    save_calibration(calib)
    
    print(f"Calibration complete! SEC_PER_CELL = {sec_per_cell:.3f}s")
    return sec_per_cell

def calibrate_turn(pwm, speed=2500):
    """Calibrate 90-degree turn parameters"""
    print("\n=== Turn Calibration ===")
    print("This will measure the time needed for a 90-degree turn")
    input("Press Enter when ready to start calibration...")
    
    # Load current calibration
    calib = load_calibration()
    
    # Measure time for turn
    start_time = time.time()
    pwm.setMotorModel(-speed, -speed, speed, speed)  # Left turn
    input("Press Enter when the car has turned 90 degrees...")
    pwm.setMotorModel(0, 0, 0, 0)
    end_time = time.time()
    
    # Calculate and update calibration
    turn_duration = end_time - start_time
    calib["TURN_DURATION_90"] = turn_duration
    
    # Save updated calibration
    save_calibration(calib)
    
    print(f"Calibration complete! TURN_DURATION_90 = {turn_duration:.3f}s")
    return turn_duration

def calibrate_sensors(adc):
    """Calibrate line sensor thresholds"""
    print("\n=== Sensor Calibration ===")
    print("This will calibrate the line sensor thresholds")
    input("Place the car over a white surface and press Enter...")
    
    # Load current calibration
    calib = load_calibration()
    
    # Measure white surface values
    white_values = []
    for _ in range(10):
        white_values.append(adc.recvADC(0))
        time.sleep(0.1)
    white_avg = sum(white_values) / len(white_values)
    
    input("Now place the car over a black line and press Enter...")
    
    # Measure black line values
    black_values = []
    for _ in range(10):
        black_values.append(adc.recvADC(0))
        time.sleep(0.1)
    black_avg = sum(black_values) / len(black_values)
    
    # Calculate threshold
    threshold = (white_avg + black_avg) / 2
    calib["SENSOR_THRESHOLD"] = threshold
    
    # Save updated calibration
    save_calibration(calib)
    
    print(f"Calibration complete! SENSOR_THRESHOLD = {threshold:.0f}")
    return threshold

def run_full_calibration(pwm, adc):
    """Run complete calibration procedure"""
    print("\n=== Starting Full Calibration ===")
    
    # Calibrate straight movement
    calibrate_straight_movement(pwm)
    
    # Calibrate turns
    calibrate_turn(pwm)
    
    # Calibrate sensors
    calibrate_sensors(adc)
    
    print("\n=== Full Calibration Complete ===")
    print("All parameters have been calibrated and saved.") 