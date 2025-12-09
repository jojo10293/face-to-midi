"""
py2app setup script for Face to MIDI
Usage: python setup_mac.py py2app

This will create a standalone macOS application bundle that includes:
- All Python modules (face_tracker, midi_controller, config_manager, calibration_wizard)
- All dependencies (OpenCV, MediaPipe, rtmidi, numpy, tkinter)
- Documentation files
- Default configuration

The .py modules are automatically included by py2app when imported by main.py,
but we explicitly list them here to ensure they're found.
"""

from setuptools import setup
import os

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
