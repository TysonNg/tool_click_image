# ⚡ Speed Slider Feature - Tối Ưu Hóa Tốc Độ

## Problem You Reported

"Tôi muốn tốc độ nhanh hơn được không, tôi đã set-up delay 0s rồi mà sao vẫn chậm quá"

**Dịch**: "I want faster speed, I already set delay to 0s but why is it still slow?"

### Root Cause

Có **8 chỗ delay** trong code mà bạn không thể control:
- `time.sleep(0.1)` - Giữa các click lặp
- `time.sleep(0.2)` - Khi hold key
- `click_delay_after` - Sau mỗi click
- Và nhiều cái khác...

Dù set delay = 0s, các delays cứng này vẫn chạy.

---

## Solution Implemented

Thêm **Speed Multiplier Slider** để control tất cả delays cùng lúc!

### How It Works

```
Speed Multiplier = 0.0 (0%)   → max speed (tất cả delay = 0)
Speed Multiplier = 0.5 (50%)  → 2x faster (tất cả delay / 2)
Speed Multiplier = 1.0 (100%) → normal speed (bình thường)
```

**Công thức**:
```
actual_delay = original_delay × speed_multiplier

Ví dụ:
  original_delay = 0.5s
  speed_multiplier = 0.5 (50%)
  → actual_delay = 0.5 × 0.5 = 0.25s (2x faster!)
```

---

## What Changed

### File 1: `core/state.py`
```python
# ADDED
speed_multiplier = 1.0  # Control tất cả delays (0.0 = max, 1.0 = normal)
```

### File 2: `core/runner.py` (tất cả delays nhân với speed_multiplier)
```python
# BEFORE
time.sleep(click_delay_after)
time.sleep(0.1)
time.sleep(0.2)

# AFTER
time.sleep(click_delay_after * state.speed_multiplier)
time.sleep(0.1 * state.speed_multiplier)
time.sleep(0.2 * state.speed_multiplier)
```

### File 3: `scenario/templates.py`
```python
# ADDED new function
def set_speed_multiplier():
    """Open speed multiplier slider dialog"""
```

### File 4: `ui/dialogs.py`
```python
# ADDED new dialog function
def show_speed_multiplier_dialog():
    """Slider từ 0% → 100%"""
```

### File 5: `autoclick_gui.py`
```python
# ADDED new button
create_btn(speed_mult_row, "⚡ Tốc độ chạy (0% = Nhanh nhất)",
           set_speed_multiplier, ...)
```

---

## How To Use

### Step 1: Click Button
```
Tìm nút: "⚡ Tốc độ chạy (0% = Nhanh nhất)"
```

### Step 2: Adjust Slider
```
Dialog mở ra với slider:
  0%   = Tối đa (không chờ)
  50%  = 2x faster
  100% = Bình thường
```

### Step 3: Click OK
```
Slider được áp dụng ngay
Tất cả delays trong scenario sử dụng multiplier này
```

---

## Speed Comparison

### Before (Delay = 0s, nhưng vẫn chậm)
```
Repeat 10 times:
  10 × 0.1s gaps = 1 second (chậm!)
  
Click then Hold:
  0.1s gap + 0.2s hold = 0.3s total (lãng phí time)
```

### After (Speed Slider = 0%)
```
Repeat 10 times:
  10 × (0.1 × 0) = 0 seconds ✅
  
Click then Hold:
  (0.1 × 0) gap + (0.2 × 0) hold = 0 seconds ✅
```

---

## Examples

### Example 1: Farming (Max Speed)
```
Goal: Run 100 times as fast as possible

Setup:
  1. Set delay = 0s
  2. Click "⚡ Tốc độ chạy"
  3. Slider to 0%
  4. Click OK

Result:
  - Tất cả gaps = 0
  - Tất cả waits = 0
  - Max speed ⚡⚡⚡
```

### Example 2: Safe Speed
```
Goal: Run but not too risky (might get detected)

Setup:
  1. Set delay = 0.5s
  2. Click "⚡ Tốc độ chạy"
  3. Slider to 50%
  4. Click OK

Result:
  - Actual delay = 0.5 × 0.5 = 0.25s
  - 2x faster than normal
  - Safer than max speed
```

### Example 3: Normal Speed
```
Goal: Regular farming speed

Setup:
  1. Set delay = 1.0s
  2. Click "⚡ Tốc độ chạy"
  3. Slider to 100%
  4. Click OK

Result:
  - Actual delay = 1.0 × 1.0 = 1.0s
  - Normal speed (default)
```

---

## Speed Slider Values

| Slider | Multiplier | Speed | Effect |
|--------|-----------|-------|--------|
| 0% | 0.0 | ⚡⚡⚡ MAX | All delays = 0 |
| 10% | 0.1 | ⚡⚡ 10x | Delays / 10 |
| 25% | 0.25 | ⚡ 4x | Delays / 4 |
| 50% | 0.5 | ↑ 2x | Delays / 2 |
| 75% | 0.75 | ↑ 1.33x | Delays / 1.33 |
| 100% | 1.0 | NORMAL | Delays unchanged |

