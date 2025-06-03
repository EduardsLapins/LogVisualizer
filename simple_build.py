#!/usr/bin/env python3
"""
Simple One-File Build Script for Drone Log Analyzer
Creates a single executable file with minimal dependencies
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def clean_build():
    """Clean previous builds"""
    print("🧹 Cleaning previous builds...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}")
    
    # Remove spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"   Removed {spec_file}")

def build_simple():
    """Build with simple PyInstaller command"""
    print("🚀 Building single executable...")
    
    cmd = [
        "pyinstaller",
        "--onefile",           # Single file
        "--windowed",          # No console (GUI mode)
        "--name", "DroneLogAnalyzer",
        "--clean",
        
        # Exclude heavy libraries we don't need
        "--exclude-module", "torch",
        "--exclude-module", "torchvision", 
        "--exclude-module", "torchaudio",
        "--exclude-module", "tensorflow",
        "--exclude-module", "sklearn",
        "--exclude-module", "scipy",
        "--exclude-module", "sympy",
        "--exclude-module", "cupy",
        "--exclude-module", "numba",
        "--exclude-module", "PyQt5",
        "--exclude-module", "PyQt6",
        "--exclude-module", "PySide2",
        "--exclude-module", "PySide6",
        "--exclude-module", "wx",
        "--exclude-module", "gi",
        "--exclude-module", "cairo",
        "--exclude-module", "gstreamer",
        
        # Add only what we need
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk", 
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "matplotlib.backends.backend_tkagg",
        
        # Fix PIL/Pillow issues
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageTk",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "PIL._imaging",
        
        # Add matplotlib backend data
        "--collect-data", "matplotlib",
        
        # Main file
        "main.py"
    ]
    
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        
        executable = Path("dist/DroneLogAnalyzer")
        if executable.exists():
            size_mb = executable.stat().st_size / (1024 * 1024)
            print(f"📦 Executable: {executable.absolute()}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Make executable
            executable.chmod(0o755)
            print("✅ Made executable")
            
            return True
        else:
            print("❌ Executable not found")
            return False
    else:
        print("❌ Build failed!")
        print("STDERR:", result.stderr[-2000:])  # Last 2000 chars
        return False

def test_executable():
    """Test if executable works"""
    executable = Path("dist/DroneLogAnalyzer")
    if executable.exists():
        print("🧪 Testing executable...")
        print("   Run this to test:")
        print(f"   {executable.absolute()}")
        print("   (The GUI should open)")

def main():
    print("🚀 Simple Drone Log Analyzer Build")
    print("=" * 40)
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found!")
        sys.exit(1)
    
    try:
        # Step 1: Clean
        clean_build()
        print()
        
        # Step 2: Build
        if build_simple():
            print()
            test_executable()
            print()
            print("🎉 Build completed!")
            print("📁 Find your executable in: dist/DroneLogAnalyzer")
        else:
            print("❌ Build failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()