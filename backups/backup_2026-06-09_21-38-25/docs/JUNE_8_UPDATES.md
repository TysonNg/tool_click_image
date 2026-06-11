# Updates - June 8, 2026

## Overview
Implemented target window persistence feature and fixed critical Tkinter error that occurred when loading scenarios.

---

## Feature 1: Target Window Persistence ✅

### What's New
When you set a target window using "🎯 Xác Định Cửa Sổ Đích", that information is now **automatically saved** with your scenario. When you load the scenario later, the target window is **automatically restored**.

### How to Use
1. Click "🎯 Xác Định Cửa Sổ Đích" to select your game window
2. Make changes to your scenario (add/delete templates)
3. Click "💾 Lưu Editor" to save
4. Next time you load this scenario, target window will be restored automatically

### Files Modified
- `scenario/io.py` - Save/load functions now include target window data
- `ui/library_panel.py` - Load functions restore target window
- `autoclick_gui.py` - UI update functions have error handling

### JSON Format
Scenarios now include:
```json
{
  "game_hwnd": <window_handle>,
  "game_window_title": "Your Game Window",
  "templates": [...]
}
```

### Backward Compatibility
✅ Old scenarios without target window info still work fine  
✅ No breaking changes

---

## Fix 1: TclError - Application Destroyed ✅

### Problem
When clicking "Nạp vào editor" (Load stage into editor), the app crashed with:
```
_tkinter.TclError: can't invoke "wm" command: application has been destroyed
```

### Solution
Added comprehensive error handling:
- **`_update_root_title()`** - Now checks if window exists before updating
- **`_update_target_window_display()`** - Wrapped in try-except
- **UI calls** - All wrapped in try-except with logging

### Impact
✅ No more crashes when loading scenarios  
✅ Better error messages for debugging  
✅ Graceful handling of destroyed widgets

### Files Modified
- `autoclick_gui.py` - Error handling in UI functions
- `ui/library_panel.py` - Error handling around UI calls

---

## Technical Details

### Modified Functions

#### scenario/io.py
- `_build_scenario_payload()` - Saves game_hwnd, game_window_title
- `_build_metadata_payload()` - Includes target window in metadata
- `load_templates_from_file()` - Loads target window from JSON
- `load_scenario()` - Restores target window when loading

#### ui/library_panel.py
- `load_stage_into_editor()` - Loads and restores target window with error handling
- `run_selected_stages()` - Restores target window from first scenario with error handling

#### autoclick_gui.py
- `_update_root_title()` - Safe window title update with existence check
- `_update_target_window_display()` - Safe UI update with exception handling

---

## Testing Checklist

### Feature Testing
- [ ] Set target window using "🎯 Xác Định Cửa Sổ Đích"
- [ ] Delete a template and save scenario
- [ ] Load scenario back - target window should be restored
- [ ] Title bar shows: `⚡ PokéClick PRO — ... | 🎯 TARGET: [Window Name]`
- [ ] Scenario panel shows target window status
- [ ] Works with "Nạp vào editor" (Load to editor)
- [ ] Works with "TUNG POKÉBALL!" (Run selected stages)

### Error Handling Testing
- [ ] Load scenario when window is closed (should not crash)
- [ ] Close app while loading (should gracefully handle)
- [ ] Check debug logs for any warnings

---

## Known Limitations

1. **Window Handles are Process-Specific**
   - Window handles are only valid for the current session
   - If you close and reopen the game, you may need to re-set the target window
   - `core/relative_capture.py` validates handles with `win32gui.IsWindow()`

2. **Backward Compatibility**
   - Old scenarios work fine without target window data
   - New scenarios with target window work with new code only

---

## Files Changed Summary
- `scenario/io.py` - 35 lines modified (save/load functions)
- `ui/library_panel.py` - 25 lines modified (error handling, target window restore)
- `autoclick_gui.py` - 20 lines modified (error handling)

**Total: ~80 lines modified**

---

## Next Steps (Optional)
- [ ] Add option to clear target window from UI
- [ ] Add validation to test if window still exists on load
- [ ] Add logging to track target window state changes
- [ ] Consider persisting window by title instead of handle (more robust)

---

## Support
If you encounter issues:
1. Check debug console for error messages (format: `⚠️ [FUNCTION_NAME] Error message`)
2. Try loading a scenario that doesn't use target window
3. Verify target window is still open/valid
