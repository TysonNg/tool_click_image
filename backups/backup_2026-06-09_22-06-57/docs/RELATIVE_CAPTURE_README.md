# 📍 Lấy Tọa Độ Tương Đối - Complete Implementation Guide

## 🎯 Overview

The **Relative Coordinate Capture** feature allows you to capture game window-relative coordinates with a single click. Instead of using fixed screen coordinates that break when the window moves, this system captures coordinates relative to the game window itself.

**Key Benefit**: Coordinates work perfectly even if the game window moves to a different monitor or position!

---

## 🚀 Quick Start (1 Minute)

### Step 1: Open AutoClick GUI
```
python autoclick_gui.py
```

### Step 2: Click the Button
Look for: **"📍 Lấy Tọa Độ Tương Đối (Relative)"**
- Location: Left panel, purple button
- Section: ⚔️ KỸ NĂNG CHIẾN ĐẤU

### Step 3: Enter Window Name
```
Dialog appears:
"📍 Xác Định Cửa Sổ Game"

Type: "Chrome" (or game window name)
Click: OK
```

### Step 4: Capture Coordinates
```
Instruction popup appears:

1️⃣ Move mouse to target position
2️⃣ Press ENTER
3️⃣ Done!
```

### Step 5: Configure Settings
```
Dialog opens with pre-filled coordinates:

📍 Tọa độ X: [450]  ← From your cursor position!
📍 Tọa độ Y: [200]  ← From your cursor position!

Set other options (optional):
- Click type: single/double/hold
- Delay: 0.5s (or custom)
- Repeat: 1 (or more)

Click: OK
```

### Step 6: Template Added!
```
Right panel shows:
📍 (450, 200) [56.3%, 33.3%] (single, 0.5s)
```

✅ **Done!** You can now execute this template with the bot.

---

## 📚 Detailed Documentation

### For Users
👉 **Read**: [`CAPTURE_WITH_CONFIG.md`](./CAPTURE_WITH_CONFIG.md)
- Complete workflow
- Real-world examples
- Screenshots/diagrams
- Tips and tricks

### For Testing
👉 **Read**: [`RELATIVE_CAPTURE_TEST_GUIDE.md`](./RELATIVE_CAPTURE_TEST_GUIDE.md)
- 10 test scenarios
- Expected results
- Error handling
- Debug output

### For Developers
👉 **Read**: [`IMPLEMENTATION_VERIFICATION.md`](./IMPLEMENTATION_VERIFICATION.md)
- Technical implementation
- Code structure
- API reference
- Integration details

### Quick Overview
👉 **Read**: [`FEATURE_COMPLETE_SUMMARY.md`](./FEATURE_COMPLETE_SUMMARY.md)
- What was built
- Files changed
- Quick summary

---

## 🎮 Real-World Example

### Scenario: Capture "Accept" Button in Game

**Step 1: Start Capture**
```
Button: "📍 Lấy Tọa Độ Tương Đối"
Click!
```

**Step 2: Select Window**
```
Dialog: "Nhập tên cửa sổ game"
Type: "my game"
Click: OK

Status: ✅ Đã xác định: My Game | Vị trí: (100, 50) | Kích thước: 1024x768
```

**Step 3: Position Mouse**
```
Move mouse to "Accept" button
in the game window
```

**Step 4: Capture**
```
Press: ENTER

Console: ✅ Lấy tọa độ: Pixel(450, 300) | Phần trăm(43.9%, 39.1%)
```

**Step 5: Configure**
```
Config Dialog:
📍 X: [450]
📍 Y: [300]
Click type: [single] ✓
Delay: [0.5]
Repeat: [1]

Click: OK
```

**Step 6: Added!**
```
List shows:
📍 (450, 300) [43.9%, 39.1%] (single, 0.5s)
```

**Step 7: Use It**
```
Click "⚡ TUNG POKÉBALL!"
Bot clicks at relative position (450, 300)

✅ Works even if game window moves!
```

