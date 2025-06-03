"""
Plot Manager Module
Handles all plotting and visualization functionality
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
            'color_scheme': 'Blues'
        },
        'Temperature': {
            'keywords': ['temp', 'temperature'],
            'units': ['°C', 'celsius'],
            'color_scheme': 'Reds'
        },
        'Orientation': {
            'keywords': ['roll', 'pitch', 'yaw', 'orientation'],
            'units': ['degrees', '°'],
            'color_scheme': 'Greens'
        },
        'Voltage & Current': {
            'keywords': ['voltage', 'current'],
            'units': ['V', 'A', 'mA'],
            'color_scheme': 'Oranges'
        },
        'Motor Data': {
            'keywords': ['motor'],
            'units': ['PWM', 'inputs'],
            'color_scheme': 'Purples'
        },
        'Sonar & Distance': {
            'keywords': ['sonar', 'distance', 'confidence'],
            'units': ['m', '%'],
            'color_scheme': 'Greys'
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
    """Handles plot styling and aesthetics"""
    
    # Color schemes
    COLOR_SCHEMES = {
        'default': plt.cm.tab10,
        'Blues': plt.cm.Blues,
        'Reds': plt.cm.Reds,
        'Greens': plt.cm.Greens,
        'Oranges': plt.cm.Oranges,
        'Purples': plt.cm.Purples,
        'Greys': plt.cm.Greys
    }
    
    @staticmethod
    def get_colors(n_colors: int, scheme: str = 'default') -> List[Tuple[float, float, float, float]]:
        """Get color palette for plotting"""
        if scheme in PlotStyler.COLOR_SCHEMES:
            colormap = PlotStyler.COLOR_SCHEMES[scheme]
        else:
            colormap = PlotStyler.COLOR_SCHEMES['default']
        
        if n_colors <= 1:
            return [colormap(0.7)]
        
        return [colormap(i / (n_colors - 1) * 0.8 + 0.2) for i in range(n_colors)]
    
    @staticmethod
    def style_axis(ax, title: str = "", xlabel: str = "", ylabel: str = "", 
                  show_grid: bool = True, grid_alpha: float = 0.3):
        """Apply consistent styling to axis"""
        if title:
            ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10)
        
        if show_grid:
            ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.5)
        
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

class PlotManager:
    """Main plot management class"""
    
    def __init__(self, figure: Figure):
        self.figure = figure
        self.styler = PlotStyler()
        self.grouper = DataGrouper()
    
    def clear_plots(self):
        """Clear all plots from figure"""
        self.figure.clear()
    
    def create_combined_plot(self, data: Dict[str, Dict[str, Any]], 
                           session_name: str = "", show_grid: bool = True):
        """Create a single combined plot with all data"""
        self.clear_plots()
        
        if not data:
            return
        
        ax = self.figure.add_subplot(111)
        
        # Get colors for all data series
        colors = self.styler.get_colors(len(data))
        
        # Plot each data series
        for (data_key, data_info), color in zip(data.items(), colors):
            self._plot_data_series(ax, data_info, color, alpha=0.7)
        
        # Style the plot
        title = f'Drone Data Overview - {session_name}' if session_name else 'Drone Data Overview'
        self.styler.style_axis(ax, title=title, xlabel='Time', ylabel='Value', show_grid=show_grid)
        
        # Add legend if there are multiple series
        if len(data) > 1:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        
        # Format time axis
        self.figure.autofmt_xdate()
    
    def create_separate_plots(self, data: Dict[str, Dict[str, Any]], 
                            session_name: str = "", show_grid: bool = True):
        """Create separate plots grouped by data type"""
        self.clear_plots()
        
        if not data:
            return
        
        # Group data by type
        groups = self.grouper.group_data(data)
        n_groups = len(groups)
        
        if n_groups == 0:
            return
        
        # Create subplots
        for i, (group_name, group_data) in enumerate(groups.items()):
            ax = self.figure.add_subplot(n_groups, 1, i + 1)
            
            if not group_data:
                continue
            
            # Get color scheme for this group
            color_scheme = self.grouper.DATA_GROUPS.get(group_name, {}).get('color_scheme', 'default')
            colors = self.styler.get_colors(len(group_data), color_scheme)
            
            # Plot data in this group
            for (data_key, data_info), color in zip(group_data.items(), colors):
                self._plot_data_series(ax, data_info, color, alpha=0.8)
            
            # Style subplot
            ylabel = self._get_group_ylabel(group_name, group_data)
            xlabel = 'Time' if i == n_groups - 1 else ''  # Only show xlabel on bottom plot
            
            self.styler.style_axis(ax, title=group_name, xlabel=xlabel, 
                                 ylabel=ylabel, show_grid=show_grid)
            
            # Add legend if multiple series in group
            if len(group_data) > 1:
                ax.legend(fontsize=8, loc='best')
        
        # Add overall title
        if session_name:
            self.figure.suptitle(f'Drone Data Analysis - {session_name}', 
                               fontsize=14, fontweight='bold', y=0.98)
        
        # Format time axis
        self.figure.autofmt_xdate()
    
    def _plot_data_series(self, ax, data_info: Dict[str, Any], color, alpha: float = 0.7):
        """Plot a single data series"""
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
        
        # Plot the data
        line = ax.plot(timestamps, values, label=label, color=color, 
                      alpha=alpha, linewidth=1.5, marker='', markersize=2)
        
        # Add markers for sparse data
        if len(timestamps) < 100:
            line[0].set_marker('o')
            line[0].set_markersize(3)
    
    def _get_group_ylabel(self, group_name: str, group_data: Dict[str, Dict[str, Any]]) -> str:
        """Get appropriate ylabel for a data group"""
        # Try to infer units from data
        common_units = {
            'Depth & Pressure': 'Depth (m) / Pressure (mbar)',
            'Temperature': 'Temperature (°C)',
            'Orientation': 'Angle (degrees)',
            'Voltage & Current': 'Voltage (V) / Current (A)',
            'Motor Data': 'PWM Value',
            'Sonar & Distance': 'Distance (m) / Confidence (%)'
        }
        
        return common_units.get(group_name, 'Value')
    
    def add_time_markers(self, ax, events: List[Tuple[datetime, str]]):
        """Add vertical lines for important events"""
        for event_time, event_label in events:
            ax.axvline(x=event_time, color='red', linestyle='--', alpha=0.7)
            ax.text(event_time, ax.get_ylim()[1] * 0.9, event_label, 
                   rotation=90, verticalalignment='top', fontsize=8)
    
    def export_plot(self, filename: str, dpi: int = 300, format: str = 'png'):
        """Export current plot to file"""
        try:
            self.figure.savefig(filename, dpi=dpi, format=format, bbox_inches='tight',
                              facecolor='white', edgecolor='none')
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