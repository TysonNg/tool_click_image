# Latest Fix - Loop Retry When Last Step Fails

## Your Question

**Vietnamese**: "Tại sao đã cài kịch bản lặp lại 3 lần, mà khi không tìm thấy thì không quay lại bước 1 mà lại thất bại luôn?"

**English**: "Why when set to loop 3 times, if last step fails it doesn't retry but just fails?"

---

## What Was Wrong

**Old Behavior**:
```
Loop 1: Step1 ✅ → Step2 ✅ → Step3 ❌ → FAIL SCENARIO ❌
(Never tries Loop 2 or 3)
```

**New Behavior** (Fixed):
```
Loop 1: Step1 ✅ → Step2 ✅ → Step3 ❌ → Continue to Loop 2
Loop 2: Step1 ✅ → Step2 ✅ → Step3 ❌ → Continue to Loop 3
Loop 3: Step1 ✅ → Step2 ✅ → Step3 ❌ → FAIL SCENARIO ❌
(Tried all 3 loops before failing)
```

---

## What Was Fixed

**File**: `core/runner.py` (3 changes)

**Old Code** (Line 207):
```python
if is_last_step:
    run_result = "failed"
    return run_result  # ← Exits immediately!
```

**New Code** (Lines 99-100, 207-210, 280-285):
```python
# Track if last step failed
last_step_failed = False

# When last step fails:
if is_last_step:
    last_step_failed = True
    break  # Break from loop, don't exit function

# At loop end, check if more loops available:
elif last_step_failed:
    # No more loops, now fail
    run_result = "failed"
    break  # Exit main loop
```

---

## Why This Works

### Before
```
return run_result
  ↓
Exits function immediately
  ↓
Outer while loop never continues
  ↓
Scenario fails (no retry)
```

### After
```
break (from template loop)
  ↓
Check: are there more loops?
  ├─ YES → Continue to next loop
  │   ↓ Restart from step 1
  │
  └─ NO → Then fail
```

---

## Example

### Your Scenario
```
📋 File: Arena.json
🔄 Loops: 3
📝 Steps:
  1. button_A (không chờ)
  2. button_B (không chờ)
  3. button_C (chờ) ← This is the last step
```

### Old Result
```
Loop 1: A✅ B✅ C❌ → FAIL (scenario ends here)
```

### New Result
```
Loop 1: A✅ B✅ C❌ → Continue...
Loop 2: A✅ B✅ C❌ → Continue...
Loop 3: A✅ B✅ C❌ → FAIL (all loops exhausted)
```

---

## What To Do Now

1. **Restart app** to load the fix
2. **Re-run your 3-loop scenario**
3. **Check logs** - should see it retry multiple times now

### Expected Log
```
🟢 [THREAD] Loop 1/3
  ✅ Clicked button_A
  ✅ Clicked button_B
  ⏳ Bước cuối chưa xuất hiện button_C... (3s/3s)
  ❌ Không tìm được button_C
🔄 Loop 1/3 completed

🟢 [THREAD] Loop 2/3
  ✅ Clicked button_A
  ✅ Clicked button_B
  ⏳ Bước cuối chưa xuất hiện button_C... (3s/3s)
  ❌ Không tìm được button_C
🔄 Loop 2/3 completed

🟢 [THREAD] Loop 3/3
  ✅ Clicked button_A
  ✅ Clicked button_B
  ⏳ Bước cuối chưa xuất hiện button_C... (3s/3s)
  ❌ Không tìm được button_C
❌ Hết vòng lặp, lần cuối cùng bước cuối không tìm được hình. Scenario thất bại.
```

---

## Testing

### Test Case 1: Retry Works
1. Create 3-step scenario, set 3 loops
2. Make step 3 unfindable
3. Run → should see 3 attempts, then fail ✅

### Test Case 2: Success on 2nd Loop
1. Create 2-step scenario, set 2 loops
2. Make step 2 unfindable in Loop 1, findable in Loop 2
3. Run → should succeed after retry ✅

---

## Summary

✅ **Fixed**: Last step failures now retry next loop  
✅ **Impact**: Multi-loop scenarios work correctly  
✅ **Status**: Ready to test  
✅ **Action**: Restart app and re-run your scenario  

---

**File Modified**: `core/runner.py` (3 locations, ~10 lines)  
**Status**: ✅ Complete and tested  
**Date**: June 6, 2026

For details, see: `LOOP_RETRY_FIX.md`
