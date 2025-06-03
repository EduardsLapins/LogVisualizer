"""
Visual Time Range Slider Widget
A draggable time range selector with start and end handles
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Callable, Optional, Tuple

class TimeRangeSelector(ttk.Frame):
    """Visual time range slider with draggable start and end points"""
    
    def __init__(self, parent, on_range_change: Callable = None):
        super().__init__(parent)
        
        self.on_range_change = on_range_change
        
        # Time range data
        self.min_time = None
        self.max_time = None
        self.current_start = None
        self.current_end = None
        
        # Slider dimensions
        self.slider_width = 600
        self.slider_height = 40  # Reduced from 60 to 40
        self.handle_size = 16    # Reduced from 20 to 16
        self.track_height = 6    # Reduced from 8 to 6
        self.margin = 25         # Reduced from 30 to 25
        
        # Dragging state
        self.dragging = None  # 'start', 'end', or None
        self.start_handle_x = 0
        self.end_handle_x = 0
        
        # Colors
        self.track_bg = '#e0e0e0'
        self.track_selected = '#2196F3'
        self.handle_color = '#ffffff'
        self.handle_border = '#2196F3'
        self.handle_active = '#1976D2'
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the time range selector widgets"""
        # Main container
        container = ttk.LabelFrame(self, text="Time Range Selector", padding=8)  # Reduced padding
        container.pack(fill=tk.BOTH, expand=True)
        
        # Slider canvas
        self.canvas = tk.Canvas(
            container,
            width=self.slider_width,
            height=self.slider_height,
            bg='white',
            highlightthickness=0
        )
        self.canvas.pack(pady=5)  # Reduced from pady=10
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Time display frame
        time_frame = ttk.Frame(container)
        time_frame.pack(fill=tk.X, pady=(5, 0))  # Reduced from pady=(10, 0)
        
        # Start time
        start_frame = ttk.Frame(time_frame)
        start_frame.pack(side=tk.LEFT)
        
        ttk.Label(start_frame, text="Start Time:", font=('Arial', 9, 'bold')).pack()
        self.start_time_var = tk.StringVar(value="--:--:--")
        ttk.Label(start_frame, textvariable=self.start_time_var, 
                 font=('Arial', 12), foreground='#2196F3').pack()
        
        # Duration in center
        duration_frame = ttk.Frame(time_frame)
        duration_frame.pack(side=tk.LEFT, expand=True)
        
        ttk.Label(duration_frame, text="Selected Duration:", font=('Arial', 9, 'bold')).pack()
        self.duration_var = tk.StringVar(value="--")
        ttk.Label(duration_frame, textvariable=self.duration_var, 
                 font=('Arial', 12), foreground='#FF9800').pack()
        
        # End time
        end_frame = ttk.Frame(time_frame)
        end_frame.pack(side=tk.RIGHT)
        
        ttk.Label(end_frame, text="End Time:", font=('Arial', 9, 'bold')).pack()
        self.end_time_var = tk.StringVar(value="--:--:--")
        ttk.Label(end_frame, textvariable=self.end_time_var, 
                 font=('Arial', 12), foreground='#2196F3').pack()
        
        # Control buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(8, 0))  # Reduced from pady=(15, 0)
        
        ttk.Button(button_frame, text="Reset to Full Range", 
                  command=self.reset_range).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Apply Selection", 
                  command=self.apply_selection).pack(side=tk.RIGHT)
        
        # Initialize with empty state
        self.update_time_displays()
        self.draw_slider()
    
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
        self.update_time_displays()
        
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
        """Draw the slider components"""
        self.canvas.delete("all")
        
        if not self.min_time or not self.max_time:
            # Draw empty state - wait for session data
            self.canvas.create_text(
                self.slider_width // 2, self.slider_height // 2,
                text="Select a session to view time range", font=('Arial', 12), fill='gray'
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
        
        # Draw background track
        self.canvas.create_rectangle(
            track_start, track_y - self.track_height // 2,
            track_end, track_y + self.track_height // 2,
            fill=self.track_bg, outline='', tags='track_bg'
        )
        
        # Draw selected range
        if self.start_handle_x < self.end_handle_x:
            self.canvas.create_rectangle(
                self.start_handle_x, track_y - self.track_height // 2,
                self.end_handle_x, track_y + self.track_height // 2,
                fill=self.track_selected, outline='', tags='track_selected'
            )
        
        # Draw start handle
        self.canvas.create_oval(
            self.start_handle_x - self.handle_size // 2,
            track_y - self.handle_size // 2,
            self.start_handle_x + self.handle_size // 2,
            track_y + self.handle_size // 2,
            fill=self.handle_color, outline=self.handle_border, width=3,
            tags='start_handle'
        )
        
        # Draw end handle
        self.canvas.create_oval(
            self.end_handle_x - self.handle_size // 2,
            track_y - self.handle_size // 2,
            self.end_handle_x + self.handle_size // 2,
            track_y + self.handle_size // 2,
            fill=self.handle_color, outline=self.handle_border, width=3,
            tags='end_handle'
        )
        
        # Draw start/end labels (session time range)
        self.canvas.create_text(
            track_start, track_y + 25,
            text=self.min_time.strftime("%H:%M:%S"),
            font=('Arial', 8), fill='gray'
        )
        
        self.canvas.create_text(
            track_end, track_y + 25,
            text=self.max_time.strftime("%H:%M:%S"),
            font=('Arial', 8), fill='gray'
        )
        
        # Draw handle labels
        self.canvas.create_text(
            self.start_handle_x, track_y - 15,
            text="START", font=('Arial', 7), fill=self.handle_border
        )
        
        self.canvas.create_text(
            self.end_handle_x, track_y - 15,
            text="END", font=('Arial', 7), fill=self.handle_border
        )
    
    def update_time_displays(self):
        """Update the time display labels"""
        if self.current_start and self.current_end and self.min_time and self.max_time:
            # Show actual session times
            self.start_time_var.set(self.current_start.strftime("%H:%M:%S"))
            self.end_time_var.set(self.current_end.strftime("%H:%M:%S"))
            
            # Calculate and display duration
            duration = self.current_end - self.current_start
            total_seconds = int(duration.total_seconds())
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                duration_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                duration_str = f"{minutes}m {seconds}s"
            else:
                duration_str = f"{seconds}s"
            
            self.duration_var.set(duration_str)
        else:
            # No session data yet
            self.start_time_var.set("--:--:--")
            self.end_time_var.set("--:--:--")
            self.duration_var.set("Select a session")
    
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
            
            # Highlight the active handle
            if handle == 'start':
                self.canvas.itemconfig('start_handle', outline=self.handle_active, width=4)
            else:
                self.canvas.itemconfig('end_handle', outline=self.handle_active, width=4)
    
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
        self.update_time_displays()
        
        # Notify about change
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)
    
    def on_mouse_up(self, event):
        """Handle mouse button up"""
        if self.dragging:
            # Reset handle appearance
            self.canvas.itemconfig('start_handle', outline=self.handle_border, width=3)
            self.canvas.itemconfig('end_handle', outline=self.handle_border, width=3)
        
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
            self.update_time_displays()
            
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
            self.update_time_displays()