---

## 🔧 How It Works (Technical)

### Coordinate System

**Before (Absolute - BROKEN):**
```
Screen: 1920x1080
Game Window: Position (200, 100)

Captured: Click at (650, 350) on screen
Problem: If window moves to (400, 100), click breaks!
```

**After (Relative - WORKS):**
```
Screen: 1920x1080
Game Window: Position (200, 100), Size (1024x768)

Relative Click: (450, 250) within window
On Click:
  - Get window position: (200, 100)
  - Calculate: screen_x = 200 + 450 = 650
  - Calculate: screen_y = 100 + 250 = 350
  - Click at (650, 350)

Result: Works if window moves to (400, 100)!
  - screen_x = 400 + 450 = 850
  - screen_y = 100 + 250 = 350
  - Click at (850, 350) ✅ Correct!
```

### Implementation Structure

```python
core/relative_capture.py
├─ RelativeCoordinateCapture (class)
│  ├─ get_game_window_info()      # Find window + get position/size
│  ├─ screen_to_relative()        # Convert screen → relative
│  ├─ relative_to_screen()        # Convert relative → screen
│  ├─ percentage_to_relative()    # Convert % → pixels
│  └─ start_capture_ui()          # Show popup + capture

autoclick_gui.py
├─ ask_window_title_custom()      # Custom dialog for window name
├─ capture_relative_coordinates() # Main handler (Step 1-7)
└─ Button "📍 Lấy Tọa Độ Tương Đối"

ui/dialogs.py
└─ show_coordinate_config_dialog(initial_x, initial_y)
   # Dialog with pre-filled values

core/state.py
├─ game_hwnd                # Window handle
├─ captured_relative_x      # Last captured X
├─ captured_relative_y      # Last captured Y
└─ captured_relative_percent_x/y
```

---

## 🎯 Features

### ✅ What You Get

| Feature | Description |
|---------|-------------|
| 📍 Window Selection | Enter partial window name, auto-finds |
| 🖱️ Click Capture | Move mouse + ENTER to capture |
| 🔄 Auto-Convert | Converts to relative + percentage |
| ⚙️ Pre-fill | Config dialog shows captured X, Y |
| 🎛️ Full Config | Set click type, delay, repeat count |
| 📊 Template | Added to list with full details |
| 💾 Save/Load | Works with scenario save/load |
| ♻️ Window Move | Coordinates still work when window moves |

### ⚙️ Configuration Options

```
After capturing coordinates, you can set:

📍 Tọa độ X, Y
   Pre-filled from capture
   Can edit if needed

📍 Số lần click
   1 = Click once
   N = Click N times

🖱️ Loại click
   ◉ single (default)
   ○ double (fast double-click)
   ○ hold (hold mouse button)

⏱️ Delay sau click
   0.5s (default)
   Can set any value
```

---

## 📋 Display Format

### In the List

```
📍 (450, 300) [43.9%, 39.1%] (single, 0.5s)

Breakdown:
📍 = Icon (coordinate action)
450, 300 = Pixel coordinates (relative to window)
43.9%, 39.1% = Percentage of window width/height
single = Click type
0.5s = Delay after click
```

### Properties You See

| Property | Example | Meaning |
|----------|---------|---------|
| Icon | 📍 | Type: Coordinate |
| X | 450 | Horizontal position in pixels |
| Y | 300 | Vertical position in pixels |
| %X | 43.9% | X as % of window width |
| %Y | 39.1% | Y as % of window height |
| Type | single | Click behavior |
| Delay | 0.5s | Seconds to wait after |

---

## 🛠️ Working With Templates

### Edit Template

```
1. Click to select template in list:
   📍 (450, 300) [43.9%, 39.1%] (single, 0.5s)

2. Click "✏️ Sửa" button

3. Edit any field:
   - X, Y coordinates
   - Click type
   - Delay
   - Repeat count

4. Click OK to save changes
```

