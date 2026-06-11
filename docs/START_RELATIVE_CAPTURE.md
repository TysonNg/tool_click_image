# 🎯 START HERE - Lấy Tọa Độ Tương Đối (Relative Coordinate Capture)

## ⚡ Welcome!

This document is your entry point to the **Relative Coordinate Capture** feature.

**What is it?** A professional tool for capturing game window coordinates that work even when the window moves!

**How long does it take?** 5 minutes to learn, 30 seconds to use.

---

## 🚀 Quickest Start (2 minutes)

### Step 1: Open AutoClick GUI
```bash
python autoclick_gui.py
```

### Step 2: Find the Button
Look for this purple button in the left panel:
```
📍 Lấy Tọa Độ Tương Đối (Relative)
```

### Step 3: Click It!
Dialog appears asking for window name:
```
Dialog: "Nhập tên cửa sổ game"
Type: "notepad" (or your game window)
Click: OK
```

### Step 4: Capture
Instruction popup shows:
```
1️⃣ Move mouse to target position
2️⃣ Press ENTER
```

### Step 5: Done!
Config dialog opens with your coordinates pre-filled. Click OK and done!

---

## 📚 Full Documentation (Choose Your Path)

### Path 1: I Want to Learn Everything (15 min)
👉 Read: [`RELATIVE_CAPTURE_README.md`](./RELATIVE_CAPTURE_README.md)

This gives you:
- Complete overview
- How it works (technical)
- Examples and tips
- Troubleshooting

### Path 2: I Want Step-by-Step Guide (20 min)
👉 Read: [`CAPTURE_WITH_CONFIG.md`](./CAPTURE_WITH_CONFIG.md)

This gives you:
- Detailed workflow
- Real-world examples
- Configuration options
- Template management

### Path 3: I'm a Developer (30 min)
👉 Read: [`IMPLEMENTATION_VERIFICATION.md`](./IMPLEMENTATION_VERIFICATION.md)

This gives you:
- Technical architecture
- Code structure
- API documentation
- Integration details

### Path 4: I Just Want to Test It (2 min)
👉 Read: [`RELATIVE_CAPTURE_TEST_GUIDE.md`](./RELATIVE_CAPTURE_TEST_GUIDE.md)

This gives you:
- 10 test scenarios
- Expected results
- Error handling

### Path 5: Navigation Help
👉 Read: [`RELATIVE_CAPTURE_DOCS_INDEX.md`](./RELATIVE_CAPTURE_DOCS_INDEX.md)

This gives you:
- Complete navigation
- What each doc contains
- Learning paths
- Quick reference

---

## 🎯 What This Feature Does

```
PROBLEM:
  Game at position (100, 50) on screen
  You capture click at (500, 300)
  You move game window to (200, 100)
  Your click breaks! ❌

SOLUTION:
  Capture click relative to window: (400, 250)
  Click = window_position + relative_position
  Move window anywhere → Click still works! ✅
```

---

## 📋 Feature Overview

### Main Features
✅ **Window Selection** - Easy dialog to select game window  
✅ **Coordinate Capture** - Move mouse + press ENTER  
✅ **Auto-Configuration** - Config dialog with pre-filled values  
✅ **Template Management** - Edit, delete, reorder templates  
✅ **Save/Load** - Works with scenario save/load  
✅ **Window Movement** - Coordinates work when window moves  

### What You Get
- 📍 Beautiful purple button in UI
- 🪟 Custom window selection dialog
- ⌨️ ENTER key to capture
- ⚙️ Configuration with pre-filled coordinates
- 📊 Template displayed with full details
- 💾 Saves with your scenarios

---

## 🔄 Complete Workflow

```
1. Click Button
   📍 Lấy Tọa Độ Tương Đối
          ↓
2. Enter Window Name
   "Chrome", "Notepad", etc.
          ↓
3. See Confirmation
   ✅ Đã xác định: Chrome | Vị trí: (100, 50)
          ↓
4. Move Mouse & Press ENTER
   Position your cursor at target
   Press ENTER to capture
          ↓
5. Config Dialog Opens
   X: [450]  ← Pre-filled!
   Y: [200]  ← Pre-filled!
          ↓
6. Adjust Settings (optional)
   - Click type: single/double/hold
   - Delay: 0.5s (or custom)
   - Repeat: 1 (or more)
          ↓
7. Click OK
          ↓
8. Template Added!
   📍 (450, 200) [56.3%, 33.3%] (single, 0.5s)
          ↓
9. Use in Bot Execution
   Click "⚡ TUNG POKÉBALL!"
   Bot clicks at coordinates
   Works even if window moves!
```

---

## 💡 Example Use Case

### Scenario: Automate a Game

**Game Window**: At position (50, 50) on screen  
**Game Size**: 800x600 pixels

**Your Goal**: Click the "Accept" button in the center of the game

