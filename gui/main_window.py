"""
Main Window GUI Module
Contains the main application window and user interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_loader import DataLoader, DataFilter
from plotting.plot_manager import PlotManager
from gui.data_selection_panel import DataSelectionPanel
from gui.time_range_selector import TimeRangeSelector

class DroneLogAnalyzer:
    """Main application class with modern styling"""
    
    # Modern color scheme
    COLORS = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8fafc',
        'bg_tertiary': '#f1f5f9',
        'accent': '#3b82f6',
        'accent_hover': '#2563eb',
        'text_primary': '#1e293b',
        'text_secondary': '#64748b',
        'border': '#e2e8f0',
        'border_light': '#f1f5f9',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444'
    }
    
    def __init__(self, root):
        self.root = root
        
        # Configure modern styling
        self.setup_modern_theme()
        
        # Initialize data components
        self.data_loader = DataLoader()
        self.data_filter = DataFilter()
        
        # Data storage
        self.sessions = {}
        self.current_session = None
        self.session_data = {}
        self.selected_data_vars = {}
        
        # Initialize control variables
        self.folder_var = tk.StringVar()
        self.session_var = tk.StringVar()
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        
        # Status variables
        self.status_var = tk.StringVar()
        self.session_info_var = tk.StringVar()
        
        # GUI components
        self.data_panel = None
        self.plot_manager = None
        self.canvas = None
        self.time_selector = None
        self.session_combo = None
        self.folder_entry = None
        
        # Create a simple proxy object for compatibility with any code expecting control_panel
        class ControlPanelProxy:
            def __init__(self, main_window):
                self.main_window = main_window
            
            def set_folder_path(self, path):
                self.main_window.set_folder_path(path)
            
            def get_folder_path(self):
                return self.main_window.get_folder_path()
            
            def set_sessions(self, sessions):
                self.main_window.set_sessions(sessions)
            
            def set_current_session(self, session):
                self.main_window.set_current_session(session)
            
            def get_current_session(self):
                return self.main_window.get_current_session()
            
            def set_time_range_hint(self, start_time, end_time):
                if hasattr(self.main_window, 'time_selector') and self.main_window.time_selector:
                    self.main_window.time_selector.set_time_range(start_time, end_time)
            
            def get_time_filter(self):
                return self.main_window.get_time_filter()
            
            def reset_time_filter(self):
                self.main_window.reset_time_filter()
        
        self.control_panel = ControlPanelProxy(self)
        
        # Create GUI
        self.create_gui()
        
        # Load default folder if exists
        if os.path.exists("drone_logs"):
            try:
                self.load_sessions("drone_logs")
            except Exception as e:
                print(f"Error loading default drone_logs folder: {e}")
                # Don't fail initialization if default folder has issues
                pass
    
    def setup_modern_theme(self):
        """Configure modern theme for the application"""
        # Configure root window with modern styling
        self.root.configure(bg=self.COLORS['bg_secondary'])
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure frame styles
        style.configure('Card.TFrame', 
                       background=self.COLORS['bg_primary'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('CardHeader.TLabelframe', 
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_primary'],
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('CardHeader.TLabelframe.Label',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure button styles
        style.configure('Modern.TButton',
                       background=self.COLORS['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       font=('Segoe UI', 9),
                       padding=(16, 8))
        
        style.map('Modern.TButton',
                 background=[('active', self.COLORS['accent_hover']),
                           ('pressed', self.COLORS['accent_hover'])])
        
        style.configure('Secondary.TButton',
                       background=self.COLORS['bg_tertiary'],
                       foreground=self.COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       font=('Segoe UI', 9),
                       padding=(12, 6))
        
        # Configure entry and combobox styles
        style.configure('Modern.TEntry',
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.COLORS['border'],
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.configure('Modern.TCombobox',
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.COLORS['border'],
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        # Configure label styles
        style.configure('Modern.TLabel',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 9))
        
        style.configure('Heading.TLabel',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Secondary.TLabel',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_secondary'],
                       font=('Segoe UI', 8))
    
    def create_gui(self):
        """Create the main GUI layout with optimal positioning"""
        # Create main container with modern spacing - more compact
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_secondary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Reduced from 15
        
        # Create header section - more compact
        self.create_header(main_frame)
        
        # Create top control bar (session + time controls in one row)
        self.create_top_control_bar(main_frame)
        
        # Create main content area with optimal layout
        content_frame = tk.Frame(main_frame, bg=self.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))  # Reduced padding
        
        # Create left sidebar for data selection (optimized width)
        left_sidebar = tk.Frame(content_frame, bg=self.COLORS['bg_primary'],
                               relief='flat', bd=1, highlightbackground=self.COLORS['border'],
                               width=320)  # Reduced from 350 to 320
        left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))  # Reduced padding
        left_sidebar.pack_propagate(False)  # Maintain fixed width
        
        self.data_panel = DataSelectionPanel(
            left_sidebar,
            on_selection_change=self.on_data_selection_change,
            on_plot_option_change=self.update_plots
        )
        self.data_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Reduced padding
        
        # Create main plot area (takes remaining space)
        plot_container = tk.Frame(content_frame, bg=self.COLORS['bg_primary'],
                                relief='flat', bd=1, highlightbackground=self.COLORS['border'])
        plot_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_plot_area(plot_container)
        
        # Create modern status bar
        self.create_status_bar(main_frame)
    
    def create_top_control_bar(self, parent):
        """Create horizontal control bar with session and time controls"""
        control_container = tk.Frame(parent, bg=self.COLORS['bg_primary'], 
                                   relief='flat', bd=1, highlightbackground=self.COLORS['border'])
        control_container.pack(fill=tk.X, pady=(0, 15))
        
        # Control bar content
        control_content = tk.Frame(control_container, bg=self.COLORS['bg_primary'])
        control_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Left side - Session controls (folder + session selection)
        session_section = tk.Frame(control_content, bg=self.COLORS['bg_primary'])
        session_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.create_compact_session_controls(session_section)
        
        # Right side - Time range controls
        time_section = tk.Frame(control_content, bg=self.COLORS['bg_primary'])
        time_section.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(30, 0))
        
        self.create_compact_time_controls(time_section)
    
    def create_compact_session_controls(self, parent):
        """Create compact session controls for the top bar"""
        # Session section header
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame,
                text="📁 Session Control",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        # Folder selection row
        folder_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        folder_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(folder_frame,
                text="Folder:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                font=('Segoe UI', 9),
                width=8).pack(side=tk.LEFT)
        
        self.folder_entry = tk.Entry(folder_frame, 
                                   textvariable=self.folder_var,
                                   state='readonly',
                                   bg=self.COLORS['bg_tertiary'],
                                   fg=self.COLORS['text_primary'],
                                   font=('Segoe UI', 9),
                                   relief='flat',
                                   bd=1,
                                   highlightbackground=self.COLORS['border'],
                                   highlightthickness=1)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 8))
        
        browse_btn = tk.Button(folder_frame,
                             text="Browse",
                             command=self.browse_folder,
                             bg=self.COLORS['accent'],
                             fg='white',
                             font=('Segoe UI', 8),
                             relief='flat',
                             borderwidth=0,
                             padx=12, pady=4,
                             cursor='hand2')
        browse_btn.pack(side=tk.RIGHT)
        
        # Session selection row
        session_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        session_frame.pack(fill=tk.X)
        
        tk.Label(session_frame,
                text="Session:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                font=('Segoe UI', 9),
                width=8).pack(side=tk.LEFT)
        
        self.session_combo = ttk.Combobox(session_frame, 
                                        textvariable=self.session_var,
                                        state='readonly',
                                        font=('Segoe UI', 9))
        self.session_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 8))
        self.session_combo.bind('<<ComboboxSelected>>', self._on_session_selected)
        
        refresh_btn = tk.Button(session_frame,
                              text="↻",
                              command=self.refresh_sessions,
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 10),
                              relief='flat',
                              borderwidth=1,
                              highlightbackground=self.COLORS['border'],
                              width=3,
                              padx=4, pady=4,
                              cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT)
        
        # Add variables for compatibility - FIXED: Set variables after creating widgets
        if not hasattr(self, 'folder_var'):
            self.folder_var = tk.StringVar()
        if not hasattr(self, 'session_var'):
            self.session_var = tk.StringVar()
            
        self.folder_entry.configure(textvariable=self.folder_var)
        self.session_combo.configure(textvariable=self.session_var)
        
        # Add hover effects
        self.add_hover_effect(browse_btn, self.COLORS['accent'], self.COLORS['accent_hover'])
        self.add_hover_effect(refresh_btn, self.COLORS['bg_tertiary'], self.COLORS['border'])
    
    def browse_folder(self):
        """Handle folder browse button click"""
        folder = filedialog.askdirectory(
            title="Select Drone Logs Folder",
            initialdir=os.getcwd()
        )
        if folder:
            self.load_sessions(folder)
    
    def refresh_sessions(self):
        """Refresh sessions from current folder"""
        folder_path = self.get_folder_path()
        if folder_path:
            self.load_sessions(folder_path)
    
    def create_compact_time_controls(self, parent):
        """Create compact time range controls for the top bar"""
        # Time section header
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame,
                text="⏱️ Time Range",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        # Time display row
        time_display_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        time_display_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Start time
        start_frame = tk.Frame(time_display_frame, bg=self.COLORS['bg_primary'])
        start_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(start_frame,
                text="Start:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        self.start_time_var = tk.StringVar(value="--:--:--")
        tk.Label(start_frame,
                textvariable=self.start_time_var,
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['accent'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        # Duration (center)
        duration_frame = tk.Frame(time_display_frame, bg=self.COLORS['bg_primary'])
        duration_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        
        tk.Label(duration_frame,
                text="Duration:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                font=('Segoe UI', 8)).pack()
        
        self.duration_var = tk.StringVar(value="--")
        tk.Label(duration_frame,
                textvariable=self.duration_var,
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['warning'],
                font=('Segoe UI', 10, 'bold')).pack()
        
        # End time
        end_frame = tk.Frame(time_display_frame, bg=self.COLORS['bg_primary'])
        end_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        tk.Label(end_frame,
                text="End:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                font=('Segoe UI', 8)).pack(anchor=tk.E)
        
        self.end_time_var = tk.StringVar(value="--:--:--")
        tk.Label(end_frame,
                textvariable=self.end_time_var,
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['accent'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.E)
        
        # Create integrated time selector
        self.time_selector = TimeRangeSelector(
            parent,
            on_range_change=self._on_time_range_changed
        )
        # Make it more compact for the top bar
        self.time_selector.slider_height = 35
        self.time_selector.pack(fill=tk.X)
    
    def create_header(self, parent):
        """Create compact header section"""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_secondary'], height=45)  # Reduced height
        header_frame.pack(fill=tk.X, pady=(0, 10))  # Reduced padding
        header_frame.pack_propagate(False)
        
        # App title - smaller
        title_label = tk.Label(header_frame, 
                             text="🚁 Drone Log Analyzer",
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_primary'],
                             font=('Segoe UI', 16, 'bold'))  # Reduced from 18
        title_label.pack(side=tk.LEFT, pady=10)  # Reduced padding
        
        # Version badge - smaller
        version_label = tk.Label(header_frame,
                               text="v1.0",
                               bg=self.COLORS['accent'],
                               fg='white',
                               font=('Segoe UI', 7, 'bold'),  # Reduced font size
                               padx=6, pady=3)  # Reduced padding
        version_label.pack(side=tk.LEFT, padx=(10, 0), pady=15)  # Adjusted positioning
    
    def create_plot_area(self, parent):
        """Create the plotting area with modern styling"""
        # Create plot header
        plot_header = tk.Frame(parent, bg=self.COLORS['bg_primary'], height=45)
        plot_header.pack(fill=tk.X, padx=15, pady=(15, 0))
        plot_header.pack_propagate(False)
        
        tk.Label(plot_header,
                text="📊 Data Visualization",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, pady=12)
        
        # Create matplotlib figure with modern styling
        self.figure = Figure(figsize=(10, 6), dpi=100, 
                           facecolor=self.COLORS['bg_primary'],
                           edgecolor=self.COLORS['border'])
        self.plot_manager = PlotManager(self.figure)
        
        # Create canvas container
        canvas_container = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create compact navigation toolbar
        toolbar_frame = tk.Frame(canvas_container, bg=self.COLORS['bg_tertiary'], height=40)
        toolbar_frame.pack(fill=tk.X, pady=(8, 0))
        toolbar_frame.pack_propagate(False)
        
        # Standard matplotlib toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Add custom modern toolbar buttons
        self.add_custom_toolbar_buttons(toolbar_frame)
    
    def add_custom_toolbar_buttons(self, toolbar_frame):
        """Add modern custom buttons to toolbar"""
        custom_frame = tk.Frame(toolbar_frame, bg=self.COLORS['bg_tertiary'])
        custom_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Export button with modern styling
        export_btn = tk.Button(custom_frame, 
                             text="📤 Export",
                             command=self.export_plot,
                             bg=self.COLORS['accent'],
                             fg='white',
                             font=('Segoe UI', 9),
                             relief='flat',
                             borderwidth=0,
                             padx=15, pady=6,
                             cursor='hand2')
        export_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Statistics button
        stats_btn = tk.Button(custom_frame,
                            text="📊 Stats",
                            command=self.show_statistics,
                            bg=self.COLORS['bg_primary'],
                            fg=self.COLORS['text_primary'],
                            font=('Segoe UI', 9),
                            relief='flat',
                            borderwidth=1,
                            highlightbackground=self.COLORS['border'],
                            padx=15, pady=6,
                            cursor='hand2')
        stats_btn.pack(side=tk.LEFT)
        
        # Add hover effects
        def on_enter(widget, bg_color):
            def handler(event):
                widget.configure(bg=bg_color)
            return handler
        
        def on_leave(widget, bg_color):
            def handler(event):
                widget.configure(bg=bg_color)
            return handler
        
        export_btn.bind('<Enter>', on_enter(export_btn, self.COLORS['accent_hover']))
        export_btn.bind('<Leave>', on_leave(export_btn, self.COLORS['accent']))
        
        stats_btn.bind('<Enter>', on_enter(stats_btn, self.COLORS['bg_tertiary']))
        stats_btn.bind('<Leave>', on_leave(stats_btn, self.COLORS['bg_primary']))
    
    def create_status_bar(self, parent):
        """Create modern status bar"""
        self.status_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'], 
                                   height=50, relief='flat', bd=1,
                                   highlightbackground=self.COLORS['border'])
        self.status_frame.pack(fill=tk.X, pady=(20, 0))
        self.status_frame.pack_propagate(False)
        
        # Status text
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = tk.Label(self.status_frame, 
                              textvariable=self.status_var,
                              bg=self.COLORS['bg_primary'],
                              fg=self.COLORS['text_secondary'],
                              font=('Segoe UI', 9))
        status_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Session info on right
        self.session_info_var = tk.StringVar()
        session_info_label = tk.Label(self.status_frame, 
                                    textvariable=self.session_info_var,
                                    bg=self.COLORS['bg_primary'],
                                    fg=self.COLORS['text_primary'],
                                    font=('Segoe UI', 9, 'bold'))
        session_info_label.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def add_hover_effect(self, widget, normal_color, hover_color):
        """Add hover effect to button"""
        def on_enter(event):
            widget.configure(bg=hover_color)
        
        def on_leave(event):
            widget.configure(bg=normal_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _on_session_selected(self, event=None):
        """Handle session selection"""
        session_name = self.session_var.get()
        if session_name:
            self.on_session_change(session_name)
    
    def _on_time_range_changed(self, start_time: datetime, end_time: datetime):
        """Handle time range selector change"""
        # Update the display variables
        self.start_time_var.set(start_time.strftime("%H:%M:%S"))
        self.end_time_var.set(end_time.strftime("%H:%M:%S"))
        
        # Calculate and display duration
        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            duration_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = f"{seconds}s"
        
        self.duration_var.set(duration_str)
        
        # Trigger filter update
        self.apply_time_filter()
    
    def get_time_filter(self):
        """Get current time filter values from the time selector"""
        if hasattr(self, 'time_selector') and self.time_selector:
            return self.time_selector.get_selected_range()
        return None, None
    
    def set_folder_path(self, path: str):
        """Set the folder path display"""
        self.folder_var.set(path)
    
    def get_folder_path(self) -> str:
        """Get the current folder path"""
        return self.folder_var.get()
    
    def set_sessions(self, sessions: list):
        """Set available sessions"""
        if hasattr(self, 'session_combo') and self.session_combo:
            self.session_combo['values'] = sessions
    
    def set_current_session(self, session: str):
        """Set the current session"""
        self.session_var.set(session)
    
    def get_current_session(self) -> str:
        """Get the current session"""
        return self.session_var.get()
    
    def reset_time_filter(self):
        """Reset time filter to full range"""
        if hasattr(self, 'time_selector') and self.time_selector:
            self.time_selector.reset_range()
        """Handle folder browse button click"""
        folder = filedialog.askdirectory(
            title="Select Drone Logs Folder",
            initialdir=os.getcwd()
        )
        if folder:
            self.load_sessions(folder)
    
    def load_sessions(self, folder_path):
        """Load all sessions from folder"""
        self.status_var.set("Loading sessions...")
        self.root.update()
        
        try:
            # Update control panel with folder path
            self.control_panel.set_folder_path(folder_path)
            
            # Find sessions
            self.sessions = self.data_loader.find_sessions(folder_path)
            
            if not self.sessions:
                messagebox.showwarning("No Sessions", "No valid session folders found in the selected directory.")
                self.status_var.set("No sessions found")
                return
            
            # Update session dropdown
            session_names = sorted(self.sessions.keys(), reverse=True)  # Latest first
            self.control_panel.set_sessions(session_names)
            
            # Auto-select first session
            if session_names:
                self.control_panel.set_current_session(session_names[0])
                self.on_session_change(session_names[0])
            
            self.status_var.set(f"Loaded {len(self.sessions)} sessions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading sessions: {str(e)}")
            self.status_var.set("Error loading sessions")
    
    def refresh_sessions(self):
        """Refresh sessions from current folder"""
        folder_path = self.control_panel.get_folder_path()
        if folder_path:
            self.load_sessions(folder_path)
    
    def on_session_change(self, session_name=None):
        """Handle session selection change"""
        if session_name is None:
            session_name = self.get_current_session()
        
        if not session_name or session_name not in self.sessions:
            return
        
        self.status_var.set(f"Loading session: {session_name}")
        self.root.update()
        
        try:
            self.current_session = session_name
            session_path = self.sessions[session_name]
            
            # Load session data
            self.session_data = self.data_loader.load_session_data(session_path)
            
            if not self.session_data:
                messagebox.showwarning("No Data", "No valid log files found in the selected session.")
                self.status_var.set("No data in session")
                return
            
            # Update data selection panel
            self.data_panel.update_data_categories(self.session_data)
            self.selected_data_vars = self.data_panel.get_selection_vars()
            
            # Update time range
            self.update_time_range_info()
            
            # Clear plots
            self.plot_manager.clear_plots()
            self.canvas.draw()
            
            # Update status
            data_count = sum(len(df) for df in self.session_data.values())
            self.status_var.set(f"Session loaded: {len(self.session_data)} data files, {data_count} total records")
            self.session_info_var.set(f"Session: {session_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading session data: {str(e)}")
            self.status_var.set("Error loading session")
    
    def update_time_range_info(self):
        """Update time range information in control panel"""
        if not self.session_data or not self.current_session:
            return
        
        # Get session time range using folder name and data
        min_time, max_time = self.data_filter.get_session_time_range(self.current_session, self.session_data)
        
        if min_time and max_time:
            self.control_panel.set_time_range_hint(min_time, max_time)
    
    def on_data_selection_change(self):
        """Handle data selection change"""
        self.update_plots()
    
    def apply_time_filter(self):
        """Apply time filter and update plots"""
        self.update_plots()
    
    def reset_time_filter(self):
        """Reset time filter"""
        self.control_panel.reset_time_filter()
        self.update_plots()
    
    def get_filtered_data(self):
        """Get currently selected and filtered data"""
        if not self.session_data or not self.selected_data_vars:
            return {}
        
        filtered_data = {}
        
        # Get time filter values
        start_time, end_time = self.control_panel.get_time_filter()
        
        # Process each selected data series
        for data_key, var in self.selected_data_vars.items():
            if not var.get():  # Skip unselected data
                continue
            
            try:
                category_file, column = data_key.rsplit('/', 1)
                if category_file not in self.session_data:
                    continue
                
                df = self.session_data[category_file]
                if df.empty or column not in df.columns:
                    continue
                
                # Apply time filter
                filtered_df = self.data_filter.filter_by_time(df, start_time, end_time)
                
                if filtered_df.empty:
                    continue
                
                # Prepare data for plotting
                filtered_data[data_key] = {
                    'timestamp': filtered_df['timestamp'].values,
                    'data': filtered_df[column].values,
                    'label': f"{category_file.split('/')[-1]} - {column}"
                }
                
            except Exception as e:
                print(f"Error processing data {data_key}: {e}")
                continue
        
        return filtered_data

    def on_data_selection_change(self):
        """Handle data selection change"""
        self.update_plots()

    def update_plots(self):
        """Update all plots with current selection and filters"""
        try:
            filtered_data = self.get_filtered_data()
            
            if not filtered_data:
                self.plot_manager.clear_plots()
                self.canvas.draw()
                self.status_var.set("No data selected for plotting")
                return
            
            # Get plot options
            separate_plots = self.data_panel.get_separate_plots_option()
            show_grid = self.data_panel.get_show_grid_option()
            
            # Create plots
            if separate_plots:
                self.plot_manager.create_separate_plots(
                    filtered_data, 
                    self.current_session or "", 
                    show_grid
                )
            else:
                self.plot_manager.create_combined_plot(
                    filtered_data, 
                    self.current_session or "", 
                    show_grid
                )
            
            # Update layout and refresh canvas
            self.figure.tight_layout()
            self.canvas.draw()
            
            # Update status
            self.status_var.set(f"Plotting {len(filtered_data)} data series")
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error updating plots: {str(e)}")
            self.status_var.set("Error updating plots")

    def export_plot(self):
        """Export current plot to file"""
        if not hasattr(self, 'figure') or not self.figure.get_axes():
            messagebox.showwarning("No Plot", "No plot to export")
            return
        
        # Ask user for filename
        filename = filedialog.asksaveasfilename(
            title="Export Plot",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPEG files", "*.jpg")
            ]
        )
        
        if filename:
            try:
                success = self.plot_manager.export_plot(filename)
                if success:
                    messagebox.showinfo("Export Successful", f"Plot exported to {filename}")
                else:
                    messagebox.showerror("Export Failed", "Failed to export plot")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting plot: {str(e)}")
    
    def show_statistics(self):
        """Show statistics about current data with modern styling"""
        filtered_data = self.get_filtered_data()
        
        if not filtered_data:
            messagebox.showinfo("No Data", "No data selected for statistics")
            return
        
        try:
            stats = self.plot_manager.get_plot_statistics(filtered_data)
            
            # Create modern statistics window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Data Statistics")
            stats_window.geometry("600x500")
            stats_window.resizable(True, True)
            stats_window.configure(bg=self.COLORS['bg_secondary'])
            
            # Header
            header_frame = tk.Frame(stats_window, bg=self.COLORS['bg_primary'], height=60)
            header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame,
                    text="📊 Data Statistics",
                    bg=self.COLORS['bg_primary'],
                    fg=self.COLORS['text_primary'],
                    font=('Segoe UI', 14, 'bold')).pack(pady=20)
            
            # Content frame
            content_frame = tk.Frame(stats_window, bg=self.COLORS['bg_primary'])
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Create text widget with modern styling
            text_widget = tk.Text(content_frame, wrap=tk.WORD, 
                                font=('Consolas', 10),
                                bg=self.COLORS['bg_tertiary'],
                                fg=self.COLORS['text_primary'],
                                relief='flat',
                                borderwidth=0,
                                padx=20, pady=20)
            
            scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Format and insert statistics
            stats_text = self.format_statistics(stats)
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Statistics Error", f"Error generating statistics: {str(e)}")
    
    def format_statistics(self, stats):
        """Format statistics for display"""
        text = f"Data Statistics for Session: {self.current_session or 'Unknown'}\n"
        text += "=" * 60 + "\n\n"
        
        text += f"Total Data Series: {stats['total_series']}\n"
        text += f"Total Data Points: {stats['data_points']}\n"
        
        if stats['time_range']:
            start_time, end_time = stats['time_range']
            duration = end_time - start_time
            text += f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            text += f"Duration: {duration}\n"
        
        text += "\nSeries Details:\n"
        text += "-" * 40 + "\n"
        
        for series_name, series_info in stats['series_info'].items():
            text += f"\n{series_name}:\n"
            text += f"  Points: {series_info['points']}\n"
            
            if 'min_value' in series_info:
                text += f"  Min: {series_info['min_value']:.3f}\n"
                text += f"  Max: {series_info['max_value']:.3f}\n"
                text += f"  Mean: {series_info['mean_value']:.3f}\n"
            elif 'data_type' in series_info:
                text += f"  Type: {series_info['data_type']}\n"
        
        return text
    
    def update_plots(self):
        """Update all plots with current selection and filters"""
        try:
            filtered_data = self.get_filtered_data()
            
            if not filtered_data:
                self.plot_manager.clear_plots()
                self.canvas.draw()
                self.status_var.set("No data selected for plotting")
                return
            
            # Get plot options
            separate_plots = self.data_panel.get_separate_plots_option()
            show_grid = self.data_panel.get_show_grid_option()
            
            # Create plots
            if separate_plots:
                self.plot_manager.create_separate_plots(
                    filtered_data, 
                    self.current_session or "", 
                    show_grid
                )
            else:
                self.plot_manager.create_combined_plot(
                    filtered_data, 
                    self.current_session or "", 
                    show_grid
                )
            
            # Update layout and refresh canvas
            self.figure.tight_layout()
            self.canvas.draw()
            
            # Update status
            self.status_var.set(f"Plotting {len(filtered_data)} data series")
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error updating plots: {str(e)}")
            self.status_var.set("Error updating plots")
    
    def export_plot(self):
        """Export current plot to file"""
        if not hasattr(self, 'figure') or not self.figure.get_axes():
            messagebox.showwarning("No Plot", "No plot to export")
            return
        
        # Ask user for filename
        filename = filedialog.asksaveasfilename(
            title="Export Plot",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPEG files", "*.jpg")
            ]
        )
        
        if filename:
            try:
                success = self.plot_manager.export_plot(filename)
                if success:
                    messagebox.showinfo("Export Successful", f"Plot exported to {filename}")
                else:
                    messagebox.showerror("Export Failed", "Failed to export plot")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting plot: {str(e)}")
    
    def show_statistics(self):
        """Show statistics about current data with modern styling"""
        filtered_data = self.get_filtered_data()
        
        if not filtered_data:
            messagebox.showinfo("No Data", "No data selected for statistics")
            return
        
        try:
            stats = self.plot_manager.get_plot_statistics(filtered_data)
            
            # Create modern statistics window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Data Statistics")
            stats_window.geometry("600x500")
            stats_window.resizable(True, True)
            stats_window.configure(bg=self.COLORS['bg_secondary'])
            
            # Header
            header_frame = tk.Frame(stats_window, bg=self.COLORS['bg_primary'], height=60)
            header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame,
                    text="📊 Data Statistics",
                    bg=self.COLORS['bg_primary'],
                    fg=self.COLORS['text_primary'],
                    font=('Segoe UI', 14, 'bold')).pack(pady=20)
            
            # Content frame
            content_frame = tk.Frame(stats_window, bg=self.COLORS['bg_primary'])
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Create text widget with modern styling
            text_widget = tk.Text(content_frame, wrap=tk.WORD, 
                                font=('Consolas', 10),
                                bg=self.COLORS['bg_tertiary'],
                                fg=self.COLORS['text_primary'],
                                relief='flat',
                                borderwidth=0,
                                padx=20, pady=20)
            
            scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Format and insert statistics
            stats_text = self.format_statistics(stats)
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Statistics Error", f"Error generating statistics: {str(e)}")
    
    def format_statistics(self, stats):
        """Format statistics for display"""
        text = f"Data Statistics for Session: {self.current_session or 'Unknown'}\n"
        text += "=" * 60 + "\n\n"
        
        text += f"Total Data Series: {stats['total_series']}\n"
        text += f"Total Data Points: {stats['data_points']}\n"
        
        if stats['time_range']:
            start_time, end_time = stats['time_range']
            duration = end_time - start_time
            text += f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            text += f"Duration: {duration}\n"
        
        text += "\nSeries Details:\n"
        text += "-" * 40 + "\n"
        
        for series_name, series_info in stats['series_info'].items():
            text += f"\n{series_name}:\n"
            text += f"  Points: {series_info['points']}\n"
            
            if 'min_value' in series_info:
                text += f"  Min: {series_info['min_value']:.3f}\n"
                text += f"  Max: {series_info['max_value']:.3f}\n"
                text += f"  Mean: {series_info['mean_value']:.3f}\n"
            elif 'data_type' in series_info:
                text += f"  Type: {series_info['data_type']}\n"
        
        return text