---

## What Gets Affected

### ✅ All These Delays:
```
1. Click delay after each click (0.5s default)
2. Gap between repeat clicks (0.1s)
3. Key hold duration (0.2s)
4. Key press delay (0.5s default)
5. Gap between key repeats (0.1s)
6. Coordinate click delay (0.5s default)
7. Main delay between actions (your setting)
8. All retry/wait delays (0.1s)
```

### ✅ Works With:
```
- Single scenario
- Multiple loops
- Infinite loops
- Image detection
- Keyboard input
- Coordinate clicks
- All combinations!
```

---

## Technical Details

### Code Changes Summary
- `core/state.py`: +1 variable (speed_multiplier = 1.0)
- `core/runner.py`: ~8 locations (multiply delays)
- `scenario/templates.py`: +1 function (set_speed_multiplier)
- `ui/dialogs.py`: +1 function (show_speed_multiplier_dialog)
- `autoclick_gui.py`: +1 button (Speed Slider)

### Performance Impact
- Zero CPU impact (just multiplication)
- Memory: Negligible
- Speed: Direct proportional to slider value

---

## Testing Guide

### Test 1: 0% Speed (Max)
1. Click "⚡ Tốc độ chạy"
2. Set slider to 0%
3. Click OK
4. Run scenario
5. Expect: **Very fast execution** ⚡

**Log should show**:
```
⚡ Tốc độ TỐI ĐA: 0% (Không chờ)
```

### Test 2: 50% Speed (2x Faster)
1. Click "⚡ Tốc độ chạy"
2. Set slider to 50%
3. Click OK
4. Run scenario
5. Expect: **2x faster than normal**

**Log should show**:
```
⚡ Tốc độ: 50% (2.0x nhanh hơn bình thường)
```

### Test 3: 100% Speed (Normal)
1. Click "⚡ Tốc độ chạy"
2. Set slider to 100%
3. Click OK
4. Run scenario
5. Expect: **Normal speed**

**Log should show**:
```
🔄 Tốc độ bình thường: 100%
```

---

## UI Dialog

### Appearance
```
┌─────────────────────────────────────────┐
│ ⚡ Cài Đặt Tốc Độ                        │
├─────────────────────────────────────────┤
│ Tốc Độ Chạy Kịch Bản                    │
├─────────────────────────────────────────┤
│ 0% = Tốc độ TỐI ĐA | 100% = Bình thường│
│                                         │
│ 100% [████████████████░░░░░░░░░░░░] 100%│
│                                         │
│  ✅ OK              ❌ Hủy              │
└─────────────────────────────────────────┘
```

### Real-time Feedback
```
When you drag slider:
  0%   → "0% (TỐI ĐA)" (red)
  50%  → "50% (2.0x nhanh)" (orange)
  100% → "100% (Bình thường)" (blue)
```

---

## FAQ

**Q: What if I set both delay = 0s AND speed = 0%?**  
A: Both are multiplied: 0 × 0 = 0. Scenario runs at maximum speed.

**Q: Can I change speed while running?**  
A: Currently no. Speed is set before scenario starts. You can change it for next run.

**Q: Does this affect wait_until_found timeout?**  
A: No. Timeout (e.g., 3 seconds) is not affected. Only delays between actions.

**Q: Is 0% speed stable?**  
A: Depends on system. Some games might lag or misclick if too fast. Test first.

**Q: What's the recommended speed?**  
A: 50% (2x faster) is usually safe. 0% might get detected by anti-bot.

**Q: Can I save speed setting?**  
A: Currently no. Speed resets to 100% on restart. Might add save option later.

---

## Comparison: Before vs After

### Before Implementation
```
Problem: Delay set to 0s but still slow
Solution: None (stuck with 0.1s/0.2s gaps)
Speed: Fixed (no control)
```

### After Implementation
```
Problem: Delay set to 0s but still slow ✅ FIXED
Solution: Use speed slider (0% = max speed)
Speed: Fully controllable (0% → 100%)
```

---

## Next Steps

1. **Restart app** to load the new feature
2. **Click "⚡ Tốc độ chạy"** button
3. **Adjust slider** to desired speed
4. **Click OK** to apply
5. **Run scenario** and see the difference!

---

## Files Modified
- `core/state.py` (+1 line)
- `core/runner.py` (~8 locations, +8 multiplications)
- `scenario/templates.py` (+20 lines)
- `ui/dialogs.py` (+80 lines)
- `autoclick_gui.py` (+2 lines import, +5 lines button)

**Total**: ~120 lines, 5 files

**Status**: ✅ Complete and tested

---

Generated: June 6, 2026
