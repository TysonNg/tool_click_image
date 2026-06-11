# 🔧 AutoClick Tool — System Status Report
**Date:** June 9, 2026  
**Status:** ✅ **ALL SYSTEMS OPERATIONAL**

---

## ✅ Fixed Issues Summary

### 1. Window Handle Invalid Error ✅
- **Problem:** Script crashed when window was minimized, hidden, or closed
- **Solution:** `WindowGuard` module created with auto-validation and auto-restore
- **Files Modified:**
  - `core/window_guard.py` (new)
  - `core/runner.py` - Added pre-flight checks and continuous window protection
  - `core/relative_capture.py` - Added validation before operations

### 2. Auto-Restore Window on File Load ✅
- **Problem:** When loading saved scenario file, window target wasn't automatically restored
- **Solution:** Updated `load_scenario()` and `load_scenario_combo()` to auto-detect and restore window
- **Files Modified:**
  - `scenario/io.py` - Auto-restore functions
  - Scenario JSON files now save `"game_window_title"` at root level

### 3. Relative Coordinates Clicking Wrong Position ✅
- **Problem:** Relative coordinates were clicking at incorrect positions
- **Root Cause:** Coordinate offset logic was not properly adding window offset when clicking
- **Solution:** Corrected logic:
  - **Capture:** Get mouse screen coords → subtract window offset → save relative coords
  - **Click:** Load relative coords → add window offset → click at screen position
- **Files Modified:**
  - `core/runner.py` - Fixed coordinate handling

### 4. Window Title Matching After Restart ✅
- **Problem:** When user closed game and opened new instance with same title, script couldn't recognize it
- **Solution:** Auto-recovery by finding window by title using `RelativeCoordinateCapture.find_window_by_title()`
- **Files Modified:**
  - `core/runner.py` - `smart_start()` function added auto-recovery
  - `core/relative_capture.py` - Added `find_window_by_title()` method

### 5. Import Old Scenario (Kịch Bản Cũ) ✅
- **Problem:** Couldn't find image files when importing old scenarios due to filename duplicates
- **Root Cause:** Old save system created duplicates with suffixes (1_2.png, 1_3.png) but old paths referenced wrong files
- **Solution:** Enhanced `import_old_scenario()` with smart image discovery:
  - Try exact filename first
  - Try base name without suffix (remove _2, _3, etc with regex)
  - Ask user to specify custom image directory if not found
- **Files Modified:**
  - `scenario/library.py` - Enhanced import function

### 6. Full Tool Backup System ✅
- **Problem:** No backup system for tool safety
- **Solution:** Created `create_backup.py` script that:
  - Backs up entire tool (excludes .git, __pycache__, backups)
  - Creates timestamped folders
  - Keeps only latest 3 backups automatically
- **Files Created:**
  - `create_backup.py`
- **Latest Backups:**
  - `backup_2026-06-09_21-36-45`
  - `backup_2026-06-09_21-38-25`
  - `backup_2026-06-09_21-38-56`

---

## 📊 System Architecture

### Window Protection Flow
```
User clicks "Run" 
    ↓
smart_start() checks window validity
    ↓
WindowGuard.protect_window() called
    ↓
    ├─ Window visible? If minimized/hidden → restore
    ├─ Window valid? If invalid handle → find by title
    └─ Window focused? If not → bring to foreground
    ↓
find_and_click() executes templates
    ↓
Before each template: WindowGuard.validate_window()
    ↓
If window lost during execution → auto-recovery or error
```

### Coordinate System Flow
**Relative Coordinates:**
```
Step 1: CAPTURE PHASE
  User clicks "Lấy Tọa Độ Tương Đối"
  ↓
  Get mouse position on screen (absolute)
  ↓
  Get game window offset (client_left, client_top)
  ↓
  Calculate relative = screen - offset
  ↓
  Save relative to file + window_title for verification

Step 2: EXECUTION PHASE
  Load scenario file
  ↓
  Load relative coordinates and window_title
  ↓
  Get current window offset
  ↓
  Calculate screen = relative + offset
  ↓
  Click at screen position
```

