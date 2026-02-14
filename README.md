# Automation Builder - Desktop Automation Tool

A complete, professional desktop automation application built with Python that allows users to automate any software without writing code manually.

## Features

### Core Capabilities

- **Visual Automation Builder**: Create automations through an intuitive GUI
- **Multiple Step Types**: Support for mouse clicks, image-based clicks, keyboard input, hotkeys, and delays
- **Step Management**: Add, edit, delete, and reorder steps with unlimited steps per automation
- **Image Recognition**: Click on screen elements by matching images with configurable confidence levels
- **Background Execution**: Automations run in separate threads, keeping the UI responsive
- **Comprehensive Logging**: Real-time execution logs with error tracking
- **Database Storage**: SQLite database for persistent storage of automations and configurations

### Step Types

1. **Mouse Click**: Click at specific X, Y coordinates with position capture tool
2. **Image-based Click**: Find and click on screen elements by matching uploaded images (with retry logic)
3. **Keyboard Type**: Type text with optional Enter key press
4. **Hotkey**: Execute keyboard shortcuts (Ctrl+C, Shift+Tab, etc.)
5. **Wait / Delay**: Add time delays between steps

### Advanced Features

- **Delays**: Configurable delays before and after each step
- **Image Confidence**: Adjustable confidence slider (0.5 - 1.0) for image matching
- **Retry Logic**: Automatic retry (3 attempts) for image-based clicks
- **Screenshot Debugging**: Automatic screenshots on failure for troubleshooting
- **Failsafe**: PyAutoGUI failsafe enabled (move mouse to corner to stop)
- **Cross-platform**: Works on Windows, macOS, and Linux (Windows optimized)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Building Executable (.exe)

### Option 1: Using the Build Script (Recommended)

**Windows:**
```bash
build.bat
```

This will automatically:
- Install/update PyInstaller
- Build the executable
- Create `dist/AutomationBuilder.exe`

**Manual build:**
```bash
python build_exe.py
```

### Option 2: Using PyInstaller Directly

```bash
pyinstaller --name=AutomationBuilder --onefile --windowed --add-data="automation_images;automation_images" main.py
```

### Option 3: Using Advanced Spec File

For more control over the build:
```bash
pyinstaller build_exe_advanced.spec
```

### Executable Output

- **Location**: `dist/AutomationBuilder.exe`
- **Size**: ~50-100 MB (includes Python runtime and all dependencies)
- **Distribution**: Can be run on any Windows PC without Python installed

### Notes

- First build may take 5-10 minutes
- Windows Defender may flag unsigned executables (this is normal)
- The executable is self-contained and portable
- Database and images folder will be created in the same directory as the .exe

## Usage Guide

### Creating an Automation

1. **Open the "Create Automation" tab**
2. **Enter automation details**:
   - Automation Name (required)
   - Description (optional)
3. **Click "New Automation"** to start fresh
4. **Add steps**:
   - Click "Add Step"
   - Select step type from dropdown
   - Configure step parameters:
     - **Mouse Click**: Use "Capture Position" button or enter X, Y manually
     - **Image-based Click**: Browse and select an image file (PNG/JPG)
     - **Keyboard Type**: Enter text to type
     - **Hotkey**: Enter keys in format `ctrl+c` or `shift+tab`
     - **Wait**: Set delay duration in "Delay After" field
   - Set delays (before/after step) if needed
   - Click "Save"
5. **Manage steps**:
   - Select a step and click "Edit Step" to modify
   - Click "Delete Step" to remove
   - Use "Move Up/Down" to reorder steps
6. **Save automation**: Click "Save Automation" when done

### Running an Automation

1. **Open the "Run Automation" tab**
2. **Select an automation** from the dropdown
3. **Click "Start Automation"**
4. **Monitor progress**:
   - Status updates in real-time
   - Current step information
   - Detailed logs in the "Logs" tab
5. **Stop if needed**: Click "Stop Automation" (stops after current step completes)

### Managing Automations

1. **Open the "Manage Automations" tab**
2. **View all automations** in the list
3. **Actions available**:
   - **Refresh**: Update the list
   - **Delete Selected**: Remove an automation (and all its steps)
   - **View Steps**: See all steps for an automation

### Logs

