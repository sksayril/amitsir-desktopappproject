"""
Script to build executable using PyInstaller.
Run this script to create a standalone .exe file that works on all Windows systems.
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """Build the executable with all necessary dependencies."""
    
    # Ensure automation_images directory exists
    if not os.path.exists('automation_images'):
        os.makedirs('automation_images')
    
    # PyInstaller arguments for Windows compatibility
    args = [
        'main.py',                          # Main script
        '--name=AutomationBuilder',         # Name of executable
        '--onefile',                        # Single executable file
        '--windowed',                       # No console window (GUI app)
        '--noupx',                          # Disable UPX compression for better compatibility
        # '--icon=icon.ico',                # Uncomment and add path if you have an icon file
        
        # Include data files
        '--add-data=automation_images;automation_images',  # Include images folder (Windows format)
        
        # Hidden imports - ensure all modules are included
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageTk',
        '--hidden-import=pyautogui',
        '--hidden-import=pyscreeze',
        '--hidden-import=pygetwindow',
        '--hidden-import=pyrect',
        '--hidden-import=sqlite3',
        '--hidden-import=datetime',
        '--hidden-import=threading',
        '--hidden-import=time',
        '--hidden-import=os',
        '--hidden-import=sys',
        
        # Collect all dependencies
        '--collect-all=pyautogui',         # Collect all PyAutoGUI dependencies
        '--collect-all=PIL',               # Collect all Pillow dependencies
        '--collect-all=pyscreeze',         # Collect PyScreeze (used by PyAutoGUI)
        
        # Exclude unnecessary modules to reduce size
        '--exclude-module=PyQt6',
        '--exclude-module=PySide6',
        '--exclude-module=qtpy',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        
        # Windows-specific options
        '--target-arch=x86_64',            # 64-bit Windows (works on all modern Windows)
        
        # Build options
        '--noconfirm',                      # Overwrite output without asking
        '--clean',                          # Clean cache before building
        '--log-level=INFO',                 # Show build information
    ]
    
    print("="*60)
    print("Building Automation Builder Executable")
    print("="*60)
    print("This may take 5-10 minutes...")
    print("Please wait...")
    print("="*60)
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*60)
        print("✓ Build completed successfully!")
        print("="*60)
        print(f"\nExecutable location: {os.path.abspath('dist/AutomationBuilder.exe')}")
        print(f"File size: {os.path.getsize('dist/AutomationBuilder.exe') / (1024*1024):.1f} MB")
        print("\n" + "="*60)
        print("IMPORTANT NOTES:")
        print("="*60)
        print("1. The first time you run the .exe, Windows Defender may")
        print("   show a security warning. This is normal for unsigned executables.")
        print("2. You may need to click 'More info' and then 'Run anyway'")
        print("3. The .exe is standalone and works on all Windows 10/11 systems")
        print("4. No Python installation is required on the target computer")
        print("5. The automation_images folder will be created automatically")
        print("="*60)
    except Exception as e:
        print("\n" + "="*60)
        print("✗ ERROR: Build failed!")
        print("="*60)
        print(f"Error details: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PyInstaller is installed: pip install pyinstaller")
        print("2. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("3. Try running as administrator")
        print("4. Check that you have enough disk space (need ~500MB free)")
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
