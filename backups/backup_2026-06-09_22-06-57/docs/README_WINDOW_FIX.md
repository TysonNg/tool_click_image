# Window Handle Invalid - Fixed! ✅

## 🎯 Problem

```
Window handle 1051690 is no longer valid, clearing...
🖱️ Double-clicked coordinate (512,451)
Script stops running unexpectedly
```

**Root Cause:** Game window became invalid (closed, minimized, hidden, lost focus)

---

## ✅ Solution Implemented

A new **WindowGuard** system automatically:

1. ✅ **Validates** window before script starts
2. ✅ **Restores** window if minimized/hidden
3. ✅ **Protects** window during execution
4. ✅ **Warns** user if issues detected
5. ✅ **Stops safely** if window is lost

---

## 🚀 Quick Start

### Step 1: Set Target Window
```
Click: "🎯 Xác Định Cửa Sổ Đích" (Set Target Window)
Enter: Game window name (e.g., "MapleStory")
Result: ✅ Window validated and protected
```

### Step 2: Add Actions
```
Click: Add images, coordinates, or keyboard keys
Ensure: Window remains visible (not minimized)
```

### Step 3: Run Script
```
Click: "⚡ TUNG POKÉBALL!" (Start)
System automatically:
  ✅ Validates window is still valid
  ✅ Restores if minimized
  ✅ Keeps window in foreground
  ✅ Monitors throughout execution
```

---

## 🛡️ New Features

### Pre-flight Checks (Before Running)
```
❌ No window set          → Warning + guidance
⚠️ Window minimized       → Ask to restore or select new
⚠️ Window hidden          → Ask to restore or select new
⚠️ Window closed          → Stop + error message
✅ Window valid           → Proceed
```

### Continuous Protection (During Execution)
```
Every template action:
  1. Check if window still valid
  2. Restore if minimized
  3. Bring to foreground
  4. Execute action
  5. Repeat
```

### Safety Stops (On Errors)
```
If window becomes invalid:
  ✅ Stop script immediately
  ✅ Release all resources
  ✅ Show clear error message
  ✅ Allow user to resume
```

---

## 📊 Before vs After

| Feature | Before | After |
|---------|--------|-------|
| Window validation | ❌ Start only | ✅ Before + During |
| Auto-restore from minimize | ❌ No | ✅ Yes |
| Foreground protection | ❌ No | ✅ Yes |
| Smart warnings | ❌ Simple | ✅ Detailed with options |
| Safety stops | ⚠️ Basic | ✅ Advanced |
| Debugging info | ❌ Limited | ✅ Detailed logs |

---

## 🔧 Files Modified/Created

### New Files:
- ✅ `core/window_guard.py` - WindowGuard module
- ✅ `TEST_WINDOW_GUARD.py` - Unit tests
- ✅ `docs/WINDOW_HANDLE_FIX.md` - Detailed guide (Vietnamese)
- ✅ `docs/QUICK_START_FIXED.md` - Quick start (Vietnamese)
- ✅ `docs/README_WINDOW_FIX.md` - This file

### Modified Files:
- ✅ `core/runner.py` - Pre-flight checks + monitoring
- ✅ `core/relative_capture.py` - Bug fixes

---

## 🆘 Troubleshooting

### Script won't run?

```
1. Check: Is game window visible (not minimized)?
2. Check: Status bar shows ✅ target window set?
3. Try: Click "🎯 Xác Định Cửa Sổ Đích" again
4. Try: Restart application
5. Run: python TEST_WINDOW_GUARD.py to test system
```

### Window keeps minimizing?

```
1. Close unnecessary applications
2. Keep game window in safe location (visible)
3. Don't Alt-Tab while script runs
4. Don't click minimize button
```

### Coordinates are wrong?

```
1. Resize window back to original size
2. Use "📍 Lấy Tọa Độ Tương Đối" (Relative coordinates)
3. Re-capture coordinates after resizing
4. Try with larger threshold value
```

---

## 📝 Log Examples

