# ⚡ QUICK START GUIDE - PokéClick PRO v2.0

## 🎮 Bắt Đầu Nhanh

### 1️⃣ Chạy Bot
```bash
python autoclick_gui.py
```

### 2️⃣ Giao Diện Chính
```
┌─ HEADER ───────────────────────────────┐
│ ⚡ POKÉCLICK PRO                       │
└────────────────────────────────────────┘
┌─ LEFT PANEL ─┬─ CENTER ─┬─ RIGHT PANEL ┐
│ Settings    │ Scenario  │ Library       │
│ Buttons     │ Items     │ Games/Stages  │
└─────────────┴───────────┴───────────────┘
```

### 3️⃣ Thêm Hình Ảnh
- Click **"📸 Chụp & Thêm Hình"**
- Chọn vùng trên màn hình
- Đặt tên (optional)
- ✅ Hình được thêm vào danh sách

---

## 🔑 HOTKEYS (Phím Tắt)

| Phím | Chức Năng | Mặc Định |
|------|----------|---------|
| **Bắt Đầu** | Start clicking | F6 |
| **Dừng** | Stop clicking | F7 |
| **Chụp Hình** | Capture & Add | F8 |

Để thay đổi hotkey: Settings → Edit Hotkeys

---

## ⚙️ SETTINGS (CÀI ĐẶT)

### 1. Precision Mode 🎯
- **BẬT**: Scale 85-115% (nhanh, chính xác)
- **TẮT**: Scale 70-130% (linh hoạt hơn)

