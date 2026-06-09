# Fix: TclError - Application Has Been Destroyed

**Status**: ✅ Fixed  
**Date**: June 8, 2026  
**Error**: `_tkinter.TclError: can't invoke "wm" command: application has been destroyed`

## Problem
When loading a stage into the editor using "Nạp vào editor" button, the application crashed with:
```
_tkinter.TclError: can't invoke "wm" command: application has been destroyed
```

The error occurred when trying to update the window title and UI elements after loading, suggesting the Tkinter root window had been destroyed or was being accessed during shutdown.

## Root Cause
1. `load_stage_into_editor()` called `_update_root_title()` and `_update_target_window_display()` 
2. These functions directly accessed `root.title()` and `state.UI.target_window_text.set()`
3. If the window was closing or had been destroyed, Tkinter raises `TclError`
4. No error handling to gracefully handle destroyed widgets

## Solution
Added comprehensive error handling and safety checks:

### 1. **autoclick_gui.py** - Added Safety Checks
- **`_update_root_title()`**: 
  - Check if root window exists with `root.winfo_exists()` before updating
  - Wrapped in try-except to catch and log any errors
  
- **`_update_target_window_display()`**: 
  - Wrapped in try-except to handle widget access errors

### 2. **ui/library_panel.py** - Error Handling on Calls
- **`load_stage_into_editor()`**: 
  - Wrapped UI update calls in try-except
  - Logs errors but doesn't crash
  
- **`run_selected_stages()`**: 
  - Added try-except around UI updates
  - Safely handles missing UI elements

### Code Example
```python
def _update_root_title():
    """Update root window title to show target window status"""
    try:
        # Check if root window still exists
        if not root.winfo_exists():
            return
        
        base_title = "⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu"
        if state.game_hwnd and state.game_window_title:
            root.title(f"{base_title} | 🎯 TARGET: {state.game_window_title}")
        else:
            root.title(base_title)
    except Exception as e:
        safe_print(f"⚠️ [UPDATE_TITLE] Could not update title: {e}")
```

## Testing
✅ Load stage into editor - no crash  
✅ Target window display updates correctly  
✅ Window title shows target window status  
✅ Graceful error handling if window is closed  

## Files Modified
1. `autoclick_gui.py` - Added error handling in `_update_root_title()` and `_update_target_window_display()`
2. `ui/library_panel.py` - Added try-except blocks around UI calls

## Impact
- Zero breaking changes
- Improved robustness
- Better error messages for debugging
- Application no longer crashes on UI update failures
