"""
GUI module for the automation builder application.
Provides a professional Tkinter interface with tabs for all features.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional, List, Dict, Callable
from datetime import datetime, timedelta
import time
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
        
        # Timer and auto-run variables
        self.automation_start_time: Optional[float] = None
        self.automation_duration: float = 0.0
        self.auto_run_enabled: bool = False
        self.auto_run_interval: int = 5  # minutes
        self.auto_run_timer_id: Optional[str] = None
        self.auto_run_automation_id: Optional[int] = None
        
        self.setup_window()
        self.create_widgets()
        self.refresh_automations_list()
        self.start_timer_update()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("🚀 Automation Builder - Desktop Automation Tool")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#2C3E50',
            'bg_secondary': '#34495E',
            'bg_light': '#ECF0F1',
            'accent': '#3498DB',
            'accent_hover': '#2980B9',
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'border': '#BDC3C7'
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg_light'])
        
        # Style configuration with modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 16, 'bold'),
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Heading.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        
        style.configure('Success.TButton',
                       font=('Segoe UI', 10),
                       padding=8)
        
        style.configure('Danger.TButton',
                       font=('Segoe UI', 10),
                       padding=8)
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['accent_hover']),
                            ('!active', self.colors['accent'])])
        
        # Configure notebook (tabs) style
        style.configure('TNotebook',
                       background=self.colors['bg_light'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'),
                       background=self.colors['bg_secondary'],
                       foreground='white')
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent']),
                            ('active', self.colors['bg_secondary'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # Configure frame styles
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=1)
        
        style.configure('TLabelFrame',
                       font=('Segoe UI', 10, 'bold'),
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       relief='flat')
        
        style.configure('TLabelFrame.Label',
                       font=('Segoe UI', 10, 'bold'),
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'])
    
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
        # Main container
        main_container = tk.Frame(self.create_tab, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Automation info
        left_frame = ttk.LabelFrame(main_container, text="📝 Automation Details", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=5)
        
        left_inner = tk.Frame(left_frame, bg='white')
        left_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Automation name
        ttk.Label(left_inner, text="Automation Name:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=10, padx=10)
        self.create_name_var = tk.StringVar()
        name_entry = ttk.Entry(left_inner, textvariable=self.create_name_var, width=35, font=('Segoe UI', 10))
        name_entry.grid(row=0, column=1, pady=10, padx=10, sticky=tk.W+tk.E)
        
        # Description
        ttk.Label(left_inner, text="Description:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W+tk.N, pady=10, padx=10)
        self.create_desc_text = tk.Text(left_inner, width=35, height=5, font=('Segoe UI', 10), wrap=tk.WORD)
        self.create_desc_text.grid(row=1, column=1, pady=10, padx=10, sticky=tk.W+tk.E)
        
        left_inner.columnconfigure(1, weight=1)
        
        # Buttons with modern styling
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        btn_new = tk.Button(button_frame, text="🆕 New Automation", command=self.new_automation,
                           bg=self.colors['accent'], fg='white', font=('Segoe UI', 10, 'bold'),
                           padx=15, pady=10, relief='flat', cursor='hand2',
                           activebackground=self.colors['accent_hover'], activeforeground='white')
        btn_new.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        btn_save = tk.Button(button_frame, text="💾 Save Automation", command=self.save_automation,
                            bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                            padx=15, pady=10, relief='flat', cursor='hand2',
                            activebackground='#229954', activeforeground='white')
        btn_save.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        btn_load = tk.Button(button_frame, text="📂 Load Automation", command=self.load_automation_for_edit,
                            bg=self.colors['warning'], fg='white', font=('Segoe UI', 10, 'bold'),
                            padx=15, pady=10, relief='flat', cursor='hand2',
                            activebackground='#D68910', activeforeground='white')
        btn_load.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Right panel - Steps
        right_frame = ttk.LabelFrame(main_container, text="📋 Steps", padding=15)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        # Steps list with scrollbar
        list_frame = tk.Frame(right_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.steps_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                        height=20, font=('Segoe UI', 10),
                                        bg='white', fg=self.colors['text_primary'],
                                        selectbackground=self.colors['accent'],
                                        selectforeground='white',
                                        relief='flat', borderwidth=1)
        self.steps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.steps_listbox.bind('<<ListboxSelect>>', self.on_step_select)
        scrollbar.config(command=self.steps_listbox.yview)
        
        # Step management buttons with modern styling
        step_buttons = tk.Frame(right_frame, bg='white')
        step_buttons.pack(fill=tk.X, pady=5, padx=5)
        
        btn_add = tk.Button(step_buttons, text="➕ Add Step", command=self.show_add_step_dialog,
                           bg=self.colors['success'], fg='white', font=('Segoe UI', 9, 'bold'),
                           padx=12, pady=8, relief='flat', cursor='hand2',
                           activebackground='#229954', activeforeground='white')
        btn_add.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        btn_edit = tk.Button(step_buttons, text="✏️ Edit", command=self.edit_selected_step,
                            bg=self.colors['accent'], fg='white', font=('Segoe UI', 9, 'bold'),
                            padx=12, pady=8, relief='flat', cursor='hand2',
                            activebackground=self.colors['accent_hover'], activeforeground='white')
        btn_edit.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        btn_delete = tk.Button(step_buttons, text="🗑️ Delete", command=self.delete_selected_step,
                              bg=self.colors['danger'], fg='white', font=('Segoe UI', 9, 'bold'),
                              padx=12, pady=8, relief='flat', cursor='hand2',
                              activebackground='#C0392B', activeforeground='white')
        btn_delete.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        btn_up = tk.Button(step_buttons, text="⬆️ Up", command=self.move_step_up,
                          bg=self.colors['warning'], fg='white', font=('Segoe UI', 9, 'bold'),
                          padx=12, pady=8, relief='flat', cursor='hand2',
                          activebackground='#D68910', activeforeground='white')
        btn_up.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        btn_down = tk.Button(step_buttons, text="⬇️ Down", command=self.move_step_down,
                            bg=self.colors['warning'], fg='white', font=('Segoe UI', 9, 'bold'),
                            padx=12, pady=8, relief='flat', cursor='hand2',
                            activebackground='#D68910', activeforeground='white')
        btn_down.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
    
    def build_manage_tab(self):
        """Build the Manage Automations tab."""
        main_container = tk.Frame(self.manage_tab, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame - List
        list_frame = ttk.LabelFrame(main_container, text="📋 Automations", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        list_inner = tk.Frame(list_frame, bg='white')
        list_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for automations
        columns = ('ID', 'Name', 'Description', 'Created')
        self.manage_tree = ttk.Treeview(list_inner, columns=columns, show='headings', height=18)
        
        for col in columns:
            self.manage_tree.heading(col, text=col)
            self.manage_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_inner, orient=tk.VERTICAL, command=self.manage_tree.yview)
        self.manage_tree.configure(yscrollcommand=scrollbar.set)
        
        self.manage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom frame - Actions with modern buttons
        action_frame = tk.Frame(main_container, bg=self.colors['bg_light'])
        action_frame.pack(fill=tk.X)
        
        btn_refresh = tk.Button(action_frame, text="🔄 Refresh", command=self.refresh_automations_list,
                               bg=self.colors['accent'], fg='white', font=('Segoe UI', 10, 'bold'),
                               padx=20, pady=10, relief='flat', cursor='hand2',
                               activebackground=self.colors['accent_hover'], activeforeground='white')
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_delete = tk.Button(action_frame, text="🗑️ Delete Selected", command=self.delete_selected_automation,
                              bg=self.colors['danger'], fg='white', font=('Segoe UI', 10, 'bold'),
                              padx=20, pady=10, relief='flat', cursor='hand2',
                              activebackground='#C0392B', activeforeground='white')
        btn_delete.pack(side=tk.LEFT, padx=5)
        
        btn_view = tk.Button(action_frame, text="👁️ View Steps", command=self.view_automation_steps,
                            bg=self.colors['warning'], fg='white', font=('Segoe UI', 10, 'bold'),
                            padx=20, pady=10, relief='flat', cursor='hand2',
                            activebackground='#D68910', activeforeground='white')
        btn_view.pack(side=tk.LEFT, padx=5)
    
    def build_run_tab(self):
        """Build the Run Automation tab."""
        # Main container with padding
        main_container = tk.Frame(self.run_tab, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Selection frame with modern styling
        select_frame = ttk.LabelFrame(main_container, text="📋 Select Automation", padding=15)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        select_inner = tk.Frame(select_frame, bg='white')
        select_inner.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(select_inner, text="Automation:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.run_automation_var = tk.StringVar()
        self.run_automation_combo = ttk.Combobox(select_inner, textvariable=self.run_automation_var, 
                                                  state='readonly', width=45, font=('Segoe UI', 10))
        self.run_automation_combo.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Control buttons with modern styling
        control_frame = ttk.LabelFrame(main_container, text="🎮 Controls", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_container = tk.Frame(control_frame, bg='white')
        button_container.pack(fill=tk.X, padx=5, pady=5)
        
        self.run_button = tk.Button(button_container, text="▶️ Start Automation", 
                                    command=self.start_automation,
                                    bg=self.colors['success'],
                                    fg='white',
                                    font=('Segoe UI', 11, 'bold'),
                                    padx=20, pady=12,
                                    relief='flat',
                                    cursor='hand2',
                                    activebackground=self.colors['success'],
                                    activeforeground='white')
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_container, text="⏹️ Stop Automation", 
                                     command=self.stop_automation,
                                     bg=self.colors['danger'],
                                     fg='white',
                                     font=('Segoe UI', 11, 'bold'),
                                     padx=20, pady=12,
                                     relief='flat',
                                     cursor='hand2',
                                     state=tk.DISABLED,
                                     activebackground=self.colors['danger'],
                                     activeforeground='white')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(button_container, text="⏸️ Pause", 
                                      command=self.pause_automation,
                                      bg=self.colors['warning'],
                                      fg='white',
                                      font=('Segoe UI', 11, 'bold'),
                                      padx=20, pady=12,
                                      relief='flat',
                                      cursor='hand2',
                                      state=tk.DISABLED,
                                      activebackground=self.colors['warning'],
                                      activeforeground='white')
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar frame
        progress_frame = ttk.LabelFrame(main_container, text="📊 Progress", padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        progress_inner = tk.Frame(progress_frame, bg='white')
        progress_inner.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_inner, variable=self.progress_var, 
                                           maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        self.progress_label = ttk.Label(progress_inner, text="0%", font=('Segoe UI', 10, 'bold'))
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # Status frame with enhanced display
        status_frame = ttk.LabelFrame(main_container, text="📈 Status & Timing", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_inner = tk.Frame(status_frame, bg='white')
        status_inner.pack(fill=tk.X, padx=5, pady=5)
        
        # Status display
        status_left = tk.Frame(status_inner, bg='white')
        status_left.pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Label(status_left, text="Status:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        self.status_label = tk.Label(status_left, text="🟢 Ready", 
                                     font=('Segoe UI', 14, 'bold'),
                                     bg='white',
                                     fg=self.colors['success'])
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Current step display
        ttk.Label(status_left, text="Current Step:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        self.current_step_label = tk.Label(status_left, text="No step running", 
                                           font=('Segoe UI', 10),
                                           bg='white',
                                           fg=self.colors['text_secondary'])
        self.current_step_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Timer display
        status_right = tk.Frame(status_inner, bg='white')
        status_right.pack(side=tk.LEFT, padx=30, pady=10)
        
        ttk.Label(status_right, text="⏱️ Duration:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        self.duration_label = tk.Label(status_right, text="00:00:00", 
                                       font=('Segoe UI', 16, 'bold'),
                                       bg='white',
                                       fg=self.colors['accent'])
        self.duration_label.pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Label(status_right, text="Estimated Time:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        self.estimated_time_label = tk.Label(status_right, text="Calculating...", 
                                             font=('Segoe UI', 10),
                                             bg='white',
                                             fg=self.colors['text_secondary'])
        self.estimated_time_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Auto-run frame
        autorun_frame = ttk.LabelFrame(main_container, text="🔄 Auto-Run Scheduler", padding=15)
        autorun_frame.pack(fill=tk.X, pady=(0, 10))
        
        autorun_inner = tk.Frame(autorun_frame, bg='white')
        autorun_inner.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(autorun_inner, text="Run every:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        
        self.autorun_interval_var = tk.IntVar(value=5)
        interval_spin = ttk.Spinbox(autorun_inner, from_=1, to=60, 
                                    textvariable=self.autorun_interval_var,
                                    width=10, font=('Segoe UI', 10))
        interval_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(autorun_inner, text="minutes", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        
        self.autorun_button = tk.Button(autorun_inner, text="▶️ Enable Auto-Run", 
                                       command=self.toggle_auto_run,
                                       bg=self.colors['accent'],
                                       fg='white',
                                       font=('Segoe UI', 10, 'bold'),
                                       padx=15, pady=8,
                                       relief='flat',
                                       cursor='hand2',
                                       activebackground=self.colors['accent_hover'],
                                       activeforeground='white')
        self.autorun_button.pack(side=tk.LEFT, padx=10)
        
        self.autorun_status_label = tk.Label(autorun_inner, text="⏸️ Auto-Run: Disabled", 
                                            font=('Segoe UI', 10),
                                            bg='white',
                                            fg=self.colors['text_secondary'])
        self.autorun_status_label.pack(side=tk.LEFT, padx=10)
        
        # Refresh automations for run tab
        self.refresh_run_automations()
    
    def build_logs_tab(self):
        """Build the Logs tab."""
        main_container = tk.Frame(self.logs_tab, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        logs_frame = ttk.LabelFrame(main_container, text="📜 Execution Logs", padding=15)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        logs_inner = tk.Frame(logs_frame, bg='white')
        logs_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(logs_inner, height=35, wrap=tk.WORD,
                                                    font=('Consolas', 9),
                                                    bg='#1E1E1E', fg='#D4D4D4',
                                                    insertbackground='white')
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear button with modern styling
        btn_clear = tk.Button(logs_inner, text="🗑️ Clear Logs", command=self.clear_logs,
                             bg=self.colors['danger'], fg='white', font=('Segoe UI', 10, 'bold'),
                             padx=20, pady=10, relief='flat', cursor='hand2',
                             activebackground='#C0392B', activeforeground='white')
        btn_clear.pack(pady=10)
    
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
                    key_press=step_data.get('key_press'),
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
            img_path = step.get('image_path', 'N/A')
            # Show just the filename for cleaner display
            if img_path and img_path != 'N/A':
                img_name = os.path.basename(img_path)
                details.append(f"Image: {img_name}")
            else:
                details.append(f"Image: {img_path}")
            details.append(f"Confidence: {step.get('confidence', 0.8)}")
        elif step['step_type'] == 'Keyboard Type':
            if step.get('key_press'):
                details.append(f"Press Key: {step.get('key_press', 'N/A').upper()}")
            else:
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
        dialog.geometry("550x650")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configure dialog background
        dialog.configure(bg=self.colors['bg_light'])
        
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
        fields_frame = ttk.LabelFrame(dialog, text="Step Parameters", padding=15)
        fields_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        
        # Configure column weights for responsive layout
        dialog.columnconfigure(1, weight=1)
        fields_frame.columnconfigure(1, weight=1)
        
        # Variables for step-specific fields
        x_var = tk.IntVar(value=step_data.get('x', 0) if step_data else 0)
        y_var = tk.IntVar(value=step_data.get('y', 0) if step_data else 0)
        image_path_var = tk.StringVar(value=step_data.get('image_path', '') if step_data else '')
        text_var = tk.StringVar(value=step_data.get('text', '') if step_data else '')
        hotkey_var = tk.StringVar(value=step_data.get('hotkey', '') if step_data else '')
        confidence_var = tk.DoubleVar(value=step_data.get('confidence', 0.8) if step_data else 0.8)
        key_var = tk.StringVar(value=step_data.get('key_press', '') if step_data else '')
        
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
                # Determine initial mode based on existing data
                initial_mode = 'key' if (step_data and step_data.get('key_press')) else 'type'
                if step_data and step_data.get('text') and not step_data.get('key_press'):
                    initial_mode = 'type'
                
                # Mode selection (Type Text or Press Key)
                mode_var = tk.StringVar(value=initial_mode)
                
                mode_frame = tk.Frame(fields_frame, bg='white')
                mode_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
                
                ttk.Label(mode_frame, text="Mode:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=5)
                ttk.Radiobutton(mode_frame, text="Type Text", variable=mode_var, value='type',
                               command=lambda: self.update_keyboard_mode(fields_frame, mode_var)).pack(side=tk.LEFT, padx=10)
                ttk.Radiobutton(mode_frame, text="Press Key", variable=mode_var, value='key',
                               command=lambda: self.update_keyboard_mode(fields_frame, mode_var)).pack(side=tk.LEFT, padx=10)
                
                row += 1
                
                # Text input frame (shown when mode is 'type')
                text_frame = tk.Frame(fields_frame, bg='white')
                text_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
                
                ttk.Label(text_frame, text="Text to Type:").pack(side=tk.LEFT, padx=5)
                text_entry = ttk.Entry(text_frame, textvariable=text_var, width=30)
                text_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                
                row += 1
                
                # Key selection frame (shown when mode is 'key')
                key_frame = tk.Frame(fields_frame, bg='white')
                key_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
                
                ttk.Label(key_frame, text="Key to Press:").pack(side=tk.LEFT, padx=5)
                key_display = ttk.Entry(key_frame, textvariable=key_var, width=20, state='readonly')
                key_display.pack(side=tk.LEFT, padx=5)
                
                key_btn = tk.Button(key_frame, text="⌨️ Select Key", 
                                   command=lambda: self.capture_key_press(key_var, dialog),
                                   bg=self.colors['accent'], fg='white',
                                   font=('Segoe UI', 9, 'bold'),
                                   padx=15, pady=5, relief='flat', cursor='hand2',
                                   activebackground=self.colors['accent_hover'], activeforeground='white')
                key_btn.pack(side=tk.LEFT, padx=5)
                
                # Store references for later use
                fields_frame.mode_var = mode_var
                fields_frame.key_var = key_var
                fields_frame.text_var = text_var
                fields_frame.text_frame = text_frame
                fields_frame.key_frame = key_frame
                
                # Initial mode update
                self.update_keyboard_mode(fields_frame, mode_var)
            
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
                # Get mode from fields_frame
                mode = getattr(fields_frame, 'mode_var', None)
                if mode:
                    mode_value = mode.get()
                    if mode_value == 'key':
                        # Press key mode
                        if not key_var.get():
                            messagebox.showerror("Error", "Please select a key to press.")
                            return
                        step_dict['key_press'] = key_var.get()
                        step_dict['text'] = None  # Clear text when using key press
                    else:
                        # Type text mode
                        if not text_var.get():
                            messagebox.showerror("Error", "Please enter text to type.")
                            return
                        step_dict['text'] = text_var.get()
                        step_dict['key_press'] = None  # Clear key when using text
                else:
                    # Fallback to text mode for backward compatibility
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
    
    def update_keyboard_mode(self, fields_frame, mode_var):
        """Update the keyboard mode UI (show/hide text or key fields)."""
        mode = mode_var.get()
        text_frame = getattr(fields_frame, 'text_frame', None)
        key_frame = getattr(fields_frame, 'key_frame', None)
        
        if mode == 'type':
            # Show text input, hide key selection
            if text_frame:
                text_frame.grid()
            if key_frame:
                key_frame.grid_remove()
        else:  # mode == 'key'
            # Show key selection, hide text input
            if text_frame:
                text_frame.grid_remove()
            if key_frame:
                key_frame.grid()
    
    def capture_key_press(self, key_var: tk.StringVar, parent_dialog):
        """Capture a key press from the user."""
        capture_dialog = tk.Toplevel(parent_dialog)
        capture_dialog.title("Press a Key")
        capture_dialog.geometry("400x200")
        capture_dialog.transient(parent_dialog)
        capture_dialog.grab_set()
        
        # Center the dialog
        capture_dialog.update_idletasks()
        x = (capture_dialog.winfo_screenwidth() // 2) - (capture_dialog.winfo_width() // 2)
        y = (capture_dialog.winfo_screenheight() // 2) - (capture_dialog.winfo_height() // 2)
        capture_dialog.geometry(f"+{x}+{y}")
        
        info_label = tk.Label(capture_dialog, 
                             text="Press any key on your keyboard...",
                             font=('Segoe UI', 12, 'bold'),
                             pady=20)
        info_label.pack(pady=20)
        
        key_display = tk.Label(capture_dialog, 
                              text="Waiting for key...",
                              font=('Segoe UI', 14),
                              fg=self.colors['accent'],
                              pady=10)
        key_display.pack(pady=10)
        
        captured_key = [None]  # Use list to allow modification in nested function
        
        def on_key_press(event):
            """Handle key press event."""
            key_name = event.keysym
            # Map common key names to pyautogui format
            key_mapping = {
                'Return': 'enter',
                'space': 'space',
                'Tab': 'tab',
                'Escape': 'esc',
                'BackSpace': 'backspace',
                'Delete': 'delete',
                'Up': 'up',
                'Down': 'down',
                'Left': 'left',
                'Right': 'right',
                'Home': 'home',
                'End': 'end',
                'Page_Up': 'pageup',
                'Page_Down': 'pagedown',
                'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4',
                'F5': 'f5', 'F6': 'f6', 'F7': 'f7', 'F8': 'f8',
                'F9': 'f9', 'F10': 'f10', 'F11': 'f11', 'F12': 'f12',
            }
            
            # Use mapped name or lowercase the key name
            mapped_key = key_mapping.get(key_name, key_name.lower())
            captured_key[0] = mapped_key
            
            # Update display
            display_name = key_name.replace('_', ' ').title()
            key_display.config(text=f"Key captured: {display_name}", fg=self.colors['success'])
            
            # Close dialog after short delay
            capture_dialog.after(500, lambda: finish_capture())
        
        def finish_capture():
            """Finish key capture and close dialog."""
            if captured_key[0]:
                key_var.set(captured_key[0])
                capture_dialog.destroy()
            else:
                messagebox.showwarning("No Key", "No key was captured. Please try again.")
        
        # Bind key press event
        capture_dialog.bind('<KeyPress>', on_key_press)
        capture_dialog.focus_set()
        
        # Cancel button
        cancel_btn = tk.Button(capture_dialog, text="Cancel", 
                              command=capture_dialog.destroy,
                              bg=self.colors['danger'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              padx=20, pady=10, relief='flat', cursor='hand2',
                              activebackground='#C0392B', activeforeground='white')
        cancel_btn.pack(pady=20)
    
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
            if step.get('key_press'):
                return f"Press: {step.get('key_press', '').upper()}"
            else:
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
        
        # Get total steps for progress calculation
        steps = self.db.get_steps(automation_id)
        self.total_steps = len(steps) if steps else 0
        
        # Calculate estimated time based on delays
        estimated_seconds = 0
        if steps:
            for step in steps:
                estimated_seconds += step.get('delay_before', 0) or 0
                estimated_seconds += step.get('delay_after', 0) or 0
                # Add base time for each step (1 second)
                estimated_seconds += 1
        
        if estimated_seconds > 0:
            hours = int(estimated_seconds // 3600)
            minutes = int((estimated_seconds % 3600) // 60)
            seconds = int(estimated_seconds % 60)
            self.estimated_time_label.config(
                text=f"Estimated: {hours:02d}:{minutes:02d}:{seconds:02d}",
                fg=self.colors['accent']
            )
        else:
            self.estimated_time_label.config(text="Estimated: Calculating...", fg=self.colors['text_secondary'])
        
        # Reset progress
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.automation_start_time = time.time()
        self.automation_duration = 0.0
        
        if self.run_callback:
            self.run_callback(automation_id)
        
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
    
    def stop_automation(self):
        """Stop the running automation."""
        if self.stop_callback:
            self.stop_callback()
    
    def set_run_button_state(self, state: str):
        """Set the state of the run button."""
        self.run_button.config(state=state)
        if state == tk.NORMAL:
            if hasattr(self, 'pause_button'):
                self.pause_button.config(state=tk.DISABLED)
            # Update estimated time
            if self.automation_duration > 0:
                hours = int(self.automation_duration // 3600)
                minutes = int((self.automation_duration % 3600) // 60)
                seconds = int(self.automation_duration % 60)
                self.estimated_time_label.config(
                    text=f"Last run: {hours:02d}:{minutes:02d}:{seconds:02d}",
                    fg=self.colors['success']
                )
    
    def set_stop_button_state(self, state: str):
        """Set the state of the stop button."""
        self.stop_button.config(state=state)
    
    def update_status(self, status: str):
        """Update status label with visual indicators."""
        status_icons = {
            'Ready': '🟢',
            'Running': '🟡',
            'Completed': '✅',
            'Stopped': '⏹️',
            'Error': '❌',
            'Paused': '⏸️'
        }
        icon = status_icons.get(status, '⚪')
        self.status_label.config(text=f"{icon} {status}")
        
        # Update color based on status
        color_map = {
            'Ready': self.colors['success'],
            'Running': self.colors['warning'],
            'Completed': self.colors['success'],
            'Stopped': self.colors['danger'],
            'Error': self.colors['danger'],
            'Paused': self.colors['warning']
        }
        self.status_label.config(fg=color_map.get(status, self.colors['text_primary']))
        
        # Start timer when automation starts
        if status == 'Running' and self.automation_start_time is None:
            self.automation_start_time = time.time()
        # Stop timer when automation ends
        elif status in ['Completed', 'Stopped', 'Error']:
            if self.automation_start_time:
                self.automation_duration = time.time() - self.automation_start_time
                self.automation_start_time = None
            # Reschedule auto-run if enabled
            if self.auto_run_enabled:
                self.schedule_next_auto_run()
    
    def update_current_step(self, step_num: int, step_info: str):
        """Update current step label."""
        self.current_step_label.config(text=f"Step {step_num}: {step_info}")
        
        # Update progress bar if we have total steps info
        if hasattr(self, 'total_steps') and self.total_steps > 0:
            progress = (step_num / self.total_steps) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{int(progress)}%")
    
    def start_timer_update(self):
        """Start the timer update loop."""
        def update_loop():
            self.update_timer()
            self.root.after(100, update_loop)
        update_loop()
    
    def update_timer(self):
        """Update the duration timer display."""
        if self.automation_start_time:
            elapsed = time.time() - self.automation_start_time
            self.automation_duration = elapsed
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.duration_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            if self.automation_duration > 0:
                hours = int(self.automation_duration // 3600)
                minutes = int((self.automation_duration % 3600) // 60)
                seconds = int(self.automation_duration % 60)
                self.duration_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.duration_label.config(text="00:00:00")
    
    def toggle_auto_run(self):
        """Toggle auto-run functionality."""
        if self.auto_run_enabled:
            # Disable auto-runtabtabtabenter
            self.auto_run_enabled = False
            if self.auto_run_timer_id:
                self.root.after_cancel(self.auto_run_timer_id)
                self.auto_run_timer_id = None
            self.autorun_button.config(text="▶️ Enable Auto-Run", bg=self.colors['accent'])
            self.autorun_status_label.config(text="⏸️ Auto-Run: Disabled", fg=self.colors['text_secondary'])
        else:
            # Enable auto-run
            selection = self.run_automation_var.get()
            if not selection:
                messagebox.showerror("Error", "Please select an automation first.")
                return
            
            try:
                automation_id = int(selection.split('(ID: ')[1].split(')')[0])
                self.auto_run_automation_id = automation_id
                self.auto_run_interval = self.autorun_interval_var.get()
                self.auto_run_enabled = True
                
                self.autorun_button.config(text="⏸️ Disable Auto-Run", bg=self.colors['danger'])
                self.autorun_status_label.config(
                    text=f"🔄 Auto-Run: Enabled (every {self.auto_run_interval} min)",
                    fg=self.colors['success']
                )
                
                # Schedule first run
                self.schedule_next_auto_run()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to enable auto-run: {str(e)}")
    
    def schedule_next_auto_run(self):
        """Schedule the next auto-run."""
        if not self.auto_run_enabled:
            return
        
        # Check if automation is currently running
        if hasattr(self, 'status_label'):
            status_text = self.status_label.cget('text')
            if 'Running' in status_text or '🟡' in status_text:
                # Check again in 5 seconds
                self.auto_run_timer_id = self.root.after(5000, self.schedule_next_auto_run)
                return
        
        # Convert minutes to milliseconds
        interval_ms = self.auto_run_interval * 60 * 1000
        
        # Schedule the run
        self.auto_run_timer_id = self.root.after(interval_ms, self.execute_auto_run)
        
        # Update status with next run time
        next_run_time = datetime.now() + timedelta(minutes=self.auto_run_interval)
        self.autorun_status_label.config(
            text=f"🔄 Auto-Run: Next run at {next_run_time.strftime('%H:%M:%S')}",
            fg=self.colors['success']
        )
    
    def execute_auto_run(self):
        """Execute the scheduled auto-run."""
        if not self.auto_run_enabled or not self.auto_run_automation_id:
            return
        
        # Check if automation is already running
        if hasattr(self, 'status_label'):
            status_text = self.status_label.cget('text')
            if 'Running' in status_text or '🟡' in status_text:
                # Reschedule for later
                self.schedule_next_auto_run()
                return
        
        # Run the automation
        if self.run_callback:
            self.add_log(f"INFO: Auto-run triggered for automation ID: {self.auto_run_automation_id}")
            self.run_callback(self.auto_run_automation_id)
            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
        
        # Schedule next run (will be called after automation completes)
        # We'll reschedule in the status update when automation completes
    
    def pause_automation(self):
        """Pause the currently running automation."""
        # This is a placeholder - actual pause functionality would need engine support
        messagebox.showinfo("Pause", "Pause functionality will be implemented in the automation engine.")
    
    # Logging methods
    def add_log(self, message: str):
        """Add a log message."""
        self.logs_text.insert(tk.END, message + "\n")
        self.logs_text.see(tk.END)
    
    def clear_logs(self):
        """Clear all logs."""
        self.logs_text.delete(1.0, tk.END)
