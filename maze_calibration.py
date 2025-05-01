#!/usr/bin/env python3
# maze_calibration.py - Calibration utilities for maze navigation system
# This module handles the calibration of movement parameters, sensor thresholds,
# and other critical values needed for accurate maze navigation.

import json
import os
import time
from pathlib import Path

# Default calibration parameters for the maze navigation system
DEFAULT_CALIBRATION_VALUES = {
    "seconds_per_cell": 0.5,      # Time required to move one cell forward (seconds)
    "turn_duration_90_degrees": 0.65, # Time required for a 90-degree turn (seconds)
    "base_motor_speed": 2000,     # Default motor speed for straight movement
    "turn_motor_speed": 2500,     # Motor speed used during turns
    "line_sensor_threshold": 1000, # Threshold value for line detection
    "wall_following_distance": 15.0, # Optimal distance to maintain from walls (cm)
    "line_following_speed": 1500  # Motor speed for line following mode
}

def load_calibration_settings(calibration_file_path="~/maze_solver/calibration.json"):
    """
    Load calibration parameters from a JSON configuration file.
    
    Args:
        calibration_file_path (str): Path to the calibration file
        
    Returns:
        dict: Dictionary containing calibration parameters
    """
    expanded_path = Path(os.path.expanduser(calibration_file_path))
    
    # Ensure the directory exists
    expanded_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if expanded_path.exists():
            with open(expanded_path, 'r') as config_file:
                return json.load(config_file)
        else:
            # Create default calibration file if it doesn't exist
            save_calibration_settings(DEFAULT_CALIBRATION_VALUES, calibration_file_path)
            return DEFAULT_CALIBRATION_VALUES
    except Exception as error:
        print(f"Error loading calibration settings: {error}")
        return DEFAULT_CALIBRATION_VALUES

def save_calibration_settings(calibration_data, calibration_file_path="~/maze_solver/calibration.json"):
    """
    Save calibration parameters to a JSON configuration file.
    
    Args:
        calibration_data (dict): Dictionary containing calibration parameters
        calibration_file_path (str): Path to save the calibration file
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    expanded_path = Path(os.path.expanduser(calibration_file_path))
    
    # Ensure the directory exists
    expanded_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(expanded_path, 'w') as config_file:
            json.dump(calibration_data, config_file, indent=2)
        print(f"Calibration settings saved to {expanded_path}")
        return True
    except Exception as error:
        print(f"Error saving calibration settings: {error}")
        return False

def calibrate_forward_movement(motor_controller, target_speed=2000):
    """
    Calibrate the forward movement parameters for the maze navigation system.
    Measures the time required to move one cell forward at a given speed.
    
    Args:
        motor_controller: The motor controller interface
        target_speed (int): Desired motor speed for calibration
        
    Returns:
        float: Time in seconds required to move one cell forward
    """
    print("\n=== Forward Movement Calibration ===")
    print("This procedure will measure the time needed to move one cell forward")
    input("Press Enter when ready to start calibration...")
    
    # Load current calibration settings
    current_calibration = load_calibration_settings()
    
    # Measure time for forward movement
    start_time = time.time()
    motor_controller.setMotorModel(target_speed, target_speed, target_speed, target_speed)
    input("Press Enter when the car has moved one cell forward...")
    motor_controller.setMotorModel(0, 0, 0, 0)
    end_time = time.time()
    
    # Calculate and update calibration
    movement_time = end_time - start_time
    current_calibration["seconds_per_cell"] = movement_time
    
    # Save updated calibration
    save_calibration_settings(current_calibration)
    
    print(f"Calibration complete! Time per cell = {movement_time:.3f} seconds")
    return movement_time

def calibrate_turning(motor_controller, turn_speed=2500):
    """
    Calibrate the turning parameters for 90-degree turns.
    Measures the time required to complete a 90-degree turn.
    
    Args:
        motor_controller: The motor controller interface
        turn_speed (int): Desired motor speed for turning
        
    Returns:
        float: Time in seconds required for a 90-degree turn
    """
    print("\n=== Turning Calibration ===")
    print("This procedure will measure the time needed for a 90-degree turn")
    input("Press Enter when ready to start calibration...")
    
    # Load current calibration settings
    current_calibration = load_calibration_settings()
    
    # Measure time for turn
    start_time = time.time()
    motor_controller.setMotorModel(-turn_speed, -turn_speed, turn_speed, turn_speed)  # Left turn
    input("Press Enter when the car has turned 90 degrees...")
    motor_controller.setMotorModel(0, 0, 0, 0)
    end_time = time.time()
    
    # Calculate and update calibration
    turn_time = end_time - start_time
    current_calibration["turn_duration_90_degrees"] = turn_time
    
    # Save updated calibration
    save_calibration_settings(current_calibration)
    
    print(f"Calibration complete! Turn duration = {turn_time:.3f} seconds")
    return turn_time

def calibrate_line_sensors(adc_interface):
    """
    Calibrate the line sensor thresholds for accurate line detection.
    Measures sensor values on white and black surfaces to determine optimal threshold.
    
    Args:
        adc_interface: The ADC interface for reading sensor values
        
    Returns:
        int: Calculated threshold value for line detection
    """
    print("\n=== Line Sensor Calibration ===")
    print("This procedure will calibrate the line sensor thresholds")
    input("Place the car over a white surface and press Enter...")
    
    # Load current calibration settings
    current_calibration = load_calibration_settings()
    
    # Measure white surface values
    white_surface_readings = []
    for _ in range(10):
        white_surface_readings.append(adc_interface.recvADC(0))
        time.sleep(0.1)
    white_surface_average = sum(white_surface_readings) / len(white_surface_readings)
    
    input("Now place the car over a black line and press Enter...")
    
    # Measure black line values
    black_line_readings = []
    for _ in range(10):
        black_line_readings.append(adc_interface.recvADC(0))
        time.sleep(0.1)
    black_line_average = sum(black_line_readings) / len(black_line_readings)
    
    # Calculate optimal threshold
    detection_threshold = (white_surface_average + black_line_average) / 2
    current_calibration["line_sensor_threshold"] = detection_threshold
    
    # Save updated calibration
    save_calibration_settings(current_calibration)
    
    print(f"Calibration complete! Line detection threshold = {detection_threshold:.0f}")
    return detection_threshold

def perform_full_calibration(motor_controller, adc_interface):
    """
    Execute the complete calibration procedure for all system parameters.
    This includes forward movement, turning, and line sensor calibration.
    
    Args:
        motor_controller: The motor controller interface
        adc_interface: The ADC interface for reading sensor values
    """
    print("\n=== Starting Complete Calibration Procedure ===")
    
    # Calibrate forward movement
    calibrate_forward_movement(motor_controller)
    
    # Calibrate turning
    calibrate_turning(motor_controller)
    
    # Calibrate line sensors
    calibrate_line_sensors(adc_interface)
    
    print("\n=== Calibration Complete ===")
    print("All system parameters have been calibrated and saved.") 