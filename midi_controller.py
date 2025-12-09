"""
MIDI Controller Module
Handles MIDI output and conversion of head pose data to MIDI messages
"""

import sys
import platform

# Handle platform-specific imports
try:
    import rtmidi
except ImportError as e:
    print(f"Error importing rtmidi: {e}")
    print("Please install python-rtmidi: pip install python-rtmidi")
    raise

from typing import Dict, Optional, List


class MIDIController:
    def __init__(self):
        """Initialize MIDI output"""
        self.midi_out = rtmidi.MidiOut()
        self.available_ports = self.midi_out.get_ports()
        self.current_port = None
        
        # MIDI CC values cache to avoid sending duplicate messages
        self.last_values = {
            'pitch': None,
            'yaw': None,
            'roll': None
        }
        
    def list_ports(self) -> List[str]:
        """Get list of available MIDI output ports"""
        return self.available_ports
    
    def open_port(self, port_index: int = None, virtual_port_name: str = None) -> bool:
        """
        Open a MIDI port for output
        
        Args:
            port_index: Index of the port to open (from list_ports)
            virtual_port_name: Name for a virtual port (if port_index is None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if port_index is not None and port_index < len(self.available_ports):
                self.midi_out.open_port(port_index)
                self.current_port = port_index
                print(f"✓ MIDI port opened: {self.available_ports[port_index]}")
                return True
            elif virtual_port_name:
                self.midi_out.open_virtual_port(virtual_port_name)
                self.current_port = -1  # Virtual port indicator
                print(f"✓ Virtual MIDI port created: {virtual_port_name}")
                return True
            return False
        except Exception as e:
            print(f"✗ Could not open MIDI port: {e}")
            print("  → Enable 'Debug Mode (No MIDI)' to test face tracking without MIDI output")
            return False
    
    def close_port(self):
        """Close the current MIDI port"""
        if self.midi_out.is_port_open():
            self.midi_out.close_port()
            self.current_port = None
    
    def send_cc(self, channel: int, cc_number: int, value: int):
        """
        Send a MIDI Control Change message
        
        Args:
            channel: MIDI channel (0-15)
            cc_number: CC number (0-127)
            value: CC value (0-127)
        """
        if self.midi_out.is_port_open():
            # MIDI CC message: [Status byte, CC number, Value]
            # Status byte: 0xB0 + channel (176 + channel)
            message = [0xB0 + channel, cc_number, value]
            self.midi_out.send_message(message)
    
    def map_value(self, input_value: float, input_min: float, input_max: float, 
                  output_min: int = 0, output_max: int = 127) -> int:
        """
        Map a value from input range to MIDI range (0-127)
        
        Args:
            input_value: The input value to map
            input_min: Minimum input value
            input_max: Maximum input value
            output_min: Minimum output value (default 0)
            output_max: Maximum output value (default 127)
            
        Returns:
            Mapped value clamped to output range
        """
        # Clamp input value to input range
        input_value = max(input_min, min(input_max, input_value))
        
        # Map to output range
        input_range = input_max - input_min
        output_range = output_max - output_min
        
        if input_range == 0:
            return output_min
        
        normalized = (input_value - input_min) / input_range
        output_value = int(normalized * output_range + output_min)
        
        # Clamp to output range
        return max(output_min, min(output_max, output_value))
    
    def process_head_pose(self, head_pose: Dict[str, float], config: Dict) -> Dict[str, int]:
        """
        Convert head pose data to MIDI CC messages based on configuration
        
        Args:
            head_pose: Dictionary with pitch, yaw, roll values
            config: Configuration dictionary with mappings and limits
            
        Returns:
            Dictionary with MIDI values sent
        """
        midi_values = {}
        
        for axis in ['pitch', 'yaw', 'roll']:
            if axis in head_pose and config[axis]['enabled']:
                # Get configuration for this axis
                input_min = config[axis]['input_min']
                input_max = config[axis]['input_max']
                output_min = config[axis]['output_min']
                output_max = config[axis]['output_max']
                cc_number = config[axis]['cc_number']
                channel = config[axis]['channel']
                
                # Map head pose value to MIDI range
                midi_value = self.map_value(
                    head_pose[axis],
                    input_min,
                    input_max,
                    output_min,
                    output_max
                )
                
                # Only send if value changed (reduce MIDI traffic)
                if self.last_values[axis] != midi_value:
                    self.send_cc(channel, cc_number, midi_value)
                    self.last_values[axis] = midi_value
                
                midi_values[axis] = midi_value
        
        return midi_values
    
    def send_note_on(self, channel: int, note: int, velocity: int = 64):
        """
        Send a MIDI Note On message
        
        Args:
            channel: MIDI channel (0-15)
            note: Note number (0-127)
            velocity: Note velocity (0-127)
        """
        if self.midi_out.is_port_open():
            message = [0x90 + channel, note, velocity]
            self.midi_out.send_message(message)
    
    def send_note_off(self, channel: int, note: int):
        """
        Send a MIDI Note Off message
        
        Args:
            channel: MIDI channel (0-15)
            note: Note number (0-127)
        """
        if self.midi_out.is_port_open():
            message = [0x80 + channel, note, 0]
            self.midi_out.send_message(message)
    
    def release(self):
        """Release MIDI resources"""
        self.close_port()
        del self.midi_out
