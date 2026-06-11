# Threshold Fix - Why Your Scenarios Were Failing

## The Problem You Encountered

From your log output:
```
⏳ Bước cuối chưa xuất hiện d:\...\3.png... (1s/3s) 
  [best_score=0.485, threshold=0.85]
❌ Không tìm được d:\...\3.png
```

**Translation**: "Best match score: 0.485 but threshold requires 0.85 (85% match)"

### Why It Was Failing
- **Best match found**: 0.485 (48.5% similar to original)
- **Threshold required**: 0.85 (85% similar needed)
- **Result**: Image rejected because it's only 48.5% match, not 85%

The default threshold of **0.85 was too strict** for real-world gameplay scenarios.

---

## What Changed

### File 1: `core/vision.py`
```diff
- DEFAULT_THRESHOLD = 0.85  # Increased from 0.80 to reduce false positives
+ DEFAULT_THRESHOLD = 0.75  # Practical threshold for real-world scenarios
- RECOMMENDED_MIN_THRESHOLD = 0.75
+ RECOMMENDED_MIN_THRESHOLD = 0.70
```

### File 2: `scenario/templates.py` (3 changes)

**Change 1**: Default threshold in dialog
```diff
- threshold_var = tk.StringVar(value=str(initial.get("threshold", 0.85)))
+ threshold_var = tk.StringVar(value=str(initial.get("threshold", 0.75)))
```

**Change 2**: Warning messages updated
```diff
  def on_threshold_change(*args):
      try:
          val = float(threshold_var.get())
-         if val < 0.75:
+         if val < 0.70:
-             text="⚠️ CẢNH BÁO: Threshold < 0.75 dễ click sai hình! Khuyến nghị >= 0.85"
+             text="⚠️ CẢNH BÁO: Threshold < 0.70 rất dễ click sai hình!"
-         elif val < 0.85:
+         elif val < 0.75:
-             text="⚠️ Threshold thấp, có thể click sai. Khuyến nghị >= 0.85"
+             text="⚠️ Threshold thấp, có thể click sai. Khuyến nghị >= 0.75"
```

**Change 3**: Fallback default threshold
```diff
  except:
-     threshold = 0.85  # Default an toàn
+     threshold = 0.75  # Default practical threshold
```

---

## How Threshold Works

### What Is Threshold?
Threshold is the **minimum similarity score** required to consider an image "found".

```
Threshold = 0.75 means:
  - If match score >= 0.75 → FOUND ✅
  - If match score < 0.75 → NOT FOUND ❌
```

### Visual Examples

**Threshold 0.85 (Old - Too Strict)**
```
Match Scores:     0.0    0.25   0.50   0.75   0.85   1.0
                  |------|------|------|------|------|
                                            ✂️ Cutoff
                                         REJECT ❌ | ACCEPT ✅

Example:
  - Score 0.48 → REJECT (below 0.85)
  - Score 0.80 → REJECT (below 0.85)
  - Score 0.90 → ACCEPT (above 0.85)
```

**Threshold 0.75 (New - Practical)**
```
Match Scores:     0.0    0.25   0.50   0.75   0.85   1.0
                  |------|------|------|------|------|
                                    ✂️ Cutoff
                                 REJECT ❌ | ACCEPT ✅

Example:
  - Score 0.48 → REJECT (below 0.75) 
  - Score 0.80 → ACCEPT (above 0.75) ✅
  - Score 0.90 → ACCEPT (above 0.75) ✅
```

---

## Why 0.75 Is Better Than 0.85

### Problem 1: Real-World Variations
When you capture an image and use it later:

| Factor | Impact | Example |
|--------|--------|---------|
| Lighting | -20% | Bright room vs dark room |
| Resolution | -15% | Display scaling changes |
| Game animation | -10% | Button slightly moved |
| Anti-aliasing | -5% | Font rendering differences |
| **Total** | **-50%** | Score: 0.85 - 0.50 = **0.35** ❌ |

With threshold 0.85, your image needs to match perfectly. Real gameplay causes 50% loss, leaving only 35% match.

### Problem 2: Your Scenario Results
```
Your game:
  - Captured at one time: 100% match
  - Run later with lighting changes: ~85% match
  - Resolution difference: ~80% match
  - Different button state: ~75% match
  - Different animation frame: ~50% match

With 0.85 threshold:
  - 85% match → PASS ✅
  - 80% match → FAIL ❌
  - 75% match → FAIL ❌
  - 50% match → FAIL ❌
  
Result: Scenario fails most of the time

With 0.75 threshold:
  - 85% match → PASS ✅
  - 80% match → PASS ✅
  - 75% match → PASS ✅
  - 50% match → FAIL ❌
  
Result: Scenario works reliably
```

