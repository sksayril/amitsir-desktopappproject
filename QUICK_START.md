# Quick Start Guide

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Your First Automation

### Example: Automate Notepad

1. **Create a new automation**:
   - Go to "Create Automation" tab
   - Name: "Open Notepad and Type"
   - Click "New Automation"

2. **Add steps**:
   
   **Step 1: Open Notepad**
   - Click "Add Step"
   - Type: "Hotkey"
   - Hotkey: `win+r` (Windows Run dialog)
   - Delay After: 1 second
   - Save
   
   **Step 2: Type notepad**
   - Click "Add Step"
   - Type: "Keyboard Type"
   - Text: `notepad`
   - Delay After: 0.5 seconds
   - Save
   
   **Step 3: Press Enter**
   - Click "Add Step"
   - Type: "Hotkey"
   - Hotkey: `enter`
   - Delay After: 2 seconds
   - Save
   
   **Step 4: Type text**
   - Click "Add Step"
   - Type: "Keyboard Type"
   - Text: `Hello from Automation Builder!`
   - Save

3. **Save the automation**:
   - Click "Save Automation"

4. **Run it**:
   - Go to "Run Automation" tab
   - Select your automation
   - Click "Start Automation"

## Tips

- **Use delays**: Add 0.5-2 second delays between steps for reliability
- **Test incrementally**: Start with 2-3 steps, then add more
- **Image clicks**: Use PNG format, take clear screenshots of UI elements
- **Check logs**: Always review the Logs tab after running

## Common Step Configurations

### Click a Button
- Type: Image-based Click
- Upload: Screenshot of the button
- Confidence: 0.8 (default)

### Type and Press Enter
- Step 1: Keyboard Type (your text)
- Step 2: Hotkey (`enter`)

### Wait for Window to Load
- Type: Wait / Delay
- Delay After: 2-5 seconds

### Click at Specific Location
- Type: Mouse Click
- Use "Capture Position" button
- Or enter X, Y manually

## Troubleshooting

**Automation stops early?**
- Check logs for errors
- Increase delays between steps
- Verify image paths exist

**Image not found?**
- Lower confidence to 0.7 or 0.6
- Check screenshot in `automation_images/` folder
- Ensure image is visible on screen

**Coordinates wrong?**
- Use "Capture Position" instead of manual entry
- Be aware of screen resolution changes
