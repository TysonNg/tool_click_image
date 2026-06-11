# Diagnosis Guide - Why Match Score Is 0.485

Your log showed:
```
best_score=0.485, threshold=0.85
```

A 0.485 score means the matched image is only **48.5% similar** to your template. This is very low.

## Common Causes (In Order of Likelihood)

### 1. ❌ Image Was Captured in Wrong State
**Problem**: Button was in different state when captured vs when running
- Button color/appearance changed
- Button animation frame changed
- Button became highlighted/disabled

**Solution**:
1. Take a screenshot during gameplay
2. Compare with captured image
3. Recapture if different

**Check**: Open both images side-by-side. Are they visibly different?

---

### 2. ❌ Extreme Lighting Change
**Problem**: Game lighting changed drastically between capture and run
- Captured during day, running at night
- Captured indoors, running outdoors  
- Game changed brightness setting

**Example**:
```
Captured:     Bright yellow button on white
Later:        Dim orange button on gray
Match:        48.5% (colors very different)
```

**Solution**:
- Recapture in conditions matching gameplay
- Or adjust threshold to 0.50-0.60
- Or use mask to ignore color variations

---

### 3. ❌ Resolution Mismatch
**Problem**: Game resolution changed between capture and run
- Captured at 1920x1080, running at 2560x1440
- Captured at 2x zoom, running at 1x zoom
- Display scaling changed

**Example**:
```
Captured:     100x50 pixels (button)
Running:      150x75 pixels (same button, scaled)
Match:        Partial match because sizes different
```

**Solution**:
- Check game resolution setting
- Recapture at current resolution
- Use scale matching (already in code)

---

### 4. ❌ UI Element Moved
**Problem**: Button position or layout changed
- UI redesign moved button
- Window was resized
- Menu position changed

**Example**:
```
Captured:     Button at top-left
Running:      Button at center (after UI update)
Search region: Looking in wrong area
Match:        Can't find it, score=0.0 or very low
```

**Solution**:
- Verify search region is correct
- Check if window size matches capture
- Recapture if UI layout changed

---

### 5. ❌ Image Quality Too Low
**Problem**: Original capture was blurry or poor quality
- Captured at night with low brightness
- Capture tool zoomed wrong
- Image got corrupted

**Example**:
```
Captured:     Blurry button (low contrast)
Running:      Clear button (high contrast)
Match:        Can't match blurry to clear
Score:        ~40-50%
```

**Solution**:
- Check image file in `scenarios/Dragoncity/Arena/`
- Open in image viewer
- Look for blurriness
- Recapture if needed

---

### 6. ❌ Search Region Wrong
**Problem**: Match algorithm looking in wrong area
- Search region coordinates incorrect
- Search region outside visible area
- Region too small

**Solution**:
1. Go to image config
2. Check "Phạm vi tìm kiếm" (search region)
3. Verify coordinates are correct
4. Test with full screen (0,0 to max)

---

### 7. ❌ Threshold Too Strict (Now Fixed)
**Problem**: Default threshold was 0.85
- Already fixed! Now 0.75 default
- But score 0.485 is still below even 0.75

---

## Diagnostic Steps

### Step 1: Visual Inspection
```python
1. Open: d:\Program Files\Autoclick_ver_2\tool_click_image\scenarios\Dragoncity\Arena\3.png
2. Compare with what you see in game
3. Are they visibly the same? YES/NO

If NO → Problem is in captured image
If YES → Problem is in matching algorithm
```

### Step 2: Check File Properties
```
File: 3.png
- File size: Should be reasonable (20KB+)
- Image size: Should be clear (not 1x1 pixels)
- Modified date: Should match when you captured
```

### Step 3: Check Game State
```
1. Run game
2. Get to the exact moment before clicking 3.png
3. Take screenshot
4. Compare screenshot with capture_2.png and 3.png
5. Are all three similar? YES/NO

If NO → Image state changed
If YES → Something else is wrong
```

### Step 4: Test with Full Screen Search
```
1. Edit the image config for 3.png
2. Set search region to FULL SCREEN
   - X1: 0, Y1: 0
   - X2: 1920, Y2: 1080 (or your resolution)
3. Re-run scenario
4. Check if score improves
```

### Step 5: Debug Log
```
When running, check for these messages:
- "Bước cuối chưa xuất hiện 3.png..." (last step, waiting)
- "best_score=0.485" (very low)

This tells us:
✅ Image was searched
✅ Match algorithm ran
❌ But found only 48.5% match
```

---

## Score Interpretation Guide

| Score | Meaning | Action |
|-------|---------|--------|
| 0.90+ | Perfect match | ✅ Image will always work |
| 0.80-0.90 | Very good match | ✅ Works most of time |
| 0.75-0.80 | Good match | ✅ Works reliably |
| 0.70-0.75 | OK match | ⚠️ May work, risky |
| 0.60-0.70 | Poor match | ❌ Likely to fail |
| 0.50-0.60 | Very poor match | ❌ Your current situation |
| <0.50 | Bad match | ❌ Recapture needed |

---

## Why capture_2.png Was Skipped

Your log showed:
```
⏭️ Bỏ qua (không chờ): d:\...\Arena\capture_2.png
```

This worked as designed! Because:
- capture_2.png had "Không chờ" (don't wait)
- It wasn't found
- It wasn't the last step
- So it was skipped (this is correct!)

Then it tried 3.png (the last step), which failed.

---

## Action Plan

### Immediate (Tonight)
1. [ ] Open `scenarios/Dragoncity/Arena/3.png` in image viewer
2. [ ] Compare with game screenshot
3. [ ] Check if visibly the same
4. [ ] If different, recapture

### Short Term (Next Run)
1. [ ] Restart app (loads new 0.75 threshold)
2. [ ] Run scenario again
3. [ ] Check if better
4. [ ] If still fails, follow diagnostic steps

### If Still Failing
1. [ ] Reduce threshold to 0.70 or 0.65
2. [ ] Or recapture the image
3. [ ] Or check search region

---

## Quick Checklist

- [ ] Is 3.png file readable? (check size > 0KB)
- [ ] Is 3.png visually similar to game state?
- [ ] Did capture_2.png get skipped correctly? (YES = good!)
- [ ] Is 3.png marked as last step? (YES = why it must find)
- [ ] Did you restart app after threshold fix? (Do this!)
- [ ] Did you recapture recently? (If no, try recapturing)

---

## Need Help?

Check these files for more info:
- `THRESHOLD_FIX_EXPLANATION.md` - Why threshold matters
- `DEBUG_IMAGE_RECOGNITION.md` - Image matching troubleshooting
- `QUICK_START_TESTING.md` - Testing guide

---

**Your Situation**:
- Match score: 0.485 (too low) ❌
- Threshold: Now 0.75 (was 0.85) ✅
- Next step: Recapture image or investigate why score is low

**Most Likely**: Image was captured in different state than gameplay
**Solution**: Recapture 3.png during gameplay

---

Generated: June 6, 2026
