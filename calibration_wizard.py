"""
Calibration Wizard
Guided calibration sequence for face tracking
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Optional, Callable


class CalibrationWizard:
    def __init__(self, parent, config_manager, get_current_pose_callback: Callable):
        """
        Initialize calibration wizard
        
        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            get_current_pose_callback: Function that returns current head pose
        """
        self.parent = parent
        self.config_manager = config_manager
        self.get_current_pose = get_current_pose_callback
        
        # Calibration state
        self.calibration_steps = [
            {
                'title': 'Neutral Position',
                'instruction': 'Look straight ahead at the camera.\nKeep your head level and centered.\n\nThis will be your zero/neutral position.',
                'action': 'capture_neutral',
                'duration': 6,
                'axes': ['pitch', 'yaw', 'roll']
            },
            {
                'title': 'Pitch - Look Up',
                'instruction': 'Tilt your head UP as far as comfortable.\n\nThis sets the maximum upward angle.',
                'action': 'capture_pitch_max',
                'duration': 4,
                'axes': ['pitch']
            },
            {
                'title': 'Pitch - Look Down',
                'instruction': 'Tilt your head DOWN as far as comfortable.\n\nThis sets the maximum downward angle.',
                'action': 'capture_pitch_min',
                'duration': 4,
                'axes': ['pitch']
            },
            {
                'title': 'Yaw - Turn Right',
                'instruction': 'Turn your head to the RIGHT as far as comfortable.\n\nThis sets the maximum right angle.',
                'action': 'capture_yaw_max',
                'duration': 4,
                'axes': ['yaw']
            },
            {
                'title': 'Yaw - Turn Left',
                'instruction': 'Turn your head to the LEFT as far as comfortable.\n\nThis sets the maximum left angle.',
                'action': 'capture_yaw_min',
                'duration': 4,
                'axes': ['yaw']
            },
            {
                'title': 'Roll - Tilt Right',
                'instruction': 'Tilt your head to the RIGHT SIDE\n(ear toward right shoulder).\n\nThis sets the maximum right tilt.',
                'action': 'capture_roll_max',
                'duration': 4,
                'axes': ['roll']
            },
            {
                'title': 'Roll - Tilt Left',
                'instruction': 'Tilt your head to the LEFT SIDE\n(ear toward left shoulder).\n\nThis sets the maximum left tilt.',
                'action': 'capture_roll_min',
                'duration': 4,
                'axes': ['roll']
            },
            {
                'title': 'Calibration Complete!',
                'instruction': 'Calibration successful!\n\nYour head movements are now mapped.\nYou can adjust individual settings in the axis tabs.',
                'action': 'complete',
                'duration': 0,
                'axes': []
            }
        ]
        
        self.current_step = 0
        self.is_running = False
        self.neutral_values = {}
        self.captured_values = {}
        
        # Create wizard window
        self.create_window()
    
    def create_window(self):
        """Create the calibration wizard window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Calibration Wizard")
        self.window.geometry("500x550")
        self.window.resizable(False, False)
        
        # Make it modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.window, 
            mode='determinate',
            maximum=len(self.calibration_steps) - 1
        )
        self.progress.pack(fill="x", padx=20, pady=(20, 10))
        
        # Step counter
        self.step_label = ttk.Label(
            self.window, 
            text=f"Step 1 of {len(self.calibration_steps) - 1}",
            font=("", 10)
        )
        self.step_label.pack(pady=(0, 10))
        
        # Title
        self.title_label = ttk.Label(
            self.window,
            text="",
            font=("", 14, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Instruction text
        self.instruction_text = tk.Text(
            self.window,
            height=8,
            width=50,
            wrap="word",
            font=("", 11),
            relief="flat",
            background=self.window.cget('background')
        )
        self.instruction_text.pack(pady=10, padx=20)
        self.instruction_text.tag_configure("center", justify="center")
        
        # Countdown label
        self.countdown_label = ttk.Label(
            self.window,
            text="",
            font=("", 24, "bold"),
            foreground="blue"
        )
        self.countdown_label.pack(pady=10)
        
        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Calibration",
            command=self.start_calibration
        )
        self.start_button.pack(side="left", padx=5)
        
        self.skip_button = ttk.Button(
            button_frame,
            text="Skip Step",
            command=self.skip_step,
            state="disabled"
        )
        self.skip_button.pack(side="left", padx=5)
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack(side="left", padx=5)
        
        # Show first step
        self.show_step(0)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def show_step(self, step_index: int):
        """Display a calibration step"""
        if step_index >= len(self.calibration_steps):
            return
        
        step = self.calibration_steps[step_index]
        
        # Update progress
        self.progress['value'] = step_index
        if step_index < len(self.calibration_steps) - 1:
            self.step_label.config(text=f"Step {step_index + 1} of {len(self.calibration_steps) - 1}")
        else:
            self.step_label.config(text="Complete!")
        
        # Update title
        self.title_label.config(text=step['title'])
        
        # Update instruction
        self.instruction_text.config(state="normal")
        self.instruction_text.delete(1.0, "end")
        self.instruction_text.insert(1.0, step['instruction'])
        self.instruction_text.tag_add("center", 1.0, "end")
        self.instruction_text.config(state="disabled")
        
        # Clear countdown
        self.countdown_label.config(text="")
    
    def start_calibration(self):
        """Start the calibration sequence"""
        self.is_running = True
        self.current_step = 0
        self.neutral_values = {}
        self.captured_values = {}
        
        self.start_button.config(state="disabled")
        self.skip_button.config(state="normal")
        
        self.run_current_step()
    
    def run_current_step(self):
        """Execute the current calibration step"""
        if not self.is_running or self.current_step >= len(self.calibration_steps):
            return
        
        step = self.calibration_steps[self.current_step]
        
        if step['action'] == 'complete':
            self.finish_calibration()
            return
        
        # Show countdown
        duration = step['duration']
        self.countdown(duration, step['action'])
    
    def countdown(self, seconds: int, action: str):
        """Display countdown and capture at the end"""
        if not self.is_running:
            return
        
        if seconds > 0:
            self.countdown_label.config(text=str(seconds), foreground="blue")
            self.window.after(1000, lambda: self.countdown(seconds - 1, action))
        else:
            self.countdown_label.config(text="✓", foreground="green")
            self.capture_position(action)
            self.window.after(500, self.next_step)
    
    def capture_position(self, action: str):
        """Capture the current head pose"""
        pose = self.get_current_pose()
        
        if pose is None:
            print(f"Warning: No face detected during calibration step: {action}")
            return
        
        if action == 'capture_neutral':
            # Store neutral position
            self.neutral_values = pose.copy()
            print(f"Neutral position captured: {pose}")
            
        elif action == 'capture_pitch_max':
            # Calculate relative to neutral and set as max
            value = pose['pitch'] - self.neutral_values.get('pitch', 0)
            self.captured_values['pitch_max'] = value
            print(f"Pitch max captured: {value:.1f}°")
            
        elif action == 'capture_pitch_min':
            value = pose['pitch'] - self.neutral_values.get('pitch', 0)
            self.captured_values['pitch_min'] = value
            print(f"Pitch min captured: {value:.1f}°")
            
        elif action == 'capture_yaw_max':
            value = pose['yaw'] - self.neutral_values.get('yaw', 0)
            self.captured_values['yaw_max'] = value
            print(f"Yaw max captured: {value:.1f}°")
            
        elif action == 'capture_yaw_min':
            value = pose['yaw'] - self.neutral_values.get('yaw', 0)
            self.captured_values['yaw_min'] = value
            print(f"Yaw min captured: {value:.1f}°")
            
        elif action == 'capture_roll_max':
            value = pose['roll'] - self.neutral_values.get('roll', 0)
            self.captured_values['roll_max'] = value
            print(f"Roll max captured: {value:.1f}°")
            
        elif action == 'capture_roll_min':
            value = pose['roll'] - self.neutral_values.get('roll', 0)
            self.captured_values['roll_min'] = value
            print(f"Roll min captured: {value:.1f}°")
    
    def next_step(self):
        """Move to the next calibration step"""
        if not self.is_running:
            return
        
        self.current_step += 1
        
        if self.current_step < len(self.calibration_steps):
            self.show_step(self.current_step)
            self.run_current_step()
        else:
            self.finish_calibration()
    
    def skip_step(self):
        """Skip the current step"""
        if not self.is_running:
            return
        
        self.countdown_label.config(text="Skipped", foreground="orange")
        self.window.after(500, self.next_step)
    
    def finish_calibration(self):
        """Apply calibration and close wizard"""
        self.is_running = False
        self.skip_button.config(state="disabled")
        
        # Save neutral offsets
        if self.neutral_values:
            self.config_manager.set_neutral_offsets(self.neutral_values)
            print(f"Neutral offsets saved: {self.neutral_values}")
        
        # Apply captured values to configuration
        for axis in ['pitch', 'yaw', 'roll']:
            min_key = f'{axis}_min'
            max_key = f'{axis}_max'
            
            if min_key in self.captured_values and max_key in self.captured_values:
                # Ensure min is actually less than max
                min_val = min(self.captured_values[min_key], self.captured_values[max_key])
                max_val = max(self.captured_values[min_key], self.captured_values[max_key])
                
                self.config_manager.update_axis_config(axis, 'input_min', min_val)
                self.config_manager.update_axis_config(axis, 'input_max', max_val)
                print(f"{axis.capitalize()} range set: {min_val:.1f}° to {max_val:.1f}°")
        
        # Change button to close
        self.cancel_button.config(text="Close", command=self.close)
    
    def cancel(self):
        """Cancel calibration"""
        self.is_running = False
        self.window.destroy()
    
    def close(self):
        """Close the wizard"""
        self.window.destroy()
