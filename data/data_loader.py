"""
Data Loader Module
Handles loading and parsing of drone log files
"""

import os
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from typing import Dict, List, Optional, Tuple

class LogFileConfig:
    """Configuration for different log file types"""
    
    # Define log file configurations
    LOG_CONFIGS = {
        'rov_data': {
            'depth.log': ['depth', 'target_depth', 'depth_error', 'mode', 'depth_sensor_reading'],
            'motor.log': ['motor_inputs'],
            'orientation.log': ['roll', 'pitch', 'yaw'],
            'target_orientation.log': ['target_roll', 'target_pitch', 'target_yaw']
        },
        'sensor_data': {
            'analog_circuit_data.log': ['motor_voltage_left', 'motor_voltage_right', 
                                      'motor_current_left', 'motor_current_right',
                                      'current_5v', 'voltage_5v', 'current_battery'],
            'pressure_sensor.log': ['pressure_mbar', 'water_temp_c', 'depth_m'],
            'sonar.log': ['sonar_altitude_m', 'confidence_pct'],
            'temperature_data.log': ['front_temp_1', 'front_temp_2', 'front_temp_3', 'front_temp_4',
                                   'back_temp_1', 'back_temp_2', 'back_temp_3', 'back_temp_4']
        }
    }
    
    @classmethod
    def get_expected_fields(cls, category: str, log_file: str) -> List[str]:
        """Get expected fields for a log file"""
        return cls.LOG_CONFIGS.get(category, {}).get(log_file, [])
    
    @classmethod
    def add_log_config(cls, category: str, log_file: str, fields: List[str]) -> None:
        """Add new log file configuration"""
        if category not in cls.LOG_CONFIGS:
            cls.LOG_CONFIGS[category] = {}
        cls.LOG_CONFIGS[category][log_file] = fields

