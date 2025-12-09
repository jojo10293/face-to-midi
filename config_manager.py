"""
Configuration Manager
Handles saving/loading settings and calibration data
"""

import json
import os
from typing import Dict


class ConfigManager:
    def __init__(self, config_file: str = "face_to_midi_config.json"):
        """Initialize configuration manager"""
        self.config_file = config_file
        self.config = self.load_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'pitch': {
                'enabled': True,
                'input_min': -30.0,    # Looking down
                'input_max': 30.0,     # Looking up
                'output_min': 0,       # MIDI min
                'output_max': 127,     # MIDI max
                'cc_number': 1,        # MIDI CC number (Modulation wheel by default)
                'channel': 0           # MIDI channel (1 in user terms, 0 indexed)
            },
            'yaw': {
                'enabled': True,
                'input_min': -30.0,    # Looking left
                'input_max': 30.0,     # Looking right
                'output_min': 0,
                'output_max': 127,
                'cc_number': 2,        # Breath Controller
                'channel': 0
            },
            'roll': {
                'enabled': True,
                'input_min': -30.0,    # Tilting left
                'input_max': 30.0,     # Tilting right
                'output_min': 0,
                'output_max': 127,
                'cc_number': 3,        # Undefined CC
                'channel': 0
            },
            'camera': {
                'device_id': 0,        # Default camera
                'width': 640,
                'height': 480,
                'fps': 30
            },
            'midi': {
                'port_index': None,    # Auto-select or virtual port
                'virtual_port_name': 'Face to MIDI'
            },
            'neutral': {
                'pitch': 0.0,          # Neutral pitch offset
                'yaw': 0.0,            # Neutral yaw offset
                'roll': 0.0            # Neutral roll offset
            }
        }
    
    def load_config(self) -> Dict:
        """Load configuration from file or return defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle new keys
                    default_config = self.get_default_config()
                    return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.get_default_config()
        return self.get_default_config()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        for key, value in default.items():
            if key in loaded:
                if isinstance(value, dict) and isinstance(loaded[key], dict):
                    default[key] = self._merge_configs(value, loaded[key])
                else:
                    default[key] = loaded[key]
        return default
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, indent=4, fp=f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def update_axis_config(self, axis: str, key: str, value):
        """Update a specific axis configuration"""
        if axis in self.config and key in self.config[axis]:
            self.config[axis][key] = value
            return True
        return False
    
    def calibrate_axis(self, axis: str, current_value: float, is_min: bool):
        """
        Set calibration point for an axis
        
        Args:
            axis: 'pitch', 'yaw', or 'roll'
            current_value: Current head pose value
            is_min: True to set as minimum, False to set as maximum
        """
        if axis in self.config:
            if is_min:
                self.config[axis]['input_min'] = current_value
            else:
                self.config[axis]['input_max'] = current_value
            return True
        return False
    
    def reset_axis_to_default(self, axis: str):
        """Reset an axis configuration to default values"""
        default_config = self.get_default_config()
        if axis in default_config:
            self.config[axis] = default_config[axis].copy()
            return True
        return False
    
    def get_axis_config(self, axis: str) -> Dict:
        """Get configuration for a specific axis"""
        return self.config.get(axis, {})
    
    def get_camera_config(self) -> Dict:
        """Get camera configuration"""
        return self.config.get('camera', {})
    
    def get_midi_config(self) -> Dict:
        """Get MIDI configuration"""
        return self.config.get('midi', {})
    
    def get_neutral_offsets(self) -> Dict:
        """Get neutral position offsets"""
        return self.config.get('neutral', {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0})
    
    def set_neutral_offsets(self, offsets: Dict):
        """Set neutral position offsets"""
        if 'neutral' not in self.config:
            self.config['neutral'] = {}
        self.config['neutral'].update(offsets)
