# 🎯 PRECISION MODE vs 🔎 SEARCH REGION - Phân Biệt Chi Tiết

## ❓ CÂU HỎI
> "thế khác gì giới hạn phạm vi tìm kiếm" - Phân biệt Precision Mode với Search Region là gì?

---

## 📊 BẢNG SO SÁNH NHANH

| Tính Năng | Precision Mode 🎯 | Search Region 🔎 |
|-----------|-------------------|-------------------|
| **Mục đích** | Cải thiện độ chính xác matching | Thu hẹp phạm vi tìm ảnh |
| **Cấu hình** | Bật/Tắt global (toàn bộ bot) | Vẽ vùng trên màn hình |
| **Ảnh hưởng** | Scale scanning (zoom %) | Tọa độ pixel (vị trí) |
| **Tốc độ** | Nhanh hơn (ưu tiên 1.0) | Nhanh hơn (ít pixel scan) |
| **Linh hoạt** | Ít (chỉ có on/off) | Cao (tùy chỉnh từng hình) |
| **Mục tiêu** | Tránh match nhầm hình | Bỏ qua vùng không cần thiết |

---

## 🎯 PRECISION MODE - Kiểm Soát ZOOM %

### Khái Niệm
**Precision Mode** kiểm soát **phạm vi ZOOM** (scale %) khi tìm ảnh.

```
Khi ảnh chụp có thể bị zoom/phóng đại khác nhau:
- Ảnh gốc: 100x100 pixel
- Màn hình: 75%, 80%, 100%, 120%, 150%, ...

→ Precision Mode giúp bot biết nên tìm ở % nào
```

### BẬT Precision Mode (ON) - Scale hẹp
```
Dải scan: 85% - 115% (±15% xung quanh 100%)
Ưu tiên:  1.0 (100%) TRƯỚC, rồi ±5%, ±10%, ±15%

Ví dụ scan order:
  1. 100% (scale 1.0)    ← Thử trước tiên
  2. 95% (scale 0.95)
  3. 105% (scale 1.05)
  4. 90% (scale 0.90)
  5. 110% (scale 1.10)
  ...

✅ Ưu điểm:
  - Nhanh (90% hình match ở 100%)
  - Chính xác (tập trung vùng gần gốc)
  - Tránh false positive (không scan quá xa)

❌ Nhược điểm:
  - Nếu ảnh zoom quá (30-40%), sẽ miss
  - Cần ảnh chụp ở resolution tiêu chuẩn
```

### TẮT Precision Mode (OFF) - Scale rộng
```
Dải scan: 70% - 130% (±30% xung quanh 100%)
Ưu tiên:  1.0 (100%) TRƯỚC, rồi scan rộng

Ví dụ scan order:
  1. 100% (scale 1.0)    ← Thử trước tiên
  2. 95%, 105%, 90%, 110%, ...
  3. 85%, 115%, 80%, 120%, ...
  4. 75%, 125%, 70%, 130%   ← Cuối cùng

✅ Ưu điểm:
  - Linh hoạt (ảnh có thể zoom 30-40%)
  - Tìm được mọi size ảnh
  - Không bị miss hình

❌ Nhược điểm:
  - Chậm hơn (scan thêm nhiều scale)
  - Dễ match nhầm (quá linh hoạt)
```

---

## 🔎 SEARCH REGION - Giới Hạn VÙNG PIXEL

### Khái Niệm
**Search Region** giới hạn **vùng pixel** (tọa độ XY) khi tìm ảnh.

```
Thay vì scan toàn bộ màn hình (1920x1080):
→ Chỉ scan vùng nhất định, ví dụ (100,100) → (800,600)

Ứng dụng:
- Chỉ tìm ảnh ở phía trái màn hình
- Bỏ qua menu phía trên
- Bỏ qua chat box phía dưới
```

### Cách Sử Dụng
```python
# Bước 1: Click "🔎 Giới hạn phạm vi tìm kiếm"
# Bước 2: Kéo chuột vẽ hình chữ nhật
# Bước 3: Nhả chuột → Lưu vùng

# Sau đó, tất cả hình ảnh sẽ chỉ tìm trong vùng này
# Thay vì scan toàn bộ màn hình
```

### Ví Dụ Thực Tế
```
Maple Story layout:
┌──────────────────────────────────┐
│ TOP MENU (bỏ qua)                │
├──────────────────────────────────┤
│ 🔎 GAME AREA (search region)      │  ← Chỉ scan vùng này
│                                   │
└──────────────────────────────────┘
│ CHAT / SKILL BAR (bỏ qua)        │

→ Giới hạn phạm vi = chỉ scan vùng GAME AREA
→ Không phải scan menu + chat = nhanh hơn!
```

### Xóa Search Region
```python
Click "🔎 Xóa Giới Hạn" hoặc "❌ Quay Lại Full Screen"
→ Quay về scan toàn bộ màn hình
```

---

## 📝 VÍ DỤ THỰC TIỄN

### Scenario: Tìm Nút "Battle Start"

#### ❌ SAI - Không hiệu quả
```python
# Không dùng Search Region
# → Bot scan toàn bộ 1920x1080 mỗi frame
# → Chậm, dễ match nhầm (nút khác trên menu có cùng hình)
```

