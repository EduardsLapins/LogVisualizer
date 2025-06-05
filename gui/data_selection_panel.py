"""
Data Selection Panel GUI Component - FIXED VERSION
Handles data series selection and plot options
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable
import pandas as pd

class DataSelectionPanel(ttk.Frame):
    """Modern panel for selecting data series and plot options"""
    
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
        'error': '#ef4444'
    }
    
    def __init__(self, parent, on_selection_change: Callable = None, 
                 on_plot_option_change: Callable = None):
        super().__init__(parent)
        
        # Store callbacks
        self.on_selection_change = on_selection_change
        self.on_plot_option_change = on_plot_option_change
        
        # Data storage
        self.data_categories = {}
        self.selection_vars = {}
        
        # Plot option variables
        self.separate_plots_var = tk.BooleanVar(value=False)
        self.show_grid_var = tk.BooleanVar(value=True)
        
        # GUI components - initialize properly
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.canvas_window = None
        self.selection_count_var = None
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create all panel widgets with modern styling"""
        # Set minimum width
        self.configure(width=300)
        
        # Main container
        main_frame = tk.Frame(self, bg=self.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self.create_header(main_frame)
        
        # Data selection area
        self.create_data_selection_area(main_frame)
        
        # Plot options
        self.create_plot_options(main_frame)
    
    def create_header(self, parent):
        """Create compact header"""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'], height=45)
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame,
                             text="📊 Data Selection",
                             bg=self.COLORS['bg_primary'],
                             fg=self.COLORS['text_primary'],
                             font=('Segoe UI', 11, 'bold'))
        title_label.pack(anchor=tk.W, pady=(8, 0))
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                text="Choose data series to visualize",
                                bg=self.COLORS['bg_primary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 8))
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))

    def create_data_selection_area(self, parent):
        """Create FIXED scrollable data selection area"""
        selection_container = tk.Frame(parent, bg=self.COLORS['bg_secondary'])
        selection_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 0))
        
        # Section header
        header_frame = tk.Frame(selection_container, bg=self.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(header_frame,
                text="Available Data",
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Selection count badge
        self.selection_count_var = tk.StringVar(value="0")
        count_label = tk.Label(header_frame,
                            textvariable=self.selection_count_var,
                            bg=self.COLORS['accent'],
                            fg='white',
                            font=('Segoe UI', 8, 'bold'),
                            padx=8, pady=2)
        count_label.pack(side=tk.RIGHT)
        
        # Create main scroll area
        scroll_container = tk.Frame(selection_container, bg=self.COLORS['accent'], relief='solid', bd=1)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Create canvas and scrollbar PROPERLY
        self.canvas = tk.Canvas(scroll_container, 
                               bg=self.COLORS['bg_primary'],
                               highlightthickness=0)
        
        self.scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        
        # IMPORTANT: Pack scrollbar first, then canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_primary'])
        
        # Create canvas window ONLY ONCE
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind configuration events SAFELY
        def update_scrollregion(event=None):
            try:
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except tk.TclError:
                pass  # Widget might be destroyed
        
        def update_canvas_width(event=None):
            try:
                if self.canvas_window and event:
                    self.canvas.itemconfig(self.canvas_window, width=event.width)
            except tk.TclError:
                pass  # Widget might be destroyed
        
        # Bind events
        self.scrollable_frame.bind("<Configure>", update_scrollregion)
        self.canvas.bind("<Configure>", update_canvas_width)
        
        # SIMPLIFIED mousewheel binding
        def on_mousewheel(event):
            try:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        # Bind mousewheel events safely
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
    
    def create_plot_options(self, parent):
        """Create modern plot options controls"""
        options_container = tk.Frame(parent, bg=self.COLORS['bg_secondary'])
        options_container.pack(fill=tk.X, padx=20, pady=(15, 20))
        
        # Section header
        header_frame = tk.Frame(options_container, bg=self.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(header_frame,
                text="⚙️ Plot Options",
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Options
        options_frame = tk.Frame(options_container, bg=self.COLORS['bg_secondary'])
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Separate plots option
        separate_frame = tk.Frame(options_frame, bg=self.COLORS['bg_secondary'])
        separate_frame.pack(fill=tk.X, pady=(0, 8))
        
        separate_cb = tk.Checkbutton(separate_frame,
                                   text="Separate plots by data type",
                                   variable=self.separate_plots_var,
                                   command=self._on_plot_option_change,
                                   bg=self.COLORS['bg_secondary'],
                                   fg=self.COLORS['text_primary'],
                                   font=('Segoe UI', 9),
                                   activebackground=self.COLORS['bg_secondary'],
                                   activeforeground=self.COLORS['text_primary'],
                                   selectcolor=self.COLORS['accent'],
                                   relief='flat',
                                   borderwidth=0)
        separate_cb.pack(anchor=tk.W)
        
        # Show grid option
        grid_frame = tk.Frame(options_frame, bg=self.COLORS['bg_secondary'])
        grid_frame.pack(fill=tk.X)
        
        grid_cb = tk.Checkbutton(grid_frame,
                               text="Show grid lines",
                               variable=self.show_grid_var,
                               command=self._on_plot_option_change,
                               bg=self.COLORS['bg_secondary'],
                               fg=self.COLORS['text_primary'],
                               font=('Segoe UI', 9),
                               activebackground=self.COLORS['bg_secondary'],
                               activeforeground=self.COLORS['text_primary'],
                               selectcolor=self.COLORS['accent'],
                               relief='flat',
                               borderwidth=0)
        grid_cb.pack(anchor=tk.W)
    
    def update_data_categories(self, data_categories: Dict[str, pd.DataFrame]):
        """Update data categories and create modern checkboxes"""
        self.data_categories = data_categories
        self.clear_selection_widgets()
        self.create_selection_widgets()
        self.update_selection_count()
    
    def clear_selection_widgets(self):
        """Clear existing selection widgets SAFELY"""
        # Clear selection variables
        self.selection_vars.clear()
        
        # Destroy children safely
        if self.scrollable_frame:
            for child in self.scrollable_frame.winfo_children():
                try:
                    child.destroy()
                except:
                    pass
        
        # Force update the canvas scroll region
        if self.canvas:
            try:
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
    
    def create_selection_widgets(self):
        """Create modern checkboxes for data selection"""
        if not self.data_categories:
            # Show empty state
            empty_frame = tk.Frame(self.scrollable_frame, bg=self.COLORS['bg_primary'])
            empty_frame.pack(fill=tk.X, padx=20, pady=40)
            
            tk.Label(empty_frame,
                    text="📊",
                    bg=self.COLORS['bg_primary'],
                    fg=self.COLORS['text_secondary'],
                    font=('Segoe UI', 24)).pack(pady=(0, 10))
            
            tk.Label(empty_frame,
                    text="No data available",
                    bg=self.COLORS['bg_primary'],
                    fg=self.COLORS['text_primary'],
                    font=('Segoe UI', 11, 'bold')).pack(pady=(0, 5))
            
            tk.Label(empty_frame,
                    text="Select a session to begin analysis",
                    bg=self.COLORS['bg_primary'],
                    fg=self.COLORS['text_secondary'],
                    font=('Segoe UI', 9)).pack()
            return
        
        # Group data by category
        categories = self.group_data_by_category()
        
        for category_name, category_data in categories.items():
            # Create category card
            category_card = tk.Frame(self.scrollable_frame, 
                                   bg=self.COLORS['bg_tertiary'],
                                   relief='flat', bd=1)
            category_card.pack(fill=tk.X, padx=10, pady=(0, 8))
            
            # Category header
            header_frame = tk.Frame(category_card, bg=self.COLORS['bg_tertiary'])
            header_frame.pack(fill=tk.X, padx=10, pady=(8, 5))
            
            # Category name
            category_icon = self.get_category_icon(category_name)
            header_label = tk.Label(header_frame,
                                  text=f"{category_icon} {category_name}",
                                  bg=self.COLORS['bg_tertiary'],
                                  fg=self.COLORS['text_primary'],
                                  font=('Segoe UI', 9, 'bold'))
            header_label.pack(side=tk.LEFT)
            
            # Category controls
            self.create_category_controls(header_frame, category_name, category_data)
            
            # Data items
            content_frame = tk.Frame(category_card, bg=self.COLORS['bg_tertiary'])
            content_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
            
            # Create checkboxes for each data field
            for data_key, columns in category_data.items():
                self.create_data_checkboxes(content_frame, data_key, columns)
    
    def get_category_icon(self, category_name):
        """Get icon for category"""
        icons = {
            'rov_data': '🤖',
            'sensor_data': '📡',
            'Other': '📋'
        }
        return icons.get(category_name, '📄')
    
    def group_data_by_category(self) -> Dict[str, Dict[str, list]]:
        """Group data files by their category"""
        categories = {}
        
        for data_key, df in self.data_categories.items():
            # Extract category from data key
            if '/' in data_key:
                category = data_key.split('/')[0]
            else:
                category = "Other"
            
            if category not in categories:
                categories[category] = {}
            
            # Get available columns (excluding timestamp)
            columns = [col for col in df.columns if col != 'timestamp']
            categories[category][data_key] = columns
        
        return categories
    
    def create_category_controls(self, parent, category_name: str, category_data: Dict[str, list]):
        """Create category-level selection controls"""
        controls_frame = tk.Frame(parent, bg=self.COLORS['bg_tertiary'])
        controls_frame.pack(side=tk.RIGHT)
        
        # Select all button
        select_btn = tk.Button(controls_frame,
                             text="All",
                             command=lambda: self.select_category_data(category_data, True),
                             bg=self.COLORS['accent_light'],
                             fg=self.COLORS['accent'],
                             font=('Segoe UI', 7),
                             relief='flat',
                             borderwidth=0,
                             padx=8, pady=4)
        select_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear all button
        clear_btn = tk.Button(controls_frame,
                            text="None",
                            command=lambda: self.select_category_data(category_data, False),
                            bg=self.COLORS['bg_primary'],
                            fg=self.COLORS['text_secondary'],
                            font=('Segoe UI', 7),
                            relief='flat',
                            borderwidth=1,
                            padx=8, pady=4)
        clear_btn.pack(side=tk.LEFT)
    
    def create_data_checkboxes(self, parent, data_key: str, columns: list):
        """Create checkboxes for data columns"""
        file_frame = tk.Frame(parent, bg=self.COLORS['bg_tertiary'])
        file_frame.pack(fill=tk.X, pady=(0, 6))
        
        # File label
        file_name = data_key.split('/')[-1] if '/' in data_key else data_key
        file_label = tk.Label(file_frame,
                            text=f"📄 {file_name}:",
                            bg=self.COLORS['bg_tertiary'],
                            fg=self.COLORS['text_primary'],
                            font=('Segoe UI', 8, 'bold'))
        file_label.pack(anchor=tk.W, padx=(5, 0))
        
        # Create checkboxes for each column
        for column in columns:
            var = tk.BooleanVar()
            full_key = f"{data_key}/{column}"
            self.selection_vars[full_key] = var
            
            checkbox_frame = tk.Frame(file_frame, bg=self.COLORS['bg_tertiary'])
            checkbox_frame.pack(fill=tk.X, padx=(15, 0), pady=1)
            
            checkbox = tk.Checkbutton(checkbox_frame,
                                    text=self.format_column_name(column),
                                    variable=var,
                                    command=self._on_selection_change,
                                    bg=self.COLORS['bg_tertiary'],
                                    fg=self.COLORS['text_primary'],
                                    font=('Segoe UI', 8),
                                    activebackground=self.COLORS['bg_tertiary'],
                                    activeforeground=self.COLORS['text_primary'],
                                    selectcolor=self.COLORS['accent'],
                                    relief='flat',
                                    borderwidth=0)
            checkbox.pack(anchor=tk.W)
    
    def format_column_name(self, column: str) -> str:
        """Format column name for display"""
        formatted = column.replace('_', ' ').title()
        
        # Handle common abbreviations
        replacements = {
            'Temp': 'Temperature',
            'Mbar': 'mBar',
            'Pct': '%',
            'M': 'm',
            'C': '°C'
        }
        
        for old, new in replacements.items():
            formatted = formatted.replace(old, new)
        
        return formatted
    
    def update_selection_count(self):
        """Update the selection count badge"""
        if self.selection_count_var:
            count = self.get_selected_count()
            self.selection_count_var.set(str(count))
    
    # Event handlers
    def _on_selection_change(self):
        """Handle data selection change"""
        self.update_selection_count()
        if self.on_selection_change:
            self.on_selection_change()
    
    def _on_plot_option_change(self):
        """Handle plot option change"""
        if self.on_plot_option_change:
            self.on_plot_option_change()
    
    # Public interface methods
    def get_selection_vars(self) -> Dict[str, tk.BooleanVar]:
        """Get all selection variables"""
        return self.selection_vars
    
    def get_separate_plots_option(self) -> bool:
        """Get separate plots option"""
        return self.separate_plots_var.get()
    
    def get_show_grid_option(self) -> bool:
        """Get show grid option"""
        return self.show_grid_var.get()
    
    def select_all_data(self):
        """Select all data series"""
        for var in self.selection_vars.values():
            var.set(True)
        self._on_selection_change()
    
    def clear_all_data(self):
        """Clear all data selections"""
        for var in self.selection_vars.values():
            var.set(False)
        self._on_selection_change()
    
    def select_category_data(self, category_data: Dict[str, list], select: bool):
        """Select/deselect all data in a category"""
        for data_key, columns in category_data.items():
            for column in columns:
                full_key = f"{data_key}/{column}"
                if full_key in self.selection_vars:
                    self.selection_vars[full_key].set(select)
        self._on_selection_change()
    
    def get_selected_count(self) -> int:
        """Get count of selected data series"""
        return sum(1 for var in self.selection_vars.values() if var.get())