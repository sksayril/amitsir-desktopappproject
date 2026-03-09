"""
Data models for automations and steps.
Provides structured data classes for type safety and clarity.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class StepType(Enum):
    """Enumeration of available step types."""
    MOUSE_CLICK = "Mouse Click"
    IMAGE_CLICK = "Image-based Click"
    KEYBOARD_TYPE = "Keyboard Type"
    HOTKEY = "Hotkey"
    WAIT = "Wait / Delay"


@dataclass
class Automation:
    """Represents an automation workflow."""
    id: int
    name: str
    description: str
    created_at: str
    
    def __str__(self):
        return f"Automation(id={self.id}, name='{self.name}')"


@dataclass
class Step:
    """Represents a single step in an automation."""
    id: int
    automation_id: int
    step_order: int
    step_type: str
    x: Optional[int] = None
    y: Optional[int] = None
    image_path: Optional[str] = None
    text: Optional[str] = None
    hotkey: Optional[str] = None
    key_press: Optional[str] = None
    delay_before: float = 0.0
    delay_after: float = 0.0
    confidence: float = 0.8
    
    def __str__(self):
        return f"Step(id={self.id}, order={self.step_order}, type={self.step_type})"
    
    def to_dict(self) -> dict:
        """Convert step to dictionary for database operations."""
        return {
            'id': self.id,
            'automation_id': self.automation_id,
            'step_order': self.step_order,
            'step_type': self.step_type,
            'x': self.x,
            'y': self.y,
            'image_path': self.image_path,
            'text': self.text,
            'hotkey': self.hotkey,
            'key_press': self.key_press,
            'delay_before': self.delay_before,
            'delay_after': self.delay_after,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Step':
        """Create Step instance from dictionary."""
        return cls(
            id=data['id'],
            automation_id=data['automation_id'],
            step_order=data['step_order'],
            step_type=data['step_type'],
            x=data.get('x'),
            y=data.get('y'),
            image_path=data.get('image_path'),
            text=data.get('text'),
            hotkey=data.get('hotkey'),
            key_press=data.get('key_press'),
            delay_before=data.get('delay_before', 0.0),
            delay_after=data.get('delay_after', 0.0),
            confidence=data.get('confidence', 0.8)
        )