class DataLoader:
    """Handles loading and parsing of drone log files"""
    
    def __init__(self):
        self.session_pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
    
    def find_sessions(self, folder_path: str) -> Dict[str, str]:
        """Find all valid session folders"""
        sessions = {}
        
        if not os.path.exists(folder_path):
            return sessions
        
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path) and self.is_valid_session_name(item):
                sessions[item] = item_path
        
        return sessions
    
    def is_valid_session_name(self, name: str) -> bool:
        """Check if name matches session pattern: yyyy-mm-dd_hh-mm-ss"""
        return re.match(self.session_pattern, name) is not None
    
    def load_session_data(self, session_path: str) -> Dict[str, pd.DataFrame]:
        """Load all data for a session"""
        data_categories = {}
        
        # Load data from each configured log file
        for category, log_files in LogFileConfig.LOG_CONFIGS.items():
            category_path = os.path.join(session_path, category)
            if os.path.exists(category_path):
                for log_file in log_files.keys():
                    log_path = os.path.join(category_path, log_file)
                    if os.path.exists(log_path):
                        data = self.parse_log_file(log_path)
                        if data is not None and not data.empty:
                            data_categories[f"{category}/{log_file}"] = data
        
        # Also scan for unknown log files
        self._scan_unknown_files(session_path, data_categories)
        
        return data_categories
    
    def _scan_unknown_files(self, session_path: str, data_categories: Dict[str, pd.DataFrame]) -> None:
        """Scan for log files not in configuration"""
        for root, dirs, files in os.walk(session_path):
            for file in files:
                if file.endswith('.log'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, session_path)
                    category_key = relative_path.replace(os.sep, '/')
                    
                    # Skip if already processed
                    if category_key in data_categories:
                        continue
                    
                    # Try to parse unknown log file
                    data = self.parse_log_file(file_path)
                    if data is not None and not data.empty:
                        data_categories[category_key] = data
    
    def parse_log_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Parse a single log file"""
        data = defaultdict(list)
        timestamps = []
        all_keys = set()  # Track all possible keys
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        timestamp, json_data = self._parse_log_line(line)
                        if timestamp and json_data:
                            timestamps.append(timestamp)
                            # Track all keys we've seen
                            for key, value in json_data.items():
                                if isinstance(value, list):
                                    for i in range(len(value)):
                                        all_keys.add(f"{key}_{i}")
                                else:
                                    all_keys.add(key)
                            self._extract_json_data(json_data, data, len(timestamps) - 1)
                    
                    except Exception as e:
                        print(f"Warning: Error parsing line {line_num} in {file_path}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
        
        if not timestamps:
            return None
        
        # Ensure all columns have the same length
        num_records = len(timestamps)
        for key in all_keys:
            if key not in data:
                data[key] = [None] * num_records
            elif len(data[key]) < num_records:
                data[key].extend([None] * (num_records - len(data[key])))
        
        # Convert to pandas DataFrame
        df_data = {'timestamp': timestamps}
        df_data.update(data)
        
        try:
            df = pd.DataFrame(df_data)
            
            # Convert timestamp column to pandas datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Clean and validate data types
            df = self._clean_dataframe(df)
            
            # Sort by timestamp
            if 'timestamp' in df.columns:
                df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"Error creating DataFrame for {file_path}: {e}")
            print(f"Data shapes: {[(k, len(v)) for k, v in df_data.items()]}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate DataFrame data types"""
        try:
            for column in df.columns:
                if column == 'timestamp':
                    continue
                
                # Try to convert to numeric if possible
                try:
                    # Check if the column contains mostly numeric data
                    non_null_values = df[column].dropna()
                    if len(non_null_values) > 0:
                        # Try to convert to numeric
                        numeric_series = pd.to_numeric(non_null_values, errors='coerce')
                        # If most values converted successfully, use numeric
                        if numeric_series.notna().sum() / len(non_null_values) > 0.8:
                            df[column] = pd.to_numeric(df[column], errors='coerce')
                except Exception:
                    pass  # Keep original data type
            
            return df
        except Exception as e:
            print(f"Warning: Error cleaning DataFrame: {e}")
            return df
    
    def _parse_log_line(self, line: str) -> Tuple[Optional[datetime], Optional[dict]]:
        """Parse a single log line into timestamp and JSON data"""
        # Split timestamp and JSON data
        parts = line.split(' - ', 1)
        if len(parts) != 2:
            return None, None
        
        timestamp_str, json_str = parts
        
        # Parse timestamp
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
        except ValueError:
            try:
                # Try without microseconds
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None, None
        
        # Parse JSON data
        try:
            json_data = json.loads(json_str)
            return timestamp, json_data
        except json.JSONDecodeError:
            return None, None
    
    def _extract_json_data(self, json_data: dict, data: defaultdict, row_index: int) -> None:
        """Extract data from JSON object into data dictionary"""
        for key, value in json_data.items():
            try:
                if isinstance(value, list):
                    # Handle arrays (like motor_inputs)
                    for i, v in enumerate(value):
                        column_key = f"{key}_{i}"
                        # Ensure the list is long enough
                        while len(data[column_key]) <= row_index:
                            data[column_key].append(None)
                        
                        # Convert to appropriate numeric type if possible
                        if isinstance(v, (int, float)):
                            data[column_key][row_index] = float(v)
                        else:
                            data[column_key][row_index] = str(v)
                else:
                    # Ensure the list is long enough
                    while len(data[key]) <= row_index:
                        data[key].append(None)
                    
                    if isinstance(value, (int, float)):
                        data[key][row_index] = float(value)
                    elif isinstance(value, bool):
                        data[key][row_index] = int(value)  # Convert bool to int
                    elif isinstance(value, str):
                        # Try to convert string numbers to float, otherwise keep as string
                        try:
                            if value.replace('.', '').replace('-', '').isdigit():
                                data[key][row_index] = float(value)
                            else:
                                data[key][row_index] = value
                        except (ValueError, AttributeError):
                            data[key][row_index] = str(value)
                    else:
                        # Convert other types to string
                        data[key][row_index] = str(value)
            except Exception as e:
                print(f"Warning: Error processing field {key} with value {value}: {e}")
                # Ensure the list is long enough and add None
                while len(data[key]) <= row_index:
                    data[key].append(None)

