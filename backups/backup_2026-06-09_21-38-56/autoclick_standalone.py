"""
AutoClick Pro - Window-Relative Coordinate Clicker
Complete standalone application with GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import win32gui
import win32api
import win32con
import pyautogui
import time
import threading
from typing import Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
#  WINDOW MANAGER
# ════════════════════════════════════════════════════════════
class WindowManager:
    """Handles window detection and position tracking"""
    
    def __init__(self):
        self.hwnd = None
        self.window_title = None
        self.client_left = 0
        self.client_top = 0
        self.window_width = 0
        self.window_height = 0
    
    def find_window(self, title: str) -> bool:
        """Find window by partial title match"""
        try:
            self.hwnd = win32gui.FindWindow(None, title)
            if self.hwnd == 0:
                # Try partial match
                found = False
                def enum_callback(hwnd, lParam):
                    nonlocal found
                    if title.lower() in win32gui.GetWindowText(hwnd).lower():
                        self.hwnd = hwnd
                        found = True
                        return False
                    return True
                
                win32gui.EnumWindows(enum_callback, None)
                if not found:
                    self.hwnd = None
                    return False
            
            self.window_title = win32gui.GetWindowText(self.hwnd)
            self._update_window_position()
            logger.info(f"✅ Found window: {self.window_title}")
            return True
        except Exception as e:
            logger.error(f"❌ Error finding window: {e}")
            return False
    
    def _update_window_position(self):
        """Update cached window position and size"""
        try:
            if not self.hwnd:
                return
            
            # Get client area origin
            client_pos = win32gui.ClientToScreen(self.hwnd, (0, 0))
            self.client_left = client_pos[0]
            self.client_top = client_pos[1]
            
            # Get window dimensions
            rect = win32gui.GetClientRect(self.hwnd)
            self.window_width = rect[2] - rect[0]
            self.window_height = rect[3] - rect[1]
            
            logger.debug(f"Window position: ({self.client_left}, {self.client_top}), "
                        f"Size: {self.window_width}x{self.window_height}")
        except Exception as e:
            logger.error(f"❌ Error updating window position: {e}")
    
    def get_window_info(self) -> dict:
        """Get current window information"""
        self._update_window_position()
        return {
            'title': self.window_title,
            'client_left': self.client_left,
            'client_top': self.client_top,
            'width': self.window_width,
            'height': self.window_height
        }
    
    def is_valid(self) -> bool:
        """Check if window is still valid"""
        if not self.hwnd:
            return False
        try:
            return win32gui.IsWindow(self.hwnd)
        except:
            return False


# ════════════════════════════════════════════════════════════
#  COORDINATE CONVERTER
# ════════════════════════════════════════════════════════════
class CoordinateConverter:
    """Converts between different coordinate systems"""
    
    def __init__(self, window_manager: WindowManager):
        self.wm = window_manager
    
    def screen_to_relative(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to window-relative coordinates"""
        info = self.wm.get_window_info()
        rel_x = screen_x - info['client_left']
        rel_y = screen_y - info['client_top']
        logger.debug(f"Screen ({screen_x}, {screen_y}) → Relative ({rel_x}, {rel_y})")
        return rel_x, rel_y
    
    def relative_to_screen(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
        """Convert window-relative coordinates to screen coordinates"""
        info = self.wm.get_window_info()
        screen_x = info['client_left'] + rel_x
        screen_y = info['client_top'] + rel_y
        logger.debug(f"Relative ({rel_x}, {rel_y}) → Screen ({screen_x}, {screen_y})")
        return screen_x, screen_y
    
    def percentage_to_relative(self, percent_x: float, percent_y: float) -> Tuple[int, int]:
        """Convert percentage coordinates to relative pixels"""
        info = self.wm.get_window_info()
        rel_x = int(info['width'] * (percent_x / 100))
        rel_y = int(info['height'] * (percent_y / 100))
        logger.debug(f"Percentage ({percent_x}%, {percent_y}%) → Relative ({rel_x}, {rel_y})")
        return rel_x, rel_y
    
    def relative_to_percentage(self, rel_x: int, rel_y: int) -> Tuple[float, float]:
        """Convert relative coordinates to percentage"""
        info = self.wm.get_window_info()
        if info['width'] == 0 or info['height'] == 0:
            return 0.0, 0.0
        percent_x = (rel_x / info['width']) * 100
        percent_y = (rel_y / info['height']) * 100
        return percent_x, percent_y


# ════════════════════════════════════════════════════════════
#  CLICK CONTROLLER
# ════════════════════════════════════════════════════════════
class ClickController:
    """Handles clicking operations"""
    
    def __init__(self, window_manager: WindowManager, converter: CoordinateConverter):
        self.wm = window_manager
        self.cc = converter
    
    def click_at_relative(self, rel_x: int, rel_y: int, button: str = 'left', 
                         duration: float = 0.1, restore_position: bool = True):
        """Click at relative coordinates"""
        try:
            if not self.wm.is_valid():
                logger.error("❌ Window is no longer valid")
                return False
            
            # Convert to screen coordinates
            screen_x, screen_y = self.cc.relative_to_screen(rel_x, rel_y)
            
            # Save current position if restore is enabled
            if restore_position:
                current_x, current_y = pyautogui.position()
            
            # Move and click
            logger.info(f"🖱️ Clicking at relative ({rel_x}, {rel_y}) → screen ({screen_x}, {screen_y})")
            pyautogui.moveTo(screen_x, screen_y, duration=0.1)
            time.sleep(0.05)
            
            if button == 'left':
                pyautogui.click(button='left')
            elif button == 'right':
                pyautogui.click(button='right')
            
            time.sleep(0.05)
            
            # Restore position
            if restore_position:
                pyautogui.moveTo(current_x, current_y, duration=0.1)
            
            logger.info("✅ Click completed")
            return True
        except Exception as e:
            logger.error(f"❌ Click failed: {e}")
            return False
    
    def get_current_mouse_screen_coords(self) -> Tuple[int, int]:
        """Get current mouse position in screen coordinates"""
        return pyautogui.position()


# ════════════════════════════════════════════════════════════
#  GUI APPLICATION
# ════════════════════════════════════════════════════════════
class AutoClickGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClick Pro - Window-Relative Clicker")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Core components
        self.wm = WindowManager()
        self.cc = CoordinateConverter(self.wm)
        self.click_ctrl = ClickController(self.wm, self.cc)
        
        # State
        self.capturing = False
        self.captured_coords = None
        
        # Build UI
        self._create_styles()
        self._create_ui()
    
    def _create_styles(self):
        """Setup modern styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.bg_main = '#1e1e2e'
        self.bg_card = '#2a2a3e'
        self.fg_text = '#ffffff'
        self.accent_blue = '#0099ff'
        self.accent_green = '#00cc66'
        self.accent_red = '#ff3333'
        
        self.root.configure(bg=self.bg_main)
    
    def _create_ui(self):
        """Build UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_main)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ─────────────────────────────────────────────
        # SECTION 1: Window Selection
        # ─────────────────────────────────────────────
        self._create_section(main_frame, "1️⃣ SELECT WINDOW", self._create_window_section)
        
        # ─────────────────────────────────────────────
        # SECTION 2: Coordinate Capture
        # ─────────────────────────────────────────────
        self._create_section(main_frame, "2️⃣ CAPTURE COORDINATES", self._create_capture_section)
        
        # ─────────────────────────────────────────────
        # SECTION 3: Click Target
        # ─────────────────────────────────────────────
        self._create_section(main_frame, "3️⃣ CLICK TARGET", self._create_click_section)
        
        # ─────────────────────────────────────────────
        # SECTION 4: Info Display
        # ─────────────────────────────────────────────
        self._create_section(main_frame, "📊 INFO", self._create_info_section)
    
    def _create_section(self, parent, title, builder_func):
        """Create a collapsible section"""
        section_frame = tk.Frame(parent, bg=self.bg_card, relief=tk.RAISED, bd=1)
        section_frame.pack(fill=tk.X, pady=10)
        
        # Header
        header = tk.Frame(section_frame, bg=self.accent_blue, height=40)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, font=("Segoe UI", 12, "bold"),
                               bg=self.accent_blue, fg="white")
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Content
        content_frame = tk.Frame(section_frame, bg=self.bg_card)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        builder_func(content_frame)
    
    def _create_window_section(self, parent):
        """Window selection UI"""
        row1 = tk.Frame(parent, bg=self.bg_card)
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="Window Title:", font=("Segoe UI", 9),
                bg=self.bg_card, fg=self.fg_text).pack(side=tk.LEFT, padx=5)
        
        self.window_entry = tk.Entry(row1, font=("Segoe UI", 9), width=35)
        self.window_entry.pack(side=tk.LEFT, padx=5)
        self.window_entry.insert(0, "Untitled")
        
        btn_find = tk.Button(row1, text="🔍 Find Window", command=self._find_window,
                            bg=self.accent_blue, fg="white", font=("Segoe UI", 9),
                            relief=tk.FLAT, padx=15, pady=5)
        btn_find.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.window_status = tk.Label(parent, text="❌ No window selected",
                                      font=("Segoe UI", 9), bg=self.bg_card, fg="#ff9999")
        self.window_status.pack(pady=10)
    
    def _create_capture_section(self, parent):
        """Coordinate capture UI"""
        btn_capture = tk.Button(parent, text="🎯 Capture Relative Position (Click anywhere in window)",
                               command=self._start_capture, bg=self.accent_green, fg="white",
                               font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=20, pady=12)
        btn_capture.pack(fill=tk.X, pady=5)
        
        self.capture_status = tk.Label(parent, text="⏳ Click the button above to capture...",
                                       font=("Segoe UI", 9), bg=self.bg_card, fg="#ffcc66")
        self.capture_status.pack(pady=10)
        
        # Captured coordinates display
        info_frame = tk.Frame(parent, bg="#2a2a3e", relief=tk.SUNKEN, bd=1)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text="Captured Coordinates:", font=("Segoe UI", 8, "bold"),
                bg="#2a2a3e", fg="#aaaaaa").pack(anchor=tk.W, padx=10, pady=(8, 2))
        
        coords_frame = tk.Frame(info_frame, bg="#2a2a3e")
        coords_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(coords_frame, text="Pixels (X, Y):", font=("Segoe UI", 8),
                bg="#2a2a3e", fg="#999999").pack(side=tk.LEFT, padx=5)
        self.captured_pixels_label = tk.Label(coords_frame, text="---",
                                              font=("Segoe UI", 8, "bold"),
                                              bg="#2a2a3e", fg=self.accent_green)
        self.captured_pixels_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(coords_frame, text="Percentage (%):", font=("Segoe UI", 8),
                bg="#2a2a3e", fg="#999999").pack(side=tk.LEFT, padx=5)
        self.captured_percent_label = tk.Label(coords_frame, text="---",
                                               font=("Segoe UI", 8, "bold"),
                                               bg="#2a2a3e", fg=self.accent_blue)
        self.captured_percent_label.pack(side=tk.LEFT, padx=5)
    
    def _create_click_section(self, parent):
        """Click target input UI"""
        # Mode selector
        mode_frame = tk.Frame(parent, bg=self.bg_card)
        mode_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(mode_frame, text="Coordinate Mode:", font=("Segoe UI", 9),
                bg=self.bg_card, fg=self.fg_text).pack(side=tk.LEFT, padx=5)
        
        self.coord_mode = tk.StringVar(value="pixels")
        ttk.Radiobutton(mode_frame, text="Pixels", variable=self.coord_mode,
                       value="pixels").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Percentage", variable=self.coord_mode,
                       value="percentage").pack(side=tk.LEFT, padx=10)
        
        # Input fields
        input_frame = tk.Frame(parent, bg=self.bg_card)
        input_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(input_frame, text="X:", font=("Segoe UI", 9),
                bg=self.bg_card, fg=self.fg_text).pack(side=tk.LEFT, padx=5)
        self.x_input = tk.Entry(input_frame, font=("Segoe UI", 9), width=10)
        self.x_input.pack(side=tk.LEFT, padx=5)
        self.x_input.insert(0, "0")
        
        tk.Label(input_frame, text="Y:", font=("Segoe UI", 9),
                bg=self.bg_card, fg=self.fg_text).pack(side=tk.LEFT, padx=20)
        self.y_input = tk.Entry(input_frame, font=("Segoe UI", 9), width=10)
        self.y_input.pack(side=tk.LEFT, padx=5)
        self.y_input.insert(0, "0")
        
        # Click buttons
        btn_frame = tk.Frame(parent, bg=self.bg_card)
        btn_frame.pack(fill=tk.X, pady=10)
        
        btn_test = tk.Button(btn_frame, text="🖱️ Test Click", command=self._test_click,
                            bg=self.accent_blue, fg="white", font=("Segoe UI", 10, "bold"),
                            relief=tk.FLAT, padx=15, pady=8)
        btn_test.pack(side=tk.LEFT, padx=5)
        
        btn_use_captured = tk.Button(btn_frame, text="📌 Use Captured", command=self._use_captured_coords,
                                    bg="#666666", fg="white", font=("Segoe UI", 10),
                                    relief=tk.FLAT, padx=15, pady=8)
        btn_use_captured.pack(side=tk.LEFT, padx=5)
        
        self.click_status = tk.Label(parent, text="", font=("Segoe UI", 9),
                                    bg=self.bg_card, fg="#cccccc")
        self.click_status.pack(pady=5)
    
    def _create_info_section(self, parent):
        """Info display UI"""
        self.info_text = tk.Text(parent, height=8, font=("Courier New", 8),
                                bg="#1a1a2e", fg="#00dd00", relief=tk.SUNKEN, bd=1,
                                wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
        self.info_text.insert(tk.END, "📝 Ready to start. Select a window first.\n")
        self.info_text.config(state=tk.DISABLED)
    
    def _log_info(self, message: str):
        """Add message to info display"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
        logger.info(message)
    
    def _find_window(self):
        """Find window by title"""
        title = self.window_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a window title")
            return
        
        if self.wm.find_window(title):
            info = self.wm.get_window_info()
            self.window_status.config(
                text=f"✅ Window found: {info['title']}\n   Position: ({info['client_left']}, {info['client_top']}) | "
                     f"Size: {info['width']}x{info['height']}",
                fg="#99ff99"
            )
            self._log_info(f"✅ Window found: {info['title']}")
            self._log_info(f"   Client area: ({info['client_left']}, {info['client_top']})")
            self._log_info(f"   Size: {info['width']}x{info['height']}")
        else:
            self.window_status.config(text="❌ Window not found", fg="#ff9999")
            messagebox.showerror("Error", "Window not found. Try partial title.")
    
    def _start_capture(self):
        """Start capturing coordinates"""
        if not self.wm.is_valid():
            messagebox.showerror("Error", "No valid window selected")
            return
        
        self.capturing = True
        self.capture_status.config(text="🎯 Capturing... Move your mouse and click to capture!", fg="#ffff99")
        self.root.update()
        
        # Wait for mouse click
        def capture_thread():
            try:
                import keyboard
                # Wait for any mouse click
                while self.capturing:
                    screen_x, screen_y = pyautogui.position()
                    time.sleep(0.1)
                
                if self.capturing:
                    rel_x, rel_y = self.cc.screen_to_relative(screen_x, screen_y)
                    percent_x, percent_y = self.cc.relative_to_percentage(rel_x, rel_y)
                    
                    self.captured_coords = (rel_x, rel_y)
                    self.captured_pixels_label.config(text=f"({rel_x}, {rel_y})")
                    self.captured_percent_label.config(text=f"({percent_x:.1f}%, {percent_y:.1f}%)")
                    self.capture_status.config(text="✅ Coordinates captured! You can now use them.", fg="#99ff99")
                    
                    self._log_info(f"✅ Captured relative: ({rel_x}, {rel_y})")
                    self._log_info(f"   Percentage: ({percent_x:.1f}%, {percent_y:.1f}%)")
            except Exception as e:
                self.capture_status.config(text=f"❌ Error: {e}", fg="#ff9999")
                self._log_info(f"❌ Capture error: {e}")
            finally:
                self.capturing = False
        
        # Simple approach: Wait for user to manually select coordinates
        self.capture_status.config(text="🎯 Move mouse to target position and press ENTER to capture", fg="#ffff99")
        self.root.bind('<Return>', lambda e: self._capture_on_enter())
    
    def _capture_on_enter(self):
        """Capture coordinates when user presses Enter"""
        screen_x, screen_y = pyautogui.position()
        
        if not self.wm.is_valid():
            messagebox.showerror("Error", "Window is no longer valid")
            return
        
        try:
            rel_x, rel_y = self.cc.screen_to_relative(screen_x, screen_y)
            percent_x, percent_y = self.cc.relative_to_percentage(rel_x, rel_y)
            
            self.captured_coords = (rel_x, rel_y)
            self.captured_pixels_label.config(text=f"({rel_x}, {rel_y})")
            self.captured_percent_label.config(text=f"({percent_x:.1f}%, {percent_y:.1f}%)")
            self.capture_status.config(text="✅ Coordinates captured! You can now use them.", fg="#99ff99")
            
            self._log_info(f"✅ Captured relative: ({rel_x}, {rel_y})")
            self._log_info(f"   Screen was: ({screen_x}, {screen_y})")
            self._log_info(f"   Percentage: ({percent_x:.1f}%, {percent_y:.1f}%)")
            
            self.root.unbind('<Return>')
        except Exception as e:
            self.capture_status.config(text=f"❌ Error: {e}", fg="#ff9999")
            self._log_info(f"❌ Capture error: {e}")
    
    def _use_captured_coords(self):
        """Fill input fields with captured coordinates"""
        if not self.captured_coords:
            messagebox.showinfo("Info", "No coordinates captured yet")
            return
        
        rel_x, rel_y = self.captured_coords
        self.x_input.delete(0, tk.END)
        self.y_input.delete(0, tk.END)
        self.x_input.insert(0, str(rel_x))
        self.y_input.insert(0, str(rel_y))
        self.coord_mode.set("pixels")
        self._log_info(f"📌 Using captured coordinates: ({rel_x}, {rel_y})")
    
    def _test_click(self):
        """Test click at target coordinates"""
        if not self.wm.is_valid():
            messagebox.showerror("Error", "No valid window selected")
            return
        
        try:
            x_val = self.x_input.get().strip()
            y_val = self.y_input.get().strip()
            
            if not x_val or not y_val:
                messagebox.showerror("Error", "Please enter X and Y values")
                return
            
            x = float(x_val)
            y = float(y_val)
            
            if self.coord_mode.get() == "percentage":
                x, y = self.cc.percentage_to_relative(x, y)
            else:
                x, y = int(x), int(y)
            
            self.click_status.config(text="⏳ Clicking...", fg="#ffff99")
            self.root.update()
            
            # Small delay to show status
            time.sleep(0.3)
            
            success = self.click_ctrl.click_at_relative(int(x), int(y), restore_position=True)
            
            if success:
                self.click_status.config(text="✅ Click successful!", fg="#99ff99")
                self._log_info(f"✅ Clicked at relative: ({int(x)}, {int(y)})")
            else:
                self.click_status.config(text="❌ Click failed", fg="#ff9999")
                self._log_info(f"❌ Click failed at ({int(x)}, {int(y)})")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Click error: {e}")
            self._log_info(f"❌ Error: {e}")


# ════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    app = AutoClickGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
