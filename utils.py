"""
Utility functions for image handling, screenshots, and common operations.
"""

import os
import sys
import pyautogui
from PIL import Image
from datetime import datetime
from typing import Optional, Tuple


# Ensure failsafe is enabled
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Small pause between actions


def get_base_directory():
    """Get the base directory (works for both script and executable)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def ensure_image_directory():
    """Ensure the automation_images directory exists."""
    base_dir = get_base_directory()
    img_dir = os.path.join(base_dir, "automation_images")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir


def resolve_image_path(image_path: str) -> str:
    """
    Resolve image path to absolute path.
    Handles both relative and absolute paths, and works with executables.
    
    Args:
        image_path: Image path (can be relative or absolute)
        
    Returns:
        Absolute path to the image
    """
    if not image_path:
        return image_path
    
    # If already absolute and exists, return as is
    if os.path.isabs(image_path) and os.path.exists(image_path):
        return image_path
    
    # Try relative to base directory first
    base_dir = get_base_directory()
    abs_path = os.path.join(base_dir, image_path)
    if os.path.exists(abs_path):
        return os.path.abspath(abs_path)
    
    # Try relative to current working directory
    if os.path.exists(image_path):
        return os.path.abspath(image_path)
    
    # Try in automation_images directory
    img_dir = ensure_image_directory()
    img_path = os.path.join(img_dir, os.path.basename(image_path))
    if os.path.exists(img_path):
        return os.path.abspath(img_path)
    
    # Return the original path (will fail later with better error message)
    return image_path


def copy_image_to_project(image_path: str) -> str:
    """
    Copy an image to the automation_images directory.
    
    Args:
        image_path: Source image path
        
    Returns:
        New path in automation_images directory (relative path for storage)
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
    
    # Return relative path for storage in database
    # This allows the path resolution to work correctly
    return os.path.join("automation_images", new_filename)


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
    # Resolve the image path to absolute path
    resolved_path = resolve_image_path(image_path)
    
    if not os.path.exists(resolved_path):
        print(f"Image file not found: {resolved_path} (original: {image_path})")
        return None
    
    try:
        # Use the resolved absolute path
        location = pyautogui.locateOnScreen(resolved_path, confidence=confidence)
        if location:
            # Get center of the found image
            center = pyautogui.center(location)
            return (center.x, center.y)
    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        print(f"Error finding image '{resolved_path}': {e}")
        return None
    
    return None


def find_image_with_retry(image_path: str, confidence: float = 0.8, 
                          max_retries: int = 3, retry_delay: float = 1.0) -> Optional[Tuple[int, int]]:
    """
    Find an image on screen with retry logic.
    
    Args:
        image_path: Path to the image file (will be resolved to absolute path)
        confidence: Confidence level
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Tuple of (x, y) coordinates if found, None otherwise
    """
    import time
    
    # Resolve path first
    resolved_path = resolve_image_path(image_path)
    
    for attempt in range(max_retries):
        result = find_image_on_screen(resolved_path, confidence)
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
