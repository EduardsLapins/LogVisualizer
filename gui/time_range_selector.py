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
        self.min_time: Optional[datetime] = None
        self.max_time: Optional[datetime] = None
        self.current_start: Optional[datetime] = None
        self.current_end: Optional[datetime] = None

        # -------------------------------------------------------
        #    Slider dimensions (we bump height from 35→60)
        # -------------------------------------------------------
        self.slider_width = 400
        self.slider_height = 60    # was 35 → now 60
        self.handle_size = 16
        self.track_height = 6
        self.margin = 20

        # Step in seconds (for snapping)
        self.step_seconds = 1

        # Dragging state
        self.dragging = None  # will be 'start' or 'end' or None
        self.start_handle_x = 0
        self.end_handle_x = 0

        self.create_widgets()

    def create_widgets(self):
        """Create the (now taller) time range selector widgets"""
        container = tk.Frame(self, bg=self.COLORS['bg_primary'])
        container.pack(fill=tk.X)

        # The Canvas is now 60px tall instead of 35px:
        self.canvas = tk.Canvas(
            container,
            width=self.slider_width,
            height=self.slider_height,
            bg=self.COLORS['bg_primary'],
            highlightthickness=0,
            relief='flat'
        )
        # Add extra top‐padding so nothing above overlaps
        self.canvas.pack(pady=(15, 5))

        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Configure>', self.on_resize)

        # Compact “Reset” / “Apply” row
        button_frame = tk.Frame(container, bg=self.COLORS['bg_primary'])
        button_frame.pack(pady=(5, 0))

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

        self.add_hover_effect(reset_btn, self.COLORS['bg_tertiary'], self.COLORS['border_light'])
        self.add_hover_effect(apply_btn, self.COLORS['accent'], self.COLORS['accent_hover'])

        # Draw the slider (initially empty)
        self.draw_slider()

    def add_hover_effect(self, widget, normal_color, hover_color):
        """Add hover effect to a button"""
        def on_enter(event):
            widget.configure(bg=hover_color)
        def on_leave(event):
            widget.configure(bg=normal_color)
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def set_time_range(self, min_time: datetime, max_time: datetime):
        """Initialize the available full time range (called by main window)"""
        self.min_time = min_time
        self.max_time = max_time

        # Start + end default to the full range
        self.current_start = min_time
        self.current_end = max_time

        # Compute handle positions from those datetimes
        self.calculate_handle_positions()
        self.draw_slider()

        # Notify the parent immediately of the full‐range selection
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)

    def get_selected_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Return the currently selected (start, end) as datetimes."""
        return self.current_start, self.current_end

    def set_step(self, seconds: int):
        """
        Called from DroneLogAnalyzer when the user types a new Step (s) value.
        We snap future positions to multiples of this many seconds.
        """
        self.step_seconds = seconds

        # Snap current_start/current_end to the nearest multiple of step_seconds
        if self.min_time and self.current_start is not None and self.current_end is not None:
            total_seconds_full = (self.current_start - self.min_time).total_seconds()
            snapped_start_offset = round(total_seconds_full / self.step_seconds) * self.step_seconds
            self.current_start = self.min_time + timedelta(seconds=snapped_start_offset)

            total_seconds_full = (self.current_end - self.min_time).total_seconds()
            snapped_end_offset = round(total_seconds_full / self.step_seconds) * self.step_seconds
            self.current_end = self.min_time + timedelta(seconds=snapped_end_offset)

            # Re‐compute handle x positions from the snapped times
            self.calculate_handle_positions()
            self.draw_slider()

        # If desired, you could also immediately fire on_range_change with the newly‐snapped values:
        if self.on_range_change and self.current_start and self.current_end:
            self.on_range_change(self.current_start, self.current_end)

    def calculate_handle_positions(self):
        """Compute the X‐coordinates of each handle given current_start/end."""
        if not (self.min_time and self.max_time):
            return

        canvas_width = self.canvas.winfo_width() or self.slider_width
        track_width = canvas_width - (2 * self.margin)
        total_duration = (self.max_time - self.min_time).total_seconds()

        if total_duration <= 0:
            return

        # Snap current_start/end to step_seconds before computing ratio:
        start_offset = (self.current_start - self.min_time).total_seconds()
        end_offset = (self.current_end - self.min_time).total_seconds()

        start_ratio = start_offset / total_duration
        end_ratio = end_offset / total_duration

        self.start_handle_x = self.margin + (start_ratio * track_width)
        self.end_handle_x   = self.margin + (end_ratio   * track_width)

    def calculate_time_from_position(self, x_position: float) -> datetime:
        """
        Given an X on the Canvas, return the corresponding datetime,
        snapped to the nearest `step_seconds`.
        """
        canvas_width = self.canvas.winfo_width() or self.slider_width
        track_width = canvas_width - (2 * self.margin)

        # Clamp X to [margin, margin+track_width]
        x_position = max(self.margin, min(x_position, self.margin + track_width))

        ratio = (x_position - self.margin) / track_width
        total_secs = (self.max_time - self.min_time).total_seconds()
        raw_seconds = ratio * total_secs

        # Snap raw_seconds to the nearest multiple of step_seconds:
        snapped_offset = round(raw_seconds / self.step_seconds) * self.step_seconds
        snapped_offset = max(0, min(snapped_offset, total_secs))

        return self.min_time + timedelta(seconds=snapped_offset)

    def draw_slider(self):
        """Draw the track, the selected‐range bar, and the two handles (taller canvas)"""
        self.canvas.delete("all")
        if not (self.min_time and self.max_time):
            # No session loaded yet → display a placeholder
            self.canvas.create_text(
                self.slider_width // 2, self.slider_height // 2,
                text="Select a session to view time range",
                font=('Segoe UI', 9),
                fill=self.COLORS['text_secondary']
            )
            return

        # Make sure current_start/end exist
        if not (self.current_start and self.current_end):
            self.current_start = self.min_time
            self.current_end   = self.max_time
            self.calculate_handle_positions()

        canvas_w = self.canvas.winfo_width() or self.slider_width
        canvas_h = self.canvas.winfo_height() or self.slider_height
        track_y = canvas_h // 2
        track_start = self.margin
        track_end   = canvas_w - self.margin

        # Draw the background track
        self.canvas.create_rectangle(
            track_start, track_y - self.track_height // 2,
            track_end,   track_y + self.track_height // 2,
            fill=self.COLORS['track_bg'],
            outline='',
            tags='track_bg'
        )

        # Draw the “selected range” in accent color
        if self.start_handle_x < self.end_handle_x:
            self.canvas.create_rectangle(
                self.start_handle_x, track_y - self.track_height // 2,
                self.end_handle_x,   track_y + self.track_height // 2,
                fill=self.COLORS['track_selected'],
                outline='',
                tags='track_selected'
            )

        # Draw “Start” handle (with shadow)
        # Shadow:
        self.canvas.create_oval(
            self.start_handle_x - self.handle_size // 2 + 1,
            track_y - self.handle_size // 2 + 1,
            self.start_handle_x + self.handle_size // 2 + 1,
            track_y + self.handle_size // 2 + 1,
            fill=self.COLORS['handle_shadow'],
            outline='',
            tags='start_handle_shadow'
        )
        # Handle circle:
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
        # Center dot:
        self.canvas.create_oval(
            self.start_handle_x - 2,
            track_y - 2,
            self.start_handle_x + 2,
            track_y + 2,
            fill=self.COLORS['handle_border'],
            outline='',
            tags='start_handle_dot'
        )

        # Draw “End” handle (with shadow)
        self.canvas.create_oval(
            self.end_handle_x - self.handle_size // 2 + 1,
            track_y - self.handle_size // 2 + 1,
            self.end_handle_x + self.handle_size // 2 + 1,
            track_y + self.handle_size // 2 + 1,
            fill=self.COLORS['handle_shadow'],
            outline='',
            tags='end_handle_shadow'
        )
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
        self.canvas.create_oval(
            self.end_handle_x - 2,
            track_y - 2,
            self.end_handle_x + 2,
            track_y + 2,
            fill=self.COLORS['handle_border'],
            outline='',
            tags='end_handle_dot'
        )

        # Draw the min/max time labels BELOW the track
        self.canvas.create_text(
            track_start, track_y + 25,
            text=self.min_time.strftime("%H:%M:%S"),
            font=('Segoe UI', 7),
            fill=self.COLORS['text_secondary']
        )
        self.canvas.create_text(
            track_end, track_y + 25,
            text=self.max_time.strftime("%H:%M:%S"),
            font=('Segoe UI', 7),
            fill=self.COLORS['text_secondary']
        )

    def get_handle_at_position(self, x: float, y: float) -> Optional[str]:
        """Return 'start' or 'end' if the (x,y) is over a handle, else None."""
        canvas_h = self.canvas.winfo_height() or self.slider_height
        track_y = canvas_h // 2

        # Check if (x,y) is within the start handle’s circle
        if (abs(x - self.start_handle_x) <= self.handle_size // 2 and
                abs(y - track_y) <= self.handle_size // 2):
            return 'start'

        # Check end handle
        if (abs(x - self.end_handle_x) <= self.handle_size // 2 and
                abs(y - track_y) <= self.handle_size // 2):
            return 'end'

        return None

    def on_mouse_down(self, event):
        """When user clicks, decide if they’re on the start or end handle."""
        if not (self.min_time and self.max_time):
            return
        handle = self.get_handle_at_position(event.x, event.y)
        if handle:
            self.dragging = handle
            self.canvas.config(cursor='hand2')
            # Highlight the dragged handle
            if handle == 'start':
                self.canvas.itemconfig('start_handle', outline=self.COLORS['accent_hover'], width=4)
            else:
                self.canvas.itemconfig('end_handle', outline=self.COLORS['accent_hover'], width=4)

    def on_mouse_drag(self, event):
        """While dragging, move either the start or the end handle."""
        if not (self.dragging and self.min_time and self.max_time):
            return

        if self.dragging == 'start':
            # New X for the start handle is between [margin, end_handle_x]
            new_x = max(self.margin, min(event.x, self.end_handle_x))
            self.start_handle_x = new_x
            self.current_start = self.calculate_time_from_position(self.start_handle_x)

        elif self.dragging == 'end':
            # New X for the end handle is between [start_handle_x, canvas_width - margin]
            cw = self.canvas.winfo_width() or self.slider_width
            max_x = cw - self.margin
            new_x = max(self.start_handle_x, min(event.x, max_x))
            self.end_handle_x = new_x
            self.current_end = self.calculate_time_from_position(self.end_handle_x)

        self.draw_slider()
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)

    def on_mouse_up(self, event):
        """Reset handle outline when user releases the mouse."""
        if self.dragging:
            self.canvas.itemconfig('start_handle', outline=self.COLORS['handle_border'], width=2)
            self.canvas.itemconfig('end_handle',   outline=self.COLORS['handle_border'], width=2)
        self.dragging = None
        self.canvas.config(cursor='')

    def on_mouse_move(self, event):
        """Change cursor to a hand if over a handle."""
        if not self.dragging:
            handle = self.get_handle_at_position(event.x, event.y)
            if handle:
                self.canvas.config(cursor='hand2')
            else:
                self.canvas.config(cursor='')

    def on_resize(self, event):
        """When the Canvas is resized, recalculate handle positions & redraw."""
        self.calculate_handle_positions()
        self.draw_slider()

    def reset_range(self):
        """Reset both handles to the full min→max range."""
        if self.min_time and self.max_time:
            self.current_start = self.min_time
            self.current_end = self.max_time
            self.calculate_handle_positions()
            self.draw_slider()
            if self.on_range_change:
                self.on_range_change(self.current_start, self.current_end)

    def apply_selection(self):
        """Explicitly fire the on_range_change callback with the current range."""
        if self.on_range_change:
            self.on_range_change(self.current_start, self.current_end)

    def set_selected_range(self, start_time: Optional[datetime], end_time: Optional[datetime]):
        """
        Programmatically set the two handles to a given (start, end).
        They will be clamped to [min_time, max_time] and snapped to step_seconds.
        """
        if not (self.min_time and self.max_time):
            return

        if start_time:
            clamped_start = max(self.min_time, min(start_time, self.max_time))
            total_sec = (clamped_start - self.min_time).total_seconds()
            snapped = round(total_sec / self.step_seconds) * self.step_seconds
            self.current_start = self.min_time + timedelta(seconds=snapped)

        if end_time:
            clamped_end = max(self.min_time, min(end_time, self.max_time))
            total_sec = (clamped_end - self.min_time).total_seconds()
            snapped = round(total_sec / self.step_seconds) * self.step_seconds
            self.current_end = self.min_time + timedelta(seconds=snapped)

        # Ensure start ≤ end
        if self.current_start > self.current_end:
            self.current_start, self.current_end = self.current_end, self.current_start

        self.calculate_handle_positions()
        self.draw_slider()

