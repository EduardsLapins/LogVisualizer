#!/usr/bin/env python3
"""
Drone Log Analyzer - Main Entry Point
Author: Assistant
Description: Main application entry point for the drone log visualization tool
"""
import sys
import tkinter as tk
from gui.main_window import DroneLogAnalyzer

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # ─── Make the app DPI‐aware on Windows ────────────────────────────────
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    
    # ─── Instead of a hard‐coded 1920x1080, size to 90% of the real screen ─
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    
    # Choose 90% of each dimension (you can tweak 0.9 up or down)
    window_w = int(screen_w * 0.9)
    window_h = int(screen_h * 0.9)
    
    # Center on screen
    x = (screen_w - window_w) // 2
    y = (screen_h - window_h) // 2
    
    root.geometry(f"{window_w}x{window_h}+{x}+{y}")
    root.minsize(800, 500)
    
    # If you prefer “fully maximized” on Windows, you could do:
    # if sys.platform.startswith("win"):
    #     root.state('zoomed')
    
    # ─── Set title, then create the app ────────────────────────────────────
    root.title("Drone Log Analyzer v2.0")
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
