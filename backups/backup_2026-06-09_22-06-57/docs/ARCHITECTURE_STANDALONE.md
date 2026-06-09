# 🏗️ AutoClick Pro - Architecture Documentation

## System Overview

```
┌────────────────────────────────────────────────────────────┐
│                      AutoClick Pro                         │
│                     (Tkinter GUI)                          │
└────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    ┌────────┐          ┌──────────┐        ┌──────────────┐
    │ Window │          │Coordinate│        │    Click     │
    │Manager │          │Converter │        │  Controller  │
    └────────┘          └──────────┘        └──────────────┘
         ↓                    ↓                    ↓
  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐
  │win32gui API │    │Math Operators│    │pyautogui Click │
  │win32api API │    │Calculations  │    │Mouse Movement  │
  └─────────────┘    └──────────────┘    └────────────────┘
```

---

## Component Architecture

### 1️⃣ WindowManager
**Purpose**: Find and track target windows

**Responsibilities**:
- Locate windows by title (exact or partial)
- Get window handle (hwnd)
- Calculate window position in screen coordinates
- Track window size
- Validate window still exists

**Key Methods**:
```python
class WindowManager:
    def find_window(title: str) -> bool
    def _update_window_position()
    def get_window_info() -> dict
    def is_valid() -> bool
```

**Uses**:
- `win32gui.FindWindow()` - Find by window class/title
- `win32gui.EnumWindows()` - Enumerate all windows
- `win32gui.ClientToScreen()` - Get client area origin
- `win32gui.GetClientRect()` - Get window dimensions
- `win32gui.IsWindow()` - Validate window exists

**State Variables**:
```
hwnd                 - Window handle
window_title         - Window title string
client_left          - Screen X of window top-left
client_top           - Screen Y of window top-left
window_width         - Width in pixels
window_height        - Height in pixels
```

---

### 2️⃣ CoordinateConverter
**Purpose**: Convert between coordinate systems

**Coordinate Systems**:

#### System 1: Screen Coordinates
- Origin: (0, 0) at top-left of monitor
- Used by: Windows OS, pyautogui
- Example: (1920, 1080)

#### System 2: Window-Relative Coordinates
- Origin: (0, 0) at top-left of window client area
- Used by: Our application
- Example: (100, 50)

#### System 3: Percentage Coordinates
- Origin: (0%, 0%) at top-left
- Dimensions: (100%, 100%) at bottom-right
- Used by: Responsive, adaptive clicking
- Example: (50%, 50%) = center

**Conversions**:

```python
# Screen → Window-Relative (core operation)
rel_x = screen_x - client_left
rel_y = screen_y - client_top

# Window-Relative → Screen (for clicking)
screen_x = client_left + rel_x
screen_y = client_top + rel_y

# Window-Relative ↔ Percentage
rel_x = (percent_x / 100) * window_width
percent_x = (rel_x / window_width) * 100
```

**Key Methods**:
```python
class CoordinateConverter:
    def screen_to_relative(sx, sy) -> (rx, ry)
    def relative_to_screen(rx, ry) -> (sx, sy)
    def percentage_to_relative(px, py) -> (rx, ry)
    def relative_to_percentage(rx, ry) -> (px, py)
```

**Advantages of Window-Relative**:
- ✅ Works if window moves to different monitor
- ✅ Works if window is repositioned
- ✅ Coordinates remain valid long-term
- ✅ Can share coordinates between users (different screen sizes)

---

### 3️⃣ ClickController
**Purpose**: Perform clicking operations safely

**Click Workflow**:
```
1. Validate window still exists
2. Convert relative coords → screen coords
3. Save current mouse position (optional)
4. Move mouse to target
5. Click (left/right button)
6. Restore mouse position (if enabled)
```

**Key Methods**:
```python
class ClickController:
    def click_at_relative(rel_x, rel_y, button, duration, restore) -> bool
    def get_current_mouse_screen_coords() -> (x, y)
```

**Safety Features**:

1. **Window Validation**
   ```python
   if not self.wm.is_valid():
       raise WindowError()
   ```

2. **Position Restoration**
   ```python
   current_pos = pyautogui.position()
   # ... click ...
   pyautogui.moveTo(current_pos, duration=0.1)
   ```

3. **Error Handling**
   ```python
   try:
       # click operation
   except Exception as e:
       logger.error(f"Click failed: {e}")
       return False
   ```

4. **Timing Controls**
   ```python
   time.sleep(0.05)  # Before click
   pyautogui.moveTo(..., duration=0.1)  # Move speed
   time.sleep(0.05)  # After click
   ```

---

