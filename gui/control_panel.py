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
    """Control panel for session and time management"""
    
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
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all control panel widgets"""
        # Main container with some styling
        main_frame = ttk.LabelFrame(self, text="Session Control", padding=10)
        main_frame.pack(fill=tk.X)
        
        # Folder selection row
        self.create_folder_selection(main_frame)
        
        # Session selection row
        self.create_session_selection(main_frame)
        
        # Interactive time range selector (THE VISUAL SLIDER!)
        self.create_time_selector(main_frame)
    
    def create_folder_selection(self, parent):
        """Create folder selection controls"""
        folder_frame = ttk.Frame(parent)
        folder_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(folder_frame, text="Log Folder:", width=12).pack(side=tk.LEFT)
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, state='readonly')
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self._on_browse_click)
        browse_btn.pack(side=tk.RIGHT)
        
        # Add tooltip
        self.create_tooltip(browse_btn, "Select the folder containing drone log sessions")
    
    def create_session_selection(self, parent):
        """Create session selection controls"""
        session_frame = ttk.Frame(parent)
        session_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(session_frame, text="Session:", width=12).pack(side=tk.LEFT)
        
        self.session_combo = ttk.Combobox(session_frame, textvariable=self.session_var, 
                                         state='readonly', width=25)
        self.session_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.session_combo.bind('<<ComboboxSelected>>', self._on_session_selected)
        
        refresh_btn = ttk.Button(session_frame, text="Refresh", command=self._on_refresh_click)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Add tooltips
        self.create_tooltip(self.session_combo, "Select a drone session to analyze")
        self.create_tooltip(refresh_btn, "Refresh the list of available sessions")
    
    def create_time_selector(self, parent):
        """Create the visual time range selector (SLIDER!)"""
        self.time_selector = TimeRangeSelector(
            parent, 
            on_range_change=self._on_time_range_changed
        )
        self.time_selector.pack(fill=tk.X, pady=(10, 0))
    
    def create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background='#ffffe0', 
                            relief='solid', borderwidth=1, font=('TkDefaultFont', 8))
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