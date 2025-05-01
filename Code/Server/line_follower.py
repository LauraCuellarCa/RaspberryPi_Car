import time
import RPi.GPIO as GPIO
from motor import *
from ultrasonic import Ultrasonic
from buzzer import Buzzer
import numpy as np
from maze_navigator import MazeNavigator

print("Starting line follower initialization...")

# Sensor pin configuration
LEFT_SENSOR_PIN = 14
CENTER_SENSOR_PIN = 15
RIGHT_SENSOR_PIN = 23

print(f"Setting up GPIO pins: Left={LEFT_SENSOR_PIN}, Center={CENTER_SENSOR_PIN}, Right={RIGHT_SENSOR_PIN}")

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_SENSOR_PIN, GPIO.IN)
GPIO.setup(CENTER_SENSOR_PIN, GPIO.IN)
GPIO.setup(RIGHT_SENSOR_PIN, GPIO.IN)

print("GPIO setup complete")

# Initialize hardware components
print("Initializing motor controller...")
try:
    motor_controller = Ordinary_Car()
    print("Motor controller initialized successfully")
except Exception as e:
    print(f"Error initializing motor controller: {e}")
    GPIO.cleanup()
    exit(1)

print("Initializing ultrasonic sensor...")
try:
    distance_sensor = Ultrasonic()
    print("Ultrasonic sensor initialized successfully")
except Exception as e:
    print(f"Error initializing ultrasonic sensor: {e}")
    motor_controller.close()
    GPIO.cleanup()
    exit(1)

print("Initializing buzzer...")
try:
    alert_buzzer = Buzzer()
    print("Buzzer initialized successfully")
except Exception as e:
    print(f"Error initializing buzzer: {e}")
    motor_controller.close()
    GPIO.cleanup()
    exit(1)

# PID Controller configuration
PROPORTIONAL_GAIN = 12   # Increased for faster corrections
INTEGRAL_GAIN = 0.1     # Small integral term to eliminate steady-state error
DERIVATIVE_GAIN = 8     # Increased for quicker response

# Motor speed configuration
NORMAL_SPEED = 1200     # Base speed for normal operation
TURNING_SPEED = 2500    # Speed for turning maneuvers
MAX_ACCELERATION = 800  # Maximum speed change per step

# Line following state tracking
previous_error = 0
error_integral = 0
last_update_time = time.time()
line_lost_count = 0
MAX_LOST_LINE_COUNT = 2  # Reduced for faster turn detection
current_turn_state = 'STRAIGHT'
turn_start_timestamp = 0
TURN_TIMEOUT_DURATION = 0.8  # Reduced timeout for faster recovery

# Motor speed tracking
current_left_motor_speed = 0
current_right_motor_speed = 0

# Sensor configuration
should_invert_sensors = False

def calibrate_sensors():
    """Calibrate sensors and verify they're working"""
    print("\nStarting sensor calibration...")
    print("Please position the car so that:")
    print("1. All sensors are OVER the line")
    print("2. Press Enter when ready")
    input()
    
    print("\nReading sensor values when over the line...")
    # Read all sensors multiple times
    sensor_readings = []
    for reading_count in range(10):
        left_value = GPIO.input(LEFT_SENSOR_PIN)
        center_value = GPIO.input(CENTER_SENSOR_PIN)
        right_value = GPIO.input(RIGHT_SENSOR_PIN)
        sensor_readings.append((left_value, center_value, right_value))
        print(f"Reading {reading_count+1}/10: L={left_value}, C={center_value}, R={right_value}")
        time.sleep(0.1)
    
    # Calculate most common reading
    most_common_reading = max(set(sensor_readings), key=sensor_readings.count)
    print(f"\nMost common reading when over line: L={most_common_reading[0]}, C={most_common_reading[1]}, R={most_common_reading[2]}")
    
    print("\nNow position the car so that:")
    print("1. All sensors are OFF the line")
    print("2. Press Enter when ready")
    input()
    
    print("\nReading sensor values when off the line...")
    # Read all sensors multiple times
    sensor_readings = []
    for reading_count in range(10):
        left_value = GPIO.input(LEFT_SENSOR_PIN)
        center_value = GPIO.input(CENTER_SENSOR_PIN)
        right_value = GPIO.input(RIGHT_SENSOR_PIN)
        sensor_readings.append((left_value, center_value, right_value))
        print(f"Reading {reading_count+1}/10: L={left_value}, C={center_value}, R={right_value}")
        time.sleep(0.1)
    
    # Calculate most common reading
    most_common_off_reading = max(set(sensor_readings), key=sensor_readings.count)
    print(f"\nMost common reading when off line: L={most_common_off_reading[0]}, C={most_common_off_reading[1]}, R={most_common_off_reading[2]}")
    
    # Determine if we need to invert the readings
    global should_invert_sensors
    should_invert_sensors = (most_common_reading[0] == 0)  # If 0 means "on line", we need to invert
    
    print(f"\nSensor logic {'will' if should_invert_sensors else 'will not'} be inverted")
    print("Calibration complete!")
    print("\nPosition the car on the line and press Enter to start")
    input()
    
    # Test motor response
    print("\nTesting motor response...")
    try:
        print("Setting all motors to 0...")
        motor_controller.set_motor_model(0, 0, 0, 0)
        time.sleep(1)
        
        print("Testing forward motion...")
        motor_controller.set_motor_model(500, 500, 500, 500)
        time.sleep(0.5)
        
        print("Testing stop...")
        motor_controller.set_motor_model(0, 0, 0, 0)
        time.sleep(0.5)
        
        print("Motor test complete!")
    except Exception as e:
        print(f"Error during motor test: {e}")
        return False
    
    return True

