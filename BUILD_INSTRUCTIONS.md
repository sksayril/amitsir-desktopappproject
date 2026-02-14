# Building Executable Instructions

## Quick Build (Windows)

1. **Double-click `build.bat`**
   - This will automatically install PyInstaller and build the .exe
   - The executable will be in the `dist` folder

## Manual Build Steps

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

Or if already in requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Build the Executable

**Simple method:**
```bash
python build_exe.py
```

**Or use PyInstaller directly:**
```bash
pyinstaller --name=AutomationBuilder --onefile --windowed --add-data="automation_images;automation_images" main.py
```

**Or use the advanced spec file:**
```bash
pyinstaller build_exe_advanced.spec
```

### Step 3: Find Your Executable

- Location: `dist/AutomationBuilder.exe`
- Size: Approximately 50-100 MB
- This is a standalone file that includes Python and all dependencies

## Build Options Explained

### `--onefile`
Creates a single executable file instead of a folder with multiple files.

### `--windowed` or `-w`
Hides the console window (important for GUI applications).

### `--add-data`
Includes the `automation_images` folder so images are available at runtime.

### `--name`
Sets the name of the output executable.

## Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" errors
Add hidden imports in `build_exe.py`:
```python
'--hidden-import=module_name',
```

### Large file size
This is normal - PyInstaller bundles Python and all dependencies. The first run may be slower.

### Windows Defender warning
Unsigned executables may trigger Windows Defender. This is expected. You can:
- Click "More info" → "Run anyway"
- Add an exception for the file
- Sign the executable with a code signing certificate (advanced)

### Executable doesn't run
1. Check if all dependencies are included
2. Try building with `--console` flag to see error messages:
   ```bash
   pyinstaller --name=AutomationBuilder --onefile --console main.py
   ```

### Database/Images not found
The executable creates the database and images folder in the same directory as the .exe. Make sure the .exe has write permissions.

## Distribution

To distribute your application:

1. **Copy the executable**: `dist/AutomationBuilder.exe`
2. **Optional**: Create a folder structure:
   ```
   AutomationBuilder/
   ├── AutomationBuilder.exe
   └── README.txt (instructions for users)
   ```
3. **Zip and distribute**: Users can run the .exe directly without installing Python

## Adding an Icon

1. Create or download a `.ico` file
2. Update `build_exe.py`:
   ```python
   '--icon=icon.ico',  # Add this line
   ```
3. Or update `build_exe_advanced.spec`:
   ```python
   icon='icon.ico',  # In the EXE() section
   ```

## Advanced: Code Signing (Optional)

To avoid Windows Defender warnings, you can sign the executable:

1. Obtain a code signing certificate
2. Use `signtool` or similar tool to sign the .exe
3. This requires a paid certificate from a Certificate Authority

## Build Time

- First build: 5-10 minutes (PyInstaller analyzes all dependencies)
- Subsequent builds: 2-5 minutes (if dependencies haven't changed)

## File Size Optimization

If the .exe is too large, you can:

1. Use `--exclude-module` to exclude unused modules
2. Use UPX compression (already enabled in spec file)
3. Consider `--onedir` instead of `--onefile` (creates a folder instead)

## Testing the Executable

1. Build the .exe
2. Copy it to a different location (or different PC)
3. Run it and test all features:
   - Create automation
   - Add steps
   - Run automation
   - Check logs

Make sure it works without Python installed!
