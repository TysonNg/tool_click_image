# 🔍 Debug Image Recognition - Không Nhận Diện

## 🐛 Vấn Đề

Chụp ảnh bằng tool capture trong app, nhưng khi chạy không nhận diện được.

## 🔧 Kiểm Tra

### 1. **Xem Matching Score**

Khi chạy automation, check terminal/log xem score matching:

```
🔍 Template 'pokemon': best_score=0.5234 vs threshold=0.8500
  Scale 1.00: score=0.5234, threshold=0.8500, method=TM_CCOEFF_NORMED+EdgePenalty(0.65)
```

**Phân tích:**
- `best_score=0.5234` → Score matching
- `threshold=0.8500` → Threshold cần đạt
- `0.5234 < 0.8500` → **KHÔNG đủ**, không nhận diện ❌
- `EdgePenalty(0.65)` → Edge similarity chỉ 0.65 (khác nhau)

### 2. **Nguyên Nhân Score Thấp**

**Nguyên nhân 1: Threshold quá cao**
```
Đề xuất: threshold >= 0.85 để tránh false positive
Thực tế: Chụp tool nhiều khi chỉ match ~0.6-0.7
→ Giảm threshold xuống 0.75-0.80
```

**Nguyên nhân 2: Ảnh chụp và runtime khác nhau**
```
Khi chụp:
- Ánh sáng tối
- Đối tượng ở vị trí A

Khi chạy:
- Ánh sáng sáng hơn
- Đối tượng nhú bị di chuyển 5px
- Kích thước bị scale

→ Edge detection khác nhau → penalty mạnh
```

**Nguyên nhân 3: Screenshot vs Template resolution**
```
Chụp: 1920x1080
Runtime: 2560x1440 hoặc VGA mode
→ Mismatch

→ Cần chụp ở cùng resolution
```

## ✅ Giải Pháp

### Cách 1: Giảm Threshold

**Trước:**
```
Threshold: 0.85 (quá cao, khó match)
```

**Sau:**
```
Threshold: 0.75 (cân bằng: match dễ hơn, false positive ít hơn)
```

**Khi setup ảnh:**
1. Chụp ảnh
2. Cấu hình
   - Threshold: **0.75** (thay vì 0.85)
3. Save

**Test:**
```
🔍 Template 'pokemon': best_score=0.7234 vs threshold=0.7500
  → CLOSE! Gần vs threshold

→ Giảm xuống 0.70 thêm một chút
```

### Cách 2: Chụp Lại Với Điều Kiện Tốt

**Chuẩn bị:**
1. **Ánh sáng ổn định** - Không thay đổi
2. **Resolution cố định** - Chụp ở resolution runtime
3. **Đối tượng rõ ràng** - Contrast cao

**Chụp:**
```
1. Bấm "🖼️ Thêm Pokémon mục tiêu (Ảnh)"
2. Chọn "Chụp trên màn hình"
3. Chụp ảnh
4. Đặt điểm click
5. **Threshold: 0.80-0.85** (lần này có thể cao hơn)
6. Save
```

### Cách 3: Debug Với Template Testing

Để test trước khi chạy full:

```python
# Test matching để xem score
# code trong templates.py: test_image_matching()

1. Thêm ảnh
2. Bấm "Test" (nếu có)
3. Xem score → nếu < threshold, giảm threshold hoặc chụp lại
```

## 📊 Threshold Recommendations

| Threshold | Matching Độ Khó | False Positive Risk |
|-----------|-----------------|-------------------|
| **0.70** | Dễ nhất | Cao - cảnh báo ⚠️ |
| **0.75** | Vừa phải | Trung bình - OK ✅ |
| **0.80** | Khó | Thấp - tốt |
| **0.85+** | Rất khó | Rất thấp - quá cao |

**Khuyến nghị:** `0.75-0.80`

## 🛠️ Troubleshoot

### Scenario 1: Score ~0.60, Threshold 0.85

```
🔍 Template 'button': best_score=0.6234 vs threshold=0.8500
  Scale 1.00: score=0.6234, method=TM_CCOEFF_NORMED+EdgePenalty(0.50)

Vấn đề: EdgePenalty(0.50) = Edge khác nhau 50%!
→ Ảnh chụp vs runtime ánh sáng khác
→ Hoặc chuột che một phần
```

**Fix:**
- Chụp lại với cùng điều kiện ánh sáng
- Hoặc giảm threshold → 0.60

### Scenario 2: Score ~0.75, Threshold 0.85

```
🔍 Template 'icon': best_score=0.7534 vs threshold=0.8500
  Scale 1.00: score=0.7534, method=TM_CCOEFF_NORMED

Vấn đề: Rất gần! Chỉ cách 0.10
→ Threshold quá cao
```

**Fix:**
- Giảm threshold → 0.75
- Hoặc chụp ảnh sạch hơn (full, không bị che)

### Scenario 3: Multiple scales, score không consistent

```
🔍 Template 'player': best_score=0.6534 vs threshold=0.7500
  Scale 0.80: score=0.4234, method=TM_CCOEFF_NORMED+EdgePenalty(0.45)
  Scale 0.90: score=0.5834, method=TM_CCOEFF_NORMED+EdgePenalty(0.60)
  Scale 1.00: score=0.6534, method=TM_CCOEFF_NORMED

Vấn đề: Scale 1.0 tốt nhất, nhưng < threshold
→ Runtime độ lớn đúng, nhưng matching kém
```

**Fix:**
- Chụp ảnh lớn hơn (full object, không crop chặt)
- Giảm threshold → 0.65
- Hoặc bật "Chờ tìm được" để retry nhiều lần

## 🎯 Best Practices

1. **Luôn chụp ở resolution runtime**
   ```
   Game: 1920x1080 → Chụp: 1920x1080
   Game: 2560x1440 → Chụp: 2560x1440
   ```

2. **Chụp ảnh sạch, rõ ràng**
   - Contrast cao
   - Không bị camera cover
   - Ánh sáng ổn định

3. **Threshold hợp lý: 0.75-0.80**
   - Đủ cao để tránh false positive
   - Đủ thấp để nhận được matching

4. **Test trước khi chạy**
   - Nếu có chức năng test → dùng nó
   - Nếu không → thử manual once để xem

5. **Nếu matching thất bại → Debug**
   - Xem log score
   - Kiểm tra `EdgePenalty` có quá cao?
   - Giảm threshold hoặc chụp lại

---

**Status: 🔍 Debug info added to logs!**

Khi chạy lần tới, check terminal xem matching score để adjust threshold.