class DataFilter:
    """Handles data filtering operations"""
    
    @staticmethod
    def filter_by_time(df: pd.DataFrame, start_time: Optional[datetime] = None, 
                      end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Filter DataFrame by time range"""
        if df.empty or 'timestamp' not in df.columns:
            return df
        
        filtered_df = df.copy()
        
        try:
            if start_time:
                # Convert to pandas Timestamp for comparison
                start_ts = pd.Timestamp(start_time)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_ts]
            
            if end_time:
                # Convert to pandas Timestamp for comparison
                end_ts = pd.Timestamp(end_time)
                filtered_df = filtered_df[filtered_df['timestamp'] <= end_ts]
        
        except Exception as e:
            print(f"Error filtering by time: {e}")
            return df
        
        return filtered_df
    
    @staticmethod
    def get_time_range(df: pd.DataFrame) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the time range of a DataFrame"""
        if df.empty or 'timestamp' not in df.columns:
            return None, None
        
        try:
            # Ensure timestamp column is datetime
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            min_time = df['timestamp'].min()
            max_time = df['timestamp'].max()
            
            # Convert to Python datetime if they are pandas Timestamps
            if pd.isna(min_time) or pd.isna(max_time):
                return None, None
            
            # Convert pandas Timestamps to Python datetime objects
            if hasattr(min_time, 'to_pydatetime'):
                try:
                    min_time = min_time.to_pydatetime()
                except ValueError:
                    # Handle nanoseconds by converting to datetime64 first
                    min_time = pd.to_datetime(min_time).replace(microsecond=min_time.microsecond)
            if hasattr(max_time, 'to_pydatetime'):
                try:
                    max_time = max_time.to_pydatetime()
                except ValueError:
                    # Handle nanoseconds by converting to datetime64 first
                    max_time = pd.to_datetime(max_time).replace(microsecond=max_time.microsecond)
            
            return min_time, max_time
        
        except Exception as e:
            print(f"Error getting time range: {e}")
            return None, None
    
    @staticmethod
    def get_session_time_range(session_name: str, session_data: Dict[str, pd.DataFrame]) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get time range for a session using folder name as start and last log timestamp as end"""
        try:
            # Extract start time from session folder name (format: yyyy-mm-dd_hh-mm-ss)
            session_start = datetime.strptime(session_name, "%Y-%m-%d_%H-%M-%S")
            
            # Find the latest timestamp from all log files (especially rov_data)
            max_timestamp = None
            
            for category_file, df in session_data.items():
                if df.empty or 'timestamp' not in df.columns:
                    continue
                
                # Get the last timestamp from this file
                df_max = df['timestamp'].max()
                
                # Convert to python datetime
                if hasattr(df_max, 'to_pydatetime'):
                    try:
                        df_max = df_max.to_pydatetime()
                    except ValueError:
                        df_max = pd.to_datetime(df_max).replace(microsecond=df_max.microsecond)
                
                if max_timestamp is None or df_max > max_timestamp:
                    max_timestamp = df_max
            
            if max_timestamp:
                print(f"Session: {session_name}")
                print(f"Start time (from folder): {session_start}")
                print(f"End time (from logs): {max_timestamp}")
                print(f"Duration: {max_timestamp - session_start}")
                
                return session_start, max_timestamp
            else:
                # Fallback: use folder name time and assume some duration
                session_end = session_start + timedelta(minutes=30)  # Default 30 min session
                return session_start, session_end
                
        except ValueError as e:
            print(f"Error parsing session name {session_name}: {e}")
            # Fallback to data-based time range
            min_time = None
            max_time = None
            
            for df in session_data.values():
                if df.empty or 'timestamp' not in df.columns:
                    continue
                
                df_min, df_max = DataFilter.get_time_range(df)
                if df_min and df_max:
                    if min_time is None or df_min < min_time:
                        min_time = df_min
                    if max_time is None or df_max > max_time:
                        max_time = df_max
            
            return min_time, max_time
    
    @staticmethod
    def resample_data(df: pd.DataFrame, frequency: str = '1S') -> pd.DataFrame:
        """Resample data to reduce density for plotting"""
        if df.empty or 'timestamp' not in df.columns:
            return df
        
        try:
            df_resampled = df.set_index('timestamp').resample(frequency).mean()
            df_resampled = df_resampled.reset_index()
            return df_resampled.dropna()
        except Exception:
            return df