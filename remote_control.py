#!/usr/bin/env python3
# remote_control.py - Remote control the car using command line input

import sys
import time
import json
from datetime import datetime
from Motor import *

class RemoteControl:
    def __init__(self):
        # Movement speeds
        self.FORWARD_SPEED = 800
        self.BACKWARD_SPEED = 1500
        self.TURN_SPEED = 2000
        
        # Command mapping
        self.commands = {
            'w': 'forward',
            's': 'backward',
            'a': 'left',
            'd': 'right',
            'wa': 'forward_left',
            'wd': 'forward_right',
            'sa': 'backward_left',
            'sd': 'backward_right',
            'q': 'quit'
        }
        
        # Movement recording
        self.movement_history = []
        self.last_command_time = None
        self.recording_file = f"movement_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def record_movement(self, cmd, motor_speeds):
        """Record a movement with timestamp and motor speeds"""
        current_time = time.time()
        duration = 0
        if self.last_command_time is not None:
            duration = current_time - self.last_command_time
        
        movement = {
            'timestamp': datetime.now().isoformat(),
            'command': cmd,
            'motor_speeds': motor_speeds,
            'duration': duration
        }
        
        self.movement_history.append(movement)
        self.last_command_time = current_time
        
        # Save to file after each movement
        with open(self.recording_file, 'w') as f:
            json.dump(self.movement_history, f, indent=2)
            
    def print_help(self):
        """Print available commands"""
        print("\nAvailable commands:")
        print("w: Move forward")
        print("s: Move backward")
        print("a: Turn left")
        print("d: Turn right")
        print("wa: Move forward while turning left")
        print("wd: Move forward while turning right")
        print("sa: Move backward while turning left")
        print("sd: Move backward while turning right")
        print("q: Quit")
        print("h: Show this help message")
        
    def execute_command(self, cmd):
        """Execute a movement command"""
        try:
            motor_speeds = None
            if cmd == 'forward':
                motor_speeds = [self.FORWARD_SPEED, self.FORWARD_SPEED, 
                              self.FORWARD_SPEED, self.FORWARD_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'backward':
                motor_speeds = [-self.BACKWARD_SPEED, -self.BACKWARD_SPEED,
                              -self.BACKWARD_SPEED, -self.BACKWARD_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'left':
                motor_speeds = [-self.TURN_SPEED, -self.TURN_SPEED,
                              self.TURN_SPEED, self.TURN_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'right':
                motor_speeds = [self.TURN_SPEED, self.TURN_SPEED,
                              -self.TURN_SPEED, -self.TURN_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'forward_left':
                motor_speeds = [-self.TURN_SPEED, -self.TURN_SPEED,
                              self.FORWARD_SPEED, self.FORWARD_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'forward_right':
                motor_speeds = [self.FORWARD_SPEED, self.FORWARD_SPEED,
                              -self.TURN_SPEED, -self.TURN_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'backward_left':
                motor_speeds = [-self.BACKWARD_SPEED, -self.BACKWARD_SPEED,
                              self.TURN_SPEED, self.TURN_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'backward_right':
                motor_speeds = [self.TURN_SPEED, self.TURN_SPEED,
                              -self.BACKWARD_SPEED, -self.BACKWARD_SPEED]
                PWM.setMotorModel(*motor_speeds)
            elif cmd == 'stop':
                motor_speeds = [0, 0, 0, 0]
                PWM.setMotorModel(*motor_speeds)
                
            if motor_speeds is not None:
                self.record_movement(cmd, motor_speeds)
                
        except Exception as e:
            print(f"Error executing command: {e}")
            PWM.setMotorModel(0, 0, 0, 0)
            
    def run(self):
        """Start the remote control"""
        print("Starting remote control...")
        print(f"Movement recording will be saved to: {self.recording_file}")
        self.print_help()
        
        try:
            while True:
                # Get user input
                cmd = input("\nEnter command (h for help): ").lower().strip()
                
                # Handle help command
                if cmd == 'h':
                    self.print_help()
                    continue
                    
                # Handle quit command
                if cmd == 'q':
                    print("Stopping remote control...")
                    break
                
                # Execute command if valid
                if cmd in self.commands:
                    self.execute_command(self.commands[cmd])
                else:
                    print("Invalid command. Type 'h' for help.")
                    
        except KeyboardInterrupt:
            print("\nStopping remote control...")
        finally:
            # Stop the car
            PWM.setMotorModel(0, 0, 0, 0)
            # Save final recording
            with open(self.recording_file, 'w') as f:
                json.dump(self.movement_history, f, indent=2)
            print(f"Movement recording saved to: {self.recording_file}")

if __name__ == "__main__":
    # Create and run remote control
    remote = RemoteControl()
    remote.run() 