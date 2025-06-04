"""
Control Panel GUI Component
Handles session selection, folder browsing, and time filtering controls
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Callable, Optional, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.time_range_selector import TimeRangeSelector

class ControlPanel(ttk.Frame):
    """Modern control panel for session and time management"""
    
    # Modern color scheme matching main window
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
    
    def __init__(self, parent, on_folder_browse: Callable = None, 
                 on_session_change: Callable = None, on_refresh: Callable = None,
                 on_time_filter: Callable = None, on_reset_filter: Callable = None):
        super().__init__(parent)
        
        # Store callbacks
        self.on_folder_browse = on_folder_browse
        self.on_session_change = on_session_change
        self.on_refresh = on_refresh
        self.on_time_filter = on_time_filter
        self.on_reset_filter = on_reset_filter
        
        # Variables
        self.folder_var = tk.StringVar()
        self.session_var = tk.StringVar()
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.time_hint_var = tk.StringVar()
        
        # GUI components
        self.session_combo = None
        self.time_selector = None
        
        # Configure styling
        self.configure(style='Card.TFrame')
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all control panel widgets with modern styling"""
        # Main container with clean styling
        main_frame = tk.Frame(self, bg=self.COLORS['bg_primary'])
        main_frame.pack(fill=tk.X, expand=True)
        
        # Header section
        self.create_header(main_frame)
        
        # Controls grid
        controls_container = tk.Frame(main_frame, bg=self.COLORS['bg_primary'])
        controls_container.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Create two-column layout
        left_column = tk.Frame(controls_container, bg=self.COLORS['bg_primary'])
        left_column.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        right_column = tk.Frame(controls_container, bg=self.COLORS['bg_primary'])
        right_column.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Folder and session selection
        self.create_folder_selection(left_column)
        self.create_session_selection(right_column)
        
        # Time range selector section
        self.create_time_selector_section(main_frame)
    
    def create_header(self, parent):
        """Create modern header"""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'], height=50)
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame,
                             text="Session Control",
                             bg=self.COLORS['bg_primary'],
                             fg=self.COLORS['text_primary'],
                             font=('Segoe UI', 12, 'bold'))
        title_label.pack(side=tk.LEFT, pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                text="Select data source and time range",
                                bg=self.COLORS['bg_primary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 9))
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=10)
    
    def create_folder_selection(self, parent):
        """Create modern folder selection controls"""
        folder_section = tk.Frame(parent, bg=self.COLORS['bg_secondary'], 
                                relief='flat', bd=1, highlightbackground=self.COLORS['border_light'])
        folder_section.pack(fill=tk.X, pady=(0, 15))
        
        # Section header
        header_frame = tk.Frame(folder_section, bg=self.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(header_frame, 
                text="📁 Data Folder",
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Controls
        controls_frame = tk.Frame(folder_section, bg=self.COLORS['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Entry with modern styling
        self.folder_entry = tk.Entry(controls_frame, 
                                   textvariable=self.folder_var,
                                   state='readonly',
                                   bg=self.COLORS['bg_primary'],
                                   fg=self.COLORS['text_primary'],
                                   font=('Segoe UI', 9),
                                   relief='flat',
                                   bd=1,
                                   highlightbackground=self.COLORS['border'],
                                   highlightthickness=1)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Modern browse button
        browse_btn = tk.Button(controls_frame,
                             text="Browse",
                             command=self._on_browse_click,
                             bg=self.COLORS['accent'],
                             fg='white',
                             font=('Segoe UI', 9),
                             relief='flat',
                             borderwidth=0,
                             padx=20, pady=8,
                             cursor='hand2')
        browse_btn.pack(side=tk.RIGHT)
        
        # Add hover effect
        self.add_hover_effect(browse_btn, self.COLORS['accent'], self.COLORS['accent_hover'])
        
        # Add tooltip
        self.create_tooltip(browse_btn, "Select the folder containing drone log sessions")
    
    def create_session_selection(self, parent):
        """Create modern session selection controls"""
        session_section = tk.Frame(parent, bg=self.COLORS['bg_secondary'],
                                 relief='flat', bd=1, highlightbackground=self.COLORS['border_light'])
        session_section.pack(fill=tk.X, pady=(0, 15))
        
        # Section header
        header_frame = tk.Frame(session_section, bg=self.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(header_frame,
                text="🕒 Session",
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Controls
        controls_frame = tk.Frame(session_section, bg=self.COLORS['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Modern combobox
        self.session_combo = ttk.Combobox(controls_frame, 
                                        textvariable=self.session_var,
                                        state='readonly',
                                        font=('Segoe UI', 9),
                                        style='Modern.TCombobox')
        self.session_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.session_combo.bind('<<ComboboxSelected>>', self._on_session_selected)
        
        # Modern refresh button
        refresh_btn = tk.Button(controls_frame,
                              text="↻",
                              command=self._on_refresh_click,
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 11),
                              relief='flat',
                              borderwidth=1,
                              highlightbackground=self.COLORS['border'],
                              width=3,
                              padx=8, pady=8,
                              cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT)
        
        # Add hover effect
        self.add_hover_effect(refresh_btn, self.COLORS['bg_tertiary'], self.COLORS['border_light'])
        
        # Add tooltips
        self.create_tooltip(self.session_combo, "Select a drone session to analyze")
        self.create_tooltip(refresh_btn, "Refresh the list of available sessions")
    
    def create_time_selector_section(self, parent):
        """Create the time range selector section with modern styling"""
        time_section = tk.Frame(parent, bg=self.COLORS['bg_secondary'],
                              relief='flat', bd=1, highlightbackground=self.COLORS['border_light'])
        time_section.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Section header
        header_frame = tk.Frame(time_section, bg=self.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(header_frame,
                text="⏱️ Time Range Selection",
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        tk.Label(header_frame,
                text="Drag the handles to select a specific time window",
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_secondary'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(15, 0))
        
        # Time selector container
        selector_container = tk.Frame(time_section, bg=self.COLORS['bg_secondary'])
        selector_container.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Create the visual time selector
        self.time_selector = TimeRangeSelector(
            selector_container,
            on_range_change=self._on_time_range_changed
        )
        self.time_selector.pack(fill=tk.X)
    
    def add_hover_effect(self, widget, normal_color, hover_color):
        """Add hover effect to button"""
        def on_enter(event):
            widget.configure(bg=hover_color)
        
        def on_leave(event):
            widget.configure(bg=normal_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def create_tooltip(self, widget, text):
        """Create a modern tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(bg=self.COLORS['text_primary'])
            
            label = tk.Label(tooltip, 
                           text=text, 
                           bg=self.COLORS['text_primary'],
                           fg='white',
                           font=('Segoe UI', 8),
                           padx=10, pady=6)
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    # Event handlers
    def _on_browse_click(self):
        """Handle browse button click"""
        if self.on_folder_browse:
            self.on_folder_browse()
    
    def _on_session_selected(self, event=None):
        """Handle session selection"""
        if self.on_session_change:
            self.on_session_change(self.session_var.get())
    
    def _on_refresh_click(self):
        """Handle refresh button click"""
        if self.on_refresh:
            self.on_refresh()
    
    def _on_time_range_changed(self, start_time: datetime, end_time: datetime):
        """Handle time range selector change"""
        # Update the internal variables (for compatibility)
        self.start_time_var.set(start_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.end_time_var.set(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Trigger filter update
        if self.on_time_filter:
            self.on_time_filter()
    
    # Public interface methods
    def set_folder_path(self, path: str):
        """Set the folder path display"""
        self.folder_var.set(path)
        # Update entry styling to show content
        if path:
            self.folder_entry.configure(bg=self.COLORS['bg_primary'])
    
    def get_folder_path(self) -> str:
        """Get the current folder path"""
        return self.folder_var.get()
    
    def set_sessions(self, sessions: list):
        """Set available sessions"""
        if self.session_combo:
            self.session_combo['values'] = sessions
    
    def set_current_session(self, session: str):
        """Set the current session"""
        self.session_var.set(session)
    
    def get_current_session(self) -> str:
        """Get the current session"""
        return self.session_var.get()
    
    def set_time_range_hint(self, start_time: datetime, end_time: datetime):
        """Set the time range for the visual slider"""
        self.time_hint_var.set(f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Update the visual time selector with the available range
        if self.time_selector:
            self.time_selector.set_time_range(start_time, end_time)
    
    def get_time_filter(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get current time filter values from the visual slider"""
        # Get from visual time selector
        if self.time_selector:
            return self.time_selector.get_selected_range()
        
        # Fallback (shouldn't be needed)
        return None, None
    
    def reset_time_filter(self):
        """Reset time filter to full range"""
        if self.time_selector:
            self.time_selector.reset_range()
    
    def set_time_filter(self, start_time: Optional[datetime], end_time: Optional[datetime]):
        """Set time filter values programmatically"""
        if self.time_selector:
            self.time_selector.set_selected_range(start_time, end_time)