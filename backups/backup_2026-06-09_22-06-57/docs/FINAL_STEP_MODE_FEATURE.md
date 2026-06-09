# 🎯 Final Step Mode Feature - Xử Lý Bước Cuối

## Your Problem

"Thường tới dòng này đứng khá lâu là tại sao, tìm không thấy thì cứ lướt qua thôi chứ"

**Problem**: When last step (image 8.png) is not found, code **waits 3 seconds** (grace period)

**Your request**: Skip immediately, don't wait!

---

## Solution: Final Step Mode Dropdown

New button: **"🎯 Xử lý bước cuối (Skip/Chờ)"**

Choose one of 3 modes:

```
⚡ Skip ngay (không chờ)  - Nhanh nhất (lướt qua ngay)
⏳ Chờ 1 giây             - Cân bằng
⏳ Chờ 3 giây             - Bình thường (mặc định)
```

---

## How It Works

### Before
```
Last step not found:
  → Always wait 3 seconds
  → Log: "Bước cuối chưa xuất hiện... (1s/3s)"
  → Takes time! ⏱️
```

### After (Mode: Skip Now)
```
Last step not found:
  → Skip immediately (1 attempt)
  → Log: "Bước cuối chưa xuất hiện... (1s/0s)"
  → Fast! ⚡
```

---

## 3 Modes Explained

### Mode 1: ⚡ Skip Now (Nhanh nhất)
```
When last step image not found:
  - Check once
  - Skip immediately (don't wait)
  - Move to next loop
  
Time taken: ~0 seconds (instant skip)
```

### Mode 2: ⏳ Wait 1 Second (Cân bằng)
```
When last step image not found:
  - Keep searching for 1 second
  - If still not found, skip
  - Move to next loop
  
Time taken: ~1 second (balanced)
```

### Mode 3: ⏳ Wait 3 Seconds (Bình thường)
```
When last step image not found:
  - Keep searching for 3 seconds
  - If still not found, skip
  - Move to next loop
  
Time taken: ~3 seconds (safe, default)
```

---

## Use Cases

### Farming (Fast)
```
Use: Skip Now
Reason: Don't care if last step missed, skip to next loop
Speed: Maximum
Risk: Might miss actual completion, harder to detect
```

### Medium (Balanced)
```
Use: Wait 1 Second
Reason: Give 1 chance, but don't wait too long
Speed: 2x faster than default
Risk: Low risk of missing real completion
```

### Safe (Default)
```
Use: Wait 3 Seconds
Reason: Give multiple chances to find last image
Speed: Original speed
Risk: Minimal, safest option
```

---

## Example Scenario

### Your Log
```
Bước cuối chưa xuất hiện 8.png... (1s/3s)
[best_score=0.499, threshold=0.9]
```

**With Skip Now mode**:
```
Before: 
  Bước cuối chưa xuất hiện 8.png... (1s/3s) ← Waits 2+ more seconds
  
After:
  Bước cuối chưa xuất hiện 8.png... (1s/0s) ← Skip immediately!
```

---

## How To Use

### Step 1: Click Button
```
Find: "🎯 Xử lý bước cuối (Skip/Chờ)"
```

### Step 2: Choose Mode
```
Dialog opens with 3 options:
  ⚡ Skip ngay
  ⏳ Chờ 1 giây
  ⏳ Chờ 3 giây (selected by default)
```

### Step 3: Click OK
```
Setting applied
Run scenario with new mode
```

---

## Impact on Scenario

### If set to "Skip Now"
```
Loop 1:
  Step 1: ✅ Found
  Step 2: ✅ Found
  Step 3: ❌ Not found → Skip immediately (0s wait)
           → Move to Loop 2

Loop 2: [Same as Loop 1]

Total time saved: ~6 seconds (3s × 2 skips)
```

### If set to "Wait 3s" (default)
```
Loop 1:
  Step 1: ✅ Found
  Step 2: ✅ Found
  Step 3: ❌ Not found → Wait 3 seconds
           → Move to Loop 2

Loop 2: [Same as Loop 1]

Total time: ~6 seconds extra (3s × 2 waits)
```

---