### ✅ Success:
```
✅ Window validated and protected successfully
🔧 [WINDOW_GUARD] Window is healthy
✅ Best match found, clicking...
🖱️ Clicked at: (512, 451)
```

### ⚠️ Warnings:
```
⚠️ Target window is minimized
  [Auto-restoring...]
🔧 [WINDOW_GUARD] Restoring minimized window...
✅ Proceeding with execution
```

### ❌ Errors:
```
❌ FATAL: Window handle became invalid during execution!
   The game window was closed or lost focus
❌ Please set target window again
```

---

## 🧪 Verify System Works

Run test suite:
```bash
python TEST_WINDOW_GUARD.py
```

Expected output:
```
🧪 WINDOW GUARD TEST
==================

📝 Test 1: Check when no window set
  validate_window() when no window: False
  ✅ PASS

📝 Test 2: Get foreground window
  ✅ PASS

📝 Test 3: Validate window
  ✅ PASS

[... more tests ...]

✅ ALL TESTS PASSED!
Window Guard is working correctly for:
  • Window: [Your Window Name]
  • HWND: [Handle Number]

You can now safely use WindowGuard in your scripts! 🎉
```

---

## 🎓 Understanding WindowGuard

### What It Does:

```python
class WindowGuard:
    
    # 1. VALIDATION
    validate_window()
    # Returns: True if handle is valid, False otherwise
    
    # 2. RESTORATION
    restore_window_safe()
    # Restores from minimize/hidden states
    
    # 3. FOCUS MANAGEMENT
    bring_to_foreground_safe()
    # Brings window to front without aggressive steal
    
    # 4. FULL PROTECTION
    protect_window()
    # Does: validate + restore + bring to foreground
    # Returns: True if all operations successful
    
    # 5. STATUS CHECK
    check_and_warn()
    # Returns: Warning message if issues, None if all good
```

### How It's Used:

```python
# BEFORE STARTING
if not WindowGuard.protect_window():
    print("❌ Cannot protect window - stopping")
    return "failed"

# DURING EXECUTION
for action in actions:
    if not WindowGuard.validate_window():
        print("❌ Window lost - stopping safely")
        break
    WindowGuard.protect_window()  # Keep protecting
    execute_action()
```

---

## 💡 Best Practices

### ✅ DO:
- ✅ Keep game window visible
- ✅ Don't minimize during script execution
- ✅ Don't Alt-Tab away
- ✅ Keep game in foreground
- ✅ Re-set target window if game restarts
- ✅ Check status bar shows ✅ before running

### ❌ DON'T:
- ❌ Minimize game window while script runs
- ❌ Alt-Tab to other applications
- ❌ Close game window during execution
- ❌ Resize window dramatically
- ❌ Click other windows
- ❌ Run multiple game instances with same handle

---

## 📖 Documentation

### Full Guides (Vietnamese):
- `WINDOW_HANDLE_FIX.md` - Complete explanation
- `QUICK_START_FIXED.md` - Step-by-step tutorial
- `IMPROVEMENTS_SUMMARY.md` - Technical summary

### Quick Reference:
- `AUTOCLICK_CHEATSHEET.md` - All features at a glance

### API Reference:
- See inline comments in `core/window_guard.py`

---

## 🚀 Next Steps

1. **Read:** `QUICK_START_FIXED.md` for Vietnamese guide
2. **Test:** Run `python TEST_WINDOW_GUARD.py`
3. **Try:** Follow 5-step quick start process
4. **Enjoy:** More stable script execution! ✨

---

## 📞 Support

If issues persist:
1. Check logs for error messages
2. Run `TEST_WINDOW_GUARD.py`
3. Verify game window state (not minimized/hidden)
4. Try setting target window again
5. Restart application

---

## ✨ Summary

The WindowGuard system ensures your scripts run reliably by:
- ✅ Protecting game window integrity
- ✅ Auto-recovering from common issues
- ✅ Providing smart user guidance
- ✅ Stopping safely when needed
- ✅ Offering detailed diagnostics

**Result: Scripts that just work!** 🎉

---

**Happy clicking!** 🖱️✨
