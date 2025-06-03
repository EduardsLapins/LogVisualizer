"""
Data Selection Panel GUI Component
Handles data series selection and plot options
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable
import pandas as pd

class DataSelectionPanel(ttk.Frame):
    """Panel for selecting data series and plot options"""
    
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
        
        # GUI components
        self.scrollable_frame = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all panel widgets"""
        # Set minimum width
        self.configure(width=280)
        
        # Data selection frame
        self.create_data_selection_area()
        
        # Plot options frame
        self.create_plot_options()
        
        # Selection controls
        self.create_selection_controls()
    
    def create_data_selection_area(self):
        """Create scrollable data selection area"""
        selection_frame = ttk.LabelFrame(self, text="Data Selection", padding=5)
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable area
        canvas = tk.Canvas(selection_frame, width=250, highlightthickness=0)
        scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
    
    def create_plot_options(self):
        """Create plot options controls"""
        options_frame = ttk.LabelFrame(self, text="Plot Options", padding=5)
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Separate plots option
        separate_cb = ttk.Checkbutton(
            options_frame, 
            text="Separate plots by data type", 
            variable=self.separate_plots_var,
            command=self._on_plot_option_change
        )
        separate_cb.pack(anchor=tk.W, pady=(0, 2))
        
        # Show grid option
        grid_cb = ttk.Checkbutton(
            options_frame, 
            text="Show grid", 
            variable=self.show_grid_var,
            command=self._on_plot_option_change
        )
        grid_cb.pack(anchor=tk.W, pady=(0, 2))
        
        # Add tooltips
        self.create_tooltip(separate_cb, "Group similar data types in separate subplots")
        self.create_tooltip(grid_cb, "Show grid lines on plots")
    
    def create_selection_controls(self):
        """Create bulk selection controls"""
        controls_frame = ttk.LabelFrame(self, text="Selection Controls", padding=5)
        controls_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Button frame
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X)
        
        # Select all button
        select_all_btn = ttk.Button(
            btn_frame, 
            text="Select All", 
            command=self.select_all_data,
            width=12
        )
        select_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear all button
        clear_all_btn = ttk.Button(
            btn_frame, 
            text="Clear All", 
            command=self.clear_all_data,
            width=12
        )
        clear_all_btn.pack(side=tk.LEFT)
        
        # Category selection dropdown
        category_frame = ttk.Frame(controls_frame)
        category_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(category_frame, text="Quick select:").pack(side=tk.LEFT)
        
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            category_frame, 
            textvariable=self.category_var,
            state='readonly',
            width=15
        )
        category_combo.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        category_combo.bind('<<ComboboxSelected>>', self._on_category_selected)
        
        self.category_combo = category_combo
        
        # Add tooltips
        self.create_tooltip(select_all_btn, "Select all available data series")
        self.create_tooltip(clear_all_btn, "Deselect all data series")
        self.create_tooltip(category_combo, "Select all data from a specific category")
    
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
    
    def update_data_categories(self, data_categories: Dict[str, pd.DataFrame]):
        """Update data categories and create checkboxes"""
        self.data_categories = data_categories
        self.clear_selection_widgets()
        self.create_selection_widgets()
        self.update_category_dropdown()
    
    def clear_selection_widgets(self):
        """Clear existing selection widgets"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.selection_vars.clear()
    
    def create_selection_widgets(self):
        """Create checkboxes for data selection"""
        if not self.data_categories:
            # Show message when no data
            no_data_label = ttk.Label(
                self.scrollable_frame, 
                text="No data available.\nSelect a session to begin.",
                foreground='gray',
                justify=tk.CENTER
            )
            no_data_label.pack(pady=20)
            return
        
        # Group data by category for better organization
        categories = self.group_data_by_category()
        
        for category_name, category_data in categories.items():
            # Create category frame
            category_frame = ttk.LabelFrame(
                self.scrollable_frame, 
                text=category_name, 
                padding=5
            )
            category_frame.pack(fill=tk.X, pady=2, padx=2)
            
            # Add category-level controls
            self.create_category_controls(category_frame, category_name, category_data)
            
            # Create checkboxes for each data field
            for data_key, columns in category_data.items():
                self.create_data_checkboxes(category_frame, data_key, columns)
    
    def group_data_by_category(self) -> Dict[str, Dict[str, list]]:
        """Group data files by their category"""
        categories = {}
        
        for data_key, df in self.data_categories.items():
            # Extract category from data key (e.g., "rov_data/depth.log" -> "rov_data")
            if '/' in data_key:
                category = data_key.split('/')[0]
                file_name = data_key.split('/')[-1]
            else:
                category = "Other"
                file_name = data_key
            
            if category not in categories:
                categories[category] = {}
            
            # Get available columns (excluding timestamp)
            columns = [col for col in df.columns if col != 'timestamp']
            categories[category][data_key] = columns
        
        return categories
    
    def create_category_controls(self, parent, category_name: str, category_data: Dict[str, list]):
        """Create category-level selection controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Small buttons for category selection
        select_cat_btn = ttk.Button(
            controls_frame, 
            text="All", 
            command=lambda: self.select_category_data(category_data, True),
            width=6
        )
        select_cat_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        clear_cat_btn = ttk.Button(
            controls_frame, 
            text="None", 
            command=lambda: self.select_category_data(category_data, False),
            width=6
        )
        clear_cat_btn.pack(side=tk.LEFT)
        
        # Add tooltips
        self.create_tooltip(select_cat_btn, f"Select all data in {category_name}")
        self.create_tooltip(clear_cat_btn, f"Deselect all data in {category_name}")
    
    def create_data_checkboxes(self, parent, data_key: str, columns: list):
        """Create checkboxes for data columns"""
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.X, pady=1)
        
        # File label
        file_name = data_key.split('/')[-1] if '/' in data_key else data_key
        file_label = ttk.Label(file_frame, text=f"{file_name}:", font=('TkDefaultFont', 8, 'bold'))
        file_label.pack(anchor=tk.W)
        
        # Create checkboxes for each column
        for column in columns:
            var = tk.BooleanVar()
            full_key = f"{data_key}/{column}"
            self.selection_vars[full_key] = var
            
            checkbox = ttk.Checkbutton(
                file_frame,
                text=self.format_column_name(column),
                variable=var,
                command=self._on_selection_change
            )
            checkbox.pack(anchor=tk.W, padx=(15, 0))
            
            # Add tooltip with data info
            self.create_data_tooltip(checkbox, data_key, column)
    
    def format_column_name(self, column: str) -> str:
        """Format column name for display"""
        # Replace underscores with spaces and capitalize
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
    
    def create_data_tooltip(self, widget, data_key: str, column: str):
        """Create tooltip with data information"""
        if data_key not in self.data_categories:
            return
        
        df = self.data_categories[data_key]
        if column not in df.columns:
            return
        
        try:
            # Get basic statistics
            series = df[column]
            if series.dtype in ['int64', 'float64']:
                stats_text = f"Data: {column}\n"
                stats_text += f"Points: {len(series)}\n"
                stats_text += f"Range: {series.min():.3f} to {series.max():.3f}\n"
                stats_text += f"Mean: {series.mean():.3f}"
            else:
                stats_text = f"Data: {column}\n"
                stats_text += f"Points: {len(series)}\n"
                stats_text += f"Type: {series.dtype}"
            
            self.create_tooltip(widget, stats_text)
        except Exception:
            self.create_tooltip(widget, f"Data: {column}")
    
    def update_category_dropdown(self):
        """Update the category dropdown options"""
        if not self.data_categories:
            self.category_combo['values'] = []
            return
        
        categories = set()
        for data_key in self.data_categories.keys():
            if '/' in data_key:
                category = data_key.split('/')[0]
                categories.add(category)
        
        category_list = ['All Categories'] + sorted(categories)
        self.category_combo['values'] = category_list
    
    # Event handlers
    def _on_selection_change(self):
        """Handle data selection change"""
        if self.on_selection_change:
            self.on_selection_change()
    
    def _on_plot_option_change(self):
        """Handle plot option change"""
        if self.on_plot_option_change:
            self.on_plot_option_change()
    
    def _on_category_selected(self, event=None):
        """Handle category selection from dropdown"""
        category = self.category_var.get()
        if category == 'All Categories':
            self.select_all_data()
        elif category:
            self.select_category_by_name(category)
    
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
    
    def select_category_by_name(self, category_name: str):
        """Select all data in a named category"""
        for data_key in self.data_categories.keys():
            if data_key.startswith(f"{category_name}/"):
                df = self.data_categories[data_key]
                columns = [col for col in df.columns if col != 'timestamp']
                for column in columns:
                    full_key = f"{data_key}/{column}"
                    if full_key in self.selection_vars:
                        self.selection_vars[full_key].set(True)
        self._on_selection_change()
    
    def get_selected_count(self) -> int:
        """Get count of selected data series"""
        return sum(1 for var in self.selection_vars.values() if var.get())
    
    def set_selection_by_pattern(self, pattern: str, select: bool = True):
        """Select data series matching a pattern"""
        pattern_lower = pattern.lower()
        for data_key, var in self.selection_vars.items():
            if pattern_lower in data_key.lower():
                var.set(select)
        self._on_selection_change()