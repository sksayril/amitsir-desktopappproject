"""
Utility functions for image handling, screenshots, and common operations.
"""

import os
import pyautogui
from PIL import Image
from datetime import datetime
from typing import Optional, Tuple


# Ensure failsafe is enabled
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Small pause between actions


def ensure_image_directory():
    """Ensure the automation_images directory exists."""
    img_dir = "automation_images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir


def copy_image_to_project(image_path: str) -> str:
    """
    Copy an image to the automation_images directory.
    
    Args:
        image_path: Source image path
        
    Returns:
        New path in automation_images directory
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    img_dir = ensure_image_directory()
    filename = os.path.basename(image_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    new_path = os.path.join(img_dir, new_filename)
    
    # Copy image
    img = Image.open(image_path)
    img.save(new_path)
    
    return new_path


def take_screenshot_on_failure(step_description: str = "unknown") -> str:
    """
    Take a screenshot for debugging purposes.
    
    Args:
        step_description: Description of the step that failed
        
    Returns:
        Path to saved screenshot
    """
    img_dir = ensure_image_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error_{step_description}_{timestamp}.png"
    filepath = os.path.join(img_dir, filename)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    
    return filepath


def find_image_on_screen(image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """
    Find an image on the screen using PyAutoGUI.
    
    Args:
        image_path: Path to the image file
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        Tuple of (x, y) coordinates if found, None otherwise
    """
    if not os.path.exists(image_path):
        return None
    
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            # Get center of the found image
            center = pyautogui.center(location)
            return (center.x, center.y)
    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        print(f"Error finding image: {e}")
        return None
    
    return None


def find_image_with_retry(image_path: str, confidence: float = 0.8, 
                          max_retries: int = 3, retry_delay: float = 1.0) -> Optional[Tuple[int, int]]:
    """
    Find an image on screen with retry logic.
    
    Args:
        image_path: Path to the image file
        confidence: Confidence level
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Tuple of (x, y) coordinates if found, None otherwise
    """
    import time
    
    for attempt in range(max_retries):
        result = find_image_on_screen(image_path, confidence)
        if result:
            return result
        
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    
    return None


def validate_image_file(filepath: str) -> bool:
    """Validate that a file is a valid image."""
    if not os.path.exists(filepath):
        return False
    
    try:
        img = Image.open(filepath)
        img.verify()
        return True
    except Exception:
        return False


def get_mouse_position() -> Tuple[int, int]:
    """Get current mouse position."""
    return pyautogui.position()


def format_delay(seconds: float) -> str:
    """Format delay in seconds to readable string."""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    return f"{seconds:.1f}s"