def read_sensors():
    """Read and optionally invert sensor values"""
    left_value = GPIO.input(LEFT_SENSOR_PIN)
    center_value = GPIO.input(CENTER_SENSOR_PIN)
    right_value = GPIO.input(RIGHT_SENSOR_PIN)
    
    if should_invert_sensors:
        left_value = 1 - left_value
        center_value = 1 - center_value
        right_value = 1 - right_value
        
    print(f"Raw: L={GPIO.input(LEFT_SENSOR_PIN)}, C={GPIO.input(CENTER_SENSOR_PIN)}, R={GPIO.input(RIGHT_SENSOR_PIN)}")
    print(f"Processed: L={left_value}, C={center_value}, R={right_value}")
    return left_value, center_value, right_value

def calculate_error(left_value, center_value, right_value):
    # Debug print
    print(f"Calculating error - L:{left_value} C:{center_value} R:{right_value}")
    
    if center_value == 1 and left_value == 0 and right_value == 0:  # Center on line
        return 0
    elif left_value == 1 and center_value == 1 and right_value == 0:  # Line slightly to the left
        return -1
    elif left_value == 1 and center_value == 0 and right_value == 0:  # Line far to the left
        return -2
    elif right_value == 1 and center_value == 1 and left_value == 0:  # Line slightly to the right
        return 1
    elif right_value == 1 and center_value == 0 and left_value == 0:  # Line far to the right
        return 2
    elif left_value == 1 and center_value == 1 and right_value == 1:  # T-junction or crossroad
        return 0
    elif left_value == 1 and right_value == 1:  # Wide line or special case
        return 0
    else:  # Line lost
        return None

def smooth_speed_change(current_speed, target_speed):
    """Gradually change speed to avoid jerky movements"""
    speed_difference = target_speed - current_speed
    if abs(speed_difference) > MAX_ACCELERATION:
        if speed_difference > 0:
            return current_speed + MAX_ACCELERATION
        else:
            return current_speed - MAX_ACCELERATION
    return target_speed