### Scenario File Structure
```json
{
  "process_loops": 1,
  "infinite_loop": false,
  "click_delay": 1.0,
  "game_window_title": "MapleStoryM",  // ← Auto-restored on load
  "templates": [
    {
      "type": "image",
      "path": "1.png",
      "is_relative": false,
      ...
    },
    {
      "type": "coord",
      "x": 512,
      "y": 300,
      "is_relative": true,  // ← Relative coordinates
      "window_title": "MapleStoryM",
      "game_hwnd": null,  // ← No longer used (found by title)
      ...
    }
  ]
}
```

---

## 🛡️ Safety Features

### 1. Window Validation
- Checks window handle validity before operations
- Restores minimized/hidden windows automatically
- Brings window to foreground before clicking

### 2. Coordinate Protection
- Validates coordinates before clicking
- Supports both absolute and relative coordinates
- Auto-converts relative → absolute using current window offset

### 3. Error Recovery
- Window lost during execution → auto-finds by title
- If auto-find fails → stops cleanly and reports error
- Pre-flight checks before starting execution

### 4. Data Backup
- Automatic timestamped backups
- Keeps only 3 latest backups (cleanup of older ones)
- Full tool backup excludes cache and .git

---

## 📋 Current Scenarios

### Dragon City
- ✅ Arena
- ✅ HeartWave
- ✅ High_Fighter_Dragon
- ✅ High_Risen_Star_Dragon
- ✅ Positive_Dragon

### Maple Story M
- ✅ Change_Character
- ✅ Cooking
- ✅ Daily Dungeon (14 captures)
- ✅ Dimension
- ✅ Elite
- ✅ Evolution
- ✅ Monster_Park
- ✅ Mulung
- ✅ Quest_Story

**Note:** Old scenarios (created before window target feature) don't have `game_window_title`. When loaded, user will be prompted to select target window if it's not found automatically.

---

## ⚙️ Technical Details

### Key Modules

**`core/window_guard.py`**
- `validate_window()` - Check if handle is valid
- `protect_window()` - Restore and focus window
- `check_and_warn()` - Get warning message if window issue

**`core/relative_capture.py`**
- `get_game_window_info()` - Get window position/size
- `find_window_by_title()` - Find window by partial title match
- `start_capture_ui()` - Show capture overlay

**`core/runner.py`**
- `smart_start()` - Pre-flight checks + auto-recovery
- `find_and_click()` - Main execution loop with window protection
- `_resolve_click_point()` - Calculate click position from template

**`scenario/io.py`**
- `load_scenario()` - Load single scenario with auto-restore
- `load_scenario_combo()` - Load multiple scenarios with auto-restore
- `save_scenario_to_stage()` - Save scenario with target window

**`scenario/library.py`**
- `import_old_scenario()` - Import old scenarios with smart image discovery

---

## 🚀 Usage Tips

### Setting Up Target Window
1. Click "🎯 Xác Định Cửa Sổ Đích"
2. Enter window title (partial match supported)
3. Window will be highlighted with flash effect
4. Title will appear in window title bar

### Using Relative Coordinates
1. Set target window first
2. Click "📍 Lấy Tọa Độ Tương Đối"
3. Use capture overlay to select position
4. Coordinates automatically stored relative to window

### Running Scenarios
1. Load scenario: "📂 Tải dữ liệu Trainer"
2. Target window will be auto-restored if saved
3. Click "⚡ TUNG POKÉBALL!" to start
4. If window gets closed → auto-finds by title and resumes

---

## ✅ Verification Checklist

- [x] Window handle validation working
- [x] Auto-restore on minimized window
- [x] Auto-find by title when window changes
- [x] Relative coordinates calculating correctly
- [x] Window title saved/restored in scenarios
- [x] Old scenarios can be imported
- [x] Backup system operational
- [x] Error messages clear and actionable
- [x] Coordinate offset logic correct
- [x] Thread-safe operations

---

**Last Updated:** June 9, 2026 21:38:56  
**System:** Windows 10/11 64-bit  
**Python:** 3.12+  
**Dependencies:** pyautogui, opencv-python, pillow, win32gui, win32api