#### ✅ ĐÚNG - Tối ưu
```python
# Bước 1: Bật Precision Mode
state.precision_mode = True

# Bước 2: Giới hạn Search Region
# Click vẽ vùng "Battle Area" trên màn hình
# Ví dụ: (500, 300) → (1400, 800)

# Bước 3: Thêm ảnh nút "Battle Start"
# Bot sẽ:
# - Chỉ scan vùng (500, 300) → (1400, 800)
# - Tìm scale 85-115% (nhanh)
# - Không match nhầm nút trên menu
```

---

## 🔄 FLOW MATCHING CHI TIẾT

### Khi Cả Hai Bật (Precision Mode ON + Search Region)

```
Input: Full screenshot (1920x1080)
    ↓
[1] Cắt region (Search Region)
    → Ví dụ: (100, 100) → (800, 600) = 700x500 pixel
    ↓
[2] Scan scales (Precision Mode)
    → Thử: 100%, 95%, 105%, 90%, 110%, 85%, 115%
    ↓
[3] Template matching
    → Chỉ trong vùng (700x500 pixel)
    → Với 7 scales
    ↓
[4] Tính toán click point
    → Cộng offset region vào tọa độ cuối cùng
    ↓
Output: Click position (X, Y) trên toàn màn hình
```

### Debug Log
```
✅ Match origin: (50, 30)
✅ Matched size: 100x100
✅ Region offset: (100, 100)  ← Từ Search Region
✅ Final click point: (150, 130)  ← (50+100, 30+100)
```

---

## 🎓 HIỂU RÕ CÔNG THỨC

### Precision Mode → SCALE (%)
```python
Scales = [1.0, 0.95, 1.05, ...]  # % zoom

matched_size = base_size * scale
# Ví dụ: 100 * 1.0 = 100px (100%)
# Ví dụ: 100 * 0.95 = 95px (95%)
```

### Search Region → OFFSET (pixel)
```python
region = (100, 100, 800, 600)  # X1, Y1, X2, Y2
region_offset = (100, 100)  # Điểm (0,0) trong region ở (100,100) toàn màn hình

final_click = match_point + region_offset
# Ví dụ: (50, 30) trong region + (100, 100) offset
# → (150, 130) trên toàn màn hình
```

---

## 🚀 GỢI Ý DÙNG

### PRECISION MODE
```
✅ Bật nếu:
  - Ảnh chụp ở resolution chuẩn
  - Game UI không bị zoom nhiều
  - Muốn tốc độ nhanh

❌ Tắt nếu:
  - Game UI bị zoom 30-50%
  - Ảnh chụp ở resolution khác nhau
  - Muốn tìm khả năng cao
```

### SEARCH REGION
```
✅ Dùng nếu:
  - Game layout cố định (menu + game area riêng)
  - Muốn tránh match nhầm ở vùng khác
  - Muốn tốc độ nhanh hơn

❌ Không cần nếu:
  - Chỉ có 1-2 hình để tìm
  - Toàn bộ màn hình là vùng match
  - Layout hay thay đổi
```

---

## 📌 BEST PRACTICES

### Combo Tối Ưu
```
1. Bật Precision Mode (ON)
2. Giới hạn Search Region
3. Threshold = 0.85
4. Dùng Edge Validation (mặc định)

→ Kết quả: Nhanh, chính xác, ít false positive
```

### Flow Thiết Lập
```
1. Chụp ảnh các nút game
2. Giới hạn Search Region (vùng game area)
3. Thêm ảnh vào bot
4. Test matching
   - Nếu match tốt → OK
   - Nếu miss → Tắt Precision Mode
5. Chạy kịch bản
```

### Debug Khi Có Vấn Đề
```
❌ Không tìm thấy ảnh?
→ Kiểm tra log console:
   - Scale mismatch: Tắt Precision Mode
   - Region offset sai: Kiểm tra Search Region
   - Score < threshold: Giảm threshold

❌ Click sai vị trí?
→ Kiểm tra log:
   - Region offset: (X, Y) có đúng không?
   - Scale factor: Có quá khác 1.0 không?
   - Click point calculation: Công thức đúng không?
```

---

## 📚 CHƯƠNG TRÌNH HỌC

### Level 1 - Cơ Bản
```
☑ Biết Precision Mode là gì (scale zoom %)
☑ Biết Search Region là gì (giới hạn pixel)
☑ Biết bật/tắt chúng
```

### Level 2 - Trung Cấp
```
☑ Hiểu tầm ảnh hưởng của từng cái
☑ Biết khi nào bật/tắt
☑ Debug được khi có vấn đề
```

### Level 3 - Nâng Cao
```
☑ Tối ưu hóa scenario
☑ Kết hợp cả hai để có kết quả tốt nhất
☑ Hiểu công thức scale + offset
```

---

## 🎯 KẾT LUẬN

| Cần | Precision Mode | Search Region |
|-----|----------------|-|
| **Tốc độ nhanh?** | ✅ (nếu ảnh gốc) | ✅ (giảm pixel) |
| **Tránh false positive?** | ✅ (scale hẹp) | ✅ (vùng riêng) |
| **Linh hoạt?** | ❌ | ✅✅ (tùy chỉnh từng hình) |
| **Dễ thiết lập?** | ✅ (on/off) | ❌ (phải vẽ vùng) |

**Kết quả tốt nhất:** **Dùng CẢ HAI** 🎯🔎

---

**Developed:** Kiro AI Assistant  
**Date:** June 6, 2026  
**Version:** 1.0 - Precision Mode vs Search Region Guide  

**Status:** ✅ Ready to use