def handle_sharp_turn(left_value, center_value, right_value):
    global current_turn_state, turn_start_timestamp, line_lost_count, current_left_motor_speed, current_right_motor_speed
    
    current_time = time.time()
    
    # Reset turn state if we're back on the line
    if center_value == 1 and current_turn_state != 'STRAIGHT':
        print("Back on line - resetting turn state")
        current_turn_state = 'STRAIGHT'
        line_lost_count = 0
        return False

    # Check for sharp turn conditions - more sensitive detection
    if (center_value == 0 and (left_value == 1 or right_value == 1)) or (left_value == 0 and right_value == 1) or (left_value == 1 and right_value == 0):
        # First stop the motors briefly
        try:
            motor_controller.set_motor_model(0, 0, 0, 0)
            time.sleep(0.02)  # Even shorter pause
        except Exception as e:
            print(f"Error stopping motors: {e}")
            return False
        
        if right_value == 1:  # Sensor on right sees line - turn right
            print("Sharp right turn detected")
            current_turn_state = 'TURNING_RIGHT'
            # More aggressive turn speeds
            current_left_motor_speed = int(TURNING_SPEED * 1.2)  # Boost inside wheel
            current_right_motor_speed = int(-TURNING_SPEED * 0.8)
        elif left_value == 1:  # Sensor on left sees line - turn left
            print("Sharp left turn detected")
            current_turn_state = 'TURNING_LEFT'
            # More aggressive turn speeds
            current_left_motor_speed = int(-TURNING_SPEED * 0.8)
            current_right_motor_speed = int(TURNING_SPEED * 1.2)  # Boost inside wheel
            
        try:
            motor_controller.set_motor_model(current_left_motor_speed, current_left_motor_speed, 
                                current_right_motor_speed, current_right_motor_speed)
        except Exception as e:
            print(f"Error setting motor speeds: {e}")
            return False
        
        turn_start_timestamp = current_time
        return True
        
    # If we've lost the line completely
    if left_value == 0 and center_value == 0 and right_value == 0:
        line_lost_count += 1
        if line_lost_count > MAX_LOST_LINE_COUNT:
            # Continue turning in the last known direction with increased speed
            if current_turn_state == 'TURNING_LEFT':
                current_left_motor_speed = int(-TURNING_SPEED * 0.8)
                current_right_motor_speed = int(TURNING_SPEED * 1.2)
            elif current_turn_state == 'TURNING_RIGHT':
                current_left_motor_speed = int(TURNING_SPEED * 1.2)
                current_right_motor_speed = int(-TURNING_SPEED * 0.8)
            else:
                # If we don't know which way to turn, try turning right
                print("Line lost - attempting recovery turn right")
                current_left_motor_speed = int(TURNING_SPEED * 1.2)
                current_right_motor_speed = int(-TURNING_SPEED * 0.8)
                current_turn_state = 'TURNING_RIGHT'
                
            try:
                motor_controller.set_motor_model(current_left_motor_speed, current_left_motor_speed, 
                                    current_right_motor_speed, current_right_motor_speed)
            except Exception as e:
                print(f"Error setting motor speeds during line loss: {e}")
                return False
            return True
            
    # Check if we've been turning too long
    if current_turn_state != 'STRAIGHT' and (current_time - turn_start_timestamp) > TURN_TIMEOUT_DURATION:
        print("Turn timeout - resetting")
        current_turn_state = 'STRAIGHT'
        line_lost_count = 0
        try:
            motor_controller.set_motor_model(0, 0, 0, 0)  # Stop motors on timeout
        except Exception as e:
            print(f"Error stopping motors on timeout: {e}")
        
    return False

def check_line_end(left_value, center_value, right_value, consecutive_readings=20):
    """Check if we've reached the end of the line"""
    print("\nChecking for line end...")
    zero_readings_count = 0
    max_consecutive_zeros = 0
    current_consecutive_zeros = 0
    
    # First, stop and back up slightly to ensure we're not at an intersection
    motor_controller.set_motor_model(-1000, -1000, -1000, -1000)
    time.sleep(0.2)  # Back up briefly
    motor_controller.set_motor_model(0, 0, 0, 0)
    time.sleep(0.5)  # Wait for stability
    
    # Do a rotation check to look for lines in other directions
    print("Performing rotation check for intersections...")
    for rotation_angle in [45, 90, 135, 180, 225, 270, 315, 360]:
        # Turn to the angle
        motor_controller.set_motor_model(1000, 1000, -1000, -1000)  # Turn right
        time.sleep(rotation_angle/360.0)  # Approximate time for degree turn
        motor_controller.set_motor_model(0, 0, 0, 0)
        time.sleep(0.1)
        
        # Check sensors
        left_sensor, center_sensor, right_sensor = read_sensors()
        print(f"Rotation check at {rotation_angle}°: L={left_sensor}, C={center_sensor}, R={right_sensor}")
        if left_sensor == 1 or center_sensor == 1 or right_sensor == 1:
            print(f"Found line at {rotation_angle}° rotation - this is an intersection")
            return False
    
    # If no lines found in rotation, check for true end
    print("No lines found in rotation, checking for true end...")
    for reading_count in range(consecutive_readings):
        left_sensor, center_sensor, right_sensor = read_sensors()
        print(f"End check reading {reading_count+1}/{consecutive_readings}: L={left_sensor}, C={center_sensor}, R={right_sensor}")
        if left_sensor == 0 and center_sensor == 0 and right_sensor == 0:
            current_consecutive_zeros += 1
            max_consecutive_zeros = max(max_consecutive_zeros, current_consecutive_zeros)
            zero_readings_count += 1
        else:
            current_consecutive_zeros = 0
            print("Found line signal - not at end")
            return False
        time.sleep(0.1)
    
    # Only return True if we had enough consecutive zero readings
    if zero_readings_count == consecutive_readings and max_consecutive_zeros >= 15:
        print("Confirmed end of line - all readings showed no line")
        return True
    return False

def cleanup_components():
    """Clean up all components properly"""
    print("\nCleaning up components...")
    try:
        motor_controller.set_motor_model(0, 0, 0, 0)
        motor_controller.close()
        print("Motor cleaned up")
    except Exception as e:
        print(f"Error cleaning up motor: {e}")
    
    try:
        distance_sensor.cleanup()
        print("Ultrasonic sensor cleaned up")
    except Exception as e:
        print(f"Error cleaning up ultrasonic: {e}")
    
    try:
        alert_buzzer.cleanup()
        print("Buzzer cleaned up")
    except Exception as e:
        print(f"Error cleaning up buzzer: {e}")
    
    try:
        GPIO.cleanup()
        print("GPIO cleaned up")
    except Exception as e:
        print(f"Error cleaning up GPIO: {e}")