### 4️⃣ AutoClickGUI
**Purpose**: User interface and user interaction

**Sections**:

#### Section 1: Window Selection
- Input field for window title
- Find button
- Status display

#### Section 2: Coordinate Capture
- Capture button
- Status indicator
- Display captured coordinates (pixels and %)

#### Section 3: Click Target
- Coordinate mode selector (pixels/percentage)
- X and Y input fields
- Test Click button
- Use Captured Coordinates button

#### Section 4: Information Display
- Real-time log output
- Shows all operations
- Useful for debugging

**UI Features**:
- Dark theme with accent colors
- Status indicators (✅ ✅ ❌ ⏳)
- Real-time feedback
- Clean, organized layout
- Information scrolling

---

## Data Flow Diagrams

### Flow 1: Window Selection
```
User enters window title
         ↓
[Button: Find Window]
         ↓
WindowManager.find_window(title)
         ↓
    win32gui API
         ↓
Found? → get hwnd, position, size
         ↓
UI: Display window info (✅ Window found)
```

### Flow 2: Coordinate Capture
```
User clicks "Capture"
         ↓
[Instruction: Move mouse to target, press ENTER]
         ↓
User presses ENTER
         ↓
pyautogui.position() → screen coords
         ↓
CoordinateConverter.screen_to_relative()
         ↓
Calculate: rel_x = screen_x - client_left
           rel_y = screen_y - client_top
         ↓
Also calculate percentage
         ↓
UI: Display both coordinates
    - Pixels: (123, 456)
    - Percentage: (30.2%, 45.6%)
```

### Flow 3: Clicking
```
User enters coordinates (or uses captured)
         ↓
User selects mode (pixels or percentage)
         ↓
[Button: Test Click]
         ↓
Validate mode:
- If percentage → convert to pixels
- If pixels → use directly
         ↓
ClickController.click_at_relative(x, y)
         ↓
Check WindowManager.is_valid()
         ↓
CoordinateConverter.relative_to_screen()
         ↓
Calculate: screen_x = client_left + rel_x
           screen_y = client_top + rel_y
         ↓
Save mouse position
         ↓
pyautogui.moveTo(screen_x, screen_y)
         ↓
pyautogui.click()
         ↓
Restore mouse position
         ↓
UI: Display result (✅ Click successful!)
```

---

## Class Relationships

```
┌──────────────────┐
│ AutoClickGUI     │  (Main UI)
├──────────────────┤
│ + wm             │───────┐
│ + cc             │───┐   │
│ + click_ctrl     │─┐ │   │
│ + widgets        │ │ │   │
└──────────────────┘ │ │   │
                     │ │   │
    ┌────────────────┘ │   │
    ↓                  │   │
┌──────────────────┐   │   │
│ ClickController  │   │   │
├──────────────────┤   │   │
│ - wm             │───┘   │
│ - cc             │───┐   │
│ + click_at_...() │   │   │
└──────────────────┘   │   │
                       │   │
    ┌──────────────────┘   │
    ↓                      │
┌──────────────────┐       │
│CoordinateConverter
├──────────────────┤       │
│ - wm             │───┐   │
│ + screen_to_rel()│   │   │
│ + rel_to_screen()│   │   │
└──────────────────┘   │   │
                       │   │
    ┌──────────────────┘   │
    ↓                      │
┌──────────────────┐       │
│ WindowManager    │◄──────┘
├──────────────────┤
│ - hwnd           │
│ - client_left    │
│ - client_top     │
│ + find_window()  │
│ + get_info()     │
│ + is_valid()     │
└──────────────────┘
```

---

## Sequence Diagrams

### Sequence 1: Find Window & Capture & Click

```
User
  ├─1. Enter "Notepad" ──→ GUI
  │
  └─2. Click Find ──→ GUI
         │
         └─→ WindowManager.find_window("Notepad")
            │
            └─→ win32gui ──→ hwnd found
               │
               └─→ get position, size
                  │
                  └─→ ✅ Display in UI

  ├─3. Click Capture ──→ GUI
  │                     │
  │                     └─→ Instruction: "Press ENTER to capture"
  │
  └─4. Position mouse & press ENTER
         │
         └─→ GUI
            │
            └─→ CoordinateConverter
               │
               ├─→ screen_x, screen_y from pyautogui
               │
               └─→ rel_x = screen_x - client_left
                  rel_y = screen_y - client_top
                  │
                  └─→ ✅ Display coordinates

  ├─5. Click "Test Click" ──→ GUI
  │
  └─→ ClickController
     │
     ├─→ WindowManager.is_valid() ✅
     │
     ├─→ CoordinateConverter.relative_to_screen()
     │   screen_x = client_left + rel_x
     │   screen_y = client_top + rel_y
     │
     ├─→ Save mouse position
     │
     ├─→ pyautogui.moveTo(screen_x, screen_y)
     │
     ├─→ pyautogui.click()
     │
     ├─→ Restore mouse position
     │
     └─→ ✅ Click successful! (display in UI)
```

