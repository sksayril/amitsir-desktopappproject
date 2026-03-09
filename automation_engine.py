"""
Automation engine for executing automation workflows.
Handles step-by-step execution with threading support.
"""

import os
import time
import threading
import pyautogui
from typing import Optional, Callable, Dict
from models import Step
from utils import find_image_with_retry, take_screenshot_on_failure


class AutomationEngine:
    """Engine for executing automation workflows."""
    
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None,
                 status_callback: Optional[Callable[[str], None]] = None,
                 step_callback: Optional[Callable[[int, str], None]] = None):
        """
        Initialize automation engine.
        
        Args:
            log_callback: Function to call for logging messages
            status_callback: Function to call for status updates
            step_callback: Function to call when step changes (step_num, step_info)
        """
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.step_callback = step_callback
        self.is_running = False
        self.should_stop = False
        self.current_thread: Optional[threading.Thread] = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message using the callback."""
        if self.log_callback:
            timestamp = time.strftime("%H:%M:%S")
            self.log_callback(f"[{timestamp}] [{level}] {message}")
    
    def update_status(self, status: str):
        """Update status using the callback."""
        if self.status_callback:
            self.status_callback(status)
    
    def update_step(self, step_num: int, step_info: str):
        """Update current step using the callback."""
        if self.step_callback:
            self.step_callback(step_num, step_info)
    
    def execute_step(self, step: Step, step_number: int, total_steps: int) -> bool:
        """
        Execute a single automation step.
        
        Args:
            step: Step object to execute
            step_number: Current step number (1-indexed)
            total_steps: Total number of steps
            
        Returns:
            True if successful, False otherwise
        """
        if self.should_stop:
            return False
        
        step_info = f"Step {step_number}/{total_steps}: {step.step_type}"
        self.update_step(step_number, step_info)
        self.log(f"Executing {step_info}")
        
        # Delay before step
        if step.delay_before > 0:
            self.log(f"Waiting {step.delay_before}s before step...")
            time.sleep(step.delay_before)
            if self.should_stop:
                return False
        
        try:
            # Execute based on step type
            if step.step_type == "Mouse Click":
                success = self._execute_mouse_click(step)
            elif step.step_type == "Image-based Click":
                success = self._execute_image_click(step)
            elif step.step_type == "Keyboard Type":
                success = self._execute_keyboard_type(step)
            elif step.step_type == "Hotkey":
                success = self._execute_hotkey(step)
            elif step.step_type == "Wait / Delay":
                success = self._execute_wait(step)
            else:
                self.log(f"Unknown step type: {step.step_type}", "ERROR")
                return False
            
            if not success:
                return False
            
            # Delay after step
            if step.delay_after > 0:
                self.log(f"Waiting {step.delay_after}s after step...")
                time.sleep(step.delay_after)
                if self.should_stop:
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"Error executing step: {str(e)}", "ERROR")
            screenshot_path = take_screenshot_on_failure(f"step_{step_number}")
            self.log(f"Screenshot saved: {screenshot_path}", "DEBUG")
            return False
    
    def _execute_mouse_click(self, step: Step) -> bool:
        """Execute a mouse click step."""
        if step.x is None or step.y is None:
            self.log("Mouse click step missing coordinates", "ERROR")
            return False
        
        try:
            self.log(f"Clicking at ({step.x}, {step.y})")
            pyautogui.click(step.x, step.y)
            return True
        except Exception as e:
            self.log(f"Mouse click failed: {str(e)}", "ERROR")
            return False
    
    def _execute_image_click(self, step: Step) -> bool:
        """Execute an image-based click step."""
        if not step.image_path:
            self.log("Image click step missing image path", "ERROR")
            return False
        
        try:
            # Resolve image path to handle relative paths and executable scenarios
            from utils import resolve_image_path
            resolved_path = resolve_image_path(step.image_path)
            
            if not os.path.exists(resolved_path):
                self.log(f"Image file not found: {resolved_path} (original: {step.image_path})", "ERROR")
                screenshot_path = take_screenshot_on_failure(f"image_not_found_{step.id}")
                self.log(f"Debug screenshot saved: {screenshot_path}", "DEBUG")
                return False
            
            self.log(f"Searching for image: {resolved_path} (confidence: {step.confidence})")
            
            # Try with higher retries and longer delays for better reliability
            location = find_image_with_retry(
                resolved_path,
                confidence=step.confidence,
                max_retries=5,  # Increased retries
                retry_delay=1.5  # Longer delay between retries
            )
            
            if location:
                x, y = location
                self.log(f"Image found at ({x}, {y}), clicking...")
                pyautogui.click(x, y)
                return True
            else:
                self.log(f"Image not found after retries: {resolved_path}", "ERROR")
                self.log(f"Original path was: {step.image_path}", "DEBUG")
                screenshot_path = take_screenshot_on_failure(f"image_not_found_{step.id}")
                self.log(f"Debug screenshot saved: {screenshot_path}", "DEBUG")
                return False
                
        except Exception as e:
            self.log(f"Image click failed: {str(e)}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "DEBUG")
            screenshot_path = take_screenshot_on_failure(f"image_error_{step.id}")
            self.log(f"Debug screenshot saved: {screenshot_path}", "DEBUG")
            return False
    
    def _execute_keyboard_type(self, step: Step) -> bool:
        """Execute a keyboard type step (either type text or press a key)."""
        # Check if it's a key press or text typing
        if step.key_press:
            # Press a specific key
            try:
                key_name = step.key_press.lower()
                self.log(f"Pressing key: {key_name}")
                pyautogui.press(key_name)
                return True
            except Exception as e:
                self.log(f"Key press failed: {str(e)}", "ERROR")
                return False
        elif step.text:
            # Type text
            try:
                self.log(f"Typing: {step.text}")
                pyautogui.write(step.text, interval=0.05)
                return True
            except Exception as e:
                self.log(f"Keyboard type failed: {str(e)}", "ERROR")
                return False
        else:
            self.log("Keyboard type step missing both text and key_press", "ERROR")
            return False
    
    def _execute_hotkey(self, step: Step) -> bool:
        """Execute a hotkey step."""
        if not step.hotkey:
            self.log("Hotkey step missing hotkey definition", "ERROR")
            return False
        
        try:
            # Parse hotkey string (e.g., "ctrl+c", "shift+tab")
            keys = step.hotkey.lower().split('+')
            keys = [k.strip() for k in keys]
            
            self.log(f"Pressing hotkey: {step.hotkey}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            self.log(f"Hotkey failed: {str(e)}", "ERROR")
            return False
    
    def _execute_wait(self, step: Step) -> bool:
        """Execute a wait/delay step."""
        # Use delay_after as the wait duration for wait steps
        wait_time = step.delay_after if step.delay_after > 0 else step.delay_before
        if wait_time <= 0:
            wait_time = 1.0  # Default 1 second
        
        try:
            self.log(f"Waiting {wait_time}s...")
            time.sleep(wait_time)
            return True
        except Exception as e:
            self.log(f"Wait failed: {str(e)}", "ERROR")
            return False
    
    def execute_automation(self, steps: list[Step]):
        """
        Execute a complete automation workflow.
        
        Args:
            steps: List of Step objects to execute in order
        """
        if self.is_running:
            self.log("Automation already running", "WARNING")
            return
        
        self.is_running = True
        self.should_stop = False
        self.update_status("Running")
        
        total_steps = len(steps)
        if total_steps == 0:
            self.log("No steps to execute", "WARNING")
            self.is_running = False
            self.update_status("Ready")
            return
        
        self.log(f"Starting automation with {total_steps} step(s)")
        start_time = time.time()
        
        completed_steps = 0
        for idx, step in enumerate(steps, start=1):
            if self.should_stop:
                self.log("Automation stopped by user", "INFO")
                break
            
            success = self.execute_step(step, idx, total_steps)
            
            if success:
                completed_steps += 1
            else:
                self.log(f"Step {idx} failed, stopping automation", "ERROR")
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        if self.should_stop:
            self.update_status("Stopped")
            self.log(f"Automation stopped after {completed_steps}/{total_steps} steps", "INFO")
        else:
            self.update_status("Completed")
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            self.log(f"Automation completed successfully in {hours:02d}:{minutes:02d}:{seconds:02d} ({completed_steps}/{total_steps} steps)", "INFO")
        
        self.is_running = False
    
    def start_automation(self, steps: list[Step]):
        """
        Start automation in a separate thread.
        
        Args:
            steps: List of Step objects to execute
        """
        if self.is_running:
            self.log("Automation already running", "WARNING")
            return
        
        self.current_thread = threading.Thread(
            target=self.execute_automation,
            args=(steps,),
            daemon=True
        )
        self.current_thread.start()
    
    def stop_automation(self):
        """Stop the currently running automation."""
        if not self.is_running:
            return
        
        self.should_stop = True
        self.log("Stop signal sent, waiting for automation to finish current step...", "INFO")
    
    def is_automation_running(self) -> bool:
        """Check if automation is currently running."""
        return self.is_running