def follow_line():
    global previous_error, error_integral, last_update_time, current_left_motor_speed, current_right_motor_speed
    
    try:
        print("Starting improved line follower...")
        print("Motor controller initialized")
        
        consecutive_line_lost = 0
        LINE_END_THRESHOLD = 40  # Increased threshold for more certainty
        last_turn_time = time.time()
        MIN_TIME_BETWEEN_CHECKS = 5  # Minimum seconds between end checks
        
        while True:
            left_sensor, center_sensor, right_sensor = read_sensors()
            current_time = time.time()
            
            # Check if we've reached the end of the line
            if left_sensor == 0 and center_sensor == 0 and right_sensor == 0:
                consecutive_line_lost += 1
                if consecutive_line_lost >= LINE_END_THRESHOLD:
                    # Only do end check if enough time has passed since last check
                    if current_time - last_turn_time >= MIN_TIME_BETWEEN_CHECKS:
                        # Stop the motors before checking
                        motor_controller.set_motor_model(0, 0, 0, 0)
                        time.sleep(0.5)  # Wait for complete stop
                        
                        # Do a thorough check for line end
                        if check_line_end(left_sensor, center_sensor, right_sensor):
                            print("End of line detected - switching to maze solver")
                            motor_controller.set_motor_model(0, 0, 0, 0)
                            # Clean up components before switching to maze solver
                            cleanup_components()
                            return True  # Signal to switch to maze solving
                        else:
                            consecutive_line_lost = 0  # Reset counter if it wasn't actually the end
                            last_turn_time = current_time
                    else:
                        print("Too soon since last check, continuing line following")
                        consecutive_line_lost = 0
            else:
                consecutive_line_lost = 0
            
            # Check for sharp turn first
            if handle_sharp_turn(left_sensor, center_sensor, right_sensor):
                continue
                
            # Calculate error for PID control
            error = calculate_error(left_sensor, center_sensor, right_sensor)
            
            if error is not None:
                # PID calculations
                current_time = time.time()
                time_delta = current_time - last_update_time
                time_delta = max(time_delta, 0.001)  # Prevent division by zero
                
                # Calculate PID terms
                proportional_term = PROPORTIONAL_GAIN * error
                error_integral += INTEGRAL_GAIN * error * time_delta
                derivative_term = DERIVATIVE_GAIN * (error - previous_error) / time_delta
                
                # Calculate motor adjustment
                speed_adjustment = int(proportional_term + error_integral + derivative_term)
                
                # Calculate target speeds
                target_left_speed = int(NORMAL_SPEED - speed_adjustment)
                target_right_speed = int(NORMAL_SPEED + speed_adjustment)
                
                # Smooth speed transitions
                current_left_motor_speed = smooth_speed_change(current_left_motor_speed, target_left_speed)
                current_right_motor_speed = smooth_speed_change(current_right_motor_speed, target_right_speed)
                
                # Clamp speeds to valid range
                current_left_motor_speed = max(-4095, min(4095, current_left_motor_speed))
                current_right_motor_speed = max(-4095, min(4095, current_right_motor_speed))
                
                # Apply motor speeds
                try:
                    motor_controller.set_motor_model(current_left_motor_speed, current_left_motor_speed,
                                        current_right_motor_speed, current_right_motor_speed)
                except Exception as e:
                    print(f"Error setting motor speeds: {e}")
                    continue
                
                # Update for next iteration
                previous_error = error
                last_update_time = current_time
            
            time.sleep(0.005)  # Reduced delay for faster processing
            
    except KeyboardInterrupt:
        print("\nStopping motors...")
        try:
            motor_controller.set_motor_model(0, 0, 0, 0)
        except Exception as e:
            print(f"Error stopping motors: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error in line following: {e}")
        return False

if __name__ == "__main__":
    try:
        print("Starting line follower program...")
        print("First, let's calibrate the sensors...")
        
        # Run calibration
        if not calibrate_sensors():
            print("Calibration failed! Exiting...")
            cleanup_components()
            exit(1)
        
        print("Calibration complete! Starting line following...")
        if follow_line():  # If line following ends normally (reached end of line)
            print("Switching to maze solving mode...")
            # Initialize new GPIO for maze solver
            GPIO.setmode(GPIO.BCM)
            maze_navigator = MazeNavigator()
            maze_navigator.explore_maze()
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Clean stop
        print("Cleaning up...")
        cleanup_components()