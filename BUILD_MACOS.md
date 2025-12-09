# Building Face to MIDI for macOS

This guide explains how to create a standalone macOS application.

## Prerequisites

1. **macOS Computer** - You must build on macOS to create macOS apps
2. **Python 3.11** - Same version used for development
3. **All dependencies installed** - Run `pip install -r requirements.txt`

## Method 1: PyInstaller (Simpler, Single File)

### Install PyInstaller
```bash
pip install pyinstaller
```

### Create Executable
```bash
cd /path/to/face_to_midi
pyinstaller --name "Face to MIDI" \
            --windowed \
            --onefile \
            main.py
```

### With Custom Icon (Optional)
If you have an icon file (`.icns` format):
```bash
pyinstaller --name "Face to MIDI" \
            --windowed \
            --onefile \
            --icon=app_icon.icns \
            main.py
```

### Output
- Executable will be in `dist/Face to MIDI`
- You can drag this to `/Applications` folder

## Method 2: py2app (Better macOS Integration)

### Install py2app
```bash
pip install py2app
```

### Build the App
```bash
python setup_mac.py py2app
```

### Output
- Full `.app` bundle in `dist/Face to MIDI.app`
- Can be distributed like any macOS app
- Double-click to run

## Creating an App Icon

### Convert PNG to ICNS
If you have a PNG icon (1024x1024 recommended):

```bash
# Create iconset folder
mkdir app_icon.iconset

# Create different sizes (macOS requires multiple sizes)
sips -z 16 16     icon.png --out app_icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out app_icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out app_icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out app_icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out app_icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out app_icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out app_icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out app_icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out app_icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out app_icon.iconset/icon_512x512@2x.png

# Convert to icns
iconutil -c icns app_icon.iconset
```

## Permissions on macOS

Your app needs camera permission. When users first run it, macOS will prompt them.

If the app doesn't request permission automatically, users can manually grant it:
1. Open **System Settings** → **Privacy & Security** → **Camera**
2. Enable permission for "Face to MIDI"

## Code Signing (Optional but Recommended)

For distribution, you should sign the app:

```bash
# Sign with your developer certificate
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Face to MIDI.app"

# Verify signature
codesign --verify --verbose "dist/Face to MIDI.app"
```

## Creating a DMG for Distribution

To create a nice installer disk image:

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Face to MIDI Installer" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Face to MIDI.app" 175 120 \
  --hide-extension "Face to MIDI.app" \
  --app-drop-link 425 120 \
  "Face-to-MIDI-Installer.dmg" \
  "dist/"
```

## Testing the Build

1. **Test the executable**:
   ```bash
   ./dist/Face\ to\ MIDI
   ```

2. **Test on another Mac** (without Python installed) to ensure it's truly standalone

3. **Check camera permissions** work correctly

4. **Test MIDI output** with your DAW or MIDI monitoring software

## Troubleshooting

### "Module not found" errors
Add missing modules to PyInstaller:
```bash
pyinstaller --hidden-import=cv2 --hidden-import=mediapipe main.py
```

Or for py2app, edit `setup_mac.py` and add to `packages` list.

### "App is damaged" warning
This happens with unsigned apps. Either:
- Sign the app (see Code Signing above)
- Users can right-click → Open to bypass the warning

### Camera not working
Ensure camera permissions are granted in System Settings.

### Large file size
The app will be 200-400MB due to MediaPipe models. This is normal.
Use `--onefile` to keep it as a single file.

## Build Script

Create a file `build_mac.sh`:

```bash
#!/bin/bash
# Build Face to MIDI for macOS

echo "Building Face to MIDI for macOS..."

# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller --name "Face to MIDI" \
            --windowed \
            --onefile \
            --clean \
            main.py

echo "Build complete! Check dist/Face to MIDI"
```

Make it executable:
```bash
chmod +x build_mac.sh
./build_mac.sh
```

## Distribution Checklist

- [ ] Test on clean macOS (without Python)
- [ ] Verify camera permission request works
- [ ] Test MIDI output functionality
- [ ] Check all UI elements display correctly
- [ ] Test calibration wizard
- [ ] Include README.md and guides
- [ ] Sign the app (if distributing publicly)
- [ ] Create DMG installer
- [ ] Test DMG on another Mac

## Notes

- **First launch** may take 10-20 seconds as MediaPipe initializes
- **File size** will be large (~200-400MB) due to ML models
- **Python not required** - The app is completely standalone
- **macOS 10.13+** recommended for compatibility

## Alternative: Briefcase

Another option is **Briefcase** by BeeWare:

```bash
pip install briefcase
briefcase create
briefcase build
briefcase package
```

Briefcase creates native macOS apps with better integration.

## Questions?

If you encounter issues building on macOS:
1. Check Python version (`python --version`)
2. Verify all dependencies installed (`pip list`)
3. Check build logs for specific errors
4. Try py2app if PyInstaller fails (or vice versa)