- **View execution logs** in the "Logs" tab
- **Logs include**:
  - Timestamp for each action
  - Step execution details
  - Errors and warnings
  - Screenshot paths on failures
- **Clear logs** using the "Clear Logs" button

## Project Structure

```
.
├── main.py                 # Application entry point
├── gui.py                  # Tkinter GUI components
├── automation_engine.py    # Automation execution engine
├── database.py             # SQLite database operations
├── models.py               # Data models (Step, Automation)
├── utils.py                # Utility functions (images, screenshots)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── automations.db         # SQLite database (created automatically)
└── automation_images/     # Directory for stored images and screenshots
```

## Technical Details

### Database Schema

**automations table**:
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT, UNIQUE)
- `description` (TEXT)
- `created_at` (TEXT)

**steps table**:
- `id` (INTEGER PRIMARY KEY)
- `automation_id` (INTEGER, FOREIGN KEY)
- `step_order` (INTEGER)
- `step_type` (TEXT)
- `x`, `y` (INTEGER, for mouse clicks)
- `image_path` (TEXT, for image clicks)
- `text` (TEXT, for keyboard input)
- `hotkey` (TEXT, for hotkeys)
- `delay_before` (REAL)
- `delay_after` (REAL)
- `confidence` (REAL, for image matching)

### Architecture

- **Modular Design**: Separate files for GUI, engine, database, and utilities
- **Object-Oriented**: Classes for database, engine, and GUI
- **Threading**: Background execution keeps UI responsive
- **Error Handling**: Comprehensive try/except blocks with user-friendly messages
- **Type Hints**: Type annotations for better code clarity

## Extending the Application

### Adding New Step Types

To add a new step type:

1. **Update `models.py`**:
   - Add new type to `StepType` enum:
     ```python
     NEW_STEP_TYPE = "New Step Type"
     ```

2. **Update `database.py`**:
   - No changes needed (step_type is stored as TEXT)

3. **Update `automation_engine.py`**:
   - Add execution method:
     ```python
     def _execute_new_step_type(self, step: Step) -> bool:
         # Implementation here
         return True
     ```
   - Add case in `execute_step()` method:
     ```python
     elif step.step_type == "New Step Type":
         success = self._execute_new_step_type(step)
     ```

4. **Update `gui.py`**:
   - Add to step type dropdown in `show_add_step_dialog()`
   - Add UI fields in `update_fields()` function for the new step type
   - Update `_format_step_display()` for listbox display

### Example: Adding a "Screenshot" Step Type

```python
# In automation_engine.py
def _execute_screenshot(self, step: Step) -> bool:
    """Take a screenshot."""
    try:
        screenshot_path = take_screenshot_on_failure(step.text or "screenshot")
        self.log(f"Screenshot saved: {screenshot_path}")
        return True
    except Exception as e:
        self.log(f"Screenshot failed: {str(e)}", "ERROR")
        return False
```

## Troubleshooting

### Image Not Found

- **Check image path**: Ensure image file exists
- **Adjust confidence**: Lower confidence value (try 0.7 or 0.6)
- **Check screenshot**: Debug screenshots are saved in `automation_images/` folder
- **Image format**: Use PNG format for best results

### Automation Not Running

- **Check logs**: View error messages in the Logs tab
- **Verify steps**: Ensure all steps have required parameters
- **Database**: Check if automation was saved properly

### Mouse Position Issues

- **Screen resolution**: Coordinates are screen-relative
- **Multiple monitors**: Be aware of multi-monitor setups
- **Capture tool**: Use "Capture Position" button for accuracy

## Safety Features

- **Failsafe**: Move mouse to top-left corner to emergency stop
- **Graceful shutdown**: Stop button waits for current step to complete
- **Error recovery**: Screenshots on failures for debugging
- **Input validation**: All user inputs are validated before execution

## Best Practices

1. **Test automations** with small step counts first
2. **Use delays** between steps for reliability
3. **Save images** in high quality (PNG format recommended)
4. **Name automations** descriptively
5. **Review logs** after execution to identify issues
6. **Backup database** regularly (copy `automations.db`)

## License

This project is provided as-is for educational and automation purposes.

## Support

For issues or questions:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Verify all dependencies are installed correctly

---

**Built with Python, Tkinter, PyAutoGUI, SQLite, and Pillow**
