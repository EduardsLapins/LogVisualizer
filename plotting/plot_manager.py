"""
Plot Manager Module
Handles all plotting and visualization functionality with modern styling
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime
from typing import Dict, List, Tuple, Any
import pandas as pd

class DataGrouper:
    """Groups data by similar characteristics for separate plotting"""
    
    # Define data groups with their characteristics
    DATA_GROUPS = {
        'Depth & Pressure': {
            'keywords': ['depth', 'pressure', 'altitude'],
            'units': ['m', 'mbar'],
            'color_scheme': 'Blues',
            'icon': '🌊'
        },
        'Temperature': {
            'keywords': ['temp', 'temperature'],
            'units': ['°C', 'celsius'],
            'color_scheme': 'Reds',
            'icon': '🌡️'
        },
        'Orientation': {
            'keywords': ['roll', 'pitch', 'yaw', 'orientation'],
            'units': ['degrees', '°'],
            'color_scheme': 'Greens',
            'icon': '🧭'
        },
        'Voltage & Current': {
            'keywords': ['voltage', 'current'],
            'units': ['V', 'A', 'mA'],
            'color_scheme': 'Oranges',
            'icon': '⚡'
        },
        'Motor Data': {
            'keywords': ['motor'],
            'units': ['PWM', 'inputs'],
            'color_scheme': 'Purples',
            'icon': '⚙️'
        },
        'Sonar & Distance': {
            'keywords': ['sonar', 'distance', 'confidence'],
            'units': ['m', '%'],
            'color_scheme': 'Greys',
            'icon': '📡'
        }
    }
    
    @classmethod
    def group_data(cls, data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Group data by similar characteristics"""
        groups = {group_name: {} for group_name in cls.DATA_GROUPS.keys()}
        groups['Other'] = {}
        
        for data_key, data_info in data.items():
            group_name = cls._classify_data(data_key, data_info)
            groups[group_name][data_key] = data_info
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    @classmethod
    def _classify_data(cls, data_key: str, data_info: Dict[str, Any]) -> str:
        """Classify data into appropriate group"""
        data_key_lower = data_key.lower()
        
        for group_name, group_config in cls.DATA_GROUPS.items():
            for keyword in group_config['keywords']:
                if keyword in data_key_lower:
                    return group_name
        
        return 'Other'

class PlotStyler:
    """Handles modern plot styling and aesthetics"""
    
    # Modern color palette
    MODERN_COLORS = [
        '#3b82f6',  # Blue
        '#ef4444',  # Red
        '#10b981',  # Green
        '#f59e0b',  # Orange
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        '#84cc16',  # Lime
        '#f97316',  # Orange
        '#ec4899',  # Pink
        '#6366f1',  # Indigo
    ]
    
    # Modern color schemes with VIBRANT colors for better readability
    COLOR_SCHEMES = {
        'default': MODERN_COLORS,
        'Blues': ['#1e40af', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'],
        'Reds': ['#dc2626', '#ef4444', '#f87171', '#fca5a5', '#fecaca', '#fee2e2'],
        'Greens': ['#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'],
        'Oranges': ['#ea580c', '#f97316', '#fb923c', '#fdba74', '#fed7aa', '#ffedd5'],
        'Purples': ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe'],
        'Greys': ['#374151', '#4b5563', '#6b7280', '#9ca3af', '#d1d5db', '#f3f4f6']
    }
    
    @staticmethod
    def get_colors(n_colors: int, scheme: str = 'default') -> List[str]:
        """Get modern color palette for plotting with VIBRANT colors"""
        if scheme in PlotStyler.COLOR_SCHEMES:
            colors = PlotStyler.COLOR_SCHEMES[scheme]
        else:
            colors = PlotStyler.MODERN_COLORS
        
        if n_colors <= len(colors):
            return colors[:n_colors]
        else:
            # Cycle through colors if we need more, but use the most vibrant ones first
            result = []
            for i in range(n_colors):
                color_idx = i % len(colors)
                result.append(colors[color_idx])
            return result
    
    @staticmethod
    def style_axis(ax, title: str = "", xlabel: str = "", ylabel: str = "", 
                  show_grid: bool = True, grid_alpha: float = 0.3):
        """Apply modern styling to axis with enhanced readability"""
        # Set clean background
        ax.set_facecolor('#ffffff')  # Pure white background for better contrast
        
        # Modern title styling with better contrast
        if title:
            ax.set_title(title, fontsize=13, fontweight='600', pad=15, 
                        color='#1e293b', fontfamily='sans-serif')
        
        # Modern axis labels with better visibility
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=11, fontweight='500', color='#374151')
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=11, fontweight='500', color='#374151')
        
        # Enhanced grid styling for better readability
        if show_grid:
            ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.8, color='#e5e7eb')
            ax.set_axisbelow(True)
        
        # Modern tick styling with better contrast
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#4b5563',
                      direction='out', length=4, width=1)
        
        # Clean spine styling
        for spine in ax.spines.values():
            spine.set_color('#d1d5db')
            spine.set_linewidth(1)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    @staticmethod
    def apply_modern_theme():
        """Apply modern theme to matplotlib"""
        # Set modern style parameters
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 11,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 9,
            'figure.titlesize': 16,
            'axes.linewidth': 1,
            'axes.edgecolor': '#e2e8f0',
            'axes.facecolor': '#fafafa',
            'figure.facecolor': '#ffffff',
            'grid.alpha': 0.3,
            'grid.color': '#cbd5e1',
            'grid.linewidth': 0.8,
            'lines.linewidth': 2.5,
            'lines.markersize': 6,
            'patch.linewidth': 0,
            'savefig.facecolor': '#ffffff',
            'savefig.edgecolor': 'none',
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.2
        })