### Delete Template

```
1. Select template in list

2. Click "🗑️ Xóa" button

3. Template removed immediately
```

### Move Template

```
1. Select template

2. Click "▲ Lên" (move up)
   or "▼ Xuống" (move down)

3. Order in list changes
   (execution order when running bot)
```

---

## 💾 Save & Load

### Save Scenario

```
Steps:
1. Add templates via capture or other methods
2. Click "💾 Lưu dữ liệu Trainer"
3. Enter scenario name
4. Click Save

Result: All templates saved to file
        Including relative coordinates!
```

### Load Scenario

```
Steps:
1. Click "📂 Tải dữ liệu Trainer"
2. Select scenario file
3. Click Open

Result: All templates loaded
        Ready to use with bot!
```

---

## 🧪 Testing

### Quick Test

```
1. Click "📍 Lấy Tọa Độ Tương Đối"
2. Type window name (e.g., "notepad")
3. Press OK
4. Move mouse anywhere in the window
5. Press ENTER
6. Verify config dialog shows X, Y values
7. Click OK
8. Check list shows template with emoji
```

### Full Test

```
See RELATIVE_CAPTURE_TEST_GUIDE.md for:
- 10 detailed test scenarios
- Expected results
- Error handling tests
- Edge cases
```

---

## ⚠️ Important Notes

### Window Name

```
✅ Can use partial names:
   "chrome" → finds Google Chrome
   "note" → finds Notepad
   "my game" → finds "My Game Title"

❌ Must be case-insensitive match
❌ Window must be visible
```

### Coordinate Capture

```
✅ Press ENTER to capture
✅ Works with any position in window
✅ Shows instruction popup

❌ Must have window in focus (ideally)
❌ ENTER must be pressed on keyboard
```

### Click Execution

```
✅ Works when window is at any position
✅ Works when window moves
✅ Works on different monitors

❌ Window must still exist when clicking
❌ Position inside window must be valid
```

---

## 🐛 Troubleshooting

### Problem: Window Not Found

**Error Message**: "Không tìm thấy cửa sổ: Chrome"

**Solutions**:
1. Check exact window title: use title bar text
2. Try partial name matching
3. Ensure window is open
4. Try just first word of title

### Problem: Coordinate Wrong

**Symptom**: Click happens at wrong position

**Solutions**:
1. Move mouse to EXACT center of target
2. Press ENTER immediately after moving
3. Check X, Y values in config dialog
4. Edit if needed before clicking OK

### Problem: Dialog Doesn't Show

**Symptom**: Nothing happens after button click

**Solutions**:
1. Check if background task is running
2. Look for popup that might be hidden
3. Check system tray for hidden windows
4. Try clicking button again

### Problem: Can't Find Window

**Solutions**:
1. Use exact window title from title bar
2. Try first few words only
3. Use very unique part of title
4. Ensure window is not minimized

---

## 📞 Support

### Documentation
- User Guide: [`CAPTURE_WITH_CONFIG.md`](./CAPTURE_WITH_CONFIG.md)
- Test Guide: [`RELATIVE_CAPTURE_TEST_GUIDE.md`](./RELATIVE_CAPTURE_TEST_GUIDE.md)
- Technical: [`IMPLEMENTATION_VERIFICATION.md`](./IMPLEMENTATION_VERIFICATION.md)

### Debug

Check console output for messages like:
```
✅ Xác định cửa sổ: ...
✅ Lấy tọa độ: Pixel(...) | Phần trăm(...)
✅ Đã thêm tọa độ tương đối: ...
```

---

## 🎉 You're Ready!

The relative coordinate capture system is:
- ✅ Fully implemented
- ✅ Thoroughly tested
- ✅ Well documented
- ✅ Ready to use

**Start capturing coordinates now!** 🚀

---

**Version**: 3.0  
**Status**: Production Ready  
**Last Updated**: June 2026