**Using This Feature**:
```
1. Click "📍 Lấy Tọa Độ Tương Đối"
2. Type "my game"
3. Move mouse to Accept button (center of window)
4. Press ENTER
5. Config shows: X=400, Y=300 (center of 800x600)
6. Click OK
7. Template added: 📍 (400, 300) [50%, 50%] (single, 0.5s)

Now you can:
✅ Move game window anywhere
✅ Bot still finds and clicks the button
✅ Click always happens at 50%, 50% of window (center)
```

---

## ⚙️ Configuration Options

When the config dialog appears, you can set:

```
📍 Tọa độ X, Y
   Automatically filled from your cursor position
   Can edit if needed

📍 Số lần click
   1 = Click once
   N = Click N times

🖱️ Loại click
   single = Normal click
   double = Double-click
   hold = Hold mouse button

⏱️ Delay sau click
   0.5s = Wait 0.5 seconds (default)
   Custom = Your choice
```

---

## 🎮 Try It Now!

### Setup (1 minute)
1. Make sure AutoClick GUI is open
2. Have a game or app window open (Notepad is fine for testing)
3. Look for the purple button in left panel

### Test (1 minute)
1. Click "📍 Lấy Tọa Độ Tương Đối"
2. Enter window name
3. Move mouse anywhere in the window
4. Press ENTER
5. Click OK in config dialog
6. See template appear in right panel

### Verify (1 minute)
- Template appears with format: `📍 (X, Y) [%X, %Y] (click_type, delay)`
- Can click other buttons: Edit, Delete, Move
- Try adding another coordinate

✅ You've mastered it in 3 minutes!

---

## 🛠️ Technical Stuff (Skip if Not Needed)

### Files Involved
```
autoclick_gui.py          - Main GUI with button + handler
core/relative_capture.py  - Window detection + coordinate conversion
ui/dialogs.py             - Config dialog (already ready)
core/state.py             - State management
```

### How It Works
```
Coordinate Conversion:
  screen_coords = (mouse_x, mouse_y)
  window_pos = get_window_position()
  relative_coords = (mouse_x - window_pos.x, mouse_y - window_pos.y)
  
When clicking:
  window_pos = get_window_position()  # Get current position
  click_at = (window_pos.x + relative_x, window_pos.y + relative_y)
  
Result: Works even if window moved!
```

---

## 📞 Getting Help

### Can't Find the Button?
→ Left panel, look for "⚔️ KỸ NĂNG CHIẾN ĐẤU" section  
→ Button is purple with emoji 📍

### Window Not Found?
→ Check you typed the correct window name  
→ Try partial name (just "chrome" instead of full title)  
→ Make sure window is open/visible

### Coordinates Wrong?
→ Move mouse to exact center of target  
→ Press ENTER immediately after positioning

### Need More Help?
→ See troubleshooting in [`RELATIVE_CAPTURE_README.md`](./RELATIVE_CAPTURE_README.md)  
→ Or read full guide in [`CAPTURE_WITH_CONFIG.md`](./CAPTURE_WITH_CONFIG.md)

---

## 📊 What's Different?

### Before (Absolute Coordinates)
```
❌ Click at screen position (500, 300)
❌ Breaks when window moves
❌ Hard to maintain coordinates
```

### After (Relative Coordinates)
```
✅ Click at window position (400, 200)
✅ Works when window moves
✅ Easy to maintain and reuse
✅ Portable across monitors
```

---

## ✅ You're Ready!

### Next Step: Choose Your Path

**Path A: Quick Start** (5 min)
```
1. Try the feature right now
2. Click the button
3. Follow prompts
4. See it work
```

**Path B: Learn First** (15 min)
```
1. Read RELATIVE_CAPTURE_README.md
2. Understand how it works
3. Then try the feature
4. Feel confident
```

**Path C: Full Documentation** (1 hour)
```
1. Read all documentation
2. Review test scenarios
3. Study the code
4. Master everything
```

---

## 🎉 Summary

| What | Time | Where |
|------|------|-------|
| Quick start | 2 min | This doc |
| Learn all | 15 min | RELATIVE_CAPTURE_README.md |
| Complete guide | 20 min | CAPTURE_WITH_CONFIG.md |
| Test it | 2-4 hrs | RELATIVE_CAPTURE_TEST_GUIDE.md |
| Study code | 1+ hr | IMPLEMENTATION_VERIFICATION.md |

---

## 🚀 Let's Go!

### Immediate Action Items

Pick one:

1. **Right Now**: Open GUI and click the purple button
2. **Read First**: Open [`RELATIVE_CAPTURE_README.md`](./RELATIVE_CAPTURE_README.md)
3. **Deep Dive**: Open [`RELATIVE_CAPTURE_DOCS_INDEX.md`](./RELATIVE_CAPTURE_DOCS_INDEX.md)

---

## 🎯 Your Goal

**Learn**: How to capture window-relative coordinates  
**Achieve**: Reliable automation that works regardless of window position  
**Time**: 5-15 minutes to full competency  

---

**Version**: 3.0  
**Status**: ✅ Production Ready  
**Created**: June 2026

**Ready?** Let's make your automation better! 🚀

---

**Next Step**: Click the purple button or read the guides above!

