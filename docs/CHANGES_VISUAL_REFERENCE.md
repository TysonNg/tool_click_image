# Visual Reference: Changes Made June 6, 2026

## 1️⃣ TASK 6: Loop Count Display

### Before (Old Behavior)
```
════════════════════════════════════════════════════════════
📋 KỊCH BẢN 1: Arena.json
════════════════════════════════════════════════════════════
  1. pokemon.png (lặp 3 lần) [delay 0.5s]
  2. ⌨️ Enter (nhấn 1 lần) [delay 0.5s]
  3. trainer.png (lặp 2 lần) [delay 0.5s]

════════════════════════════════════════════════════════════
📋 KỊCH BẢN 2: BossBattle.json
════════════════════════════════════════════════════════════
  1. boss_health.png (lặp 1 lần) [delay 0.5s] [⏳ CHỜ]
  2. 🔍 [DETECTION] attack_signal.png
  3. attack_button.png (lặp 5 lần) [delay 0.5s]
```

### After (New Behavior) ✨
```
════════════════════════════════════════════════════════════
📋 KỊCH BẢN 1: Arena.json [x3 lần]
════════════════════════════════════════════════════════════
  1. pokemon.png (lặp 3 lần) [delay 0.5s]
  2. ⌨️ Enter (nhấn 1 lần) [delay 0.5s]
  3. trainer.png (lặp 2 lần) [delay 0.5s]

════════════════════════════════════════════════════════════
📋 KỊCH BẢN 2: BossBattle.json [∞ vòng lặp]
════════════════════════════════════════════════════════════
  1. boss_health.png (lặp 1 lần) [delay 0.5s] [⏳ CHỜ]
  2. 🔍 [DETECTION] attack_signal.png
  3. attack_button.png (lặp 5 lần) [delay 0.5s]
```

**Key Changes:**
- `[x3 lần]` added for finite loops (showing how many times scenario will repeat)
- `[∞ vòng lặp]` added for infinite loops
- Single-loop scenarios show no indicator (no clutter)

---

## 2️⃣ TASK 7: Skip Gracefully When Image Not Found

### Scenario Setup Example
```
Template List:
1. pokemon.png          (wait: NO)  ← Will search, if not found → SKIP
2. trainer.png          (wait: NO)  ← Will search, if not found → SKIP
3. victory.png          (wait: YES) ← Will WAIT for this
4. next_screen.png      (wait: NO)  ← LAST STEP: if not found → FAIL
```

### Before (Old Behavior - Crashes)
```
✅ Best match for pokemon.png found at (1200, 560)
✅ Final click point: (1200, 560)

✅ Best match for trainer.png found at (800, 400)
✅ Final click point: (800, 400)

⏳ Chờ tìm victory.png... (1s) [best_score=0.50]
⏳ Chờ tìm victory.png... (2s) [best_score=0.50]
⏳ Chờ tìm victory.png... (3s) [best_score=0.50]
⏳ Chờ tìm victory.png... (4s) [best_score=0.50]
⏳ Chờ tìm victory.png... (5s) [best_score=0.50]
❌ Timeout: Không tìm được victory.png ← SCENARIO FAILS HERE
⚠️ Không tìm được next_screen.png
```

### After (New Behavior - Skips Gracefully) ✨
```
✅ Best match for pokemon.png found at (1200, 560)
✅ Final click point: (1200, 560)

✅ Best match for trainer.png found at (800, 400)
✅ Final click point: (800, 400)

⏳ Chờ tìm victory.png... (1s) [best_score=0.50]
⏳ Chờ tìm victory.png... (2s) [best_score=0.50]
⏳ Chờ tìm victory.png... (3s) [best_score=0.50]
⏳ Chờ tìm victory.png... (4s) [best_score=0.50]
⏳ Chờ tìm victory.png... (5s) [best_score=0.50]
❌ Timeout: Không tìm được victory.png ← WAITS because wait_until_found=True

⏭️ Bỏ qua (không chờ): next_screen.png ← NEW: Graceful skip instead of fail
✅ Scenario completed!
```

**Key Changes:**
- When `wait_until_found=False` AND not the last step → Skip with emoji ⏭️
- Scenario continues instead of failing
- Last step still fails scenario (behavior preserved)
- Respects user's "Không chờ" setting

---

## 3️⃣ Code Flow Comparison

### TASK 7 - Decision Tree

```
Image Match Search:
│
├─ Found? ✅ YES
│  └─ Execute Click (repeat times)
│
└─ NOT Found ❌
   │
   ├─ wait_until_found = True (CHỜ)
   │  └─ Retry until timeout (existing behavior)
   │
   └─ wait_until_found = False (KHÔNG CHỜ) ← NEW LOGIC
      │
      ├─ is_last_step = True
      │  └─ Scenario FAILS (fail on last step is important)
      │
      └─ is_last_step = False
         └─ ⏭️ SKIP GRACEFULLY (NEW! ✨)
            └─ Continue to next action
```

### Code Implementation

**Before:**
```python
elif not found:
    safe_print(f"❌ Không tìm được {tpl['path']}")
    if is_last_step:
        run_result = "failed"
        return run_result
```

**After:**
```python
elif not found:
    # If wait_until_found is False and it's not the last step, skip gracefully
    if not wait_until_found and not is_last_step:
        safe_print(f"⏭️ Bỏ qua (không chờ): {tpl['path']}")
    else:
        safe_print(f"❌ Không tìm được {tpl['path']}")
        if is_last_step:
            run_result = "failed"
            return run_result
```

---

## 📊 Summary Table

| Scenario | Before | After | Notes |
|----------|--------|-------|-------|
| Load scenario with 3 loops | Header: "KỊCH BẢN 1: file.json" | Header: "KỊCH BẢN 1: file.json [x3 lần]" | TASK 6 ✅ |
| Load scenario infinite loop | Header: "KỊCH BẢN 2: file.json" | Header: "KỊCH BẢN 2: file.json [∞ vòng lặp]" | TASK 6 ✅ |
| Image not found, no wait, not last step | ❌ Scenario fails | ⏭️ Skips and continues | TASK 7 ✅ |
| Image not found, with wait | ⏳ Waits then fails | ⏳ Waits then fails | Unchanged ✓ |
| Image not found, last step | ❌ Scenario fails | ❌ Scenario fails | Unchanged ✓ |

---

Generated: June 6, 2026
By: Kiro Development Agent
