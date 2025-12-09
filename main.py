"""
Face to MIDI - Main Application
Convert head movements to MIDI control signals
"""

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from face_tracker import FaceTracker
from midi_controller import MIDIController
from config_manager import ConfigManager
from calibration_wizard import CalibrationWizard

# Suppress MediaPipe warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class FaceToMIDIApp:
    def __init__(self, root):
        """Initialize the Face to MIDI application"""
        self.root = root
        self.root.title("Face to MIDI Controller")
        self.root.geometry("800x700")
        
        # Initialize components
        self.face_tracker = FaceTracker()
        self.midi_controller = MIDIController()
        self.config_manager = ConfigManager()
        
        # Application state
        self.is_running = False
        self.camera = None
        self.camera_thread = None
        self.debug_mode = False
        
        # Create UI
        self.create_ui()
        
        # Initialize MIDI
        self.setup_midi()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        """Create the user interface"""
        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding="10")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Tracking", 
                                       command=self.toggle_tracking)
        self.start_button.pack(side="left", padx=5)
        
        self.save_button = ttk.Button(control_frame, text="Save Config", 
                                      command=self.save_config)
        self.save_button.pack(side="left", padx=5)
        
        self.calibrate_button = ttk.Button(control_frame, text="Start Calibration",
                                          command=self.start_calibration_wizard)
        self.calibrate_button.pack(side="left", padx=5)
        
        self.zero_button = ttk.Button(control_frame, text="Set Zero Position",
                                     command=self.set_zero_position)
        self.zero_button.pack(side="left", padx=5)
        
        ttk.Separator(control_frame, orient="vertical").pack(side="left", fill="y", padx=5)
        
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = ttk.Checkbutton(control_frame, text="Debug Mode (No MIDI)",
                                          variable=self.debug_var,
                                          command=self.toggle_debug_mode)
        self.debug_check.pack(side="left", padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Status: Stopped")
        self.status_label.pack(side="left", padx=20)
        
        # Help button
        self.help_button = ttk.Button(control_frame, text="?",
                                     command=self.show_help, width=3)
        self.help_button.pack(side="right", padx=5)
        
        # MIDI Port Selection
        midi_frame = ttk.LabelFrame(self.root, text="MIDI Output", padding="10")
        midi_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(midi_frame, text="MIDI Port:").pack(side="left", padx=5)
        
        self.midi_port_var = tk.StringVar()
        self.midi_port_combo = ttk.Combobox(midi_frame, textvariable=self.midi_port_var, 
                                             width=30, state="readonly")
        self.midi_port_combo.pack(side="left", padx=5)
        self.midi_port_combo.bind("<<ComboboxSelected>>", self.on_midi_port_changed)
        
        # Create notebook for axis settings
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs for each axis
        self.axis_frames = {}
        self.axis_widgets = {}
        
        for axis in ['pitch', 'yaw', 'roll']:
            self.create_axis_tab(axis)
        
        # Status display
        status_frame = ttk.LabelFrame(self.root, text="Current Values", padding="10")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.value_labels = {}
        for i, axis in enumerate(['pitch', 'yaw', 'roll']):
            label = ttk.Label(status_frame, text=f"{axis.capitalize()}: 0.0° | MIDI: 0")
            label.grid(row=0, column=i, padx=20)
            self.value_labels[axis] = label
    
    def create_axis_tab(self, axis: str):
        """Create a tab for axis configuration"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text=axis.capitalize())
        self.axis_frames[axis] = frame
        
        config = self.config_manager.get_axis_config(axis)
        widgets = {}
        
        # Enabled checkbox
        enabled_var = tk.BooleanVar(value=config['enabled'])
        enabled_check = ttk.Checkbutton(frame, text="Enable this axis", 
                                        variable=enabled_var,
                                        command=lambda: self.update_axis_enabled(axis, enabled_var.get()))
        enabled_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        widgets['enabled_var'] = enabled_var
        
        # Input range
        ttk.Label(frame, text="Input Range (degrees)", font=("", 10, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        ttk.Label(frame, text="Minimum:").grid(row=2, column=0, sticky="w", padx=5)
        input_min_var = tk.DoubleVar(value=config['input_min'])
        input_min_spin = ttk.Spinbox(frame, from_=-180, to=180, increment=1, 
                                     textvariable=input_min_var, width=10)
        input_min_spin.grid(row=2, column=1, sticky="w", padx=5)
        input_min_spin.bind("<Return>", lambda e: self.update_axis_value(axis, 'input_min', input_min_var.get()))
        widgets['input_min_var'] = input_min_var
        
        ttk.Label(frame, text="Maximum:").grid(row=3, column=0, sticky="w", padx=5)
        input_max_var = tk.DoubleVar(value=config['input_max'])
        input_max_spin = ttk.Spinbox(frame, from_=-180, to=180, increment=1, 
                                     textvariable=input_max_var, width=10)
        input_max_spin.grid(row=3, column=1, sticky="w", padx=5)
        input_max_spin.bind("<Return>", lambda e: self.update_axis_value(axis, 'input_max', input_max_var.get()))
        widgets['input_max_var'] = input_max_var
        
        # Calibration buttons
        cal_frame = ttk.Frame(frame)
        cal_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(cal_frame, text="Set as Minimum", 
                  command=lambda: self.calibrate_axis(axis, True)).pack(side="left", padx=5)
        ttk.Button(cal_frame, text="Set as Maximum", 
                  command=lambda: self.calibrate_axis(axis, False)).pack(side="left", padx=5)
        
        # Output range
        ttk.Label(frame, text="Output Range (MIDI 0-127)", font=("", 10, "bold")).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        ttk.Label(frame, text="Minimum:").grid(row=6, column=0, sticky="w", padx=5)
        output_min_var = tk.IntVar(value=config['output_min'])
        output_min_spin = ttk.Spinbox(frame, from_=0, to=127, increment=1, 
                                      textvariable=output_min_var, width=10)
        output_min_spin.grid(row=6, column=1, sticky="w", padx=5)
        output_min_spin.bind("<Return>", lambda e: self.update_axis_value(axis, 'output_min', output_min_var.get()))
        widgets['output_min_var'] = output_min_var
        
        ttk.Label(frame, text="Maximum:").grid(row=7, column=0, sticky="w", padx=5)
        output_max_var = tk.IntVar(value=config['output_max'])
        output_max_spin = ttk.Spinbox(frame, from_=0, to=127, increment=1, 
                                      textvariable=output_max_var, width=10)
        output_max_spin.grid(row=7, column=1, sticky="w", padx=5)
        output_max_spin.bind("<Return>", lambda e: self.update_axis_value(axis, 'output_max', output_max_var.get()))
        widgets['output_max_var'] = output_max_var
        
        # MIDI settings
        ttk.Label(frame, text="MIDI Settings", font=("", 10, "bold")).grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        ttk.Label(frame, text="CC Number:").grid(row=9, column=0, sticky="w", padx=5)
        cc_var = tk.IntVar(value=config['cc_number'])
        cc_spin = ttk.Spinbox(frame, from_=0, to=127, increment=1, 
                              textvariable=cc_var, width=10)
        cc_spin.grid(row=9, column=1, sticky="w", padx=5)
        cc_spin.bind("<Return>", lambda e: self.update_axis_value(axis, 'cc_number', cc_var.get()))
        widgets['cc_var'] = cc_var
        
        ttk.Label(frame, text="MIDI Channel:").grid(row=10, column=0, sticky="w", padx=5)
        channel_var = tk.IntVar(value=config['channel'] + 1)  # Display as 1-16
        channel_spin = ttk.Spinbox(frame, from_=1, to=16, increment=1, 
                                   textvariable=channel_var, width=10)
        channel_spin.grid(row=10, column=1, sticky="w", padx=5)
        channel_spin.bind("<Return>", lambda e: self.update_axis_value(axis, 'channel', channel_var.get() - 1))
        widgets['channel_var'] = channel_var
        
        # Reset button
        ttk.Button(frame, text="Reset to Default", 
                  command=lambda: self.reset_axis(axis)).grid(
            row=11, column=0, columnspan=2, pady=20)
        
        self.axis_widgets[axis] = widgets
    
    def start_calibration_wizard(self):
        """Launch the calibration wizard"""
        if not self.is_running:
            messagebox.showwarning(
                "Not Running",
                "Please start tracking first before calibrating!"
            )
            return
        
        # Create and show calibration wizard
        wizard = CalibrationWizard(
            self.root,
            self.config_manager,
            self.get_current_head_pose
        )
        
        # Wait for wizard to close, then update UI
        self.root.wait_window(wizard.window)
        self.refresh_axis_ui()
    
    def set_zero_position(self):
        """Set current head position as neutral/zero"""
        if not self.is_running:
            messagebox.showwarning(
                "Not Running",
                "Please start tracking first!"
            )
            return
        
        pose = self.get_current_head_pose()
        if pose:
            self.config_manager.set_neutral_offsets(pose)
            messagebox.showinfo(
                "Zero Position Set",
                f"Current position set as zero/neutral:\n"
                f"Pitch: {pose['pitch']:.1f}°\n"
                f"Yaw: {pose['yaw']:.1f}°\n"
                f"Roll: {pose['roll']:.1f}°"
            )
        else:
            messagebox.showwarning(
                "No Face Detected",
                "Cannot detect your face. Please ensure your face is visible to the camera."
            )
    
    def get_current_head_pose(self):
        """Get the current head pose for calibration"""
        if hasattr(self, 'last_head_pose'):
            return self.last_head_pose
        return None
    
    def refresh_axis_ui(self):
        """Refresh all axis UI elements from config"""
        for axis in ['pitch', 'yaw', 'roll']:
            config = self.config_manager.get_axis_config(axis)
            widgets = self.axis_widgets[axis]
            widgets['enabled_var'].set(config['enabled'])
            widgets['input_min_var'].set(config['input_min'])
            widgets['input_max_var'].set(config['input_max'])
            widgets['output_min_var'].set(config['output_min'])
            widgets['output_max_var'].set(config['output_max'])
            widgets['cc_var'].set(config['cc_number'])
            widgets['channel_var'].set(config['channel'] + 1)
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = self.debug_var.get()
        if self.debug_mode:
            self.midi_port_combo.config(state="disabled")
            self.status_label.config(text="Status: Debug Mode (No MIDI)")
        else:
            self.midi_port_combo.config(state="readonly")
            if not self.is_running:
                self.status_label.config(text="Status: Stopped")
    
    def setup_midi(self):
        """Initialize MIDI ports"""
        ports = self.midi_controller.list_ports()
        
        # Add virtual port option
        port_list = ["Virtual Port"] + ports
        self.midi_port_combo['values'] = port_list
        
        # Try to open the configured port or create virtual port
        midi_config = self.config_manager.get_midi_config()
        
        if ports:
            # Select first available port by default
            self.midi_port_combo.current(1)  # Skip "Virtual Port"
            success = self.midi_controller.open_port(0)
            if not success:
                print("Warning: Could not open MIDI port. Enable Debug Mode to continue without MIDI.")
        else:
            # Create virtual port
            self.midi_port_combo.current(0)
            success = self.midi_controller.open_port(
                virtual_port_name=midi_config['virtual_port_name']
            )
            if not success:
                print("Warning: Could not create virtual MIDI port. Enable Debug Mode to continue without MIDI.")
    
    def on_midi_port_changed(self, event):
        """Handle MIDI port selection change"""
        selection = self.midi_port_combo.current()
        self.midi_controller.close_port()
        
        if selection == 0:  # Virtual Port
            midi_config = self.config_manager.get_midi_config()
            self.midi_controller.open_port(
                virtual_port_name=midi_config['virtual_port_name']
            )
        else:
            self.midi_controller.open_port(selection - 1)
    
    def update_axis_enabled(self, axis: str, enabled: bool):
        """Update axis enabled state"""
        self.config_manager.update_axis_config(axis, 'enabled', enabled)
    
    def update_axis_value(self, axis: str, key: str, value):
        """Update axis configuration value"""
        self.config_manager.update_axis_config(axis, key, value)
    
    def calibrate_axis(self, axis: str, is_min: bool):
        """Calibrate axis using current head position"""
        if not self.is_running:
            messagebox.showwarning("Not Running", "Please start tracking first!")
            return
        
        if hasattr(self, 'last_head_pose') and self.last_head_pose:
            current_value = self.last_head_pose.get(axis, 0)
            self.config_manager.calibrate_axis(axis, current_value, is_min)
            
            # Update UI
            if is_min:
                self.axis_widgets[axis]['input_min_var'].set(current_value)
            else:
                self.axis_widgets[axis]['input_max_var'].set(current_value)
            
            messagebox.showinfo("Calibration", 
                              f"{axis.capitalize()} {'minimum' if is_min else 'maximum'} set to {current_value:.1f}°")
    
    def reset_axis(self, axis: str):
        """Reset axis to default configuration"""
        self.config_manager.reset_axis_to_default(axis)
        config = self.config_manager.get_axis_config(axis)
        
        # Update UI
        widgets = self.axis_widgets[axis]
        widgets['enabled_var'].set(config['enabled'])
        widgets['input_min_var'].set(config['input_min'])
        widgets['input_max_var'].set(config['input_max'])
        widgets['output_min_var'].set(config['output_min'])
        widgets['output_max_var'].set(config['output_max'])
        widgets['cc_var'].set(config['cc_number'])
        widgets['channel_var'].set(config['channel'] + 1)
    
    def save_config(self):
        """Save current configuration"""
        # Update config from UI
        for axis in ['pitch', 'yaw', 'roll']:
            widgets = self.axis_widgets[axis]
            self.config_manager.update_axis_config(axis, 'enabled', widgets['enabled_var'].get())
            self.config_manager.update_axis_config(axis, 'input_min', widgets['input_min_var'].get())
            self.config_manager.update_axis_config(axis, 'input_max', widgets['input_max_var'].get())
            self.config_manager.update_axis_config(axis, 'output_min', widgets['output_min_var'].get())
            self.config_manager.update_axis_config(axis, 'output_max', widgets['output_max_var'].get())
            self.config_manager.update_axis_config(axis, 'cc_number', widgets['cc_var'].get())
            self.config_manager.update_axis_config(axis, 'channel', widgets['channel_var'].get() - 1)
        
        if self.config_manager.save_config():
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
    
    def toggle_tracking(self):
        """Start or stop face tracking"""
        if not self.is_running:
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        """Start face tracking and MIDI output"""
        # Show loading dialog
        loading = tk.Toplevel(self.root)
        loading.title("Starting...")
        loading.geometry("300x150")
        loading.resizable(False, False)
        loading.transient(self.root)
        
        # Center the loading window
        loading.update_idletasks()
        x = (loading.winfo_screenwidth() // 2) - (300 // 2)
        y = (loading.winfo_screenheight() // 2) - (150 // 2)
        loading.geometry(f"300x150+{x}+{y}")
        
        # Loading content
        ttk.Label(loading, text="Initializing Face Tracking...", 
                 font=("", 11, "bold")).pack(pady=(20, 10))
        
        progress = ttk.Progressbar(loading, mode='indeterminate', length=200)
        progress.pack(pady=10)
        progress.start(10)
        
        status_label = ttk.Label(loading, text="Loading MediaPipe models...")
        status_label.pack(pady=10)
        
        loading.update()
        
        # Function to actually start tracking in background
        def init_tracking():
            try:
                status_label.config(text="Opening camera...")
                loading.update()
                
                camera_config = self.config_manager.get_camera_config()
                
                # Try different camera backends for M1 Mac compatibility
                import platform
                is_mac = platform.system() == 'Darwin'
                
                if is_mac:
                    # On macOS (especially M1), try AVFoundation backend first
                    status_label.config(text="Initializing camera (AVFoundation)...")
                    loading.update()
                    self.camera = cv2.VideoCapture(camera_config['device_id'], cv2.CAP_AVFOUNDATION)
                else:
                    self.camera = cv2.VideoCapture(camera_config['device_id'])
                
                # Wait a moment for camera to initialize
                import time
                time.sleep(0.5)
                
                if not self.camera.isOpened():
                    # Try again without specifying backend
                    status_label.config(text="Retrying camera initialization...")
                    loading.update()
                    self.camera = cv2.VideoCapture(camera_config['device_id'])
                    time.sleep(0.5)
                
                if not self.camera.isOpened():
                    loading.destroy()
                    messagebox.showerror("Camera Error", 
                        "Failed to open camera!\n\n"
                        "macOS Tips:\n"
                        "1. Check System Settings → Privacy & Security → Camera\n"
                        "2. Make sure 'Face to MIDI' has camera permission\n"
                        "3. Try restarting the application\n"
                        "4. Close other apps using the camera")
                    return
                
                status_label.config(text="Configuring camera...")
                loading.update()
                
                # Set camera properties with error handling
                try:
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, camera_config['width'])
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_config['height'])
                    self.camera.set(cv2.CAP_PROP_FPS, camera_config['fps'])
                except Exception as e:
                    print(f"Warning: Could not set camera properties: {e}")
                    # Continue anyway - camera will use default settings
                
                status_label.config(text="Starting face detection...")
                loading.update()
                
                self.is_running = True
                self.start_button.config(text="Stop Tracking")
                self.status_label.config(text="Status: Running")
                
                # Start camera thread
                self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
                self.camera_thread.start()
                
                # Close loading dialog
                self.root.after(500, loading.destroy)
                
            except Exception as e:
                loading.destroy()
                error_msg = str(e)
                if "Unknown C++ exception" in error_msg:
                    messagebox.showerror("Camera Error",
                        f"OpenCV camera error on macOS!\n\n"
                        f"This is often a permissions issue.\n\n"
                        f"Try these steps:\n"
                        f"1. Go to System Settings → Privacy & Security → Camera\n"
                        f"2. Enable camera access for this app\n"
                        f"3. Restart the application\n"
                        f"4. If problem persists, restart your Mac\n\n"
                        f"Technical error: {error_msg}")
                else:
                    messagebox.showerror("Error", f"Failed to start tracking: {e}")
        
        # Run initialization in background
        threading.Thread(target=init_tracking, daemon=True).start()
    
    def stop_tracking(self):
        """Stop face tracking"""
        self.is_running = False
        self.start_button.config(text="Start Tracking")
        self.status_label.config(text="Status: Stopped")
        
        if self.camera:
            self.camera.release()
            cv2.destroyAllWindows()
    
    def camera_loop(self):
        """Main camera processing loop"""
        self.last_head_pose = None
        neutral_offsets = self.config_manager.get_neutral_offsets()
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        self.root.after(0, lambda: messagebox.showerror("Camera Error", 
                            "Lost connection to camera!\n\n"
                            "The camera may be in use by another application."))
                        self.root.after(0, self.stop_tracking)
                        break
                    continue
                
                # Reset error counter on successful read
                consecutive_errors = 0
                
                # Process frame
                head_pose, annotated_frame = self.face_tracker.process_frame(frame)
                
                if head_pose:
                    # Apply neutral offsets to make calibrated position zero
                    adjusted_pose = {
                        'pitch': head_pose['pitch'] - neutral_offsets.get('pitch', 0),
                        'yaw': head_pose['yaw'] - neutral_offsets.get('yaw', 0),
                        'roll': head_pose['roll'] - neutral_offsets.get('roll', 0)
                    }
                    
                    self.last_head_pose = head_pose  # Keep raw pose for calibration
                    
                    # Convert to MIDI (skip if debug mode)
                    if not self.debug_mode:
                        midi_values = self.midi_controller.process_head_pose(
                            adjusted_pose, 
                            self.config_manager.config
                        )
                    else:
                        # In debug mode, just simulate MIDI values
                        midi_values = {}
                        for axis in ['pitch', 'yaw', 'roll']:
                            if self.config_manager.config[axis]['enabled']:
                                midi_values[axis] = self.midi_controller.map_value(
                                    adjusted_pose[axis],
                                    self.config_manager.config[axis]['input_min'],
                                    self.config_manager.config[axis]['input_max'],
                                    self.config_manager.config[axis]['output_min'],
                                    self.config_manager.config[axis]['output_max']
                                )
                    
                    # Update UI with adjusted values
                    self.root.after(0, self.update_value_display, adjusted_pose, midi_values)
                    
            except cv2.error as e:
                consecutive_errors += 1
                error_msg = str(e)
                print(f"OpenCV error in camera loop: {error_msg}")
                
                if consecutive_errors >= max_consecutive_errors:
                    self.root.after(0, lambda: messagebox.showerror("Camera Error",
                        f"Repeated camera errors detected.\n\n"
                        f"On macOS M1, this usually means:\n"
                        f"1. Camera permissions are not properly granted\n"
                        f"2. Another app is using the camera\n"
                        f"3. System needs to be restarted\n\n"
                        f"Technical error: {error_msg}"))
                    self.root.after(0, self.stop_tracking)
                    break
                
                # Brief pause before retrying
                import time
                time.sleep(0.1)
                continue
                
            except Exception as e:
                consecutive_errors += 1
                print(f"Unexpected error in camera loop: {e}")
                import traceback
                traceback.print_exc()
                
                if consecutive_errors >= max_consecutive_errors:
                    self.root.after(0, lambda: messagebox.showerror("Error",
                        f"Camera loop stopped due to repeated errors:\n{e}"))
                    self.root.after(0, self.stop_tracking)
                    break
                
                import time
                time.sleep(0.1)
                continue
            
            # Show frame
            cv2.imshow('Face to MIDI - Press Q to close', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.root.after(0, self.stop_tracking)
                break
    
    def update_value_display(self, head_pose, midi_values):
        """Update the value display labels"""
        for axis in ['pitch', 'yaw', 'roll']:
            if axis in head_pose and axis in midi_values:
                text = f"{axis.capitalize()}: {head_pose[axis]:.1f}° | MIDI: {midi_values[axis]}"
                self.value_labels[axis].config(text=text)
    
    def on_closing(self):
        """Handle window close event"""
        self.stop_tracking()
        self.face_tracker.release()
        self.midi_controller.release()
        self.root.destroy()
    
    def show_help(self):
        """Show help dialog"""
        help_text = """Face to MIDI Controller - Quick Guide

GETTING STARTED:
1. Click 'Start Tracking' to begin
2. Click 'Start Calibration' for guided setup
3. Move your head to control MIDI values

CALIBRATION OPTIONS:
• Start Calibration - Full guided setup
• Set Zero Position - Quick neutral position
• Manual - Use per-axis controls in tabs

CONTROLS:
• Pitch: Tilt head up/down
• Yaw: Turn head left/right
• Roll: Tilt head ear-to-shoulder

TIPS:
• Good lighting improves tracking
• Keep face visible to camera
• Save Config after calibration
• Use Debug Mode to test without MIDI
• Press 'Q' in video window to close it

For more help, see README.md"""
        
        messagebox.showinfo("Help", help_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FaceToMIDIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
