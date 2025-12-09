#!/bin/bash
# Build script for Face to MIDI on macOS
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

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build with PyInstaller
echo ""
echo "Building application with PyInstaller..."
pyinstaller --name "Face to MIDI" \
            --windowed \
            --onefile \
            --clean \
            --noconfirm \
            main.py

# Check if build was successful
if [ -f "dist/Face to MIDI" ]; then
    echo ""
    echo "=========================================="
    echo "Build successful!"
    echo "=========================================="
    echo ""
    echo "Executable location: dist/Face to MIDI"
    echo ""
    echo "To install:"
    echo "  cp 'dist/Face to MIDI' /Applications/"
    echo ""
    echo "To create DMG (requires create-dmg):"
    echo "  brew install create-dmg"
    echo "  create-dmg --volname 'Face to MIDI' 'Face-to-MIDI.dmg' dist/"
    echo ""
else
    echo ""
    echo "Build failed! Check the output above for errors."
    exit 1
fi
