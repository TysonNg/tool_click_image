"""
Relative Coordinate Capture
Captures window-relative coordinates (not screen-absolute)
Works even when window is moved
"""

import win32gui
import win32api
import pyautogui
import threading
import tkinter as tk
from tkinter import messagebox
from core import state
from utils import safe_print


class RelativeCoordinateCapture:
    """Captures coordinates relative to game window"""
    
    @staticmethod
    def get_game_window_info():
        """Get current game window position and size"""
        try:
            from utils import safe_print
            
            # Try to get from state if stored
            if hasattr(state, 'game_hwnd') and state.game_hwnd:
                hwnd = state.game_hwnd
                # Validate handle is still valid
                if not win32gui.IsWindow(hwnd):
                    safe_print(f"⚠️ Window handle {hwnd} is no longer valid, clearing...")
                    state.game_hwnd = None
                    return None
            else:
                # Find active window
                hwnd = win32gui.GetForegroundWindow()
            
            if hwnd == 0:
                safe_print("❌ No active window found")
                return None
            
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            
            # Get client area origin (top-left corner in screen coords)
            try:
                client_pos = win32gui.ClientToScreen(hwnd, (0, 0))
                client_left = client_pos[0]
                client_top = client_pos[1]
            except:
                # Fallback: get window rect
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    client_left = rect[0]
                    client_top = rect[1]
                except Exception as e:
                    safe_print(f"⚠️ Could not get window rect: {e}")
                    return None
            
            # Get window dimensions
            try:
                rect = win32gui.GetClientRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
            except:
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                except Exception as e:
                    safe_print(f"⚠️ Could not get window dimensions: {e}")
                    return None
            
            return {
                'hwnd': hwnd,
                'title': title,
                'client_left': client_left,
                'client_top': client_top,
                'width': width,
                'height': height
            }
        except Exception as e:
            from utils import safe_print
            safe_print(f"❌ Error getting window info: {e}")
            return None
    
    @staticmethod
    def screen_to_relative(screen_x, screen_y, window_info):
        """Convert screen coordinates to window-relative coordinates"""
        if not window_info:
            return None, None
        
        rel_x = screen_x - window_info['client_left']
        rel_y = screen_y - window_info['client_top']
        
        return rel_x, rel_y

    @staticmethod
    def find_window_by_title(window_title):
        """Find a window handle by title text using partial match."""
        try:
            found_hwnd = None
            def enum_callback(hwnd, lParam):
                nonlocal found_hwnd
                title = win32gui.GetWindowText(hwnd)
                if window_title.lower() in title.lower():
                    found_hwnd = hwnd
                    return False
                return True
            win32gui.EnumWindows(enum_callback, None)
            return found_hwnd
        except Exception:
            return None
    
    @staticmethod
    def relative_to_screen(rel_x, rel_y, window_info):
        """Convert window-relative coordinates to screen coordinates"""
        if not window_info:
            return None, None
        
        screen_x = window_info['client_left'] + rel_x
        screen_y = window_info['client_top'] + rel_y
        
        return screen_x, screen_y
    
    @staticmethod
    def percentage_to_relative(percent_x, percent_y, window_info):
        """Convert percentage to relative pixel coordinates"""
        if not window_info:
            return None, None
        
        rel_x = int(window_info['width'] * (percent_x / 100))
        rel_y = int(window_info['height'] * (percent_y / 100))
        
        return rel_x, rel_y
    
    @staticmethod
    def start_capture_ui(root, callback):
        """Start capture mode - user clicks to capture coordinate"""
        
        def capture_thread():
            try:
                # Create beautiful instruction window
                instruction = tk.Toplevel(root)
                instruction.title("📍 Lấy Tọa Độ Tương Đối")
                instruction.geometry("500x280")
                instruction.resizable(False, False)
                instruction.attributes('-topmost', True)
                instruction.configure(bg='#1e1e2e')
                
                # Header
                header = tk.Frame(instruction, bg='#0099ff', height=60)
                header.pack(fill=tk.X, padx=0, pady=0)
                header.pack_propagate(False)
                
                tk.Label(header, text="📍 Lấy Tọa Độ Tương Đối", 
                        font=("Segoe UI", 16, "bold"), bg='#0099ff', 
                        fg='white').pack(pady=12)
                
                # Content
                content = tk.Frame(instruction, bg='#1e1e2e')
                content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                # Instructions
                instruction_title = tk.Label(content, text="📋 Hướng Dẫn:", 
                                           font=("Segoe UI", 11, "bold"), 
                                           bg='#1e1e2e', fg='#ffff99')
                instruction_title.pack(anchor=tk.W, pady=(0, 10))
                
                instructions_text = tk.Label(content, 
                    text="1️⃣  Di chuyển con chuột vào vị trí muốn lấy tọa độ\n"
                         "    (Có thể là nút, NPC, hay bất kỳ điểm nào trong game)\n\n"
                         "2️⃣  Bấm phím ENTER để lấy tọa độ\n\n"
                         "3️⃣  Kết quả sẽ được tự động lưu vào danh sách kịch bản",
                    font=("Segoe UI", 10), bg='#1e1e2e', fg='#cccccc',
                    justify=tk.LEFT)
                instructions_text.pack(anchor=tk.W, pady=5)
                
                # Status
                status_frame = tk.Frame(content, bg='#2a2a3e', relief=tk.SUNKEN, bd=1)
                status_frame.pack(fill=tk.X, pady=(15, 0))
                
                status_label = tk.Label(status_frame, text="⏳ Chờ... Di chuyển chuột và bấm ENTER",
                                       font=("Segoe UI", 10), bg='#2a2a3e', 
                                       fg='#ffaa00')
                status_label.pack(pady=10, padx=10)
                
                instruction.update()
                
                # Wait for ENTER key
                instruction.bind('<Return>', lambda e: instruction.destroy())
                instruction.wait_window()
                
                # Get current mouse position (screen coordinates)
                screen_x, screen_y = pyautogui.position()
                
                # Get window info
                window_info = RelativeCoordinateCapture.get_game_window_info()
                if not window_info:
                    messagebox.showerror("❌ Lỗi", "Không tìm thấy cửa sổ game")
                    return
                
                # Convert to relative coordinates
                rel_x, rel_y = RelativeCoordinateCapture.screen_to_relative(
                    screen_x, screen_y, window_info
                )
                
                # Calculate percentage
                percent_x = (rel_x / window_info['width']) * 100 if window_info['width'] > 0 else 0
                percent_y = (rel_y / window_info['height']) * 100 if window_info['height'] > 0 else 0
                
                # Log result
                safe_print(f"✅ Lấy tọa độ: Pixel({int(rel_x)}, {int(rel_y)}) | "
                          f"Phần trăm({percent_x:.1f}%, {percent_y:.1f}%)")
                
                # Store captured coordinates in state
                state.captured_relative_x = int(rel_x)
                state.captured_relative_y = int(rel_y)
                state.captured_relative_percent_x = percent_x
                state.captured_relative_percent_y = percent_y
                state.game_hwnd = window_info['hwnd']
                
                # Call the callback to update UI
                if callback:
                    callback(int(rel_x), int(rel_y), percent_x, percent_y)
                
            except Exception as e:
                safe_print(f"❌ Lỗi capture: {e}")
                messagebox.showerror("❌ Lỗi", f"Lỗi khi lấy tọa độ: {e}")
        
        # Run in thread so UI doesn't freeze
        thread = threading.Thread(target=capture_thread, daemon=True)
        thread.start()
