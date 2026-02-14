"""
Main entry point for the Automation Builder application.
Coordinates GUI, database, and automation engine.
"""

import tkinter as tk
from database import Database
from automation_engine import AutomationEngine
from models import Step
from gui import AutomationBuilderGUI


class AutomationBuilderApp:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.db = Database()
        self.engine = AutomationEngine(
            log_callback=self.on_log,
            status_callback=self.on_status_update,
            step_callback=self.on_step_update
        )
        
        self.gui = AutomationBuilderGUI(
            self.root,
            self.db,
            run_callback=self.run_automation,
            stop_callback=self.stop_automation
        )
    
    def on_log(self, message: str):
        """Handle log messages from automation engine."""
        self.gui.add_log(message)
    
    def on_status_update(self, status: str):
        """Handle status updates from automation engine."""
        self.gui.update_status(status)
    
    def on_step_update(self, step_num: int, step_info: str):
        """Handle step updates from automation engine."""
        self.gui.update_current_step(step_num, step_info)
    
    def run_automation(self, automation_id: int):
        """Run an automation by ID."""
        try:
            # Get steps from database
            steps_data = self.db.get_steps(automation_id)
            if not steps_data:
                self.gui.add_log("ERROR: No steps found for this automation.")
                return
            
            # Convert to Step objects
            steps = [Step.from_dict(step) for step in steps_data]
            
            # Start automation in background thread
            self.engine.start_automation(steps)
            self.gui.add_log(f"INFO: Started automation (ID: {automation_id})")
            
        except Exception as e:
            self.gui.add_log(f"ERROR: Failed to start automation: {str(e)}")
            self.gui.update_status("Error")
            self.gui.set_run_button_state(tk.NORMAL)
            self.gui.set_stop_button_state(tk.DISABLED)
    
    def stop_automation(self):
        """Stop the currently running automation."""
        self.engine.stop_automation()
        self.gui.add_log("INFO: Stop signal sent to automation engine")
    
    def run(self):
        """Start the application main loop."""
        # Check if automation is running periodically
        def check_automation_status():
            if not self.engine.is_automation_running():
                # Automation finished, re-enable run button
                self.gui.set_run_button_state(tk.NORMAL)
                self.gui.set_stop_button_state(tk.DISABLED)
            else:
                # Schedule next check
                self.root.after(500, check_automation_status)
        
        # Start status checking
        self.root.after(500, check_automation_status)
        
        # Start GUI
        self.root.mainloop()


def main():
    """Main entry point."""
    app = AutomationBuilderApp()
    app.run()


if __name__ == "__main__":
    main()
