# Building Standalone Executables with ALL MediaPipe Files

This document explains how the build process ensures ALL necessary MediaPipe model files (including `.binarypb`, `.tflite`, etc.) are included in the standalone executables.

## What Gets Included

### MediaPipe Model Files
The following MediaPipe files are automatically included:
- **face_landmark_front.binarypb** - Face mesh model
- **face_landmark.tflite** - TensorFlow Lite model
- **face_detection_short_range.tflite** - Face detection model
- **All other .binarypb files** - Various MediaPipe models
- **All .tflite files** - TensorFlow Lite models
- **Configuration files** - .pbtxt, .txt files

### Build Methods

## Method 1: Local Build (Recommended for Testing)

### Windows
```powershell
cd C:\face_to_midi
.\build_windows.bat
```

This script:
1. Finds your MediaPipe installation
2. Includes ALL MediaPipe data files using `--add-data` and `--collect-all`
3. Creates `dist\Face-to-MIDI.exe` with everything embedded

### macOS
```bash
cd /path/to/face_to_midi
chmod +x build_mac.sh
./build_mac.sh
```

This script:
1. Finds your MediaPipe installation
2. Includes ALL MediaPipe data files
3. Creates `dist/Face-to-MIDI` with everything embedded

## Method 2: GitHub Actions (Automatic Cloud Build)

Push to GitHub and the workflow automatically:
1. Installs MediaPipe
2. Finds all MediaPipe data files
3. Uses `--collect-all mediapipe` to include everything
4. Builds both macOS and Windows executables
5. Uploads them as downloadable artifacts

### GitHub Actions Configuration

The `.github/workflows/build.yml` includes:
```yaml
--add-data "${MEDIAPIPE_PATH}:mediapipe"
--collect-all mediapipe
--collect-data mediapipe
```

These flags ensure:
- `--add-data`: Copies the entire MediaPipe directory
- `--collect-all`: Includes all MediaPipe Python modules and data
- `--collect-data`: Specifically collects data files

## Method 3: py2app (macOS App Bundle)

The `setup_mac.py` includes a function that:
1. Scans your MediaPipe installation
2. Finds all `.binarypb`, `.tflite`, `.txt`, `.task`, `.pbtxt` files
3. Adds them as resources in the app bundle

Run:
```bash
python setup_mac.py py2app
```

## Verification

### Check if MediaPipe Files are Included

After building, verify the executable contains the models:

**Windows (PyInstaller)**:
```powershell
# Extract the executable (it's a self-extracting archive)
# Look for mediapipe folder in temp directory when running
```

**macOS (PyInstaller)**:
```bash
# Run the app and check if face tracking works immediately
./dist/Face-to-MIDI
```

**macOS (py2app)**:
```bash
# Check the Resources folder
ls "dist/Face to MIDI.app/Contents/Resources/mediapipe/"
```

### Test the Build

1. **Copy to a clean machine** (or VM) without Python installed
2. **Run the executable**
3. **Start tracking** - Should work immediately without errors
4. **Check for errors** like "face_landmark_front.binarypb not found"

If you see model file errors, the build didn't include them properly.

## Troubleshooting

### "Module not found" errors
**Solution**: Add to `--hidden-import`:
```bash
--hidden-import=mediapipe.python.solutions.face_mesh
--hidden-import=mediapipe.python.solutions.drawing_utils
```

### "Model file not found" errors
**Solution**: Use `--collect-all mediapipe`:
```bash
pyinstaller --collect-all mediapipe --collect-data mediapipe main.py
```

### Large file size (300-500MB)
**This is NORMAL**. MediaPipe models are large:
- face_landmark models: ~50MB
- TensorFlow Lite runtime: ~100MB
- OpenCV libraries: ~50MB
- Python runtime: ~50MB
- Other dependencies: ~100MB

### Build works but app crashes
**Check**: 
1. Camera permissions (macOS)
2. Run from terminal to see error messages
3. Verify MediaPipe files in the bundle

## File Locations in Built App

### PyInstaller (Windows/macOS)
When the app runs, it extracts to a temporary directory:
```
_MEI<random>/
├── mediapipe/
│   ├── modules/
│   │   ├── face_landmark/
│   │   │   └── face_landmark_front_cpu.binarypb
│   │   └── ...
│   └── ...
└── ...
```

### py2app (macOS)
Files are in the app bundle:
```
Face to MIDI.app/
└── Contents/
    └── Resources/
        ├── mediapipe/
        │   ├── modules/
        │   │   ├── face_landmark/
        │   │   │   └── face_landmark_front_cpu.binarypb
        │   │   └── ...
        │   └── ...
        └── ...
```

## Best Practices

### 1. Always Use collect-all for MediaPipe
```bash
--collect-all mediapipe
```

### 2. Always Use collect-data for MediaPipe
```bash
--collect-data mediapipe
```

### 3. Add MediaPipe Path Explicitly
```bash
--add-data "/path/to/mediapipe:mediapipe"
```

### 4. Test on Clean System
Always test your built executable on a computer without Python or any development tools installed.

### 5. Check Logs
If models aren't loading, check the build log for:
```
WARNING: Could not collect data files for mediapipe
```

## Size Optimization

To reduce size (if needed):

### Option 1: Exclude Unused Models
If you're only using face mesh, you can exclude other MediaPipe solutions manually. However, this is complex and not recommended.

### Option 2: Use UPX Compression
```bash
pip install pyinstaller[encryption]
pyinstaller --upx-dir=/path/to/upx ...
```

Can reduce size by 30-50% but may trigger antivirus warnings.

### Option 3: Accept the Size
Recommended: Just accept 300-500MB. Modern apps are this size, and users have plenty of storage.

## Summary

✅ **Use the provided build scripts** - They handle everything  
✅ **MediaPipe files are automatically included** - via `--collect-all`  
✅ **Test on clean machine** - Ensure it works standalone  
✅ **Expect large file size** - 300-500MB is normal  
✅ **No installation needed** - Users just run the executable  

The built application is 100% standalone and includes everything needed to run without any Python installation or pip packages!
