# Automation Builder - Build Guide for Windows Executable

This guide explains how to build a standalone Windows executable that works on all Windows systems.

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **All dependencies** installed (run `pip install -r requirements.txt`)
3. **PyInstaller** (will be installed automatically by build script)

## Quick Build

### Option 1: Using the Batch Script (Easiest)

Simply double-click `build.bat` or run it from command prompt:

```batch
build.bat
```

This will:
- Install/update PyInstaller automatically
- Build the executable
- Create `dist/AutomationBuilder.exe`

### Option 2: Using Python Script

```bash
python build_exe.py
```

### Option 3: Using Spec File Directly

```bash
pyinstaller AutomationBuilder.spec
```

## Build Output

After building, you'll find:
- **Executable**: `dist/AutomationBuilder.exe`
- **Size**: Approximately 50-100 MB (includes Python runtime and all dependencies)
- **Type**: Standalone executable (no Python required on target system)

## Distribution

The `AutomationBuilder.exe` file is **completely standalone** and can be:
- Copied to any Windows 10/11 computer
- Run without installing Python
- Run without installing any dependencies
- Distributed via USB, email, or download

## Windows Compatibility

The executable works on:
- ✅ Windows 10 (all versions)
- ✅ Windows 11 (all versions)
- ✅ Windows Server 2016/2019/2022
- ✅ Both 32-bit and 64-bit systems (builds 64-bit by default)

## First Run on Target System

When running the .exe on a new Windows computer:

1. **Windows Defender Warning**: Windows may show a security warning
   - Click "More info"
   - Click "Run anyway"
   - This is normal for unsigned executables

2. **User Account Control (UAC)**: May prompt for admin rights
   - Click "Yes" if prompted
   - Required for some automation features

3. **Firewall**: Windows Firewall may ask for permission
   - Allow the application through firewall

## Troubleshooting

### Build Fails

**Error: "PyInstaller not found"**
```bash
pip install pyinstaller
```

**Error: "Module not found"**
```bash
pip install -r requirements.txt
```

**Error: "Not enough disk space"**
- Need at least 500 MB free space
- Clean temporary files: `pyinstaller --clean`

### Executable Doesn't Run

**Error: "Missing DLL"**
- Install Visual C++ Redistributable:
  - Download from Microsoft
  - Install both x86 and x64 versions

**Error: "Application failed to start"**
- Check Windows Event Viewer for details
- Try running as Administrator
- Check antivirus isn't blocking it

**Error: "Image not found"**
- The `automation_images` folder is created automatically
- Make sure the .exe has write permissions in its directory

## Advanced Build Options

### Custom Icon

1. Create or obtain a `.ico` file
2. Edit `build_exe.py` and uncomment:
   ```python
   '--icon=icon.ico',
   ```
3. Place `icon.ico` in the project root

### Reduce File Size

Edit `build_exe.py` and add more exclusions:
```python
'--exclude-module=unnecessary_module',
```

### Debug Build

Remove `--windowed` flag to see console output:
```python
# '--windowed',  # Comment this out
```

## Build Configuration

The build includes:
- ✅ All Python dependencies
- ✅ Tkinter GUI framework
- ✅ PyAutoGUI automation library
- ✅ Pillow image processing
- ✅ SQLite database
- ✅ All required DLLs and binaries

## File Structure After Build

```
dist/
  └── AutomationBuilder.exe  (Standalone executable)

automation_images/  (Created automatically when app runs)
  └── (Your automation images)

automations.db  (Created automatically when app runs)
```

## Testing the Executable

1. **Test on Build Machine**: Run `dist/AutomationBuilder.exe`
2. **Test on Clean System**: Copy to a Windows PC without Python
3. **Test All Features**:
   - Create automation
   - Add steps (mouse, keyboard, image)
   - Run automation
   - Check auto-run functionality

## Support

If you encounter issues:
1. Check the build logs
2. Verify all dependencies are installed
3. Try building with `--clean` flag
4. Check Windows Event Viewer for errors

## Notes

- First build takes 5-10 minutes
- Subsequent builds are faster (cached)
- Executable size: ~50-100 MB
- No internet connection required to run
- Works offline completely