→ [Xem chi tiết](./PRECISION_VS_SEARCH_REGION.md#🎯-precision-mode---kiểm-soát-zoom-)

### 2. Search Region 🔎
- Giới hạn vùng tìm kiếm trên màn hình
- Giúp bỏ qua vùng không cần thiết
- Tăng tốc độ và độ chính xác

→ [Xem chi tiết](./PRECISION_VS_SEARCH_REGION.md#🔎-search-region---giới-hạn-vùng-pixel)

### 3. Threshold 📊
- **0.85** (mặc định): An toàn, ít false positive
- **0.80**: Cân bằng
- **0.75**: Dễ match hơn (cẩn thận!)
- **<0.75**: ⚠️ Cảnh báo

### 4. Speed ⚡
- Adjust **click delay** giữa các action
- Mặc định: 1.0 giây

### 5. Human Click Mode 🖱️
- Mô phỏng click giống con người
- Thêm chút random delay
- Tránh bị phát hiện

---

## 📋 TẠO SCENARIO

### Option 1: Template-based
```python
1. Thêm hình ảnh → Click **"📸 Thêm Hình"**
2. Thêm click tại vị trí → Click **"🖱️ Click Tại Đây"**
3. Thêm phím bấm → Click **"⌨️ Thêm Phím"**
4. Lặp lại tới đầu → Click **"🔄 Lặp Lại"**
5. Lưu kịch bản → **Ctrl+S** hoặc **File → Save**
```

### Option 2: Library-based
```python
1. Chọn Game (ví dụ: Maple Story)
2. Chọn Stage (ví dụ: Cooking)
3. Bot sẽ tự động load các stage này
4. Click Play → Chạy từng stage lần lượt
```

---

## 🚀 CHẠY BOT

### Chạy Đơn
```
1. Click "▶ START" (hoặc F6)
2. Bot tự động thực hiện kịch bản
3. Xem log console để debug
```

### Chạy Library
```
1. Mở Library Panel (phía phải)
2. ✓ Tích các Stage cần chạy
3. Click "▶ RUN SELECTED"
4. Bot chạy từng stage lần lượt
```

### Chạy Vô Hạn (Loop)
```
1. Click "♾️ Vô Hạn"
2. Bot chạy liên tục
3. Click "⏹ STOP" để dừng
```

---

## 🐛 DEBUG & TROUBLESHOOTING

### Xem Log Console
```bash
# Console sẽ hiển thị:
✅ Best match for button => btn_battle (score: 0.92)
🔵 Final click point: (570, 390)
🖱️ Clicked at: (570, 390)
```

### Kiểm Tra Match
```
1. Thêm hình ảnh
2. Click "🧪 Test Matching"
3. Xem kết quả:
   - ✅ Found = Tốt
   - ❌ Not found = Kiểm tra threshold hoặc Precision Mode
```

### Vấn Đề Thường Gặp

| Vấn Đề | Giải Pháp |
|--------|----------|
| Click sai vị trí | Kiểm tra console log → Scale factor → Đọc PRECISION_VS_SEARCH_REGION.md |
| Không tìm thấy hình | Giảm threshold / Tắt Precision Mode |
| Chạy chậm | Bật Precision Mode / Dùng Search Region |
| Bot dừng đột ngột | Kiểm tra "Wait Until Found" timeout |

---

## 📁 FILE STRUCTURE

```
tool_click_image/
├── autoclick_gui.py          ← Main GUI
├── core/
│   ├── vision.py             ← Image matching engine
│   ├── runner.py             ← Click execution
│   ├── input.py              ← Mouse/keyboard input
│   ├── state.py              ← Global state
│   └── __init__.py
├── scenario/
│   ├── io.py                 ← Save/Load scenarios
│   ├── templates.py          ← Template UI
│   └── library.py            ← Game library
├── ui/
│   ├── theme.py              ← Colors & styling
│   ├── library_panel.py       ← Library panel
│   └── hotkeys.py            ← Hotkey management
├── scenarios/                ← Saved scenarios
│   ├── Dragoncity/
│   └── maple/
└── README_UPGRADE.md         ← Upgrade notes
```

---

## 🔧 CHỈNH SỬA ADVANCED

### Custom Click Point
```python
1. Click hình ảnh trong danh sách
2. Click "✏️ Edit"
3. Chọn "Custom Click Point"
4. Click trên ảnh để chỉ định vị trí
5. ✅ Save
```

### Per-Image Threshold
```python
1. Click hình ảnh
2. Click "✏️ Edit"
3. Điều chỉnh "Threshold" cho riêng hình này
4. ✅ Save
```

### Per-Image Search Region
```python
1. Click hình ảnh
2. Click "✏️ Edit"
3. Bật "Search Region Enabled"
4. Vẽ vùng
5. ✅ Save
```

---

## 📊 PERFORMANCE TIPS

### Tối Ưu Hóa Tốc Độ
```
1. ✅ Bật Precision Mode
2. ✅ Dùng Search Region (giới hạn vùng)
3. ✅ Giảm click delay (nhưng không quá)
4. ✅ Bỏ "Wait Until Found" nếu không cần
5. ✅ Giảm số loops nếu có thể
```

### Tối Ưu Hóa Độ Chính Xác
```
1. ✅ Threshold = 0.85 (mặc định tốt)
2. ✅ Bật Edge Validation (mặc định)
3. ✅ Chụp ảnh ở resolution chuẩn
4. ✅ Giới hạn Search Region (tránh match nhầm)
5. ✅ Custom Click Point nếu cần
```

---

## 🎓 LEARNING PATH

### Day 1: Basics
- [ ] Chạy bot lần đầu
- [ ] Thêm hình ảnh
- [ ] Tạo scenario đơn
- [ ] Click Play

### Day 2: Intermediate
- [ ] Hiểu Precision Mode
- [ ] Sử dụng Search Region
- [ ] Chỉnh Threshold
- [ ] Chạy Library

### Day 3: Advanced
- [ ] Custom Click Point
- [ ] Per-image Settings
- [ ] Optimize Performance
- [ ] Master Debugging

---

## 📚 DOCUMENTATION MAP

| File | Mô Tả |
|------|-------|
| `README_UPGRADE.md` | Nâng cấp v2.0 |
| `PRECISION_VS_SEARCH_REGION.md` | Chi tiết 2 tính năng |
| `HOW_TO_TEST.md` | Hướng dẫn test |
| `FALSE_POSITIVE_FIX.md` | Tránh match nhầm |
| `SCROLL_FIX.md` | Fix scroll issue |
| `QUICK_START_GUIDE.md` | File này |

---

## 🆘 SUPPORT

### Lỗi Import?
```bash
# Đảm bảo chạy từ thư mục gốc
cd d:\Program Files\Autoclick_ver_2\tool_click_image
python autoclick_gui.py
```

### ModuleNotFoundError?
```bash
# Cài dependencies
pip install pillow opencv-python pyautogui numpy
```

### Console hiện gì đó lạ?
```
→ Kiểm tra file tương ứng
→ Đọc log message
→ Đọc documentation matching file
→ Nếu vẫn không hiểu, search `[THREAD ERROR]` messages
```

---

## 🎉 READY TO GO!

```
✅ Installation complete
✅ All dependencies ok
✅ GUI launch ready
✅ Happy farming! 🎮⚡
```

Run: `python autoclick_gui.py`

---

**Quick Links:**
- 🎯 [Precision Mode Details](./PRECISION_VS_SEARCH_REGION.md)
- 🔎 [Search Region Guide](./PRECISION_VS_SEARCH_REGION.md)
- 🧪 [Testing Guide](./HOW_TO_TEST.md)
- 📈 [Upgrade Details](./README_UPGRADE.md)
- 🚫 [False Positive Prevention](./FALSE_POSITIVE_FIX.md)

---

**Version:** 2.0 - Enhanced Image Matching  
**Status:** ✅ Production Ready  
**Last Updated:** June 6, 2026  

Enjoy! 🎮⚡