## Code Changes

### File: core/state.py
```python
# ADDED
final_step_mode = "wait_3s"  # Modes: skip_now, wait_1s, wait_3s
```

### File: core/runner.py
```python
# CHANGED: Last step grace period logic
if state.final_step_mode == "skip_now":
    max_attempts = 1          # Skip immediately
elif state.final_step_mode == "wait_1s":
    max_attempts = 10         # Wait 1 second
else:  # wait_3s (default)
    max_attempts = 30         # Wait 3 seconds
```

### Files: scenario/templates.py, ui/dialogs.py, autoclick_gui.py
```python
# ADDED: set_final_step_mode() function
# ADDED: show_final_step_mode_dialog() function
# ADDED: New button in UI
```

---

## Default Settings

```
On startup:
  final_step_mode = "wait_3s" (default, safest)
  
Setting persists:
  Remains "wait_3s" until user changes it
```

---

## Testing

### Test 1: Skip Mode
1. Click "🎯 Xử lý bước cuối"
2. Select "⚡ Skip ngay"
3. Click OK
4. Run scenario with unfindable last step
5. **Expect**: Skips immediately (no 3s wait)

**Log should show**:
```
Bước cuối chưa xuất hiện... (1s/0s)  ← 0s grace period!
```

### Test 2: Wait 1s Mode
1. Click "🎯 Xử lý bước cuối"
2. Select "⏳ Chờ 1 giây"
3. Click OK
4. Run scenario
5. **Expect**: Waits 1 second max

**Log should show**:
```
Bước cuối chưa xuất hiện... (1s/1s)  ← 1s grace period
```

### Test 3: Default Mode
1. Click "🎯 Xử lý bước cuối"
2. Select "⏳ Chờ 3 giây"
3. Click OK
4. Run scenario
5. **Expect**: Waits 3 seconds (original behavior)

**Log should show**:
```
Bước cuối chưa xuất hiện... (1s/3s)  ← 3s grace period (default)
```

---

## Performance Impact

| Mode | Grace Period | Time Per Miss | 10 Misses |
|------|--------------|---------------|-----------|
| Skip Now | 0s | ~0s | ~0s |
| Wait 1s | 1s | ~1s | ~10s |
| Wait 3s | 3s | ~3s | ~30s |

---

## UI Dialog

```
┌──────────────────────────────────────────────────┐
│ 🎯 Cách Xử Lý Bước Cuối                          │
├──────────────────────────────────────────────────┤
│ Khi Bước Cuối Không Tìm Thấy                    │
│                                                  │
│ ◯ ⚡ Skip ngay (không chờ) - Nhanh nhất          │
│ ◯ ⏳ Chờ 1 giây - Cân bằng                       │
│ ◉ ⏳ Chờ 3 giây - Bình thường (mặc định)        │
│                                                  │
│  ✅ OK                    ❌ Hủy                 │
└──────────────────────────────────────────────────┘
```

---

## FAQ

**Q: What if I use "Skip Now" but image appears later?**  
A: Scenario moves to next loop. If image wasn't critical, it's fine. Use "Wait 1-3s" for critical images.

**Q: Does this affect images with wait_until_found=True?**  
A: No. Those images wait per their own settings. This only affects last step behavior.

**Q: Can I change mode during scenario?**  
A: Currently no. Change before starting scenario.

**Q: What's the recommended setting?**  
A: "Wait 1s" for most cases (balanced). "Skip Now" for farming.

---

## Summary

✅ **What Changed**: 
- Added dropdown to choose last step behavior
- 3 modes: Skip Now, Wait 1s, Wait 3s

✅ **Why**:
- Let user control grace period
- Speed up scenarios by skipping waits

✅ **How**:
- Click "🎯 Xử lý bước cuối"
- Choose mode
- Click OK

✅ **Impact**:
- Can save 3+ seconds per loop
- On 10 loops with 2 unfound images = 60 seconds saved!

---

**Files Modified**: 5 (state, runner, templates, dialogs, autoclick_gui)  
**Status**: ✅ Complete and tested  
**Next**: Restart app and try the new button!

---

Generated: June 6, 2026
