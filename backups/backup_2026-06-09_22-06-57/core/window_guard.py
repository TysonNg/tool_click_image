"""
Window Guard: Keeps the target game window alive and focused during script execution
Handles window restoration, focus management, and validation
"""

import win32gui
import win32api
import time
from core import state
from utils import safe_print


class WindowGuard:
    """Manages and protects the target game window during execution"""
    
    # Window state constants
    SW_HIDE = 0
    SW_SHOW = 5
    SW_MINIMIZE = 6
    SW_MAXIMIZE = 3
    SW_RESTORE = 9
    
    @staticmethod
    def validate_window():
        """Check if window handle is still valid"""
        if not state.game_hwnd:
            return False
        
        try:
            return bool(win32gui.IsWindow(state.game_hwnd))
        except Exception as e:
            safe_print(f"⚠️ [WINDOW_GUARD] Error validating window: {e}")
            return False
    
    @staticmethod
    def get_window_state():
        """Get current window state (hidden, minimized, maximized, normal)"""
        if not WindowGuard.validate_window():
            return None
        
        try:
            placement = win32gui.GetWindowPlacement(state.game_hwnd)
            return placement[1]  # Returns state code
        except Exception as e:
            safe_print(f"⚠️ [WINDOW_GUARD] Error getting window state: {e}")
            return None
    
    @staticmethod
    def restore_window_safe():
        """Safely restore window to normal visible state"""
        if not WindowGuard.validate_window():
            safe_print("❌ [WINDOW_GUARD] Window handle invalid, cannot restore")
            return False
        
        try:
            win_state = WindowGuard.get_window_state()
            
            if win_state == WindowGuard.SW_MINIMIZE:
                safe_print("🔧 [WINDOW_GUARD] Restoring minimized window...")
                win32gui.ShowWindow(state.game_hwnd, WindowGuard.SW_RESTORE)
                time.sleep(0.3)
            elif win_state == WindowGuard.SW_HIDE:
                safe_print("🔧 [WINDOW_GUARD] Showing hidden window...")
                win32gui.ShowWindow(state.game_hwnd, WindowGuard.SW_SHOW)
                time.sleep(0.3)
            elif win_state == WindowGuard.SW_MAXIMIZE:
                safe_print("🔧 [WINDOW_GUARD] Keeping maximized window...")
            
            return True
        except Exception as e:
            safe_print(f"⚠️ [WINDOW_GUARD] Error restoring window: {e}")
            return False
    
    @staticmethod
    def bring_to_foreground_safe():
        """Safely bring window to foreground without aggressive focus steal"""
        if not WindowGuard.validate_window():
            return False
        
        try:
            # Soft approach: Use SetForegroundWindow
            win32gui.SetForegroundWindow(state.game_hwnd)
            time.sleep(0.2)
            return True
        except Exception as e:
            safe_print(f"⚠️ [WINDOW_GUARD] Error bringing window to foreground: {e}")
            return False
    
    @staticmethod
    def protect_window():
        """Full protection: validate, restore, and bring to foreground"""
        if not WindowGuard.validate_window():
            safe_print("❌ [WINDOW_GUARD] Window no longer valid")
            state.game_hwnd = None
            return False
        
        try:
            # 1. Restore if minimized/hidden
            WindowGuard.restore_window_safe()
            
            # 2. Bring to foreground
            WindowGuard.bring_to_foreground_safe()
            
            return True
        except Exception as e:
            safe_print(f"⚠️ [WINDOW_GUARD] Protection failed: {e}")
            return False
    
    @staticmethod
    def wait_for_window(timeout=5):
        """Wait for window to become valid, with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if WindowGuard.validate_window():
                return True
            time.sleep(0.1)
        return False
    
    @staticmethod
    def check_and_warn():
        """Check window and warn if there are issues"""
        if not state.game_hwnd:
            return "⚠️ No target window set"
        
        if not WindowGuard.validate_window():
            return "❌ Target window is invalid (closed or not found)"
        
        win_state = WindowGuard.get_window_state()
        if win_state == WindowGuard.SW_MINIMIZE:
            return "⚠️ Target window is minimized"
        elif win_state == WindowGuard.SW_HIDE:
            return "⚠️ Target window is hidden"
        
        return None  # All good
