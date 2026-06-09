# Target Window Persistence Feature

**Status**: ✅ Implemented  
**Date**: June 8, 2026

## Problem
When users set a target window using "Xác Định Cửa Sổ Đích" (Set Target Window) and then saved a scenario, the target window information was NOT being saved. When they loaded the scenario later, the target window had to be set again.

## Solution
Target window state is now persisted in the scenario JSON files.

### Changes Made

#### 1. **scenario/io.py** - Updated Save/Load Functions
- **`_build_scenario_payload()`**: Now saves `game_hwnd` and `game_window_title`
- **`_build_metadata_payload()`**: Now includes target window fields in metadata
- **`load_templates_from_file()`**: Now loads target window data into metadata
- **`load_scenario()`**: Restored target window state when loading standalone scenarios

#### 2. **ui/library_panel.py** - Load Functions Updated
- **`load_stage_into_editor()`**: 
  - Loads target window from JSON when loading stage into editor
  - Calls `_update_target_window_display()` and `_update_root_title()` to refresh UI
  
- **`run_selected_stages()`**: 
  - Restores target window from first scenario in queue
  - Updates UI to show target window after loading

#### 3. **autoclick_gui.py** - Existing Functions (No Changes Needed)
- `set_target_window()`: Already updates `state.game_hwnd` and `state.game_window_title`
- `_update_target_window_display()`: Already displays target window in scenario panel
- `_update_root_title()`: Already shows target window in title bar

### JSON Format
Scenarios now include:
```json
{
  "process_loops": 999999,
  "infinite_loop": true,
  "click_delay": 0.1,
  "game_hwnd": <window_handle>,
  "game_window_title": "Game Window Title",
  "templates": [...]
}
```

### Backward Compatibility
- Old scenarios without `game_hwnd`/`game_window_title` still load fine
- Fields are optional (can be `null`/not present)
- No breaking changes

### Testing Checklist
1. ✅ Set target window using "Xác Định Cửa Sổ Đích" button
2. ✅ Delete a template, save scenario
3. ✅ Load scenario back - target window should be restored
4. ✅ Title bar shows: `🎯 TARGET: [Window Name]`
5. ✅ Scenario panel shows target window status
6. ✅ Works for both editor mode ("Nạp vào editor") and queue mode ("TUNG POKÉBALL!")

### Notes
- Window handles are process-specific and may not be valid if window is closed
- `core/relative_capture.py` already has validation: checks if handle is still valid with `win32gui.IsWindow()`
- If window is closed, next run will request to set target window again
