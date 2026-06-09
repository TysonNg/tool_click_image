# 📝 Auto-Restore Window on Load - Fixed! ✅

**Date:** June 9, 2026  
**Issue:** Load old file but window target not automatically restored  
**Status:** ✅ FIXED

---

## 🎯 Problem

When you:
1. **Set target window** (e.g., MapleStoryM)
2. **Add actions** (images, coordinates)
3. **Save** the file
4. **Load the file** again

**Before Fix:**
- ❌ Window target was saved but NOT restored
- ❌ You had to manually select window again via "🎯 Xác Định Cửa Sổ Đích"
- ❌ If you clicked "Start" without re-selecting, you'd get "Window handle invalid" error

**After Fix:**
- ✅ Window target is automatically restored when loading file
- ✅ If window not found, you get a friendly warning
- ✅ UI updates to show restored window
- ✅ Status bar shows clear information

---

## ✅ What Was Fixed

### Changes to `scenario/io.py`

#### 1. **Updated `load_scenario()` function**

**Added:**
- Auto-detects saved window title from JSON file
- Automatically finds window by title using `find_window_by_title()`
- Sets `state.game_hwnd` and `state.game_window_title`
- Updates UI to reflect restored window
- Shows helpful status messages

**Flow:**
```
Load JSON file
    ↓
Check if "game_window_title" saved?
    ├─ YES → Try to find window
    │   ├─ Found → Set as target + update UI ✅
    │   └─ Not Found → Show warning message ⚠️
    └─ NO → Show info message ℹ️
```

#### 2. **Updated `load_scenario_combo()` function**

**Added:**
- When loading multiple scenario files
- Uses FIRST file's window title for auto-restore
- Same auto-restore logic as `load_scenario()`
- Handles multiple files gracefully

**Flow:**
```
Load 1+ JSON files
    ↓
Get window title from FIRST file
    ├─ YES → Try to find window
    │   ├─ Found → Set as target + update UI ✅
    │   └─ Not Found → Show warning ⚠️
    └─ NO → Show info message ℹ️
```

### Code Changes

#### Before:
```python
def load_scenario():
    # ... load file ...
    state.templates = templates
    update_history()
    state.UI.status_label.config(text=f"Da tai kich ban: {os.path.basename(file_path)}")
```

#### After:
```python
def load_scenario():
    # ... load file ...
    state.templates = templates
    
    # AUTO-RESTORE WINDOW TARGET if saved in file
    saved_window_title = scenario.get("game_window_title")
    if saved_window_title:
        safe_print(f"🔍 [LOAD] Trying to restore target window: {saved_window_title}")
        
        # Try to find window by title
        hwnd = RelativeCoordinateCapture.find_window_by_title(saved_window_title)
        if hwnd:
            state.game_hwnd = hwnd
            state.game_window_title = saved_window_title
            
            # Update UI
            _update_root_title()
            _update_target_window_display()
            
            safe_print(f"✅ [LOAD] Target window restored: {saved_window_title}")
```

---

## 📊 Status Messages

### ✅ Window Successfully Restored:
```
✅ Đã tải kịch bản: Character_2.json | Cửa sổ đích: MapleStoryM
```

### ⚠️ Window Not Found:
```
⚠️ Tải kịch bản thành công nhưng không tìm được cửa sổ: MapleStoryM.
Vui lòng bấm '🎯 Xác Định Cửa Sổ Đích'
```

### ℹ️ No Window Saved:
```
✅ Tải kịch bản: Character_2.json | ⚠️ Chưa có cửa sổ đích. 
Bấm '🎯 Xác Định Cửa Sổ Đích'
```

---

## 🚀 How It Works Now

### Step by Step:

#### 1. First Time Setup:
```
1. Open game (MapleStoryM)
2. Click "🎯 Xác Định Cửa Sổ Đích" → Select MapleStoryM
3. Add actions (images, coordinates)
4. Click "💾 Lưu dữ liệu Trainer"
   → Saves file with window info ✅
```

#### 2. Load Saved File Later:
```
1. Click "📂 Tải dữ liệu Trainer"
2. Select your saved file
   → System auto-restores window ✅
3. See status: "✅ Cửa sổ đích: MapleStoryM"
4. Click "⚡ TUNG POKÉBALL!" → Runs immediately ✅
```

#### 3. If Window Not Found:
```
1. Click "📂 Tải dữ liệu Trainer"
2. Select your saved file
   → System tries to find window
   → Window not running? Sees warning ⚠️
3. See status: "⚠️ không tìm được cửa sổ"
4. Options:
   a) Start game first, then load file again
   b) Click "🎯 Xác Định Cửa Sổ Đích" to manually select
```

---

## 🎯 File Structure

### What Gets Saved:

```json
{
  "process_loops": 1,
  "infinite_loop": false,
  "click_delay": 1.0,
  "game_window_title": "MapleStoryM",
  "templates": [
    { ... template data ... }
  ]
}
```

**Key:** `"game_window_title": "MapleStoryM"` is now used on load

---

## ✨ Features

