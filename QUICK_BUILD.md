# Quick Build Instructions

## Build the Executable (3 Easy Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Build Executable
**Option A - Easiest (Windows):**
```bash
build.bat
```

**Option B - Python Script:**
```bash
python build_exe.py
```

**Option C - Using Spec File:**
```bash
pyinstaller AutomationBuilder.spec
```

### Step 3: Find Your Executable
After building, your executable is at:
```
dist/AutomationBuilder.exe
```

## What You Get

✅ **Standalone executable** - Works on any Windows 10/11 PC  
✅ **No Python required** - Target computers don't need Python  
✅ **All dependencies included** - Everything bundled in one file  
✅ **Portable** - Copy and run anywhere  

## File Size
- Approximately 50-100 MB
- Includes Python runtime + all libraries

## Distribution

Simply copy `dist/AutomationBuilder.exe` to:
- USB drive
- Network share
- Email attachment
- Download link

The executable works immediately - no installation needed!

## First Run Notes

1. **Windows Security Warning**: Click "More info" → "Run anyway"
2. **UAC Prompt**: Click "Yes" if prompted (needed for automation)
3. **Firewall**: Allow through firewall when asked

## Troubleshooting

**Build fails?**
```bash
pip install --upgrade pyinstaller
pip install -r requirements.txt
```

**Executable doesn't run?**
- Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Try running as Administrator
- Check antivirus isn't blocking it

## System Requirements

**Build Machine:**
- Windows 10/11
- Python 3.8+
- 500 MB free disk space

**Target Machine:**
- Windows 10/11 (64-bit)
- 100 MB free disk space
- No other requirements!
