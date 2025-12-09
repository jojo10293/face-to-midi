# Face to MIDI - Calibration Guide

## Quick Start

1. **Launch the app**: Run `py -3.11 main.py` or `run.bat`
2. **Start tracking**: Click "Start Tracking"
3. **Calibrate**: Click "Start Calibration"
4. **Follow prompts**: Complete each step of the wizard
5. **Save**: Click "Save Config" when done

## Calibration Wizard

The calibration wizard guides you through 7 steps to set up your head tracking:

### Step 1: Neutral Position
- Look straight ahead at the camera
- Keep your head level and centered
- This becomes your "zero" position
- **Duration**: 6 seconds

### Step 2: Pitch Up
- Tilt your head upward as far as comfortable
- Sets maximum upward tilt angle
- **Duration**: 4 seconds

### Step 3: Pitch Down
- Tilt your head downward as far as comfortable
- Sets maximum downward tilt angle
- **Duration**: 4 seconds

### Step 4: Yaw Right
- Turn your head to the right as far as comfortable
- Sets maximum right turn angle
- **Duration**: 4 seconds

### Step 5: Yaw Left
- Turn your head to the left as far as comfortable
- Sets maximum left turn angle
- **Duration**: 4 seconds

### Step 6: Roll Right
- Tilt your head to the right (ear toward right shoulder)
- Sets maximum right tilt angle
- **Duration**: 4 seconds

### Step 7: Roll Left
- Tilt your head to the left (ear toward left shoulder)
- Sets maximum left tilt angle
- **Duration**: 4 seconds

## Features

### Automatic Calibration
- **Full Wizard**: Complete 7-step guided calibration
- **Zero Position**: Quick single-click to set neutral
- **Skip Steps**: Skip any step you don't want to calibrate

### Real-Time Feedback
- See current head angles in degrees
- See corresponding MIDI values (0-127)
- Visual mesh overlay on video feed

### Debug Mode
- Test face tracking without MIDI
- Perfect for initial setup
- No MIDI hardware/software required

### Manual Controls
- Per-axis enable/disable
- Custom input ranges (degrees)
- Custom output ranges (MIDI 0-127)
- Set MIDI CC numbers (0-127)
- Set MIDI channels (1-16)

## Tips for Best Results

### Lighting
- Use good front lighting
- Avoid backlighting
- Consistent lighting is key

### Camera Position
- Place camera at eye level
- Keep face centered in frame
- Maintain consistent distance

### Calibration
- Use your natural movement range
- Don't over-extend movements
- Re-calibrate if tracking feels off

### MIDI Mapping
- Start with default CC numbers
- Test with MIDI monitor software
- Adjust ranges per your needs

## Common MIDI CC Mappings

### Default Mappings
- **CC 1 (Pitch)**: Modulation Wheel
- **CC 2 (Yaw)**: Breath Controller
- **CC 3 (Roll)**: Undefined (User-defined)

### Popular Alternatives
- **CC 7**: Volume
- **CC 10**: Pan
- **CC 11**: Expression
- **CC 74-79**: Sound Controllers (Brightness, Resonance, etc.)
- **CC 91-95**: Effects Depth (Reverb, Chorus, etc.)

## Troubleshooting

### Face Not Detected
- Improve lighting
- Move closer to camera
- Remove obstructions (masks, hands)
- Ensure face is centered

### Erratic Values
- Re-run calibration
- Check lighting consistency
- Reduce camera exposure if too bright

### MIDI Not Working
- Verify MIDI port selection
- Check MIDI monitor for output
- Try "Virtual Port" option
- Use Debug Mode to test tracking first

### Performance Issues
- Close other camera apps
- Reduce camera resolution in config
- Check CPU usage

## Configuration Files

### face_to_midi_config.json
Contains all your settings:
- Axis configurations (min/max ranges)
- MIDI mappings (CC numbers, channels)
- Neutral position offsets
- Camera settings

### Backup Your Config
Copy `face_to_midi_config.json` to save your calibration!

## Advanced Usage

### Multiple Profiles
- Save different config files
- Rename them (e.g., `config_seated.json`, `config_standing.json`)
- Load specific configs by renaming before launch

### Fine-Tuning Ranges
- Start with calibration wizard
- Adjust ranges manually in tabs
- Test and iterate
- Save when satisfied

### MIDI Learn
- Most DAWs have MIDI learn
- Move your head while in learn mode
- DAW captures the CC number automatically

## Getting Help

- Check the main README.md
- Click "?" button in app for quick help
- Review console output for errors
- Test with Debug Mode first

## Updates and Changes

After calibration:
- Values update in real-time
- Changes apply immediately
- Must click "Save Config" to persist
- Can reset individual axes to defaults
