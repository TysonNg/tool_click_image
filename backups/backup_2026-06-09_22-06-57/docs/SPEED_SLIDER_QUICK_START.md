# ⚡ Speed Slider - Quick Start

## Your Problem

"Tôi đã set delay 0s rồi mà sao vẫn chậm quá"

Nguyên nhân: Có 8 chỗ delay cứng trong code (0.1s, 0.2s) không thể set

---

## Solution: Speed Slider

New button: **"⚡ Tốc độ chạy (0% = Nhanh nhất)"**

### How To Use

1. **Click the button**
   ```
   ⚡ Tốc độ chạy (0% = Nhanh nhất)
   ```

2. **Slider opens**
   ```
   [0%]══════[50%]════════[100%]
   
   - 0%   = Tối đa (không chờ)
   - 50%  = 2x faster
   - 100% = Bình thường
   ```

3. **Drag to desired speed, click OK**
   ```
   Done! Tất cả delays áp dụng multiplier này
   ```

---

## Speed Levels

| Level | Multiplier | Effect |
|-------|-----------|--------|
| 0% | 0.0x | ⚡ MAX SPEED |
| 25% | 0.25x | ⚡ 4x faster |
| 50% | 0.5x | ⚡ 2x faster |
| 100% | 1.0x | Normal |

---

## Example

### Before (Slow)
```
Delay = 0s
But still has gaps:
  - 0.1s between clicks
  - 0.2s hold key
  - Multiple repeats = 1+ second wasted
```

### After (Fast with 0%)
```
Speed Slider = 0%
All gaps become:
  - 0.1 × 0 = 0
  - 0.2 × 0 = 0
  - INSTANT! ⚡
```

---

## What It Controls

✅ All 8 types of delays:
- Click gaps (0.1s)
- Hold key (0.2s)
- Click delays (0.5s)
- Key delays (0.5s)
- Retry waits
- And more...

---

## Recommended Settings

- **Farming**: 0% (max speed, need to risk)
- **Safe**: 50% (2x faster, relatively safe)
- **Normal**: 100% (default, balanced)

---

## Testing

1. Restart app
2. Click "⚡ Tốc độ chạy"
3. Set to 0%
4. Run scenario
5. See it run **MUCH FASTER** ⚡⚡⚡

---

**Status**: ✅ Ready to use!

For details: See `SPEED_SLIDER_FEATURE.md`
