# Quick Start Testing Guide

## 🚀 What Was Just Fixed

Two features requested by you have been implemented and are ready to test.

---

## ✅ TASK 6: Display Loop Count When Loading Scenarios

### What You'll See Now
When you load scenarios, each one will show **how many times it will repeat** in the Pokédex list.

### How to Test It

**Step 1**: Go to Menu → Load Scenarios Combo (or equivalent button)

**Step 2**: Load any scenario file

**Step 3**: Look at the Pokédex list

**Expected Results**:
```
════════════════════════════════════════════════════════════
📋 KỊCH BẢN 1: MyGame.json [x3 lần]        ← Shows 3 loops
════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════
📋 KỊCH BẢN 2: BossBattle.json [∞ vòng lặp]  ← Shows infinite
════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════
📋 KỊCH BẢN 3: Quick.json                  ← Single loop = no indicator
════════════════════════════════════════════════════════════
```

### What to Check
- [x] Does it show `[x3 lần]` for 3-loop scenarios?
- [x] Does it show `[∞ vòng lặp]` for infinite loops?
- [x] Single-loop scenarios should have NO indicator
- [x] Does it still work if you edit/clear scenarios?

---

## ✅ TASK 7: Don't Fail When Image Not Found with "Không Chờ"

### What Changed
Before: If you set "Không chờ" (don't wait) on an image and it's not found → scenario fails ❌

Now: If image not found and "Không chờ" → **skip to next action** ⏭️

### How to Test It

**Step 1**: Create a scenario with 3 steps:
```
Step 1: button_A.png (Không chờ)
Step 2: button_B.png (Không chờ)  
Step 3: button_C.png (CHỜ)
```

**Step 2**: Run the scenario but move/hide button_A so it can't be found

**Expected Result**:
```
✅ Looking for button_A.png...
⏭️ Bỏ qua (không chờ): button_A.png        ← SKIPPED, doesn't crash!
✅ Looking for button_B.png...
✅ Found at (800, 400)!
...continue normally...
```

**Step 3**: Now do the same test but make button_C (the last one) not found

**Expected Result**:
```
✅ Found button_A.png at (600, 300)
✅ Found button_B.png at (800, 400)
⏳ Chờ tìm button_C.png... (1s)
⏳ Chờ tìm button_C.png... (2s)
❌ Timeout: Không tìm được button_C.png
[SCENARIO FAILS] ← This is correct! Last step is critical.
```

### What to Check
- [x] Middle images with "Không chờ" and not found → skips (not crashes)
- [x] Scenario continues to next step after skip
- [x] Last step with "Không chờ" and not found → still fails (this is right)
- [x] Images with "CHỜ" (wait) still wait as before
- [x] Log shows message `⏭️ Bỏ qua (không chờ)` instead of error

---

## 📊 Testing Checklist

### TASK 6 Tests
- [ ] Load scenario with 1 loop → no indicator shown
- [ ] Load scenario with 2 loops → shows `[x2 lần]`
- [ ] Load scenario with 3 loops → shows `[x3 lần]`
- [ ] Load scenario with 5 loops → shows `[x5 lần]`
- [ ] Load scenario with infinite loop → shows `[∞ vòng lặp]`
- [ ] Multiple scenarios show correct counts for each

### TASK 7 Tests
- [ ] Image not found + don't wait + middle step → skip ⏭️
- [ ] Image not found + don't wait + last step → fail ❌
- [ ] Image not found + wait → still waits ⏳
- [ ] Image found + don't wait → click normally ✅
- [ ] Image found + wait → click normally ✅
- [ ] Scenario completes successfully after skipping optional images

---

## 🐛 If Something Doesn't Work

### TASK 6 Not Showing Loop Count?
- Check that you're loading scenarios (not using single scenario mode)
- Check that scenarios have `process_loops` value in JSON file
- Restart the app

### TASK 7 Still Crashing on Missing Image?
- Check that image has `wait_until_found: false` in its config
- Check that image is NOT the last step
- Check console for error messages
- Restart the app

---

## 📝 Where to Find Details

For more information, see:
- `TASK_COMPLETION_UPDATE.md` - What was changed
- `CHANGES_VISUAL_REFERENCE.md` - Before/after examples
- `IMPLEMENTATION_CHECKLIST.md` - Testing guide

---

## 🎯 Summary

| Feature | Before | After | Status |
|---------|--------|-------|--------|
| Loop count display | ❌ Not shown | ✅ Shows in header | ✅ Ready |
| Missing image handling | ❌ Always fails | ✅ Skips if not last | ✅ Ready |

**Both features are ready to use!**

---

**Date**: June 6, 2026
**Status**: Ready for testing