### Auto-Restore:
- ✅ Detects window title from saved file
- ✅ Automatically finds window by title
- ✅ No manual selection needed
- ✅ Works with partial window title match

### Smart Warnings:
- ✅ Tells you if window not found
- ✅ Suggests what to do next
- ✅ Updates UI with status
- ✅ Logs all actions

### Multiple Files:
- ✅ When loading queue of files
- ✅ Uses FIRST file's window
- ✅ Auto-restores for all scenarios

---

## 🔍 Debug Logs

When loading file, check console for:

### ✅ Success:
```
🔍 [LOAD] Trying to restore target window: MapleStoryM
✅ [LOAD] Target window restored: MapleStoryM (HWND: 12345678)
```

### ⚠️ Not Found:
```
🔍 [LOAD] Trying to restore target window: MapleStoryM
⚠️ [LOAD] Window not found: MapleStoryM
```

### ℹ️ Not Saved:
```
ℹ️ [LOAD] No target window saved in file
```

---

## 🆘 Troubleshooting

### Q: "⚠️ không tìm được cửa sổ" after loading?

**A:** 
1. Make sure game is running
2. Make sure game window is visible (not minimized)
3. Try clicking "🎯 Xác Định Cửa Sổ Đích" to re-select
4. Load file again

### Q: What if window name changed?

**A:**
1. Game renamed/updated its window title
2. Click "🎯 Xác Định Cửa Sổ Đích" to re-select
3. Re-save file with new window name

### Q: Old file has wrong window saved?

**A:**
1. Load the file
2. Click "🎯 Xác Định Cửa Sổ Đích" to select correct window
3. Re-save with "💾 Lưu dữ liệu Trainer"

---

## 📋 Before vs After

| Scenario | Before | After |
|----------|--------|-------|
| Load saved file | ❌ No window set | ✅ Auto-restore window |
| Window not found | ❌ Silent failure | ✅ Clear warning |
| UI updates | ❌ No | ✅ Yes |
| Status message | ❌ Generic | ✅ Specific |
| Multiple files | ❌ No window | ✅ Auto-restore first |

---

## 🎓 How Window Matching Works

The system uses `find_window_by_title()` which:

1. **Partial match** - Window title can be substring
   - Saved: "MapleStoryM"
   - Actual: "MapleStoryM [REBOOT]"
   - ✅ MATCH - "MapleStoryM" is in actual title

2. **Case-insensitive**
   - Saved: "maplestorym"
   - Actual: "MapleStoryM"
   - ✅ MATCH

3. **First match wins**
   - If multiple windows match, uses first one found
   - Usually the one that opened first

---

## 🔧 Technical Details

### Modified Function: `load_scenario()`

**Location:** `scenario/io.py`

**Changes:**
- Added import: `from core.relative_capture import RelativeCoordinateCapture`
- Added auto-restore logic
- Added UI update calls
- Added detailed logging
- Added status messages

**Time Complexity:** O(n) where n = number of windows (search)

### Modified Function: `load_scenario_combo()`

**Location:** `scenario/io.py`

**Changes:**
- Same as `load_scenario()` but for first file in queue
- Handles multiple files gracefully

---

## 📝 Implementation Details

### Step 1: Check Saved Window
```python
saved_window_title = scenario.get("game_window_title")
if saved_window_title:
    # Try to restore
```

### Step 2: Find Window
```python
hwnd = RelativeCoordinateCapture.find_window_by_title(saved_window_title)
if hwnd:
    # Success
else:
    # Not found
```

### Step 3: Set State
```python
state.game_hwnd = hwnd
state.game_window_title = saved_window_title
```

### Step 4: Update UI
```python
from autoclick_gui import _update_root_title, _update_target_window_display
_update_root_title()
_update_target_window_display()
```

### Step 5: Show Message
```python
state.UI.status_label.config(
    text=f"✅ Window restored: {saved_window_title}",
    fg="#00cc00"
)
```

---

## ✅ Testing Checklist

- ✅ Single file load with window restore
- ✅ Single file load without window
- ✅ Multiple files with window restore
- ✅ Window not found (game closed)
- ✅ Window not found (game not running)
- ✅ Partial window title match
- ✅ Case-insensitive matching
- ✅ UI updates correctly
- ✅ Status messages clear
- ✅ Logs helpful for debugging

---

## 🎉 Summary

### What You Get:
- ✅ **No more manual window re-selection**
- ✅ **Automatic window detection on load**
- ✅ **Clear error messages if window not found**
- ✅ **Works with multiple files**
- ✅ **Backwards compatible with old files**

### How to Use:
1. Set window → Add actions → Save
2. Later: Load file → Window auto-restored ✅
3. Click "Start" → Runs immediately

### If Issues:
- Game not running? Auto-detect fails, shows warning
- Window closed? Shows helpful message
- Just click "🎯 Set Window" again to fix

---

**Version:** 2.0.1 - Auto-Restore Window on Load  
**Date:** June 9, 2026  
**Status:** ✅ Production Ready

**Happy clicking!** 🖱️✨
