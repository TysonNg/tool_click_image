# 🎯 Target Window Indicator - Feature Documentation

## What's New?

AutoClick now **displays the current target window** in the scenario panel so you know exactly which game window is configured.

---

## Features Implemented

### 1. **Target Window Display in Scenario Panel**
- **Location**: Top of the "POKÉDEX KỊCH BẢN" section (right panel)
- **Shows**: 🎯 Cửa sổ đích: [Window Name]
- **Default**: 🎯 Cửa sổ đích: Chưa xác định (No window set)
- **Color**: Gold/Yellow (PKM_GOLD #e76f51)
- **Updates**: Automatically when you set a new target window

### 2. **Title Bar Indicator**
- **Location**: AutoClick main window title bar
- **Format**: `⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu | 🎯 TARGET: [Window Name]`
- **Updates**: Immediately after setting target window

### 3. **Visual Feedback When Setting Target Window**
When you click "Xác định cửa sổ đích":
1. ✅ AutoClick window title updates with target window name
2. ✅ Scenario panel displays target window status
3. ✅ Target game window flashes 3 times (200ms each)
4. ✅ Console message confirms: `✅ Window đích: [Name] (HWND: xxxx)`
5. ✅ Status bar shows: `✅ Đã xác định cửa sổ đích: [Name] | Kích thước: WxH`

### 4. **Clear Target Window Button**
- **Location**: Bottom right of scenario panel (row3)
- **Label**: ❌ Bỏ Cửa sổ Đích
- **Color**: Gold (PKM_GOLD)
- **Function**: Clears the current target window setting
- **Actions When Clicked**:
  - Resets window title bar to base text
  - Resets scenario panel to "Chưa xác định"
  - Shows confirmation dialog
  - Prints: `❌ Đã bỏ cửa sổ đích`

---

## UI Layout - Scenario Panel (POKÉDEX KỊCH BẢN)

```
┌─ POKÉDEX KỊCH BẢN ──────────────────────────────┐
│                                                    │
│ ┌─ Lucario Decoration (120px) ─────────────────┐ │
│ │ Lucario Ready for Battle! ⚡                   │ │
│ └────────────────────────────────────────────────┘ │
│                                                    │
│ 🎯 Cửa sổ đích: Game Window Name (or "Chưa xác định") │
│ 🔄 Vòng lặp: 1 | ⚡ Tốc độ: 1.0s                │
│                                                    │
│ ┌─ History Listbox ─────────────────────────────┐ │
│ │ 1. [KEY: e] (nhấn 5 lần) [delay 1.0s]         │ │
│ │                                                │ │
│ └────────────────────────────────────────────────┘ │
│                                                    │
│ [▲ Lên] [▼ Xuống]                                  │
│ [✏️ Sửa] [🗑️ Xóa]                                  │
│ [📋 Quản Lý Kịch Bản] [🗑️ Xóa Sạch] [❌ Bỏ Cửa sổ Đích] │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Files Modified

**1. autoclick_gui.py**
- Added `_update_target_window_display()` function
- Added `clear_target_window()` function
- Added target window frame in scenario panel (lines ~720-730)
- Added "❌ Bỏ Cửa sổ Đích" button in row3 (lines ~788-804)
- Updated `set_target_window()` to call `_update_target_window_display()` (line ~159)

**2. core/state.py**
- Added `target_window_text = None` to UI class (line 44)

---

## Code Functions

### `_update_root_title()`
Updates AutoClick window title to show target window indicator
```python
def _update_root_title():
    """Update root window title to show target window status"""
    base_title = "⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu"
    if state.game_hwnd and state.game_window_title:
        root.title(f"{base_title} | 🎯 TARGET: {state.game_window_title}")
    else:
        root.title(base_title)
```

### `_update_target_window_display()`
Updates the target window status text in scenario panel
```python
def _update_target_window_display():
    """Update target window status display in scenario panel"""
    if state.game_hwnd and state.game_window_title:
        state.UI.target_window_text.set(f"🎯 Cửa sổ đích: {state.game_window_title}")
    else:
        state.UI.target_window_text.set("🎯 Cửa sổ đích: Chưa xác định")
```

### `clear_target_window()`
Clears the current target window setting
```python
def clear_target_window():
    """Clear target window setting"""
    state.game_hwnd = None
    state.game_window_title = None
    _update_root_title()
    _update_target_window_display()
    safe_print("❌ Đã bỏ cửa sổ đích")
    messagebox.showinfo("ℹ️ Thông báo", "Đã bỏ cửa sổ đích")
```

---

## User Workflow

### Setting a Target Window:
1. Click **"Xác định cửa sổ đích"** button (left panel)
2. Select game window from list
3. **Observe**:
   - Target window flashes 3x
   - Title bar shows: `... | 🎯 TARGET: Game Name`
   - Scenario panel shows: `🎯 Cửa sổ đích: Game Name`
   - Status bar confirms: `✅ Đã xác định cửa sổ đích: ...`

### Clearing Target Window:
1. Click **"❌ Bỏ Cửa sổ Đích"** button (bottom right of scenario panel)
2. **Observe**:
   - Target window status resets to "Chưa xác định"
   - Title bar returns to base text
   - Confirmation dialog appears

---

## Status Indicators

| State | Display |
|-------|---------|
| **No window set** | 🎯 Cửa sổ đích: Chưa xác định |
| **Window set** | 🎯 Cửa sổ đích: Dragon City |
| **Title bar** | ⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu \| 🎯 TARGET: Dragon City |
| **After clear** | 🎯 Cửa sổ đích: Chưa xác định |

---

## Color Scheme

- **Target Window Display**: PKM_GOLD (#e76f51)
- **Setup Info**: PKM_YELLOW (#ffd60a)
- **Background**: PKM_BG_CARD (#16213e)
- **Button (Clear)**: PKM_GOLD (#e76f51)
- **Button Hover**: #ff8c3d (darker orange)

---

## Testing Checklist

- [x] Target window indicator shows in scenario panel
- [x] Title bar updates with target window name
- [x] Target window flashes when set
- [x] Console prints confirmation message
- [x] Status bar shows detailed info
- [x] Clear button resets status
- [x] Display updates after setting new window
- [x] Display persists after adding actions to scenario

---

**Version**: 1.0  
**Date Implemented**: June 7, 2026  
**Status**: ✅ Complete
