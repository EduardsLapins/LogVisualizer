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
from gui.control_panel import ControlPanel

class DroneLogAnalyzer:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize data components
        self.data_loader = DataLoader()
        self.data_filter = DataFilter()
        
        # Data storage
        self.sessions = {}
        self.current_session = None
        self.session_data = {}
        self.selected_data_vars = {}
        
        # GUI components
        self.control_panel = None
        self.data_panel = None
        self.plot_manager = None
        self.canvas = None
        
        # Create GUI
        self.create_gui()
        
        # Load default folder if exists
        if os.path.exists("drone_logs"):
            self.load_sessions("drone_logs")
    
    def create_gui(self):
        """Create the main GUI layout"""
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create control panel at top
        self.control_panel = ControlPanel(
            main_frame, 
            on_folder_browse=self.browse_folder,
            on_session_change=self.on_session_change,
            on_refresh=self.refresh_sessions,
            on_time_filter=self.apply_time_filter,
            on_reset_filter=self.reset_time_filter
        )
        self.control_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Create main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for data selection
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.data_panel = DataSelectionPanel(
            left_frame,
            on_selection_change=self.on_data_selection_change,
            on_plot_option_change=self.update_plots
        )
        self.data_panel.pack(fill=tk.BOTH, expand=True)
        
        # Create right panel for plots
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_plot_area(right_frame)
        
        # Create status bar
        self.create_status_bar(main_frame)
    
    def create_plot_area(self, parent):
        """Create the plotting area with matplotlib"""
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        self.plot_manager = PlotManager(self.figure)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create navigation toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(5, 0))
        
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Add custom toolbar buttons
        self.add_custom_toolbar_buttons(toolbar_frame)
    
    def add_custom_toolbar_buttons(self, toolbar_frame):
        """Add custom buttons to toolbar"""
        custom_frame = ttk.Frame(toolbar_frame)
        custom_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Export button
        ttk.Button(custom_frame, text="Export Plot", 
                  command=self.export_plot).pack(side=tk.LEFT, padx=(5, 0))
        
        # Statistics button
        ttk.Button(custom_frame, text="Show Stats", 
                  command=self.show_statistics).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # Add session info on right side
        self.session_info_var = tk.StringVar()
        session_info_label = ttk.Label(self.status_frame, textvariable=self.session_info_var)
        session_info_label.pack(side=tk.RIGHT)
    
    def browse_folder(self):
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
            session_name = self.control_panel.get_current_session()
        
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
        """Show statistics about current data"""
        filtered_data = self.get_filtered_data()
        
        if not filtered_data:
            messagebox.showinfo("No Data", "No data selected for statistics")
            return
        
        try:
            stats = self.plot_manager.get_plot_statistics(filtered_data)
            
            # Create statistics window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Data Statistics")
            stats_window.geometry("500x400")
            stats_window.resizable(True, True)
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(stats_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Format statistics
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