class PlotManager:
    """Modern plot management class"""
    
    def __init__(self, figure: Figure):
        self.figure = figure
        self.styler = PlotStyler()
        self.grouper = DataGrouper()
        
        # Apply modern theme
        self.styler.apply_modern_theme()
        
        # Configure figure with modern styling
        self.figure.patch.set_facecolor('#ffffff')
        self.figure.patch.set_edgecolor('none')
    
    def clear_plots(self):
        """Clear all plots from figure"""
        self.figure.clear()
    
    def create_combined_plot(self, data: Dict[str, Dict[str, Any]], 
                           session_name: str = "", show_grid: bool = True):
        """Create a modern single combined plot with all data"""
        self.clear_plots()
        
        if not data:
            self._create_empty_state()
            return
        
        # Set appropriate figure size for combined plot
        self.figure.set_size_inches(12, 7)
        
        ax = self.figure.add_subplot(111)
        
        # Get modern colors for all data series - use vibrant colors
        colors = self.styler.get_colors(len(data))
        
        # Plot each data series with modern styling
        for (data_key, data_info), color in zip(data.items(), colors):
            self._plot_data_series_modern(ax, data_info, color, alpha=0.9)  # Higher alpha for better visibility
        
        # Apply modern styling
        title = f'📊 {session_name} - Data Overview' if session_name else '📊 Drone Data Overview'
        self.styler.style_axis(ax, title=title, xlabel='Time', ylabel='Value', show_grid=show_grid)
        
        # Enhanced legend for combined plots
        if len(data) > 1:
            # Position legend based on number of series
            if len(data) <= 6:
                legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', 
                                 fontsize=9, frameon=True, fancybox=True, 
                                 shadow=True, framealpha=1.0)
            else:
                # For many series, use a more compact legend
                legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', 
                                 fontsize=8, frameon=True, fancybox=True, 
                                 shadow=True, framealpha=1.0, ncol=1)
            
            if legend:
                legend.get_frame().set_facecolor('#ffffff')
                legend.get_frame().set_edgecolor('#e2e8f0')
                legend.get_frame().set_linewidth(1)
        
        # Format time axis with modern styling
        self.figure.autofmt_xdate()
        
        # Add modern styling touches with better spacing
        ax.margins(x=0.01, y=0.03)
        
        # Improved layout
        self.figure.tight_layout(rect=[0, 0.03, 0.85, 0.97])
        
        # Force a redraw
        self.figure.canvas.draw_idle()
    
    def create_separate_plots(self, data: Dict[str, Dict[str, Any]], 
                            session_name: str = "", show_grid: bool = True):
        """Create modern separate plots grouped by data type"""
        self.clear_plots()
        
        if not data:
            self._create_empty_state()
            return
        
        # Group data by type
        groups = self.grouper.group_data(data)
        n_groups = len(groups)
        
        if n_groups == 0:
            self._create_empty_state()
            return
        
        # Adjust figure size dynamically for better readability
        fig_width = 12
        fig_height = max(6, min(n_groups * 3, 16))  # Scale height but cap at 16
        self.figure.set_size_inches(fig_width, fig_height)
        
        # Create subplots with better spacing
        for i, (group_name, group_data) in enumerate(groups.items()):
            ax = self.figure.add_subplot(n_groups, 1, i + 1)
            
            if not group_data:
                continue
            
            # Get VIBRANT color scheme for this group - NO FADING
            color_scheme = self.grouper.DATA_GROUPS.get(group_name, {}).get('color_scheme', 'default')
            colors = self.styler.get_colors(len(group_data), color_scheme)
            
            # Plot data in this group with FULL OPACITY and better styling
            for (data_key, data_info), color in zip(group_data.items(), colors):
                self._plot_data_series_modern(ax, data_info, color, alpha=1.0)  # Full opacity!
            
            # Get group icon and style subplot
            group_icon = self.grouper.DATA_GROUPS.get(group_name, {}).get('icon', '📄')
            ylabel = self._get_group_ylabel(group_name, group_data)
            xlabel = 'Time' if i == n_groups - 1 else ''  # Only show xlabel on bottom plot
            
            modern_title = f"{group_icon} {group_name}"
            self.styler.style_axis(ax, title=modern_title, xlabel=xlabel, 
                                 ylabel=ylabel, show_grid=show_grid)
            
            # Modern legend for each subplot with better visibility
            if len(group_data) > 1:
                legend = ax.legend(fontsize=9, loc='best', frameon=True, 
                                 fancybox=True, shadow=True, framealpha=1.0)  # Solid background
                if legend:
                    legend.get_frame().set_facecolor('#ffffff')
                    legend.get_frame().set_edgecolor('#e2e8f0')
                    legend.get_frame().set_linewidth(1)
            
            # Add margins for better appearance and ensure full visibility
            ax.margins(x=0.01, y=0.02)
            
            # Improve subplot spacing to prevent overlap
            if i < n_groups - 1:  # Not the last subplot
                ax.tick_params(labelbottom=False)  # Hide x-axis labels except for bottom
        
        # Add modern overall title
        if session_name:
            self.figure.suptitle(f'🚁 {session_name} - Detailed Analysis', 
                               fontsize=14, fontweight='600', y=0.98, color='#1e293b')
        
        # Better layout with improved spacing to prevent overlap
        self.figure.tight_layout(rect=[0, 0.02, 1, 0.96], h_pad=2.5, w_pad=1.0)
        
        # Format time axis
        self.figure.autofmt_xdate()
        
        # Force a redraw to ensure proper sizing
        self.figure.canvas.draw_idle()
    
    def _create_empty_state(self):
        """Create modern empty state visualization"""
        ax = self.figure.add_subplot(111)
        
        # Remove axes for clean look
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Modern empty state message
        ax.text(0.5, 0.6, '📊', fontsize=48, ha='center', va='center', 
               transform=ax.transAxes, color='#cbd5e1')
        
        ax.text(0.5, 0.45, 'No Data Selected', fontsize=18, ha='center', va='center',
               transform=ax.transAxes, color='#64748b', fontweight='600')
        
        ax.text(0.5, 0.35, 'Select data series from the panel to visualize', 
               fontsize=12, ha='center', va='center',
               transform=ax.transAxes, color='#94a3b8')
        
        ax.set_facecolor('#fafafa')
    
    def _plot_data_series_modern(self, ax, data_info: Dict[str, Any], color: str, alpha: float = 0.8):
        """Plot a single data series with modern styling"""
        timestamps = data_info['timestamp']
        values = data_info['data']
        label = data_info['label']
        
        # Handle different data types
        if isinstance(values[0], str):
            # Convert string data to numeric if possible
            try:
                values = [float(v) if v != 'manual' else 0 for v in values]
            except (ValueError, TypeError):
                # Skip non-numeric string data
                return
        
        # Enhanced line styling based on data density and alpha
        if alpha >= 1.0:  # For separate plots - use thicker, more visible lines
            line_width = 3.0 if len(timestamps) > 1000 else 3.5
            marker_size = 6 if len(timestamps) < 100 else 0
        else:  # For combined plots
            line_width = 2.5 if len(timestamps) > 1000 else 2.8
            marker_size = 5 if len(timestamps) < 100 else 0
        
        # Plot the data with modern styling
        line = ax.plot(timestamps, values, label=label, color=color, 
                      alpha=alpha, linewidth=line_width, solid_capstyle='round',
                      zorder=3)  # Higher z-order for better visibility
        
        # Add modern markers for sparse data
        if marker_size > 0:
            line[0].set_marker('o')
            line[0].set_markersize(marker_size)
            line[0].set_markerfacecolor(color)
            line[0].set_markeredgecolor('white')
            line[0].set_markeredgewidth(1.5 if alpha >= 1.0 else 1)
            line[0].set_zorder(4)  # Markers on top
    
    def _get_group_ylabel(self, group_name: str, group_data: Dict[str, Dict[str, Any]]) -> str:
        """Get appropriate ylabel for a data group"""
        # Modern unit formatting
        common_units = {
            'Depth & Pressure': 'Depth (m) • Pressure (mbar)',
            'Temperature': 'Temperature (°C)',
            'Orientation': 'Angle (degrees)',
            'Voltage & Current': 'Voltage (V) • Current (A)',
            'Motor Data': 'PWM Value',
            'Sonar & Distance': 'Distance (m) • Confidence (%)',
            'Other': 'Value'
        }
        
        return common_units.get(group_name, 'Value')
    
    def add_time_markers(self, ax, events: List[Tuple[datetime, str]]):
        """Add modern vertical lines for important events"""
        for event_time, event_label in events:
            # Modern event line styling
            ax.axvline(x=event_time, color='#ef4444', linestyle='--', 
                      alpha=0.8, linewidth=2)
            
            # Modern event label
            ax.text(event_time, ax.get_ylim()[1] * 0.95, event_label, 
                   rotation=90, verticalalignment='top', fontsize=9,
                   color='#ef4444', fontweight='500',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           edgecolor='#ef4444', alpha=0.9))
    
    def export_plot(self, filename: str, dpi: int = 300, format: str = 'png'):
        """Export current plot to file with modern settings"""
        try:
            self.figure.savefig(filename, dpi=dpi, format=format, 
                              bbox_inches='tight', facecolor='white', 
                              edgecolor='none', pad_inches=0.2)
            return True
        except Exception as e:
            print(f"Error exporting plot: {e}")
            return False
    
    def get_plot_statistics(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the plotted data"""
        stats = {
            'total_series': len(data),
            'time_range': None,
            'data_points': 0,
            'series_info': {}
        }
        
        if not data:
            return stats
        
        # Calculate overall statistics
        all_timestamps = []
        total_points = 0
        
        for data_key, data_info in data.items():
            timestamps = data_info['timestamp']
            values = data_info['data']
            
            all_timestamps.extend(timestamps)
            total_points += len(timestamps)
            
            # Per-series statistics
            try:
                numeric_values = [float(v) for v in values if isinstance(v, (int, float))]
                if numeric_values:
                    stats['series_info'][data_key] = {
                        'points': len(timestamps),
                        'min_value': min(numeric_values),
                        'max_value': max(numeric_values),
                        'mean_value': sum(numeric_values) / len(numeric_values)
                    }
            except (ValueError, TypeError):
                stats['series_info'][data_key] = {
                    'points': len(timestamps),
                    'data_type': 'non-numeric'
                }
        
        if all_timestamps:
            stats['time_range'] = (min(all_timestamps), max(all_timestamps))
            stats['data_points'] = total_points
        
        return stats