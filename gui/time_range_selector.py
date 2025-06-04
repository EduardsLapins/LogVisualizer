"""
Visual Time Range Slider Widget
A draggable time range selector with start and end handles
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Callable, Optional, Tuple

class TimeRangeSelector(ttk.Frame):
    """Modern visual time range slider with draggable start and end points"""
    
    # Modern color scheme
    COLORS = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8fafc',
        'bg_tertiary': '#f1f5f9',
        'accent': '#3b82f6',
        'accent_hover': '#2563eb',
        'accent_light': '#dbeafe',
        'text_primary': '#1e293b',
        'text_secondary': '#64748b',
        'border': '#e2e8f0',
        'border_light': '#f1f5f9',
        'success': '#10b981',
        'warning': '#f59e0b',
        'track_bg': '#f1f5f9',
        'track_selected': '#3b82f6',
        'handle_bg': '#ffffff',
        'handle_border': '#3b82f6',
        'handle_shadow': '#e2e8f0'
    }
    
    def __init__(self, parent, on_range_change: Callable = None):
        super().__init__(parent)
        
        self.on_range_change = on_range_change
        
        # Time range data
        self.min_time = None
        self.max_time = None
        self.current_start = None
        self.current_end = None
        
        # Compact slider dimensions for horizontal layout
        self.slider_width = 400
        self.slider_height = 35
        self.handle_size = 16
        self.track_height = 6
        self.margin = 20
        
        # Dragging state
        self.dragging = None  # 'start', 'end', or None
        self.start_handle_x = 0
        self.end_handle_x = 0
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the compact time range selector widgets"""
        # Main container - more compact for horizontal layout
        container = tk.Frame(self, bg=self.COLORS['bg_primary'])
        container.pack(fill=tk.X)
        
        # Compact slider canvas
        self.canvas = tk.Canvas(
            container,
            width=self.slider_width,
            height=self.slider_height,
            bg=self.COLORS['bg_primary'],
            highlightthickness=0,
            relief='flat'
        )
        self.canvas.pack(pady=(8, 5))
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Compact control buttons
        button_frame = tk.Frame(container, bg=self.COLORS['bg_primary'])
        button_frame.pack(pady=(5, 0))
        
        # Reset button - more compact
        reset_btn = tk.Button(button_frame,
                            text="Reset",
                            command=self.reset_range,
                            bg=self.COLORS['bg_tertiary'],
                            fg=self.COLORS['text_primary'],
                            font=('Segoe UI', 8),
                            relief='flat',
                            borderwidth=1,
                            highlightbackground=self.COLORS['border'],
                            padx=10, pady=4,
                            cursor='hand2')
        reset_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Apply button - more compact
        apply_btn = tk.Button(button_frame,
                            text="Apply",
                            command=self.apply_selection,
                            bg=self.COLORS['accent'],
                            fg='white',
                            font=('Segoe UI', 8),
                            relief='flat',
                            borderwidth=0,
                            padx=12, pady=4,
                            cursor='hand2')
        apply_btn.pack(side=tk.LEFT)
        
        # Add hover effects
        self.add_hover_effect(reset_btn, self.COLORS['bg_tertiary'], self.COLORS['border_light'])
        self.add_hover_effect(apply_btn, self.COLORS['accent'], self.COLORS['accent_hover'])
        
        # Initialize with empty state
        self.draw_slider()
    
    def add_hover_effect(self, widget, normal_color, hover_color):
        """Add hover effect to button"""
        def on_enter(event):
            widget.configure(bg=hover_color)
        
        def on_leave(event):
            widget.configure(bg=normal_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def set_time_range(self, min_time: datetime, max_time: datetime):
        """Set the available time range from session data"""
        print(f"Setting time range: {min_time} to {max_time}")  # Debug
        
        self.min_time = min_time
        self.max_time = max_time
        
        # Initialize selection to full range
        self.current_start = min_time
        self.current_end = max_time
        
        # Calculate handle positions and update display
        self.calculate_handle_positions()
        self.draw_slider()
        
        # Notify about the initial range
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)
    
    def get_selected_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the currently selected time range"""
        return self.current_start, self.current_end
    
    def calculate_handle_positions(self):
        """Calculate handle positions based on time values"""
        if not self.min_time or not self.max_time:
            return
        
        canvas_width = self.canvas.winfo_width() or self.slider_width
        track_width = canvas_width - (2 * self.margin)
        
        total_duration = (self.max_time - self.min_time).total_seconds()
        if total_duration <= 0:
            return
        
        start_ratio = (self.current_start - self.min_time).total_seconds() / total_duration
        end_ratio = (self.current_end - self.min_time).total_seconds() / total_duration
        
        self.start_handle_x = self.margin + (start_ratio * track_width)
        self.end_handle_x = self.margin + (end_ratio * track_width)
    
    def calculate_time_from_position(self, x_position: float) -> datetime:
        """Calculate time value from handle position"""
        canvas_width = self.canvas.winfo_width() or self.slider_width
        track_width = canvas_width - (2 * self.margin)
        
        # Clamp position to track bounds
        x_position = max(self.margin, min(x_position, self.margin + track_width))
        
        ratio = (x_position - self.margin) / track_width
        total_duration = (self.max_time - self.min_time).total_seconds()
        
        return self.min_time + timedelta(seconds=ratio * total_duration)
    
    def draw_slider(self):
        """Draw the compact slider components"""
        self.canvas.delete("all")
        
        if not self.min_time or not self.max_time:
            # Compact empty state
            self.canvas.create_text(
                self.slider_width // 2, self.slider_height // 2,
                text="Select a session to view time range",
                font=('Segoe UI', 9),
                fill=self.COLORS['text_secondary']
            )
            return
        
        # Ensure we have valid current times
        if not self.current_start or not self.current_end:
            self.current_start = self.min_time
            self.current_end = self.max_time
            self.calculate_handle_positions()
        
        canvas_width = self.canvas.winfo_width() or self.slider_width
        canvas_height = self.canvas.winfo_height() or self.slider_height
        
        # Track position
        track_y = canvas_height // 2
        track_start = self.margin
        track_end = canvas_width - self.margin
        
        # Draw background track with modern styling
        self.canvas.create_rectangle(
            track_start, track_y - self.track_height // 2,
            track_end, track_y + self.track_height // 2,
            fill=self.COLORS['track_bg'], 
            outline='',
            tags='track_bg'
        )
        
        # Draw selected range
        if self.start_handle_x < self.end_handle_x:
            self.canvas.create_rectangle(
                self.start_handle_x, track_y - self.track_height // 2,
                self.end_handle_x, track_y + self.track_height // 2,
                fill=self.COLORS['track_selected'], 
                outline='',
                tags='track_selected'
            )
        
        # Draw compact start handle with shadow
        # Shadow
        self.canvas.create_oval(
            self.start_handle_x - self.handle_size // 2 + 1,
            track_y - self.handle_size // 2 + 1,
            self.start_handle_x + self.handle_size // 2 + 1,
            track_y + self.handle_size // 2 + 1,
            fill=self.COLORS['handle_shadow'], 
            outline='',
            tags='start_handle_shadow'
        )
        
        # Handle
        self.canvas.create_oval(
            self.start_handle_x - self.handle_size // 2,
            track_y - self.handle_size // 2,
            self.start_handle_x + self.handle_size // 2,
            track_y + self.handle_size // 2,
            fill=self.COLORS['handle_bg'], 
            outline=self.COLORS['handle_border'], 
            width=2,
            tags='start_handle'
        )
        
        # Handle center dot
        self.canvas.create_oval(
            self.start_handle_x - 2,
            track_y - 2,
            self.start_handle_x + 2,
            track_y + 2,
            fill=self.COLORS['handle_border'], 
            outline='',
            tags='start_handle_dot'
        )
        
        # Draw compact end handle with shadow
        # Shadow
        self.canvas.create_oval(
            self.end_handle_x - self.handle_size // 2 + 1,
            track_y - self.handle_size // 2 + 1,
            self.end_handle_x + self.handle_size // 2 + 1,
            track_y + self.handle_size // 2 + 1,
            fill=self.COLORS['handle_shadow'], 
            outline='',
            tags='end_handle_shadow'
        )
        
        # Handle
        self.canvas.create_oval(
            self.end_handle_x - self.handle_size // 2,
            track_y - self.handle_size // 2,
            self.end_handle_x + self.handle_size // 2,
            track_y + self.handle_size // 2,
            fill=self.COLORS['handle_bg'], 
            outline=self.COLORS['handle_border'], 
            width=2,
            tags='end_handle'
        )
        
        # Handle center dot
        self.canvas.create_oval(
            self.end_handle_x - 2,
            track_y - 2,
            self.end_handle_x + 2,
            track_y + 2,
            fill=self.COLORS['handle_border'], 
            outline='',
            tags='end_handle_dot'
        )
        
        # Draw compact time labels
        self.canvas.create_text(
            track_start, track_y + 18,
            text=self.min_time.strftime("%H:%M:%S"),
            font=('Segoe UI', 7),
            fill=self.COLORS['text_secondary']
        )
        
        self.canvas.create_text(
            track_end, track_y + 18,
            text=self.max_time.strftime("%H:%M:%S"),
            font=('Segoe UI', 7),
            fill=self.COLORS['text_secondary']
        )
    
    def update_time_displays(self):
        """Update time displays - simplified for compact version"""
        # This method is kept for compatibility but displays are now handled externally
        pass
    
    def get_handle_at_position(self, x: float, y: float) -> Optional[str]:
        """Determine which handle (if any) is at the given position"""
        canvas_height = self.canvas.winfo_height() or self.slider_height
        track_y = canvas_height // 2
        
        # Check start handle
        if (abs(x - self.start_handle_x) <= self.handle_size // 2 and
            abs(y - track_y) <= self.handle_size // 2):
            return 'start'
        
        # Check end handle
        if (abs(x - self.end_handle_x) <= self.handle_size // 2 and
            abs(y - track_y) <= self.handle_size // 2):
            return 'end'
        
        return None
    
    def on_mouse_down(self, event):
        """Handle mouse button down"""
        if not self.min_time or not self.max_time:
            return
        
        handle = self.get_handle_at_position(event.x, event.y)
        if handle:
            self.dragging = handle
            self.canvas.config(cursor='hand2')
            
            # Highlight the active handle with modern styling
            if handle == 'start':
                self.canvas.itemconfig('start_handle', outline=self.COLORS['accent_hover'], width=4)
            else:
                self.canvas.itemconfig('end_handle', outline=self.COLORS['accent_hover'], width=4)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging or not self.min_time or not self.max_time:
            return
        
        if self.dragging == 'start':
            # Update start handle position
            self.start_handle_x = max(self.margin, min(event.x, self.end_handle_x))
            self.current_start = self.calculate_time_from_position(self.start_handle_x)
        
        elif self.dragging == 'end':
            # Update end handle position
            self.end_handle_x = max(self.start_handle_x, min(event.x, 
                                  self.canvas.winfo_width() - self.margin))
            self.current_end = self.calculate_time_from_position(self.end_handle_x)
        
        self.draw_slider()
        
        # Notify about change
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)
    
    def on_mouse_up(self, event):
        """Handle mouse button up"""
        if self.dragging:
            # Reset handle appearance
            self.canvas.itemconfig('start_handle', outline=self.COLORS['handle_border'], width=3)
            self.canvas.itemconfig('end_handle', outline=self.COLORS['handle_border'], width=3)
        
        self.dragging = None
        self.canvas.config(cursor='')
    
    def on_mouse_move(self, event):
        """Handle mouse movement for cursor changes"""
        if not self.dragging:
            handle = self.get_handle_at_position(event.x, event.y)
            if handle:
                self.canvas.config(cursor='hand2')
            else:
                self.canvas.config(cursor='')
    
    def on_resize(self, event):
        """Handle canvas resize"""
        self.calculate_handle_positions()
        self.draw_slider()
    
    def reset_range(self):
        """Reset to full time range"""
        if self.min_time and self.max_time:
            self.current_start = self.min_time
            self.current_end = self.max_time
            self.calculate_handle_positions()
            self.draw_slider()
            
            if self.on_range_change:
                self.on_range_change(self.current_start, self.current_end)
    
    def apply_selection(self):
        """Apply the current selection"""
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)
    
    def set_selected_range(self, start_time: Optional[datetime], end_time: Optional[datetime]):
        """Set the selected time range programmatically"""
        if self.min_time and self.max_time:
            if start_time:
                self.current_start = max(start_time, self.min_time)
            if end_time:
                self.current_end = min(end_time, self.max_time)
            
            # Ensure start <= end
            if self.current_start > self.current_end:
                self.current_start, self.current_end = self.current_end, self.current_start
            
            self.calculate_handle_positions()
            self.draw_slider()