---

## Error Handling

### Error Handling Strategy

```
┌─ Operation Called
│
├─ Try:
│  ├─ Validate inputs
│  ├─ Execute operation
│  └─ Return success
│
└─ Except:
   ├─ Catch specific exceptions
   ├─ Log error with context
   ├─ Display user-friendly message
   └─ Return failure
```

### Common Errors & Handling

| Error | Cause | Handling |
|-------|-------|----------|
| Window not found | Title mismatch | Try partial title, show available windows |
| Window invalid | Closed/minimized | Re-find window, show message |
| Click out of bounds | Coordinates outside window | Validate before click |
| Permission denied | Admin required | Run as Administrator |
| Import error | pyautogui/pywin32 missing | Show install instructions |

---

## Performance Characteristics

### Operation Timings

| Operation | Time | Notes |
|-----------|------|-------|
| Find window | 10-50ms | Depends on window count |
| Get window info | ~1ms | Cached, updated on demand |
| Screen→Relative conversion | <1ms | Simple math |
| Click operation | 100-200ms | Includes mouse movement |
| Coordinate capture | <1ms | Just read mouse position |

### Memory Usage

| Component | Memory |
|-----------|--------|
| WindowManager | ~2KB |
| CoordinateConverter | ~1KB |
| ClickController | ~1KB |
| GUI (Tkinter) | ~30-50MB |
| Total process | ~50-80MB |

---

## Extension Points

### How to Extend

#### Add Hotkey Support
```python
# In ClickController
def add_hotkey(key, callback):
    keyboard.add_hotkey(key, callback)
```

#### Add Click Sequences
```python
# Create list of coordinates
clicks = [(100, 100), (200, 200), (300, 300)]

# Click each in sequence
for rel_x, rel_y in clicks:
    click_ctrl.click_at_relative(rel_x, rel_y)
    time.sleep(0.5)
```

#### Add Image Detection
```python
# Find image on screen
import pyautogui
pos = pyautogui.locateOnScreen('button.png')
if pos:
    rel_x, rel_y = cc.screen_to_relative(pos[0], pos[1])
```

#### Add Right-Click Support
```python
# Already supported!
click_ctrl.click_at_relative(x, y, button='right')
```

---

## Testing Recommendations

### Unit Tests
```python
def test_screen_to_relative():
    wm.client_left = 100
    wm.client_top = 50
    result = cc.screen_to_relative(150, 100)
    assert result == (50, 50)

def test_window_valid():
    wm.find_window("Notepad")
    assert wm.is_valid() == True
```

### Integration Tests
```python
def test_full_click_workflow():
    1. Find window
    2. Capture coordinates
    3. Click at coordinates
    4. Verify click succeeded
```

### Manual Tests
```
1. ✅ Find Notepad
2. ✅ Capture center position
3. ✅ Click at captured position
4. ✅ Move window, click again
5. ✅ Percentage coordinates work
```

---

## Design Patterns Used

### 1. **Separation of Concerns**
Each class has single responsibility:
- WindowManager → window operations
- CoordinateConverter → math/conversions
- ClickController → clicking logic
- GUI → user interface

### 2. **Dependency Injection**
Classes receive dependencies through __init__:
```python
def __init__(self, window_manager, converter):
    self.wm = window_manager
    self.cc = converter
```

### 3. **State Management**
Centralized window state in WindowManager:
- One source of truth for window position
- All coordinates relative to this state
- Caching for performance

### 4. **Error Handling**
Try-except with logging:
- Graceful degradation
- User feedback
- Detailed logging for debugging

### 5. **UI Feedback**
Real-time status indicators:
- Visual feedback for every operation
- Log output for debugging
- Clear success/failure messages

---

## Future Improvements

### Planned Features
- [ ] Macro recording/playback
- [ ] Hotkey support
- [ ] Image-based clicking
- [ ] Screenshot preview
- [ ] Coordinate history
- [ ] Cross-monitor support
- [ ] Advanced scheduling

### Performance Optimizations
- [ ] Cache window lookups
- [ ] Batch operations
- [ ] Async UI updates
- [ ] Memory profiling

### Code Quality
- [ ] Unit test suite
- [ ] Integration tests
- [ ] Type hints completion
- [ ] Documentation generation

---

**End of Architecture Documentation**
