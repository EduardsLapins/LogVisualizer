#!/usr/bin/env python3
"""
Drone Log Analyzer - Main Entry Point
Author: Assistant
Description: Main application entry point for the drone log visualization tool
"""

import tkinter as tk
from gui.main_window import DroneLogAnalyzer

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Set application icon and properties
    root.title("Drone Log Analyzer v2.0")
    root.geometry("1920x1080")
    root.minsize(1000, 600)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Create and run the application
    app = DroneLogAnalyzer(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()