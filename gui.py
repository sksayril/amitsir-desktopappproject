"""
GUI module for the automation builder application.
Provides a professional Tkinter interface with tabs for all features.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional, List, Dict, Callable
from models import Step, StepType
from database import Database
from utils import get_mouse_position, copy_image_to_project, validate_image_file


class AutomationBuilderGUI:
    """Main GUI class for the automation builder application."""
    
    def __init__(self, root: tk.Tk, db: Database, 
                 run_callback: Optional[Callable[[int], None]] = None,
                 stop_callback: Optional[Callable[[], None]] = None):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
            db: Database instance
            run_callback: Callback for running automation (automation_id)
            stop_callback: Callback for stopping automation
        """
        self.root = root
        self.db = db
        self.run_callback = run_callback
        self.stop_callback = stop_callback
        
        self.current_automation_id: Optional[int] = None
        self.steps_data: List[Dict] = []
        self.selected_step_index: Optional[int] = None
        
        self.setup_window()
        self.create_widgets()
        self.refresh_automations_list()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Automation Builder - Desktop Automation Tool")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_tab = ttk.Frame(self.notebook)
        self.manage_tab = ttk.Frame(self.notebook)
        self.run_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.create_tab, text="Create Automation")
        self.notebook.add(self.manage_tab, text="Manage Automations")
        self.notebook.add(self.run_tab, text="Run Automation")
        self.notebook.add(self.logs_tab, text="Logs")
        
        # Build each tab
        self.build_create_tab()
        self.build_manage_tab()
        self.build_run_tab()
        self.build_logs_tab()
    
    def build_create_tab(self):
        """Build the Create Automation tab."""
        # Left panel - Automation info
        left_frame = ttk.LabelFrame(self.create_tab, text="Automation Details", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Automation name
        ttk.Label(left_frame, text="Automation Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.create_name_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.create_name_var, width=30).grid(row=0, column=1, pady=5, padx=5)
        
        # Description
        ttk.Label(left_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.create_desc_text = tk.Text(left_frame, width=30, height=3)
        self.create_desc_text.grid(row=1, column=1, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="New Automation", command=self.new_automation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Automation", command=self.save_automation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Automation", command=self.load_automation_for_edit).pack(side=tk.LEFT, padx=5)
        
        # Right panel - Steps
        right_frame = ttk.LabelFrame(self.create_tab, text="Steps", padding=10)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Steps list with scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.steps_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.steps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.steps_listbox.bind('<<ListboxSelect>>', self.on_step_select)
        scrollbar.config(command=self.steps_listbox.yview)
        
        # Step management buttons
        step_buttons = ttk.Frame(right_frame)
        step_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(step_buttons, text="Add Step", command=self.show_add_step_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(step_buttons, text="Edit Step", command=self.edit_selected_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(step_buttons, text="Delete Step", command=self.delete_selected_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(step_buttons, text="Move Up", command=self.move_step_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(step_buttons, text="Move Down", command=self.move_step_down).pack(side=tk.LEFT, padx=2)
    
    def build_manage_tab(self):
        """Build the Manage Automations tab."""
        # Top frame - List
        list_frame = ttk.LabelFrame(self.manage_tab, text="Automations", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for automations
        columns = ('ID', 'Name', 'Description', 'Created')
        self.manage_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.manage_tree.heading(col, text=col)
            self.manage_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.manage_tree.yview)
        self.manage_tree.configure(yscrollcommand=scrollbar.set)
        
        self.manage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom frame - Actions
        action_frame = ttk.Frame(self.manage_tab)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Refresh", command=self.refresh_automations_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_selected_automation).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="View Steps", command=self.view_automation_steps).pack(side=tk.LEFT, padx=5)
    
    def build_run_tab(self):
        """Build the Run Automation tab."""
        # Selection frame
        select_frame = ttk.LabelFrame(self.run_tab, text="Select Automation", padding=10)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Automation:").pack(side=tk.LEFT, padx=5)
        
        self.run_automation_var = tk.StringVar()
        self.run_automation_combo = ttk.Combobox(select_frame, textvariable=self.run_automation_var, 
                                                  state='readonly', width=40)
        self.run_automation_combo.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.run_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.run_button = ttk.Button(control_frame, text="Start Automation", command=self.start_automation)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Automation", command=self.stop_automation, 
                                       state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.run_tab, text="Status", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 12, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.current_step_label = ttk.Label(status_frame, text="", font=('Arial', 10))
        self.current_step_label.pack(side=tk.LEFT, padx=20)
        
        # Refresh automations for run tab
        self.refresh_run_automations()
    
    def build_logs_tab(self):
        """Build the Logs tab."""
        logs_frame = ttk.LabelFrame(self.logs_tab, text="Execution Logs", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=30, wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear button
        ttk.Button(logs_frame, text="Clear Logs", command=self.clear_logs).pack(pady=5)
    
    # Automation management methods
    def new_automation(self):
        """Create a new automation."""
        self.current_automation_id = None
        self.create_name_var.set("")
        self.create_desc_text.delete(1.0, tk.END)
        self.steps_data = []
        self.refresh_steps_list()
        messagebox.showinfo("New Automation", "New automation created. Add steps and save when ready.")
    
    def save_automation(self):
        """Save the current automation."""
        name = self.create_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter an automation name.")
            return
        
        description = self.create_desc_text.get(1.0, tk.END).strip()
        
        try:
            if self.current_automation_id:
                # Update existing
                self.db.update_automation(self.current_automation_id, name, description)
                automation_id = self.current_automation_id
            else:
                # Create new
                automation_id = self.db.create_automation(name, description)
                self.current_automation_id = automation_id
            
            # Delete existing steps and recreate
            existing_steps = self.db.get_steps(automation_id)
            for step in existing_steps:
                self.db.delete_step(step['id'])
            
            # Save all steps
            for idx, step_data in enumerate(self.steps_data, start=1):
                self.db.add_step(
                    automation_id=automation_id,
                    step_order=idx,
                    step_type=step_data['step_type'],
                    x=step_data.get('x'),
                    y=step_data.get('y'),
                    image_path=step_data.get('image_path'),
                    text=step_data.get('text'),
                    hotkey=step_data.get('hotkey'),
                    delay_before=step_data.get('delay_before', 0),
                    delay_after=step_data.get('delay_after', 0),
                    confidence=step_data.get('confidence', 0.8)
                )
            
            messagebox.showinfo("Success", f"Automation '{name}' saved successfully!")
            self.refresh_automations_list()
            self.refresh_run_automations()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save automation: {str(e)}")
    
    def load_automation_for_edit(self):
        """Load an automation for editing."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Automation")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select automation to load:").pack(pady=10)
        
        automations = self.db.get_all_automations()
        if not automations:
            messagebox.showinfo("Info", "No automations found.")
            dialog.destroy()
            return
        
        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for auto in automations:
            listbox.insert(tk.END, f"{auto['name']} (ID: {auto['id']})")
        
        def load_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Error", "Please select an automation.")
                return
            
            selected_auto = automations[selection[0]]
            self.current_automation_id = selected_auto['id']
            self.create_name_var.set(selected_auto['name'])
            self.create_desc_text.delete(1.0, tk.END)
            self.create_desc_text.insert(1.0, selected_auto.get('description', ''))
            
            # Load steps
            steps = self.db.get_steps(self.current_automation_id)
            self.steps_data = [dict(step) for step in steps]
            self.refresh_steps_list()
            
            dialog.destroy()
            messagebox.showinfo("Loaded", f"Automation '{selected_auto['name']}' loaded.")
        
        ttk.Button(dialog, text="Load", command=load_selected).pack(pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
    
    def refresh_automations_list(self):
        """Refresh the automations list in manage tab."""
        for item in self.manage_tree.get_children():
            self.manage_tree.delete(item)
        
        automations = self.db.get_all_automations()
        for auto in automations:
            self.manage_tree.insert('', tk.END, values=(
                auto['id'],
                auto['name'],
                auto.get('description', '')[:50],
                auto['created_at'][:10] if auto['created_at'] else ''
            ))
    
    def refresh_run_automations(self):
        """Refresh automations in run tab."""
        automations = self.db.get_all_automations()
        names = [f"{auto['name']} (ID: {auto['id']})" for auto in automations]
        self.run_automation_combo['values'] = names
        if names:
            self.run_automation_combo.current(0)
    
    def delete_selected_automation(self):
        """Delete the selected automation."""
        selection = self.manage_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an automation to delete.")
            return
        
        item = self.manage_tree.item(selection[0])
        automation_id = item['values'][0]
        automation_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete automation '{automation_name}'?"):
            try:
                self.db.delete_automation(automation_id)
                self.refresh_automations_list()
                self.refresh_run_automations()
                messagebox.showinfo("Success", "Automation deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def view_automation_steps(self):
        """View steps of selected automation."""
        selection = self.manage_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an automation.")
            return
        
        item = self.manage_tree.item(selection[0])
        automation_id = item['values'][0]
        
        steps = self.db.get_steps(automation_id)
        if not steps:
            messagebox.showinfo("Info", "No steps found for this automation.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Steps - {item['values'][1]}")
        dialog.geometry("600x400")
        
        tree = ttk.Treeview(dialog, columns=('Order', 'Type', 'Details'), show='headings', height=15)
        tree.heading('Order', text='Order')
        tree.heading('Type', text='Type')
        tree.heading('Details', text='Details')
        tree.column('Order', width=50)
        tree.column('Type', width=150)
        tree.column('Details', width=350)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for step in steps:
            details = self._format_step_details(step)
            tree.insert('', tk.END, values=(step['step_order'], step['step_type'], details))
    
    def _format_step_details(self, step: Dict) -> str:
        """Format step details for display."""
        details = []
        if step['step_type'] == 'Mouse Click':
            details.append(f"({step.get('x')}, {step.get('y')})")
        elif step['step_type'] == 'Image-based Click':
            details.append(f"Image: {step.get('image_path', 'N/A')}")
            details.append(f"Confidence: {step.get('confidence', 0.8)}")
        elif step['step_type'] == 'Keyboard Type':
            details.append(f"Text: {step.get('text', 'N/A')}")
        elif step['step_type'] == 'Hotkey':
            details.append(f"Keys: {step.get('hotkey', 'N/A')}")
        elif step['step_type'] == 'Wait / Delay':
            details.append(f"Duration: {step.get('delay_after', 0)}s")
        
        if step.get('delay_before', 0) > 0:
            details.append(f"Delay before: {step.get('delay_before')}s")
        if step.get('delay_after', 0) > 0:
            details.append(f"Delay after: {step.get('delay_after')}s")
        
        return " | ".join(details) if details else "No details"
    
    # Step management methods
    def show_add_step_dialog(self, step_data: Optional[Dict] = None):
        """Show dialog to add or edit a step."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Step" if step_data else "Add Step")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Step type
        ttk.Label(dialog, text="Step Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        step_type_var = tk.StringVar(value=step_data['step_type'] if step_data else "Mouse Click")
        step_type_combo = ttk.Combobox(dialog, textvariable=step_type_var, 
                                       values=[st.value for st in StepType], state='readonly', width=20)
        step_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Delays
        ttk.Label(dialog, text="Delay Before (s):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        delay_before_var = tk.DoubleVar(value=step_data.get('delay_before', 0) if step_data else 0)
        ttk.Spinbox(dialog, from_=0, to=60, increment=0.1, textvariable=delay_before_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Delay After (s):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        delay_after_var = tk.DoubleVar(value=step_data.get('delay_after', 0) if step_data else 0)
        ttk.Spinbox(dialog, from_=0, to=60, increment=0.1, textvariable=delay_after_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        # Dynamic fields frame
        fields_frame = ttk.LabelFrame(dialog, text="Step Parameters", padding=10)
        fields_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Variables for step-specific fields
        x_var = tk.IntVar(value=step_data.get('x', 0) if step_data else 0)
        y_var = tk.IntVar(value=step_data.get('y', 0) if step_data else 0)
        image_path_var = tk.StringVar(value=step_data.get('image_path', '') if step_data else '')
        text_var = tk.StringVar(value=step_data.get('text', '') if step_data else '')
        hotkey_var = tk.StringVar(value=step_data.get('hotkey', '') if step_data else '')
        confidence_var = tk.DoubleVar(value=step_data.get('confidence', 0.8) if step_data else 0.8)
        
        def update_fields(*args):
            """Update visible fields based on step type."""
            for widget in fields_frame.winfo_children():
                widget.destroy()
            
            step_type = step_type_var.get()
            row = 0
            
            if step_type == "Mouse Click":
                ttk.Label(fields_frame, text="X:").grid(row=row, column=0, sticky=tk.W, pady=2)
                ttk.Entry(fields_frame, textvariable=x_var, width=15).grid(row=row, column=1, pady=2, padx=5)
                row += 1
                ttk.Label(fields_frame, text="Y:").grid(row=row, column=0, sticky=tk.W, pady=2)
                ttk.Entry(fields_frame, textvariable=y_var, width=15).grid(row=row, column=1, pady=2, padx=5)
                row += 1
                ttk.Button(fields_frame, text="Capture Current Position", 
                          command=lambda: self.capture_mouse_position(x_var, y_var)).grid(row=row, column=0, columnspan=2, pady=5)
            
            elif step_type == "Image-based Click":
                ttk.Label(fields_frame, text="Image Path:").grid(row=row, column=0, sticky=tk.W, pady=2)
                ttk.Entry(fields_frame, textvariable=image_path_var, width=30).grid(row=row, column=1, pady=2, padx=5)
                row += 1
                ttk.Button(fields_frame, text="Browse Image", 
                          command=lambda: self.browse_image(image_path_var)).grid(row=row, column=0, columnspan=2, pady=5)
                row += 1
                ttk.Label(fields_frame, text="Confidence:").grid(row=row, column=0, sticky=tk.W, pady=2)
                confidence_scale = ttk.Scale(fields_frame, from_=0.5, to=1.0, variable=confidence_var, orient=tk.HORIZONTAL)
                confidence_scale.grid(row=row, column=1, pady=2, padx=5, sticky=tk.W+tk.E)
                row += 1
                ttk.Label(fields_frame, textvariable=confidence_var).grid(row=row, column=1, sticky=tk.W, padx=5)
            
            elif step_type == "Keyboard Type":
                ttk.Label(fields_frame, text="Text to Type:").grid(row=row, column=0, sticky=tk.W, pady=2)
                ttk.Entry(fields_frame, textvariable=text_var, width=30).grid(row=row, column=1, pady=2, padx=5)
            
            elif step_type == "Hotkey":
                ttk.Label(fields_frame, text="Hotkey (e.g., ctrl+c):").grid(row=row, column=0, sticky=tk.W, pady=2)
                ttk.Entry(fields_frame, textvariable=hotkey_var, width=30).grid(row=row, column=1, pady=2, padx=5)
                ttk.Label(fields_frame, text="Format: key1+key2+key3", font=('Arial', 8)).grid(row=row+1, column=1, sticky=tk.W, padx=5)
            
            elif step_type == "Wait / Delay":
                ttk.Label(fields_frame, text="Wait duration is set by 'Delay After' field above.", 
                         font=('Arial', 9, 'italic')).grid(row=row, column=0, columnspan=2, pady=10)
        
        step_type_combo.bind('<<ComboboxSelected>>', update_fields)
        update_fields()  # Initial call
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def save_step():
            step_type = step_type_var.get()
            step_dict = {
                'step_type': step_type,
                'delay_before': delay_before_var.get(),
                'delay_after': delay_after_var.get()
            }
            
            if step_type == "Mouse Click":
                step_dict['x'] = x_var.get()
                step_dict['y'] = y_var.get()
            elif step_type == "Image-based Click":
                if not image_path_var.get():
                    messagebox.showerror("Error", "Please select an image.")
                    return
                step_dict['image_path'] = image_path_var.get()
                step_dict['confidence'] = confidence_var.get()
            elif step_type == "Keyboard Type":
                if not text_var.get():
                    messagebox.showerror("Error", "Please enter text to type.")
                    return
                step_dict['text'] = text_var.get()
            elif step_type == "Hotkey":
                if not hotkey_var.get():
                    messagebox.showerror("Error", "Please enter a hotkey.")
                    return
                step_dict['hotkey'] = hotkey_var.get()
            
            if step_data:
                # Update existing step
                idx = self.selected_step_index
                if idx is not None:
                    self.steps_data[idx] = step_dict
            else:
                # Add new step
                self.steps_data.append(step_dict)
            
            self.refresh_steps_list()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def capture_mouse_position(self, x_var: tk.IntVar, y_var: tk.IntVar):
        """Capture current mouse position."""
        result = messagebox.askokcancel("Capture Position", 
                           "Click OK, then move your mouse to the desired position.\n"
                           "The position will be captured in 3 seconds.")
        if result:
            # Create a countdown dialog
            countdown_dialog = tk.Toplevel(self.root)
            countdown_dialog.title("Capturing Position")
            countdown_dialog.geometry("300x100")
            countdown_dialog.transient(self.root)
            countdown_dialog.grab_set()
            
            countdown_label = ttk.Label(countdown_dialog, text="3", font=('Arial', 20, 'bold'))
            countdown_label.pack(pady=20)
            
            def update_countdown(count):
                if count > 0:
                    countdown_label.config(text=str(count))
                    countdown_dialog.after(1000, lambda: update_countdown(count - 1))
                else:
                    countdown_dialog.destroy()
                    x, y = get_mouse_position()
                    x_var.set(x)
                    y_var.set(y)
                    messagebox.showinfo("Position Captured", f"Position captured: ({x}, {y})")
            
            update_countdown(3)
    
    def browse_image(self, image_path_var: tk.StringVar):
        """Browse for an image file."""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Copy image to project directory
                new_path = copy_image_to_project(filename)
                image_path_var.set(new_path)
                messagebox.showinfo("Success", f"Image copied to: {new_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy image: {str(e)}")
    
    def refresh_steps_list(self):
        """Refresh the steps listbox."""
        self.steps_listbox.delete(0, tk.END)
        for idx, step in enumerate(self.steps_data, start=1):
            step_type = step.get('step_type', 'Unknown')
            details = self._format_step_display(step)
            self.steps_listbox.insert(tk.END, f"{idx}. {step_type} - {details}")
    
    def _format_step_display(self, step: Dict) -> str:
        """Format step for listbox display."""
        step_type = step.get('step_type', '')
        if step_type == 'Mouse Click':
            return f"({step.get('x')}, {step.get('y')})"
        elif step_type == 'Image-based Click':
            img = step.get('image_path', 'N/A')
            return f"{os.path.basename(img) if img else 'N/A'}"
        elif step_type == 'Keyboard Type':
            return f"'{step.get('text', '')}'"
        elif step_type == 'Hotkey':
            return f"{step.get('hotkey', '')}"
        elif step_type == 'Wait / Delay':
            return f"{step.get('delay_after', 0)}s"
        return ""
    
    def on_step_select(self, event):
        """Handle step selection in listbox."""
        selection = self.steps_listbox.curselection()
        if selection:
            self.selected_step_index = selection[0]
    
    def edit_selected_step(self):
        """Edit the selected step."""
        selection = self.steps_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a step to edit.")
            return
        
        idx = selection[0]
        self.selected_step_index = idx
        step_data = self.steps_data[idx]
        self.show_add_step_dialog(step_data)
    
    def delete_selected_step(self):
        """Delete the selected step."""
        selection = self.steps_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a step to delete.")
            return
        
        idx = selection[0]
        if messagebox.askyesno("Confirm", "Delete this step?"):
            del self.steps_data[idx]
            self.refresh_steps_list()
    
    def move_step_up(self):
        """Move selected step up."""
        selection = self.steps_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        self.steps_data[idx], self.steps_data[idx-1] = self.steps_data[idx-1], self.steps_data[idx]
        self.refresh_steps_list()
        self.steps_listbox.selection_set(idx-1)
    
    def move_step_down(self):
        """Move selected step down."""
        selection = self.steps_listbox.curselection()
        if not selection or selection[0] >= len(self.steps_data) - 1:
            return
        
        idx = selection[0]
        self.steps_data[idx], self.steps_data[idx+1] = self.steps_data[idx+1], self.steps_data[idx]
        self.refresh_steps_list()
        self.steps_listbox.selection_set(idx+1)
    
    # Run automation methods
    def start_automation(self):
        """Start running the selected automation."""
        selection = self.run_automation_var.get()
        if not selection:
            messagebox.showerror("Error", "Please select an automation.")
            return
        
        # Extract automation ID from selection
        try:
            automation_id = int(selection.split('(ID: ')[1].split(')')[0])
        except:
            messagebox.showerror("Error", "Invalid automation selection.")
            return
        
        if self.run_callback:
            self.run_callback(automation_id)
        
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
    
    def stop_automation(self):
        """Stop the running automation."""
        if self.stop_callback:
            self.stop_callback()
    
    def set_run_button_state(self, state: str):
        """Set the state of the run button."""
        self.run_button.config(state=state)
    
    def set_stop_button_state(self, state: str):
        """Set the state of the stop button."""
        self.stop_button.config(state=state)
    
    def update_status(self, status: str):
        """Update status label."""
        self.status_label.config(text=status)
    
    def update_current_step(self, step_num: int, step_info: str):
        """Update current step label."""
        self.current_step_label.config(text=f"Current: {step_info}")
    
    # Logging methods
    def add_log(self, message: str):
        """Add a log message."""
        self.logs_text.insert(tk.END, message + "\n")
        self.logs_text.see(tk.END)
    
    def clear_logs(self):
        """Clear all logs."""
        self.logs_text.delete(1.0, tk.END)
