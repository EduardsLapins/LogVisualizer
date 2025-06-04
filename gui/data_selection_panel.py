"""
Data Selection Panel GUI Component
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
        
        # GUI components - initialize canvas and scrollbar
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.canvas_window = None
        
        # Configure styling
        self.configure(style='Card.TFrame')
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all panel widgets with modern styling"""
        # Set minimum width - more compact
        self.configure(width=300)  # Reduced from 320
        
        # Main container
        main_frame = tk.Frame(self, bg=self.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section - more compact
        self.create_header(main_frame)
        # Data selection area
        self.create_data_selection_area(main_frame)
        
        # Plot options
        self.create_plot_options(main_frame)
    
    def create_header(self, parent):
        """Create compact header"""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'], height=45)  # Reduced height
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 0))  # Reduced padding
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame,
                             text="📊 Data Selection",
                             bg=self.COLORS['bg_primary'],
                             fg=self.COLORS['text_primary'],
                             font=('Segoe UI', 11, 'bold'))  # Slightly smaller font
        title_label.pack(anchor=tk.W, pady=(8, 0))  # Reduced padding
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                text="Choose data series to visualize",
                                bg=self.COLORS['bg_primary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 8))  # Smaller font
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
    

    def create_data_selection_area(self, parent):
        """Create modern scrollable data selection area"""
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
        
        # Create FIXED scrollable area
        scroll_container = tk.Frame(selection_container, bg=self.COLORS['bg_secondary'])
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Create canvas and scrollbar with proper sizing
        self.canvas = tk.Canvas(scroll_container, 
                               bg=self.COLORS['bg_primary'],
                               highlightthickness=0,
                               relief='flat',
                               height=400)  # Fixed height to ensure proper scrolling
        
        self.scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_primary'])
        
        # Configure scrolling properly
        def configure_scrollregion(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        def configure_canvas(event=None):
            # Update the width of the scrollable frame to match canvas
            canvas_width = event.width if event else self.canvas.winfo_width()
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.scrollable_frame.bind("<Configure>", configure_scrollregion)
        self.canvas.bind("<Configure>", configure_canvas)
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack components with proper layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # FIXED mousewheel binding - bind to multiple widgets
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)  # Windows
            widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux up
            widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))   # Linux down
        
        # Bind mousewheel to canvas and scrollable frame
        bind_mousewheel(self.canvas)
        bind_mousewheel(self.scrollable_frame)
        
        # Also bind to the main container to catch mouse events
        bind_mousewheel(scroll_container)
    
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
        
        # Separate plots option with modern checkbox
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
        
        # Add tooltips
        self.create_tooltip(separate_cb, "Group similar data types in separate subplots")
        self.create_tooltip(grid_cb, "Show grid lines on plots for better readability")
    
    def add_hover_effect(self, widget, normal_color, hover_color):
        """Add hover effect to button"""
        def on_enter(event):
            widget.configure(bg=hover_color)
        
        def on_leave(event):
            widget.configure(bg=normal_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def create_tooltip(self, widget, text):
        """Create a modern tooltip for a widget - FIXED to prevent artifacts"""
        def on_enter(event):
            # Destroy any existing tooltip first
            if hasattr(widget, 'tooltip'):
                try:
                    widget.tooltip.destroy()
                except:
                    pass
                delattr(widget, 'tooltip')
            
            # Create new tooltip
            try:
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                tooltip.configure(bg=self.COLORS['text_primary'])
                
                # Ensure tooltip stays on top but not always
                tooltip.attributes('-topmost', True)
                
                label = tk.Label(tooltip, 
                               text=text, 
                               bg=self.COLORS['text_primary'],
                               fg='white',
                               font=('Segoe UI', 8),
                               padx=10, pady=6)
                label.pack()
                
                widget.tooltip = tooltip
                
                # Auto-destroy tooltip after 5 seconds to prevent artifacts
                tooltip.after(5000, lambda: on_leave(None))
                
            except Exception as e:
                print(f"Tooltip error: {e}")
        
        def on_leave(event):
            try:
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    delattr(widget, 'tooltip')
            except Exception:
                pass
        
        # Clean up any existing bindings first
        widget.unbind('<Enter>')
        widget.unbind('<Leave>')
        
        # Bind new events
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
        # Also bind to focus events to clean up tooltips
        try:
            widget.bind('<FocusOut>', on_leave)
            widget.bind('<Button-1>', on_leave)  # Clean up on click
        except:
            pass
    
    def update_data_categories(self, data_categories: Dict[str, pd.DataFrame]):
        """Update data categories and create modern checkboxes"""
        self.data_categories = data_categories
        self.clear_selection_widgets()
        self.create_selection_widgets()
        self.update_category_dropdown()
        self.update_selection_count()
    
    def clear_selection_widgets(self):
        """Clear existing selection widgets - FIXED to prevent artifacts"""
        # Clean up tooltips first
        for widget in self.scrollable_frame.winfo_children():
            self._cleanup_widget_tooltips(widget)
            widget.destroy()
        
        # Clear selection variables
        self.selection_vars.clear()
        
        # Force update the canvas scroll region
        if self.canvas:
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _cleanup_widget_tooltips(self, widget):
        """Recursively clean up tooltips for a widget and its children"""
        try:
            # Clean up tooltip for this widget
            if hasattr(widget, 'tooltip'):
                try:
                    widget.tooltip.destroy()
                except:
                    pass
                delattr(widget, 'tooltip')
            
            # Clean up tooltips for children
            for child in widget.winfo_children():
                self._cleanup_widget_tooltips(child)
                
        except Exception:
            pass  # Ignore errors during cleanup
    
    def create_selection_widgets(self):
        """Create modern checkboxes for data selection"""
        if not self.data_categories:
            # Show modern empty state
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
        
        # Group data by category for better organization
        categories = self.group_data_by_category()
        
        for i, (category_name, category_data) in enumerate(categories.items()):
            # Create modern category card - more compact
            category_card = tk.Frame(self.scrollable_frame, 
                                   bg=self.COLORS['bg_tertiary'],
                                   relief='flat', bd=1,
                                   highlightbackground=self.COLORS['border_light'])
            category_card.pack(fill=tk.X, padx=10, pady=(0, 8))  # Reduced padding
            
            # Category header with modern styling - more compact
            header_frame = tk.Frame(category_card, bg=self.COLORS['bg_tertiary'])
            header_frame.pack(fill=tk.X, padx=10, pady=(8, 5))  # Reduced padding
            
            # Category icon and name
            category_icon = self.get_category_icon(category_name)
            header_label = tk.Label(header_frame,
                                  text=f"{category_icon} {category_name}",
                                  bg=self.COLORS['bg_tertiary'],
                                  fg=self.COLORS['text_primary'],
                                  font=('Segoe UI', 9, 'bold'))  # Smaller font
            header_label.pack(side=tk.LEFT)
            
            # Category controls
            self.create_category_controls(header_frame, category_name, category_data)
            
            # Data items
            content_frame = tk.Frame(category_card, bg=self.COLORS['bg_tertiary'])
            content_frame.pack(fill=tk.X, padx=10, pady=(0, 8))  # Reduced padding
            
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
        """Create modern category-level selection controls"""
        controls_frame = tk.Frame(parent, bg=self.COLORS['bg_tertiary'])
        controls_frame.pack(side=tk.RIGHT)
        
        # Small modern buttons for category selection
        select_cat_btn = tk.Button(controls_frame,
                                 text="All",
                                 command=lambda: self.select_category_data(category_data, True),
                                 bg=self.COLORS['accent_light'],
                                 fg=self.COLORS['accent'],
                                 font=('Segoe UI', 7),
                                 relief='flat',
                                 borderwidth=0,
                                 padx=8, pady=4,
                                 cursor='hand2')
        select_cat_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_cat_btn = tk.Button(controls_frame,
                                text="None",
                                command=lambda: self.select_category_data(category_data, False),
                                bg=self.COLORS['bg_primary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 7),
                                relief='flat',
                                borderwidth=1,
                                highlightbackground=self.COLORS['border'],
                                padx=8, pady=4,
                                cursor='hand2')
        clear_cat_btn.pack(side=tk.LEFT)
        
        # Add hover effects
        self.add_hover_effect(select_cat_btn, self.COLORS['accent_light'], self.COLORS['accent'])
        self.add_hover_effect(clear_cat_btn, self.COLORS['bg_primary'], self.COLORS['border_light'])
        
        # Add tooltips
        self.create_tooltip(select_cat_btn, f"Select all data in {category_name}")
        self.create_tooltip(clear_cat_btn, f"Deselect all data in {category_name}")
    
    def create_data_checkboxes(self, parent, data_key: str, columns: list):
        """Create modern checkboxes for data columns"""
        file_frame = tk.Frame(parent, bg=self.COLORS['bg_tertiary'])
        file_frame.pack(fill=tk.X, pady=(0, 6))  # Reduced padding
        
        # File label with modern styling - more compact
        file_name = data_key.split('/')[-1] if '/' in data_key else data_key
        file_label = tk.Label(file_frame,
                            text=f"📄 {file_name}:",
                            bg=self.COLORS['bg_tertiary'],
                            fg=self.COLORS['text_primary'],
                            font=('Segoe UI', 8, 'bold'))  # Smaller font
        file_label.pack(anchor=tk.W, padx=(5, 0))  # Reduced padding
        
        # Create modern checkboxes for each column - more compact
        for column in columns:
            var = tk.BooleanVar()
            full_key = f"{data_key}/{column}"
            self.selection_vars[full_key] = var
            
            checkbox_frame = tk.Frame(file_frame, bg=self.COLORS['bg_tertiary'])
            checkbox_frame.pack(fill=tk.X, padx=(15, 0), pady=1)  # Reduced padding
            
            checkbox = tk.Checkbutton(checkbox_frame,
                                    text=self.format_column_name(column),
                                    variable=var,
                                    command=self._on_selection_change,
                                    bg=self.COLORS['bg_tertiary'],
                                    fg=self.COLORS['text_primary'],
                                    font=('Segoe UI', 8),  # Smaller font
                                    activebackground=self.COLORS['bg_tertiary'],
                                    activeforeground=self.COLORS['text_primary'],
                                    selectcolor=self.COLORS['accent'],
                                    relief='flat',
                                    borderwidth=0)
            checkbox.pack(anchor=tk.W)
            
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
                stats_text += f"Points: {len(series):,}\n"
                stats_text += f"Range: {series.min():.3f} to {series.max():.3f}\n"
                stats_text += f"Mean: {series.mean():.3f}"
            else:
                stats_text = f"Data: {column}\n"
                stats_text += f"Points: {len(series):,}\n"
                stats_text += f"Type: {series.dtype}"
            
            self.create_tooltip(widget, stats_text)
        except Exception:
            self.create_tooltip(widget, f"Data: {column}")
    
    def update_category_dropdown(self):
        """Update the category dropdown options"""
        
        categories = set()
        for data_key in self.data_categories.keys():
            if '/' in data_key:
                category = data_key.split('/')[0]
                categories.add(category)
        
        category_list = ['All Categories'] + sorted(categories)
    
    def update_selection_count(self):
        """Update the selection count badge"""
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