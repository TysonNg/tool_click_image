# ⚡ AutoClick Pro - Quick Start (5 Minutes)

## Installation (2 minutes)

### Step 1: Install Python Requirements
```bash
cd "d:\Program Files\Autoclick_ver_2\tool_click_image"
pip install -r requirements_standalone.txt
```

If you get permission errors on Windows:
```bash
pip install --user -r requirements_standalone.txt
```

### Step 2: Run the Application
```bash
python autoclick_standalone.py
```

You should see a window with title "AutoClick Pro - Window-Relative Clicker"

---

## First Time Setup (3 minutes)

### Test with Notepad (Easiest)

1. **Open Notepad** (Windows + R → type `notepad` → Enter)
   - Keep it open and visible
   
2. **In AutoClick Pro:**
   - Enter window title: `Notepad` (or just `note`)
   - Click "🔍 Find Window"
   - Should show: ✅ Window found

3. **Capture a Position:**
   - Click "🎯 Capture Relative Position"
   - Follow instruction: "Move mouse to target position and press ENTER"
   - Move mouse somewhere in Notepad window
   - Press ENTER
   - Should show captured coordinates in pixels and percentage

4. **Test Click:**
   - Coordinates should be auto-filled from capture
   - Click "🖱️ Test Click"
   - Mouse should move to that position and click
   - Cursor in Notepad should appear at that position ✅

5. **Success!** You've completed first test

---

## Detailed Workflow

### Workflow 1: Find Window & Test Click

```
┌─────────────────────────────────────┐
│  1️⃣ SELECT WINDOW                  │
├─────────────────────────────────────┤
│ Window Title: [Notepad_____]        │
│ 🔍 Find Window                      │
│ ✅ Window found: Notepad (...)      │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  2️⃣ CAPTURE COORDINATES            │
├─────────────────────────────────────┤
│ 🎯 Capture Relative Position        │
│ Move mouse → Press ENTER            │
│ Pixels (X, Y): (123, 456)           │
│ Percentage: (30.2%, 45.6%)          │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  3️⃣ CLICK TARGET                   │
├─────────────────────────────────────┤
│ Mode: ⦿ Pixels  ○ Percentage       │
│ X: [123]  Y: [456]                  │
│ 🖱️ Test Click  📌 Use Captured     │
│ ✅ Click successful!                │
└─────────────────────────────────────┘
```

### Workflow 2: Multiple Captures

1. Capture first position (e.g., "OK button")
2. Write down coordinates: `(450, 200)`
3. Capture second position (e.g., "Input field")
4. Write down: `(300, 150)`
5. Now you can:
   - Enter first coordinates: `(450, 200)` → Click
   - Enter second coordinates: `(300, 150)` → Click
   - Repeat indefinitely!

---

## Common Use Cases

### Use Case 1: Click Same Button Repeatedly

```
Scenario: Auto-click "Next" button in wizard

1. Open application with wizard
2. Find window: "Wizard" 
3. Capture position of "Next" button → (500, 600)
4. Use captured coordinates
5. Click "Test Click" multiple times ✅
```

### Use Case 2: Click Multiple Targets in Sequence

```
Scenario: Fill form automatically

Positions captured:
- Name field: (200, 100)
- Email field: (200, 150)
- Submit button: (400, 200)

Steps:
1. Enter (200, 100) → Click "Test Click"
2. Type name
3. Enter (200, 150) → Click "Test Click"
4. Type email
5. Enter (400, 200) → Click "Test Click"
```

### Use Case 3: Use Percentage for Responsive Targets

```
Scenario: Click center of any game window

1. Find window: "My Game"
2. Mode: Percentage
3. X: 50, Y: 50 (center)
4. Click "Test Click"
→ Works if window size changes!
```

---

## Tips & Tricks

### 💡 Tip 1: Quick Capture + Click
- Capture position
- Immediately click "Use Captured"
- Click "Test Click"
- All done in 3 clicks!

### 💡 Tip 2: Save Coordinates
- Found a good position?
- Take screenshot of info display
- Or write down the (X, Y) values
- Later, paste into X and Y fields

### 💡 Tip 3: Window Still Works if Moved
```
Capture: Position inside window (100, 150)
Window was at: screen (1920, 1080)

Move window to different monitor
Window now at: screen (500, 500)

Click at same relative (100, 150)
→ Automatically converts to (600, 650) ✅
```

### 💡 Tip 4: Use Percentage for Flexibility
- Percentage coordinates scale with window size
- (50%, 50%) always clicks center
- (0%, 0%) always clicks top-left
- (100%, 100%) always clicks bottom-right

### 💡 Tip 5: Test with Verbose Output
- Check the info display (bottom section)
- See all coordinates being calculated
- Helps debug if click is off-target

---

## Troubleshooting Quick Fixes

### ❌ "Window not found"
**Solution:**
- Try partial title: `"note"` instead of `"Notepad"`
- Open Notepad first
- Check exact title in taskbar

### ❌ "Click didn't work"
**Solution:**
- Make sure window is not minimized
- Try clicking closer to window center first
- Check coordinates in info display

### ❌ Mouse position wrong
**Solution:**
- When you press ENTER to capture
- Verify mouse IS inside window
- Not outside on taskbar

### ❌ Application won't start
**Solution:**
- `pip install pyautogui pywin32`
- Restart command prompt
- Run as Administrator

---

## What's Happening Behind the Scenes

### When you click "Find Window"
```
1. Searches all open windows by title
2. Gets window handle (hwnd)
3. Calculates window position in screen coordinates
4. Stores for future use
```

### When you capture coordinates
```
1. Gets current mouse position (screen coordinates)
2. Subtracts window's top-left corner
3. Result = window-relative coordinates
   
Example:
- Mouse on screen: (1920, 1080)
- Window top-left: (1800, 1000)
- Relative coords: (120, 80)
```

### When you click
```
1. Takes your input coordinates (relative)
2. Adds window's current position
3. Result = screen coordinates to click
4. Moves mouse, clicks, restores position

Example:
- Input relative: (120, 80)
- Window now at: (1850, 1050)
- Calculates screen: (1970, 1130)
- Clicks there!
```

---

## Next Steps

After mastering basic clicking:

1. **Advanced**: Open `autoclick_standalone.py` in editor
2. **Modify**: Adjust click delay, add logging, etc.
3. **Extend**: Add keyboard input, multiple clicks in sequence
4. **Integrate**: Use this in your automation scripts

---

## Keyboard Shortcuts

Currently supported:
- **ENTER**: Capture coordinates (when prompted)
- **ESC**: (Planned for future version)

---

## FAQ

**Q: Will this work on Mac/Linux?**
A: No, currently Windows-only (uses win32 API). Could be ported with cross-platform alternatives.

**Q: Can I automate games?**
A: Yes! Just make sure the game TOS allows automation.

**Q: Is it safe?**
A: Yes - open source, no data collection, runs locally only.

**Q: Can I save my clicks as macros?**
A: Not in this version, but you can write them down and re-enter them.

**Q: How fast can it click?**
A: ~5-10 clicks per second (limited by mouse movement time).

---

## You're Ready! 🎉

You now know how to:
- ✅ Find any window
- ✅ Capture relative coordinates
- ✅ Click at stored positions
- ✅ Adapt to window moves
- ✅ Use percentage coordinates

**Start automating!**

---

Need help? Check `AUTOCLICK_STANDALONE_README.md` for advanced topics.
