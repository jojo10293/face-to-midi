# Using GitHub Actions to Build Face to MIDI

This guide explains how to use GitHub Actions to automatically build macOS and Windows executables **for free** using GitHub's cloud infrastructure.

## What You Get

✅ **macOS executable** - Built on real macOS machines  
✅ **Windows executable** - Built on Windows machines  
✅ **Automatic builds** - Triggered on every push  
✅ **100% FREE** - GitHub Actions is free for public repositories  
✅ **No Mac needed** - Everything runs in the cloud

## Setup Instructions

### 1. Create a GitHub Repository

If you don't have one yet:

```bash
# Initialize git (if not already done)
cd C:\face_to_midi
git init

# Create .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore
echo "build/" >> .gitignore
echo "dist/" >> .gitignore
echo "*.spec" >> .gitignore
echo "face_to_midi_config.json" >> .gitignore

# Add all files
git add .
git commit -m "Initial commit"
```

Go to GitHub.com and create a new repository, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/face-to-midi.git
git branch -M main
git push -u origin main
```

### 2. GitHub Actions is Already Set Up!

The workflow file `.github/workflows/build.yml` is already in your project. Once you push to GitHub, it will automatically:

1. **Detect the push** to your repository
2. **Start two build jobs** - one on macOS, one on Windows
3. **Install dependencies** and build the executables
4. **Upload artifacts** that you can download

### 3. View Build Progress

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. You'll see the build running
4. Wait 5-10 minutes for builds to complete

### 4. Download Built Apps

After the build completes:

1. Click on the completed workflow run
2. Scroll down to **"Artifacts"**
3. Download:
   - **Face-to-MIDI-macOS** - macOS executable
   - **Face-to-MIDI-Windows** - Windows .exe

### 5. Create Releases (Optional)

To create downloadable releases:

```bash
# Tag a version
git tag v1.0.0
git push origin v1.0.0
```

This will:
- Trigger the build
- Automatically create a GitHub Release
- Attach both macOS and Windows executables
- Generate release notes

Users can then download from the "Releases" page!

## What Happens During Build

### macOS Build (runs on macOS-latest):
```
1. Checkout your code
2. Install Python 3.11
3. Install requirements (opencv, mediapipe, rtmidi, etc.)
4. Install PyInstaller
5. Build executable with PyInstaller
6. Upload Face-to-MIDI (macOS executable)
```

### Windows Build (runs on windows-latest):
```
1. Checkout your code
2. Install Python 3.11
3. Install requirements
4. Install PyInstaller
5. Build Face-to-MIDI.exe
6. Upload executable
```

## File Sizes

Expect these sizes:
- **macOS**: ~200-400 MB (includes MediaPipe models)
- **Windows**: ~200-400 MB (includes MediaPipe models)

This is normal due to the ML models and dependencies.

## Troubleshooting

### Build Fails

Check the Actions log:
1. Go to Actions tab
2. Click on failed run
3. Click on the failed job
4. Read the error messages

Common issues:
- **Missing dependencies** - Update `requirements.txt`
- **Import errors** - Make sure all Python files are committed
- **Permission issues** - Check file paths are correct

### Artifacts Not Appearing

- Wait for build to fully complete (green checkmark)
- Artifacts are kept for 90 days
- Download before they expire

### Can't Download Artifacts

- You must be logged into GitHub
- You need read access to the repository
- Artifacts are per workflow run

## Cost

**FREE!** 

GitHub Actions provides:
- 2,000 minutes/month for private repos
- Unlimited for public repos
- macOS builds use 10x multiplier (so 200 minutes = 2000 actual minutes)

A typical build takes ~10 minutes, so you get plenty of builds per month.

## Customization

### Change Python Version

Edit `.github/workflows/build.yml`:
```yaml
python-version: '3.12'  # Change to desired version
```

### Add Code Signing (macOS)

For signed macOS apps, you'd need to add signing certificates to GitHub Secrets. See GitHub documentation for details.

### Change Build Triggers

Edit the `on:` section:
```yaml
on:
  push:
    branches: [ main ]  # Only build on main branch
  # Remove pull_request if you don't want PR builds
```

### Build on Specific Paths

Only build when certain files change:
```yaml
on:
  push:
    paths:
      - '**.py'
      - 'requirements.txt'
```

## Advanced: Adding App Icons

To add icons to your builds:

1. Create icons:
   - macOS: `app_icon.icns`
   - Windows: `app_icon.ico`

2. Update workflow:
```yaml
pyinstaller --name "Face-to-MIDI" \
            --windowed \
            --onefile \
            --icon=app_icon.icns \  # Add this
            main.py
```

## Testing Locally Before Push

Test the PyInstaller build locally:

**Windows:**
```powershell
pip install pyinstaller
pyinstaller --name "Face-to-MIDI" --windowed --onefile main.py
```

**macOS** (if you have access):
```bash
pip install pyinstaller
pyinstaller --name "Face-to-MIDI" --windowed --onefile main.py
```

## Distribution

Once built, you can:

1. **Direct Download** - Share GitHub releases link
2. **Host Yourself** - Upload to your website
3. **App Stores** - Submit to Mac App Store (requires signing)
4. **Package Managers** - Create Homebrew formula, etc.

## Status Badge

Add a build status badge to your README.md:

```markdown
![Build Status](https://github.com/YOUR_USERNAME/face-to-midi/workflows/Build%20Face%20to%20MIDI/badge.svg)
```

## Summary

You now have:
- ✅ Automatic macOS builds (no Mac needed!)
- ✅ Automatic Windows builds
- ✅ Release management
- ✅ Version tagging
- ✅ Free cloud infrastructure

Just push your code and GitHub builds everything for you!
