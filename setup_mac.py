"""
py2app setup script for Face to MIDI
Usage: python setup_mac.py py2app

This will create a standalone macOS application bundle that includes:
- All Python modules (face_tracker, midi_controller, config_manager, calibration_wizard)
- All dependencies (OpenCV, MediaPipe, rtmidi, numpy, tkinter)
- ALL MediaPipe model files (.binarypb, .tflite, etc.)
- Documentation files
- Default configuration

The .py modules are automatically included by py2app when imported by main.py,
but we explicitly list them here to ensure they're found.
"""

from setuptools import setup
import os
import sys
import site

# Find MediaPipe data files
def find_mediapipe_files():
    """Find all MediaPipe model and data files"""
    mediapipe_files = []
    
    # Get site-packages locations
    site_packages = site.getsitepackages()
    
    for sp in site_packages:
        mediapipe_path = os.path.join(sp, 'mediapipe')
        if os.path.exists(mediapipe_path):
            # Walk through mediapipe directory and find all data files
            for root, dirs, files in os.walk(mediapipe_path):
                for file in files:
                    # Include model files and data files
                    if file.endswith(('.binarypb', '.tflite', '.txt', '.task', '.pbtxt')):
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, sp)
                        mediapipe_files.append(full_path)
                        print(f"Found MediaPipe file: {relative_path}")
    
    return mediapipe_files

# Main application entry point
APP = ['main.py']

# Additional Python modules that are imported by main.py
# py2app will automatically detect and include these, but we list them for clarity
PY_MODULES = [
    'face_tracker',
    'midi_controller', 
    'config_manager',
    'calibration_wizard'
]

# Data files to include (documentation, etc.)
# These will be placed in the Resources folder of the .app bundle
DATA_FILES = [
    'README.md',
    'CALIBRATION_GUIDE.md',
    'requirements.txt'
]

print("\n" + "="*60)
print("Searching for MediaPipe model files...")
print("="*60)
mediapipe_data = find_mediapipe_files()
print(f"\nFound {len(mediapipe_data)} MediaPipe data files")
print("="*60 + "\n")

# py2app build options
OPTIONS = {
    'argv_emulation': False,  # Don't emulate command line arguments
    
    # Explicitly include these packages and their dependencies
    'packages': [
        'cv2',           # OpenCV for camera and image processing
        'mediapipe',     # Face mesh detection
        'rtmidi',        # MIDI output
        'numpy',         # Array processing
        'tkinter',       # GUI framework
        'threading',     # Multi-threading support
        'json',          # Config file handling
        'os',            # File system operations
        'sys',           # System operations
        'platform',      # Platform detection
    ],
    
    # Additional modules to include
    'includes': [
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'fcntl',         # Unix-specific (for rtmidi on macOS)
    ],
    
    # Include all MediaPipe data files
    'resources': mediapipe_data,
    
    # Packages to exclude (reduce app size)
    'excludes': [
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'test',
        'tests',
        'unittest',
    ],
    
    # App icon (optional - add your .icns file here)
    'iconfile': None,  # Change to 'app_icon.icns' if you have one
    
    # macOS-specific settings
    'plist': {
        'CFBundleName': 'Face to MIDI',
        'CFBundleDisplayName': 'Face to MIDI Controller',
        'CFBundleIdentifier': 'com.facetomidi.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Face to MIDI',
        
        # Privacy permissions (required for camera access)
        'NSCameraUsageDescription': 'Face to MIDI needs camera access to track your head movements and convert them to MIDI signals.',
        'NSMicrophoneUsageDescription': 'Face to MIDI does not use the microphone.',
        
        # Minimum macOS version
        'LSMinimumSystemVersion': '10.13.0',
        
        # App category
        'LSApplicationCategoryType': 'public.app-category.music',
        
        # High resolution support
        'NSHighResolutionCapable': True,
    },
    
    # Build settings
    'optimize': 2,  # Optimize Python bytecode
    'compressed': True,  # Compress Python modules
    'semi_standalone': False,  # Include Python framework (fully standalone)
    'site_packages': True,  # Include site-packages
}

setup(
    name='Face to MIDI',
    app=APP,
    data_files=DATA_FILES,
    py_modules=PY_MODULES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    
    # Metadata
    version='1.0.0',
    description='Convert head movements to MIDI control signals',
    author='Your Name',
    url='https://github.com/yourusername/face-to-midi',
)
