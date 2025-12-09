# Face to MIDI Controller

Convert your head movements into MIDI control signals in real-time!

## Features

- **Face Tracking**: Uses MediaPipe Face Mesh to track facial landmarks and calculate head pose (pitch, yaw, roll)
- **MIDI Output**: Converts head movements to MIDI CC messages
- **Customizable Mappings**: Configure which head movement controls which MIDI CC number
- **Calibration**: Set your own min/max ranges for head movements
- **Adjustable Limits**: Configure output MIDI value ranges (0-127)
- **Multiple Axes**: Control up to 3 independent MIDI parameters simultaneously
- **GUI Interface**: Easy-to-use interface with real-time feedback
- **Configuration Saving**: Save and load your settings

## Installation

1. **Install Python** (3.8 or higher recommended)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Additional Requirements**:
   - Windows: Should work out of the box
   - macOS: May need to install additional audio/MIDI drivers
   - Linux: May need to install `libasound2-dev` for MIDI support

## Usage

### Starting the Application

Run the main application:
```bash
python main.py
```

### Using the Application

1. **MIDI Port Selection**: 
   - Select your MIDI output port from the dropdown
   - Or use "Virtual Port" to create a virtual MIDI device
   - Or enable "Debug Mode (No MIDI)" to test without MIDI

2. **Start Tracking**:
   - Click "Start Tracking" button
   - Position yourself in front of the camera
   - Your face should be detected with a mesh overlay

3. **Calibration Wizard** (Recommended):
   - Click "Start Calibration" button
   - Follow the on-screen instructions:
     1. **Look straight ahead** - Sets your neutral/zero position
     2. **Look up** - Sets maximum upward tilt
     3. **Look down** - Sets maximum downward tilt
     4. **Turn right** - Sets maximum right turn
     5. **Turn left** - Sets maximum left turn
     6. **Tilt right** - Sets maximum right tilt (ear to shoulder)
     7. **Tilt left** - Sets maximum left tilt (ear to shoulder)
   - Each step has a countdown timer
   - You can skip steps if needed
   - Calibration automatically adjusts your ranges

4. **Manual Configuration** (Alternative):
   - Click on the tabs (Pitch, Yaw, Roll) to configure each axis
   - **Pitch**: Head tilting up/down
   - **Yaw**: Head turning left/right
   - **Roll**: Head tilting side to side
   - Set **CC Number**: MIDI Control Change number (0-127)
   - Set **MIDI Channel**: MIDI channel (1-16)
   - Set **Output Min/Max**: MIDI value range to output
   - Use "Set as Minimum/Maximum" buttons for quick calibration

5. **Control Your MIDI**:
   - Move your head to control MIDI values in real-time
   - Watch real-time feedback in the GUI showing angles and MIDI values
   - Press 'Q' in the video window to close it

6. **Save Configuration**:
   - Click "Save Config" to save your settings
   - Settings are loaded automatically on next start

## Configuration

Settings are stored in `face_to_midi_config.json`. You can edit this file manually or use the GUI.

### Default MIDI Mappings

- **Pitch** (up/down): CC 1 (Modulation Wheel)
- **Yaw** (left/right): CC 2 (Breath Controller)
- **Roll** (tilt): CC 3

### Default Input Ranges

All axes default to ±30 degrees from center position.

## Tips

- **Lighting**: Ensure good lighting for best face tracking
- **Camera Position**: Place camera at eye level for optimal tracking
- **Calibration**: Calibrate for your natural head movement range
- **MIDI Testing**: Use a MIDI monitor to verify output
- **DAW Integration**: Route the MIDI output to your DAW or synth

## Common MIDI CC Numbers

- 1: Modulation Wheel
- 2: Breath Controller
- 7: Volume
- 10: Pan
- 11: Expression
- 74-79: Sound Controllers
- 91-95: Effects Depth

## Troubleshooting

**Camera not detected**:
- Check camera permissions
- Try changing `device_id` in config (0, 1, 2, etc.)

**No MIDI output**:
- Verify MIDI port is selected
- Check MIDI monitoring software
- Try "Virtual Port" option

**Tracking issues**:
- Improve lighting
- Remove obstructions from face
- Adjust camera position

**Performance issues**:
- Reduce camera resolution in config
- Close other camera applications

## File Structure

```
face_to_midi/
├── main.py                    # Main application with GUI
├── face_tracker.py            # Face tracking module
├── midi_controller.py         # MIDI output handling
├── config_manager.py          # Configuration management
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── face_to_midi_config.json  # Settings (created on first save)
```

## Requirements

- Python 3.8+
- Webcam
- MIDI-capable software/hardware

## License

This project is provided as-is for educational and creative purposes.

## Credits

- **MediaPipe**: Google's ML framework for face tracking
- **OpenCV**: Computer vision library
- **python-rtmidi**: Python bindings for RtMidi
