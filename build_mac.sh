#!/bin/bash
# Build script for Face to MIDI on macOS
# This ensures all MediaPipe model files are included
# Usage: ./build_mac.sh

set -e  # Exit on error

echo "=========================================="
echo "Face to MIDI - macOS Build Script"
echo "=========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Find MediaPipe data directory
echo ""
echo "Finding MediaPipe data files..."
MEDIAPIPE_PATH=$(python3 -c "import mediapipe; import os; print(os.path.dirname(mediapipe.__file__))")
echo "MediaPipe path: $MEDIAPIPE_PATH"

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build with PyInstaller
echo ""
echo "Building application with PyInstaller..."
echo "This may take several minutes..."
echo ""

pyinstaller --name "Face-to-MIDI" \
            --windowed \
            --onefile \
            --clean \
            --noconfirm \
            --add-data "${MEDIAPIPE_PATH}:mediapipe" \
            --hidden-import=mediapipe.python.solutions.face_mesh \
            --hidden-import=mediapipe.python.solutions.drawing_utils \
            --hidden-import=mediapipe.python.solutions.drawing_styles \
            --collect-all mediapipe \
            --collect-data mediapipe \
            main.py

# Check if build was successful
if [ -f "dist/Face-to-MIDI" ]; then
    echo ""
    echo "=========================================="
    echo "Build successful!"
    echo "=========================================="
    echo ""
    echo "Executable location: dist/Face-to-MIDI"
    echo ""
    echo "The executable includes:"
    echo "  - All Python code"
    echo "  - MediaPipe models (.binarypb, .tflite files)"
    echo "  - OpenCV libraries"
    echo "  - MIDI support"
    echo "  - Complete standalone application"
    echo ""
    echo "To install:"
    echo "  cp 'dist/Face-to-MIDI' /Applications/"
    echo ""
    echo "To create DMG (requires create-dmg):"
    echo "  brew install create-dmg"
    echo "  create-dmg --volname 'Face to MIDI' 'Face-to-MIDI.dmg' dist/"
    echo ""
    echo "File size will be approximately 200-400MB due to ML models."
    echo ""
else
    echo ""
    echo "Build failed! Check the output above for errors."
    exit 1
fi
