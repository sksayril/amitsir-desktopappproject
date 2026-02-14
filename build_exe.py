"""
Script to build executable using PyInstaller.
Run this script to create a standalone .exe file.
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """Build the executable."""
    
    # PyInstaller arguments
    args = [
        'main.py',                          # Main script
        '--name=AutomationBuilder',         # Name of executable
        '--onefile',                        # Single executable file
        '--windowed',                       # No console window (GUI app)
        # '--icon=icon.ico',                # Uncomment and add path if you have an icon file
        '--add-data=automation_images;automation_images',  # Include images folder (Windows format)
        '--hidden-import=tkinter',          # Ensure tkinter is included
        '--hidden-import=PIL',              # Ensure Pillow is included
        '--hidden-import=pyautogui',        # Ensure PyAutoGUI is included
        '--collect-all=pyautogui',         # Collect all PyAutoGUI dependencies
        '--collect-all=PIL',                # Collect all Pillow dependencies
        '--exclude-module=PyQt6',          # Exclude unnecessary Qt dependencies
        '--exclude-module=PySide6',         # Exclude unnecessary Qt dependencies
        '--exclude-module=qtpy',            # Exclude unnecessary Qt dependencies
        '--exclude-module=matplotlib',       # Exclude unnecessary plotting library
        '--noconfirm',                      # Overwrite output without asking
        '--clean',                          # Clean cache before building
    ]
    
    print("Building executable...")
    print("This may take a few minutes...")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*50)
        print("Build completed successfully!")
        print("="*50)
        print(f"Executable location: dist/AutomationBuilder.exe")
        print("\nNote: The first time you run the .exe, Windows may show")
        print("a security warning. This is normal for unsigned executables.")
    except Exception as e:
        print(f"\nError building executable: {e}")
        print("\nMake sure PyInstaller is installed:")
        print("  pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