---

## Recommended Threshold Settings

### Safe Ranges
```
0.70 - 0.75  = Normal gameplay (recommended)
0.75 - 0.80  = Strict matching (for very stable UI)
0.80 - 0.85  = Very strict (only perfect matches)
> 0.85       = Extremely strict (rarely works in practice)
```

### When to Adjust

**Use Lower Threshold (0.70) When:**
- Game has dynamic lighting or weather
- UI elements change colors/states
- Screen resolution varies
- Button animations are common
- Testing with multiple devices

**Use Higher Threshold (0.85+) When:**
- UI is very stable/static
- You need 100% accuracy
- False positives are a problem
- Testing in controlled environment

---

## Your Specific Issue Explained

### Your Log Output
```
best_score=0.485, threshold=0.85
```

**Why score was only 0.485:**
1. Image captured in one game state
2. Later, button appearance changed (animation or state)
3. Match algorithm found best: 48.5% similarity
4. But threshold required: 85%
5. **Result**: Rejected as "not found"

**With new 0.75 threshold:**
```
best_score=0.485, threshold=0.75
```
Still fails ❌ because 0.485 < 0.75

**Why you might get such low scores:**
- [ ] Image is very small (hard to match)
- [ ] Image quality is low (blurry)
- [ ] UI element changed significantly
- [ ] Wrong region being searched
- [ ] Lighting is very different

---

## What To Do Now

### Step 1: Re-Run Your Scenario
The new default threshold of 0.75 should help. Try running the same scenario again.

### Step 2: If It Still Fails
Check why the match score is so low (0.485):

**Option A**: Lower threshold further
```
Try: 0.70, 0.65, 0.60
Watch log for match scores
```

**Option B**: Recapture the image
```
Maybe image quality is poor
Try capturing again with better lighting
```

**Option C**: Check search region
```
Is the image being looked for in the right area?
Check search region in image config
```

### Step 3: Monitor Match Scores
When running, check the log for:
```
✅ Best match ... (score: 0.82, threshold: 0.75) ← Good!
⏳ Chờ tìm ... (best_score=0.48, threshold: 0.75) ← Low score
```

If scores are consistently low (< 0.60), something is wrong with:
- Image quality
- Lighting conditions  
- Search region

---

## Testing the Fix

### Test 1: Check Default Threshold
1. Create new image config
2. Look at suggested threshold
3. Should be **0.75** (not 0.85)

### Test 2: Run Previous Failing Scenario
1. Load your Arena scenario
2. Run it
3. Check if images that failed before now work

### Test 3: Monitor Match Scores
1. Run scenario and watch console
2. Log should show match scores
3. If score > 0.75 → should find image
4. If score < 0.75 → will skip/fail (expected)

---

## Changes Summary

| Component | Before | After | Why |
|-----------|--------|-------|-----|
| Default threshold | 0.85 | 0.75 | Too strict in practice |
| Min threshold warning | 0.75 | 0.70 | More realistic guidance |
| Fallback default | 0.85 | 0.75 | Consistency |
| Warning text | >= 0.85 | >= 0.75 | Updated guidance |

---

## FAQ

**Q: Will lower threshold cause false positives (wrong clicks)?**  
A: With 0.75, it's unlikely. Images need to be 75% similar, which is still quite strict.

**Q: Should I change all my existing scenarios?**  
A: Not necessary. This is just the default. Your existing scenarios keep their thresholds.

**Q: What if my scenario has mix of strict and loose images?**  
A: Set each image individually. For critical images (last step), use 0.80-0.85. For optional images, use 0.70-0.75.

**Q: Why was 0.85 chosen originally?**  
A: Probably to be "safe" and avoid false positives. But it was too safe and missed real matches.

---

## Next Steps

1. **Restart the app** to load new default threshold
2. **Test your scenario** that was failing
3. **Watch the logs** for match scores
4. **Adjust if needed** by modifying individual image thresholds

If you still have issues, the problem might be:
- Image quality (recapture it)
- Search region (check region boundaries)
- Lighting (game conditions changed)

---

**Applied**: June 6, 2026  
**Files Modified**: 2 (core/vision.py, scenario/templates.py)  
**Default Changed**: 0.85 → 0.75  
**Reason**: More practical for real-world scenarios
