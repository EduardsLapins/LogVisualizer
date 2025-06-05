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
        self.status_var = tk.StringVar(value="Ready")
        self.session_info_var = tk.StringVar()

        # GUI components
        self.data_panel = None
        self.plot_manager = None
        self.canvas = None
        self.time_selector = None
        self.session_combo = None
        self.folder_entry = None

        # Proxy for any existing code that expects control_panel
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

        # Build the GUI
        self.create_gui()

        # If a default folder “drone_logs” exists, try loading it
        if os.path.exists("drone_logs"):
            try:
                self.load_sessions("drone_logs")
            except Exception as e:
                print(f"Error loading default drone_logs folder: {e}")
                # Don’t fail startup if default has an issue
                pass

    def setup_modern_theme(self):
        """Configure modern theme for the application"""
        self.root.configure(bg=self.COLORS['bg_secondary'])
        style = ttk.Style()

        # Frame/Card styles
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

        # Button styles
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

        # Entry / Combobox styles
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

        # Label styles
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
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_secondary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top control bar: Session controls on the left, Time controls on the right
        self.create_top_control_bar(main_frame)

        # Main content area (left = data selection, right = plots)
        content_frame = tk.Frame(main_frame, bg=self.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Left sidebar (DataSelectionPanel)
        left_sidebar = tk.Frame(content_frame, bg=self.COLORS['bg_primary'],
                               relief='flat', bd=1, highlightbackground=self.COLORS['border'],
                               width=320)
        left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_sidebar.pack_propagate(False)

        self.data_panel = DataSelectionPanel(
            left_sidebar,
            on_selection_change=self.on_data_selection_change,
            on_plot_option_change=self.update_plots
        )
        self.data_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Right = plot area
        plot_container = tk.Frame(
            content_frame,
            bg=self.COLORS['bg_primary'],
            relief='flat', bd=1,
            highlightbackground=self.COLORS['border']
        )
        # Also give expand=True & fill=tk.BOTH here:
        plot_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


        self.create_plot_area(plot_container)

        # Status bar at the bottom
        self.create_status_bar(main_frame)


    def create_top_control_bar(self, parent):
        """Create a slimmer control bar with session & time controls"""
        # 1) Remove large bottom padding; just give a small gap below.
        control_container = tk.Frame(
            parent,
            bg=self.COLORS['bg_primary'],
            relief='flat',
            bd=1,
            highlightbackground=self.COLORS['border']
        )
        control_container.pack(fill=tk.X, pady=(0, 5))   # was (0,20)

        # 2) Inside, reduce the vertical padding
        control_content = tk.Frame(control_container, bg=self.COLORS['bg_primary'])
        control_content.pack(fill=tk.X, padx=20, pady=5)  # was pady=20

        # Session controls on left
        session_section = tk.Frame(control_content, bg=self.COLORS['bg_primary'])
        session_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.create_compact_session_controls(session_section)

        # Time controls on right
        time_section = tk.Frame(control_content, bg=self.COLORS['bg_primary'])
        time_section.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(30, 0))
        self.create_compact_time_controls(time_section)


    def create_compact_session_controls(self, parent):
        """Create a slimmer session‐controls block (left side of top bar)"""
        # 1) Header: shrink any extra vertical padding
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 5))  # was pady=(0,10)

        tk.Label(
            header_frame,
            text="📁 Session Control",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary'],
            font=('Segoe UI', 10, 'bold')   # was 11→10
        ).pack(side=tk.LEFT, pady=3)         # was pady=(0,10)

        # 2) Folder selection row: shrink vertical gaps
        folder_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        folder_frame.pack(fill=tk.X, pady=(0, 5))  # was pady=(0,8)

        tk.Label(
            folder_frame,
            text="Folder:",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary'],
            font=('Segoe UI', 8),
            width=8
        ).pack(side=tk.LEFT)

        self.folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.folder_var,
            state='readonly',
            bg=self.COLORS['bg_tertiary'],
            fg=self.COLORS['text_primary'],
            font=('Segoe UI', 9),
            relief='flat',
            bd=1,
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 8))

        browse_btn = tk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_folder,
            bg=self.COLORS['accent'],
            fg='white',
            font=('Segoe UI', 8),
            relief='flat',
            borderwidth=0,
            padx=12, pady=4,
            cursor='hand2'
        )
        browse_btn.pack(side=tk.RIGHT)

        # 3) Session dropdown row: shrink vertical gaps
        session_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        session_frame.pack(fill=tk.X)

        tk.Label(
            session_frame,
            text="Session:",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary'],
            font=('Segoe UI', 8),
            width=8
        ).pack(side=tk.LEFT)

        self.session_combo = ttk.Combobox(
            session_frame,
            textvariable=self.session_var,
            state='readonly',
            font=('Segoe UI', 9)
        )
        self.session_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 8))
        self.session_combo.bind('<<ComboboxSelected>>', self._on_session_selected)

        refresh_btn = tk.Button(
            session_frame,
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
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Hover effects
        self.add_hover_effect(browse_btn, self.COLORS['accent'], self.COLORS['accent_hover'])
        self.add_hover_effect(refresh_btn, self.COLORS['bg_tertiary'], self.COLORS['border'])

        # Tooltips (no change needed—just keep them)


    def create_compact_time_controls(self, parent):
        """Create a slimmer time‐controls block (right side of top bar)"""
        # 1) Header: shrink vertical padding
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 5))  # was pady=(0,10)

        tk.Label(
            header_frame,
            text="⏱️ Time Range",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary'],
            font=('Segoe UI', 10, 'bold')  # was 11→10
        ).pack(side=tk.LEFT)

        # 2) Time display row: reduce vertical padding around labels
        time_display_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        time_display_frame.pack(fill=tk.X, pady=(0, 5))  # was (0,8)

        # Start
        start_frame = tk.Frame(time_display_frame, bg=self.COLORS['bg_primary'])
        start_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            start_frame,
            text="Start:",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary'],
            font=('Segoe UI', 7)  # was 8→7
        ).pack(anchor=tk.W)
        self.start_time_var = tk.StringVar(value="--:--:--")
        tk.Label(
            start_frame,
            textvariable=self.start_time_var,
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['accent'],
            font=('Segoe UI', 9, 'bold')  # was 10→9
        ).pack(anchor=tk.W)

        # Duration
        duration_frame = tk.Frame(time_display_frame, bg=self.COLORS['bg_primary'])
        duration_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        tk.Label(
            duration_frame,
            text="Duration:",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary'],
            font=('Segoe UI', 7)  # was 8→7
        ).pack()
        self.duration_var = tk.StringVar(value="--")
        tk.Label(
            duration_frame,
            textvariable=self.duration_var,
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['warning'],
            font=('Segoe UI', 9, 'bold')  # was 10→9
        ).pack()

        # End
        end_frame = tk.Frame(time_display_frame, bg=self.COLORS['bg_primary'])
        end_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(
            end_frame,
            text="End:",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary'],
            font=('Segoe UI', 7)  # was 8→7
        ).pack(anchor=tk.E)
        self.end_time_var = tk.StringVar(value="--:--:--")
        tk.Label(
            end_frame,
            textvariable=self.end_time_var,
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['accent'],
            font=('Segoe UI', 9, 'bold')  # was 10→9
        ).pack(anchor=tk.E)

        # ── Integrate TimeRangeSelector (slider) ──────────────────────────
        self.time_selector = TimeRangeSelector(
            parent,
            on_range_change=self._on_time_range_changed
        )
        # Keep the slider_height bump (60) so labels above don’t get clipped:
        self.time_selector.slider_height = 60
        self.time_selector.pack(fill=tk.X, pady=(0, 0))  # was no change

        # ── “Step (s)” Entry under the slider ───────────────────────────────
        split_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        split_frame.pack(fill=tk.X, pady=(5, 0))  # minimal vertical gap

        tk.Label(
            split_frame,
            text="Step (s):",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary'],
            font=('Segoe UI', 7)  # was 8→7
        ).pack(side=tk.LEFT, padx=(10, 5))

        self.time_split_var = tk.StringVar(value="1")
        split_entry = tk.Entry(
            split_frame,
            textvariable=self.time_split_var,
            width=4,
            font=('Segoe UI', 9),
            relief='solid',
            bd=1,
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        split_entry.pack(side=tk.LEFT)

        def on_split_enter(event=None):
            raw = self.time_split_var.get().strip()
            try:
                secs = int(raw)
                if secs <= 0:
                    raise ValueError
                if hasattr(self.time_selector, 'set_step'):
                    self.time_selector.set_step(secs)
                    self.status_var.set(f"Time‐split set to {secs} s")
                else:
                    messagebox.showwarning(
                        "Unsupported",
                        "This TimeRangeSelector version cannot change step dynamically."
                    )
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a positive integer for seconds."
                )

        split_entry.bind('<Return>', on_split_enter)
        split_entry.bind('<FocusOut>', on_split_enter)

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
        # Header
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(header_frame,
                 text="⏱️ Time Range",
                 bg=self.COLORS['bg_primary'],
                 fg=self.COLORS['text_primary'],
                 font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)

        # Time display row (Start / Duration / End)
        time_display_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        time_display_frame.pack(fill=tk.X, pady=(0, 8))

        # Start
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

        # Duration
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

        # End
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

        # ── Integrate TimeRangeSelector (slider) ──────────────────────────
        self.time_selector = TimeRangeSelector(
            parent,
            on_range_change=self._on_time_range_changed
        )
        # Bump slider_height so labels above never get clipped:
        self.time_selector.slider_height = 60   # was 35 → now 60
        self.time_selector.pack(fill=tk.X, pady=(0, 0))

        # ── “Step (s)” Entry under the slider ───────────────────────────────
        split_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        split_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(split_frame,
                 text="Step (s):",
                 bg=self.COLORS['bg_primary'],
                 fg=self.COLORS['text_secondary'],
                 font=('Segoe UI', 8)
        ).pack(side=tk.LEFT, padx=(10, 5))

        self.time_split_var = tk.StringVar(value="1")
        split_entry = tk.Entry(
            split_frame,
            textvariable=self.time_split_var,
            width=4,
            font=('Segoe UI', 9),
            relief='solid',
            bd=1,
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        split_entry.pack(side=tk.LEFT)

        def on_split_enter(event=None):
            raw = self.time_split_var.get().strip()
            try:
                secs = int(raw)
                if secs <= 0:
                    raise ValueError
                # Call into TimeRangeSelector to change step
                if hasattr(self.time_selector, 'set_step'):
                    self.time_selector.set_step(secs)
                    self.status_var.set(f"Time‐split set to {secs} s")
                else:
                    messagebox.showwarning(
                        "Unsupported",
                        "This TimeRangeSelector version cannot change step dynamically."
                    )
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a positive integer for seconds."
                )

        split_entry.bind('<Return>', on_split_enter)
        split_entry.bind('<FocusOut>', on_split_enter)
        # ─────────────────────────────────────────────────────────────────────

    def create_header(self, parent):
        """Create compact header section (if you’re showing a separate header)"""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_secondary'], height=45)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame,
                               text="🚁 Drone Log Analyzer",
                               bg=self.COLORS['bg_secondary'],
                               fg=self.COLORS['text_primary'],
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, pady=10)

        version_label = tk.Label(header_frame,
                                 text="v1.0",
                                 bg=self.COLORS['accent'],
                                 fg='white',
                                 font=('Segoe UI', 7, 'bold'),
                                 padx=6, pady=3)
        version_label.pack(side=tk.LEFT, padx=(10, 0), pady=15)

    def create_plot_area(self, parent):
        """Create the plotting area with modern styling, but let the figure resize dynamically."""
        # Plot header
        plot_header = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        plot_header.pack(fill=tk.X, padx=15, pady=(15, 0))
        plot_header.pack_propagate(False)

        tk.Label(
            plot_header,
            text="📊 Data Visualization",
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary'],
            font=('Segoe UI', 12, 'bold')
        ).pack(side=tk.LEFT, pady=12)

        # Create a Figure with a small default size
        # (we'll override it on every resize)
        self.figure = Figure(figsize=(2, 2), dpi=100,  # smaller default → 200×200 px
                             facecolor=self.COLORS['bg_primary'],
                             edgecolor=self.COLORS['border'])
        self.plot_manager = PlotManager(self.figure)

        # Canvas container
        canvas_container = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        # Embed the Figure in a Tkinter widget
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_container)
        widget = self.canvas.get_tk_widget()
        widget.pack(fill=tk.BOTH, expand=True)

        # Compact toolbar
        toolbar_frame = tk.Frame(canvas_container, bg=self.COLORS['bg_tertiary'], height=40)
        toolbar_frame.pack(fill=tk.X, pady=(8, 0))
        toolbar_frame.pack_propagate(False)

        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        self.add_custom_toolbar_buttons(toolbar_frame)

        # ─────── DYNAMIC RESIZE HANDLER ─────────────────────────
        # Whenever the canvas widget is resized, recompute figsize and redraw.
        def _on_canvas_config(event):
            # event.width / event.height are the new size of the canvas in pixels
            dpi = self.figure.get_dpi()
            # Avoid zero‐division and ignore spurious tiny events:
            if event.width < 10 or event.height < 10:
                return

            # Compute new size in inches, leave a small margin for toolbar/header/padding
            new_w_in = event.width / dpi
            new_h_in = (event.height - toolbar_frame.winfo_height()) / dpi

            # Only update if the size has meaningfully changed
            old_w, old_h = self.figure.get_size_inches()
            if abs(old_w - new_w_in) > 0.1 or abs(old_h - new_h_in) > 0.1:
                self.figure.set_size_inches(new_w_in, new_h_in, forward=True)
                self.canvas.draw_idle()

        # Bind the resize handler to the canvas widget
        widget.bind("<Configure>", _on_canvas_config)
        # ──────────────────────────────────────────────────────────


    def add_custom_toolbar_buttons(self, toolbar_frame):
        """Add modern custom buttons to toolbar"""
        custom_frame = tk.Frame(toolbar_frame, bg=self.COLORS['bg_tertiary'])
        custom_frame.pack(side=tk.RIGHT, padx=15, pady=8)

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

        # Hover effects
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

        status_label = tk.Label(self.status_frame,
                                textvariable=self.status_var,
                                bg=self.COLORS['bg_primary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 9))
        status_label.pack(side=tk.LEFT, padx=20, pady=15)

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
        """Handle session selection from the combobox"""
        session_name = self.session_var.get()
        if session_name:
            self.on_session_change(session_name)

    def _on_time_range_changed(self, start_time: datetime, end_time: datetime):
        """Handle a callback from TimeRangeSelector whenever the user drags/apply/resets"""

        # Update the “Start: …” and “End: …” labels
        self.start_time_var.set(start_time.strftime("%H:%M:%S"))
        self.end_time_var.set(end_time.strftime("%H:%M:%S"))

        # Compute and display the duration
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

        # Finally, re‐plot with the new time filter
        self.apply_time_filter()

    def get_time_filter(self):
        """Get the current time range from the slider"""
        if hasattr(self, 'time_selector') and self.time_selector:
            return self.time_selector.get_selected_range()
        return None, None

    def set_folder_path(self, path: str):
        """Set the folder path display (read‐only Entry)"""
        self.folder_var.set(path)

    def get_folder_path(self) -> str:
        """Get the current folder path string"""
        return self.folder_var.get()

    def set_sessions(self, sessions: list):
        """Populate the session combobox"""
        if hasattr(self, 'session_combo') and self.session_combo:
            self.session_combo['values'] = sessions

    def set_current_session(self, session: str):
        """Programmatically select a session in the combobox"""
        self.session_var.set(session)

    def get_current_session(self) -> str:
        """Read the currently selected session string"""
        return self.session_var.get()

    def reset_time_filter(self):
        """Reset the time slider to the full session range"""
        if hasattr(self, 'time_selector') and self.time_selector:
            self.time_selector.reset_range()
        self.update_plots()

    def load_sessions(self, folder_path):
        """Scan the folder, find all sessions, and populate the dropdown"""
        self.status_var.set("Loading sessions...")
        self.root.update()

        try:
            # Tell proxy what folder we're using
            self.control_panel.set_folder_path(folder_path)

            # Find session‐named subdirectories (or however DataLoader is implemented)
            self.sessions = self.data_loader.find_sessions(folder_path)

            if not self.sessions:
                messagebox.showwarning(
                    "No Sessions",
                    "No valid session folders found in the selected directory."
                )
                self.status_var.set("No sessions found")
                return

            # Populate combobox (sorted latest first)
            session_names = sorted(self.sessions.keys(), reverse=True)
            self.control_panel.set_sessions(session_names)

            # Auto‐select the first one
            if session_names:
                self.control_panel.set_current_session(session_names[0])
                self.on_session_change(session_names[0])

            self.status_var.set(f"Loaded {len(self.sessions)} sessions")

        except Exception as e:
            messagebox.showerror("Error", f"Error loading sessions: {str(e)}")
            self.status_var.set("Error loading sessions")

    def on_session_change(self, session_name=None):
        """When the user picks a new session from the dropdown"""
        if session_name is None:
            session_name = self.get_current_session()

        if not session_name or session_name not in self.sessions:
            return

        self.status_var.set(f"Loading session: {session_name}")
        self.root.update()

        try:
            self.current_session = session_name
            session_path = self.sessions[session_name]

            # Actually read in all of the CSVs/logs for that session
            self.session_data = self.data_loader.load_session_data(session_path)

            if not self.session_data:
                messagebox.showwarning("No Data", "No valid log files found in the selected session.")
                self.status_var.set("No data in session")
                return

            # Let the left panel know what data columns are available
            self.data_panel.update_data_categories(self.session_data)
            self.selected_data_vars = self.data_panel.get_selection_vars()

            # Ask DataFilter for min/max timestamps in this session
            self.update_time_range_info()

            # Clear any old plots
            self.plot_manager.clear_plots()
            self.canvas.draw()

            # Update status bar
            data_count = sum(len(df) for df in self.session_data.values())
            self.status_var.set(
                f"Session loaded: {len(self.session_data)} data files, {data_count} total records"
            )
            self.session_info_var.set(f"Session: {session_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Error loading session data: {str(e)}")
            self.status_var.set("Error loading session")

    def update_time_range_info(self):
        """Query DataFilter for the session’s min/max time, then tell the slider"""
        if not self.session_data or not self.current_session:
            return

        min_time, max_time = self.data_filter.get_session_time_range(
            self.current_session, self.session_data
        )
        if min_time and max_time:
            self.control_panel.set_time_range_hint(min_time, max_time)

    def on_data_selection_change(self):
        """Called when the user checks/unchecks a data‐field in the left panel"""
        self.update_plots()

    def apply_time_filter(self):
        """Re‐draw the plots with the currently selected time range"""
        self.update_plots()

    def get_filtered_data(self):
        """Collect only the checked‐ON columns & time‐filtered rows into a dict for plotting"""
        if not self.session_data or not self.selected_data_vars:
            return {}

        filtered_data = {}
        start_time, end_time = self.control_panel.get_time_filter()

        for data_key, var in self.selected_data_vars.items():
            if not var.get():
                continue

            try:
                category_file, column = data_key.rsplit('/', 1)
                if category_file not in self.session_data:
                    continue

                df = self.session_data[category_file]
                if df.empty or column not in df.columns:
                    continue

                filtered_df = self.data_filter.filter_by_time(df, start_time, end_time)
                if filtered_df.empty:
                    continue

                filtered_data[data_key] = {
                    'timestamp': filtered_df['timestamp'].values,
                    'data': filtered_df[column].values,
                    'label': f"{category_file.split('/')[-1]} - {column}"
                }
            except Exception as e:
                print(f"Error processing {data_key}: {e}")
                continue

        return filtered_data

    def update_plots(self):
        """Re‐draw matplotlib plots based on `get_filtered_data()`"""
        try:
            filtered_data = self.get_filtered_data()

            if not filtered_data:
                self.plot_manager.clear_plots()
                self.canvas.draw()
                self.status_var.set("No data selected for plotting")
                return

            separate_plots = self.data_panel.get_separate_plots_option()
            show_grid = self.data_panel.get_show_grid_option()

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

            self.figure.tight_layout()
            self.canvas.draw()
            self.status_var.set(f"Plotting {len(filtered_data)} data series")

        except Exception as e:
            messagebox.showerror("Plot Error", f"Error updating plots: {str(e)}")
            self.status_var.set("Error updating plots")

    def export_plot(self):
        """Export the currently drawn matplotlib figure to file"""
        if not hasattr(self, 'figure') or not self.figure.get_axes():
            messagebox.showwarning("No Plot", "No plot to export")
            return

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
        """Pop up a new window showing summary stats of the currently plotted data"""
        filtered_data = self.get_filtered_data()
        if not filtered_data:
            messagebox.showinfo("No Data", "No data selected for statistics")
            return

        try:
            stats = self.plot_manager.get_plot_statistics(filtered_data)

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

            # Content
            content_frame = tk.Frame(stats_window, bg=self.COLORS['bg_primary'])
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

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

            stats_text = self.format_statistics(stats)
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Statistics Error", f"Error generating statistics: {str(e)}")

    def format_statistics(self, stats):
        """Format the statistics dictionary into a multi‐line string"""
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
