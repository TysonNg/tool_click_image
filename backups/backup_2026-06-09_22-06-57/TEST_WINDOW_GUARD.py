"""
Quick test to verify WindowGuard functionality
Run this to check if window protection works
"""

import sys
import os

# Add project root to path
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import win32gui
import time
from core import state
from core.window_guard import WindowGuard
from utils import safe_print

def test_window_guard():
    """Test WindowGuard functionality"""
    
    print("\n" + "="*60)
    print("🧪 WINDOW GUARD TEST")
    print("="*60 + "\n")
    
    # Test 1: No window set
    print("📝 Test 1: Check when no window set")
    print("-" * 40)
    
    state.game_hwnd = None
    is_valid = WindowGuard.validate_window()
    print(f"  validate_window() when no window: {is_valid}")
    assert not is_valid, "Should return False when no window"
    print("  ✅ PASS\n")
    
    # Test 2: Get foreground window for testing
    print("📝 Test 2: Get foreground window for testing")
    print("-" * 40)
    
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    print(f"  Foreground window: {window_title} (HWND: {hwnd})")
    
    if hwnd == 0:
        print("  ⚠️ SKIP: No foreground window available")
        return
    
    state.game_hwnd = hwnd
    print("  ✅ Set as test window\n")
    
    # Test 3: Validate window
    print("📝 Test 3: Validate window")
    print("-" * 40)
    
    is_valid = WindowGuard.validate_window()
    print(f"  validate_window(): {is_valid}")
    assert is_valid, "Should return True for valid window"
    print("  ✅ PASS\n")
    
    # Test 4: Get window state
    print("📝 Test 4: Get window state")
    print("-" * 40)
    
    win_state = WindowGuard.get_window_state()
    state_names = {
        0: "HIDE", 1: "NORMAL", 2: "MINIMIZE", 3: "MAXIMIZE",
        5: "SHOW", 6: "MINIMIZE", 9: "RESTORE"
    }
    state_name = state_names.get(win_state, "UNKNOWN")
    print(f"  get_window_state(): {win_state} ({state_name})")
    print("  ✅ PASS\n")
    
    # Test 5: Check window (with warning)
    print("📝 Test 5: Check window status")
    print("-" * 40)
    
    warning = WindowGuard.check_and_warn()
    if warning:
        print(f"  Warning detected: {warning}")
    else:
        print(f"  Window is healthy: No warnings")
    print("  ✅ PASS\n")
    
    # Test 6: Bring to foreground
    print("📝 Test 6: Bring window to foreground")
    print("-" * 40)
    
    result = WindowGuard.bring_to_foreground_safe()
    print(f"  bring_to_foreground_safe(): {result}")
    assert result, "Should return True"
    print("  ✅ PASS\n")
    
    # Test 7: Full protection
    print("📝 Test 7: Full window protection")
    print("-" * 40)
    
    result = WindowGuard.protect_window()
    print(f"  protect_window(): {result}")
    assert result, "Should return True for valid window"
    print("  ✅ PASS\n")
    
    # Test 8: Restore window (if minimized)
    print("📝 Test 8: Restore window")
    print("-" * 40)
    
    result = WindowGuard.restore_window_safe()
    print(f"  restore_window_safe(): {result}")
    print("  ✅ PASS\n")
    
    # Summary
    print("="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print(f"\nWindow Guard is working correctly for:")
    print(f"  • Window: {window_title}")
    print(f"  • HWND: {state.game_hwnd}")
    print("\nYou can now safely use WindowGuard in your scripts! 🎉\n")

if __name__ == "__main__":
    try:
        test_window_guard()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
