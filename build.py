#!/usr/bin/env python3
"""
Build script for Voice_Keyer_TTS standalone executable.

Usage:
    python build.py

Requirements:
    pip install pyinstaller

Output:
    dist/Voice_Keyer_TTS.exe (Windows)
    dist/Voice_Keyer_TTS (Linux/Mac)
"""

import subprocess
import sys
import os


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        return True


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    packages = {
        'pyttsx3': 'pyttsx3',
        'sounddevice': 'sounddevice',
        'soundfile': 'soundfile',
        'numpy': 'numpy',
    }
    for import_name, pip_name in packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"Installing missing dependencies: {missing}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)


def build():
    """Build the executable."""
    print("=" * 50)
    print("Building Voice_Keyer_TTS standalone executable")
    print("=" * 50)

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check dependencies
    check_pyinstaller()
    check_dependencies()

    # Run PyInstaller
    print("\nRunning PyInstaller...")
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'Voice_Keyer_TTS.spec'
    ])

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)

        import shutil
        exe_name = 'Voice_Keyer_TTS.exe' if sys.platform == 'win32' else 'Voice_Keyer_TTS'
        src = os.path.join('dist', exe_name)
        dst = exe_name
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"\nExecutable copied to: {dst}")
            print("(Also available in dist/ folder)")
    else:
        print("\nBuild failed. Check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    build()
