"""
Database module for managing automations and steps in SQLite.
Handles all database operations including CRUD for automations and steps.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class Database:
    """Manages SQLite database operations for automations and steps."""
    
    def __init__(self, db_path: str = "automations.db"):
        """
        Initialize database connection and create tables if they don't exist.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Create tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create automations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create steps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id INTEGER NOT NULL,
                step_order INTEGER NOT NULL,
                step_type TEXT NOT NULL,
                x INTEGER,
                y INTEGER,
                image_path TEXT,
                text TEXT,
                hotkey TEXT,
                delay_before REAL DEFAULT 0,
                delay_after REAL DEFAULT 0,
                confidence REAL DEFAULT 0.8,
                FOREIGN KEY (automation_id) REFERENCES automations(id) ON DELETE CASCADE,
                UNIQUE(automation_id, step_order)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_automation(self, name: str, description: str = "") -> int:
        """
        Create a new automation.
        
        Args:
            name: Automation name (must be unique)
            description: Optional description
            
        Returns:
            ID of created automation
            
        Raises:
            sqlite3.IntegrityError: If name already exists
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO automations (name, description, created_at)
                VALUES (?, ?, ?)
            """, (name, description, datetime.now().isoformat()))
            
            conn.commit()
            automation_id = cursor.lastrowid
            return automation_id
        finally:
            conn.close()
    
    def get_all_automations(self) -> List[Dict]:
        """Get all automations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, created_at
            FROM automations
            ORDER BY created_at DESC
        """)
        
        automations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return automations
    
    def get_automation(self, automation_id: int) -> Optional[Dict]:
        """Get a single automation by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, created_at
            FROM automations
            WHERE id = ?
        """, (automation_id,))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_automation(self, automation_id: int, name: str, description: str = ""):
        """Update an existing automation."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE automations
            SET name = ?, description = ?
            WHERE id = ?
        """, (name, description, automation_id))
        
        conn.commit()
        conn.close()
    
    def delete_automation(self, automation_id: int):
        """Delete an automation and all its steps (CASCADE)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM automations WHERE id = ?", (automation_id,))
        
        conn.commit()
        conn.close()
    
    def add_step(self, automation_id: int, step_order: int, step_type: str,
                 x: Optional[int] = None, y: Optional[int] = None,
                 image_path: Optional[str] = None, text: Optional[str] = None,
                 hotkey: Optional[str] = None, delay_before: float = 0,
                 delay_after: float = 0, confidence: float = 0.8) -> int:
        """
        Add a step to an automation.
        
        Returns:
            ID of created step
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO steps (
                    automation_id, step_order, step_type, x, y, image_path,
                    text, hotkey, delay_before, delay_after, confidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (automation_id, step_order, step_type, x, y, image_path,
                  text, hotkey, delay_before, delay_after, confidence))
            
            conn.commit()
            step_id = cursor.lastrowid
            return step_id
        finally:
            conn.close()
    
    def get_steps(self, automation_id: int) -> List[Dict]:
        """Get all steps for an automation, ordered by step_order."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, automation_id, step_order, step_type, x, y, image_path,
                   text, hotkey, delay_before, delay_after, confidence
            FROM steps
            WHERE automation_id = ?
            ORDER BY step_order ASC
        """, (automation_id,))
        
        steps = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return steps
    
    def update_step(self, step_id: int, step_type: str,
                   x: Optional[int] = None, y: Optional[int] = None,
                   image_path: Optional[str] = None, text: Optional[str] = None,
                   hotkey: Optional[str] = None, delay_before: float = 0,
                   delay_after: float = 0, confidence: float = 0.8):
        """Update an existing step."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE steps
            SET step_type = ?, x = ?, y = ?, image_path = ?, text = ?,
                hotkey = ?, delay_before = ?, delay_after = ?, confidence = ?
            WHERE id = ?
        """, (step_type, x, y, image_path, text, hotkey,
              delay_before, delay_after, confidence, step_id))
        
        conn.commit()
        conn.close()
    
    def delete_step(self, step_id: int):
        """Delete a step."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM steps WHERE id = ?", (step_id,))
        
        conn.commit()
        conn.close()
    
    def reorder_steps(self, automation_id: int, step_orders: List[Tuple[int, int]]):
        """
        Reorder steps for an automation.
        
        Args:
            automation_id: ID of automation
            step_orders: List of (step_id, new_order) tuples
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use a transaction to update all step orders
        try:
            for step_id, new_order in step_orders:
                cursor.execute("""
                    UPDATE steps
                    SET step_order = ?
                    WHERE id = ? AND automation_id = ?
                """, (new_order, step_id, automation_id))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_max_step_order(self, automation_id: int) -> int:
        """Get the maximum step_order for an automation."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(step_order) as max_order
            FROM steps
            WHERE automation_id = ?
        """, (automation_id,))
        
        row = cursor.fetchone()
        max_order = row['max_order'] if row and row['max_order'] is not None else 0
        conn.close()
        return max_order
