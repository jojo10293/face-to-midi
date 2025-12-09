@echo off
REM Build Face to MIDI for Windows with all MediaPipe data files
REM This ensures the executable includes all necessary model files

echo ==========================================
echo Face to MIDI - Windows Build Script
echo ==========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo.
echo Finding MediaPipe data files...
for /f "delims=" %%i in ('python -c "import mediapipe, os; print(os.path.dirname(mediapipe.__file__))"') do set MEDIAPIPE_PATH=%%i
echo MediaPipe path: %MEDIAPIPE_PATH%

echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Face-to-MIDI.spec" del "Face-to-MIDI.spec"

echo.
echo Building Windows executable with all dependencies...
echo This may take several minutes...
echo.

pyinstaller --name "Face-to-MIDI" ^
            --windowed ^
            --onefile ^
            --clean ^
            --noconfirm ^
            --add-data "%MEDIAPIPE_PATH%;mediapipe" ^
            --hidden-import=mediapipe.python.solutions.face_mesh ^
            --hidden-import=mediapipe.python.solutions.drawing_utils ^
            --hidden-import=mediapipe.python.solutions.drawing_styles ^
            --collect-all mediapipe ^
            --collect-data mediapipe ^
            main.py

if exist "dist\Face-to-MIDI.exe" (
    echo.
    echo ==========================================
    echo Build successful!
    echo ==========================================
    echo.
    echo Executable location: dist\Face-to-MIDI.exe
    echo.
    echo The executable includes:
    echo - All Python code
    echo - MediaPipe models (.binarypb, .tflite files)
    echo - OpenCV libraries
    echo - MIDI support
    echo - Complete standalone application
    echo.
    echo File size will be approximately 200-400MB due to ML models.
    echo.
) else (
    echo.
    echo Build failed! Check the output above for errors.
    pause
    exit /b 1
)

pause
