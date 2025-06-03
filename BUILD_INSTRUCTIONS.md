# Building Executables for Drone Log Analyzer

This guide shows how to create standalone executables for Windows, macOS, and Linux.

## Quick Build (Automated)

### 1. Run the Build Script
```bash
python build_executable.py
```

This will automatically:
- Install required dependencies
- Clean previous builds
- Create platform-specific executable
- Package for distribution

## Manual Build Process

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Install All Dependencies
```bash
pip install -r requirements.txt
```

### 3. Build Commands by Platform

#### Windows
```bash
pyinstaller --onefile --windowed --name DroneLogAnalyzer --icon icon.ico main.py
```

#### macOS
```bash
pyinstaller --onefile --windowed --name DroneLogAnalyzer --icon icon.icns main.py
```

#### Linux
```bash
pyinstaller --onefile --windowed --name DroneLogAnalyzer main.py
```

## Advanced Build Options

### Console Version (with debug output)
```bash
pyinstaller --onefile --console --name DroneLogAnalyzer main.py
```

### Include Additional Files
```bash
pyinstaller --onefile --windowed --add-data "README.md:." --name DroneLogAnalyzer main.py
```

### Optimize Size
```bash
pyinstaller --onefile --windowed --upx-dir /path/to/upx --name DroneLogAnalyzer main.py
```

## Platform-Specific Instructions

### Windows

#### Requirements
- Python 3.7+
- Windows 10 or later

#### Building
```cmd
# Install dependencies
pip install pyinstaller pandas matplotlib numpy

# Build executable
python build_executable.py

# Output: dist/DroneLogAnalyzer.exe
```

#### Optional: Add Icon
1. Create `icon.ico` (256x256 recommended)
2. Use `--icon icon.ico` flag

### macOS

#### Requirements
- Python 3.7+
- macOS 10.14 or later

#### Building
```bash
# Install dependencies
pip3 install pyinstaller pandas matplotlib numpy

# Build executable
python3 build_executable.py

# Output: dist/DroneLogAnalyzer.app
```

#### Code Signing (Optional)
```bash
codesign --sign "Developer ID Application: Your Name" dist/DroneLogAnalyzer.app
```

#### Creating DMG
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Drone Log Analyzer" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "DroneLogAnalyzer.app" 200 190 \
  --hide-extension "DroneLogAnalyzer.app" \
  --app-drop-link 400 190 \
  "DroneLogAnalyzer.dmg" \
  "dist/"
```

### Linux

#### Requirements
- Python 3.7+
- GTK development libraries

#### Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-dev

# CentOS/RHEL
sudo yum install tkinter python3-devel

# Arch Linux
sudo pacman -S tk python
```

#### Building
```bash
# Install dependencies
pip3 install pyinstaller pandas matplotlib numpy

# Build executable
python3 build_executable.py

# Output: dist/DroneLogAnalyzer
```

#### Creating AppImage (Optional)
```bash
# Download appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p DroneLogAnalyzer.AppDir/usr/bin
cp dist/DroneLogAnalyzer DroneLogAnalyzer.AppDir/usr/bin/
# ... (add .desktop file and icon)

# Build AppImage
./appimagetool-x86_64.AppImage DroneLogAnalyzer.AppDir
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Add missing modules
pyinstaller --hidden-import tkinter.filedialog --hidden-import matplotlib.backends.backend_tkagg main.py
```

#### Large File Size
```bash
# Exclude unnecessary modules
pyinstaller --exclude-module PyQt5 --exclude-module PyQt6 main.py
```

#### tkinter Issues on Linux
```bash
# Install tkinter
sudo apt-get install python3-tk
```

#### macOS Security Warning
```bash
# Remove quarantine attribute
xattr -r -d com.apple.quarantine DroneLogAnalyzer.app
```

### Build Environment Setup

#### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv drone_analyzer_build
source drone_analyzer_build/bin/activate  # Linux/macOS
# or
drone_analyzer_build\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build
python build_executable.py
```

## Distribution

### File Sizes (Approximate)
- **Windows**: 50-80 MB (.exe)
- **macOS**: 60-90 MB (.app bundle)
- **Linux**: 45-75 MB (binary)

### Compression
```bash
# Create archives for distribution
# Windows
7z a DroneLogAnalyzer-windows.zip dist/DroneLogAnalyzer.exe README.md

# macOS
tar -czf DroneLogAnalyzer-macos.tar.gz dist/DroneLogAnalyzer.app README.md

# Linux
tar -czf DroneLogAnalyzer-linux.tar.gz dist/DroneLogAnalyzer README.md
```

## CI/CD Automation

### GitHub Actions Example
```yaml
name: Build Executables

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python build_executable.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: DroneLogAnalyzer-${{ matrix.os }}
        path: dist/
```

## Testing the Executable

### Before Distribution
1. **Test on clean system** without Python installed
2. **Verify all features work**:
   - File browsing
   - Session loading
   - Time range selection
   - Data visualization
   - Plot export
3. **Check different log file formats**
4. **Test error handling**

### Performance Optimization
- Use `--upx` for smaller file size
- Use `--exclude-module` for unused libraries
- Consider `--onedir` vs `--onefile` trade-offs

## Support

For build issues:
1. Check PyInstaller documentation
2. Verify all dependencies are installed
3. Test in clean virtual environment
4. Check platform-specific requirements