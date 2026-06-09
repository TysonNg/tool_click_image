# 📍 Lấy Tọa Độ Tương Đối (Relative Coordinate) - Hướng Dẫn

## Chức Năng Mới

**Nút: "📍 Lấy Tọa Độ Tương Đối (Relative)"**
- Vị trí: Trong phần "⚔️ KỸ NĂNG CHIẾN ĐẤU" (bên trái)
- Màu sắc: Tím (để phân biệt với các nút khác)

---

## ✨ Tại Sao Cần Tọa Độ Tương Đối?

### Vấn Đề Với Tọa Độ Screen (Cũ):
```
Lưu tọa độ screen: (1920, 1080)
↓
Di chuyển cửa sổ game sang monitor khác
↓
Click tại (1920, 1080) → Click sai vị trí! ❌
```

### Giải Pháp: Tọa Độ Tương Đối Với Cửa Sổ Game
```
Lưu tọa độ relative: (450, 200) [từ top-left của game window]
↓
Di chuyển cửa sổ game sang monitor khác
↓
Bot tự động tính toán lại → Click tại vị trí đúng! ✅
```

---

## 🎯 Cách Sử Dụng

### Bước 1: Bấm Nút "📍 Lấy Tọa Độ Tương Đối"
```
Trong giao diện → Tìm nút tím "📍 Lấy Tọa Độ Tương Đối"
→ Bấm nó
```

### Bước 2: Cửa Sổ Hướng Dẫn Sẽ Xuất Hiện
```
┌─────────────────────────────────┐
│ 📍 Lấy Tọa Độ Tương Đối        │
├─────────────────────────────────┤
│ Hướng dẫn:                      │
│ 1. Di chuyển chuột vào vị trí   │
│    muốn lấy tọa độ              │
│ 2. Bấm ENTER để lấy tọa độ      │
│                                 │
│ ⏳ Chờ...                        │
└─────────────────────────────────┘
```

### Bước 3: Di Chuyển Chuột Vào Vị Trí Cần Lấy
```
- Di chuyển chuột vào vị trí muốn lấy tọa độ
  (Có thể là nút, đối tượng, hay bất kỳ điểm nào trong game)
```

### Bước 4: Bấm ENTER
```
- Giữ chuột tại vị trí
- Bấm phím ENTER trên bàn phím
```

### Bước 5: Xem Kết Quả
```
✅ Thành Công!

Tọa Độ Tương Đối:

Pixel: (450, 200)
Phần Trăm: (56.3%, 33.3%)

Cửa Sổ: [Tên cửa sổ game]
Vị Trí Cửa Sổ: (1920, 1080)
```

---

## 📊 Kết Quả Được Lưu

### Dữ Liệu Được Lưu Trong State:
```python
state.captured_relative_x = 450      # Tọa độ X tương đối
state.captured_relative_y = 200      # Tọa độ Y tương đối
state.captured_relative_percent_x = 56.3  # Phần trăm X
state.captured_relative_percent_y = 33.3  # Phần trăm Y
state.game_hwnd = <hwnd>  # Handle của cửa sổ game
```

### Hiển Thị Trong Status Bar:
```
✅ Lấy tọa độ tương đối: (450, 200) | Phần trăm: (56.3%, 33.3%)
```

---

## 🎮 Ví Dụ Thực Tế

### Ví Dụ 1: Lấy Tọa Độ Nút "Bắt Đầu" Trong Game
```
1. Bấm "📍 Lấy Tọa Độ Tương Đối"
2. Di chuyển chuột vào tâm nút "Bắt Đầu" trong game
3. Bấm ENTER
4. Kết quả: Pixel: (500, 300)
5. Lưu lại: (500, 300) = vị trí nút "Bắt Đầu"
```

### Ví Dụ 2: Lấy Tọa Độ NPC Trong Game
```
1. Bấm "📍 Lấy Tọa Độ Tương Đối"
2. Di chuyển chuột vào vị trí NPC
3. Bấm ENTER
4. Kết Quả: Pixel: (300, 250)
5. Dùng tọa độ này trong script click tự động
```

### Ví Dụ 3: Khi Cửa Sổ Game Được Di Chuyển
```
Bước 1:
- Game ở monitor 1, vị trí screen (1920, 1000)
- Lấy tọa độ relative: (450, 200)
- Pixel screen lúc đó: (1920 + 450, 1000 + 200) = (2370, 1200)

Bước 2:
- Di chuyển game sang monitor 2, vị trí screen (500, 100)
- Bot biết là tọa độ relative (450, 200)
- Bot tự động tính: (500 + 450, 100 + 200) = (950, 300) ✅
- Click tại (950, 300) → Vẫn click đúng vị trí!
```

---

## 🔄 So Sánh: Relative vs Screen Coordinates

| Aspect | Screen Coordinates | Relative Coordinates |
|--------|-------------------|----------------------|
| Dựa vào | Vị trí màn hình | Vị trí cửa sổ game |
| Khi di chuyển game | Bị sai ❌ | Vẫn đúng ✅ |
| Khi game resize | Bị sai ❌ | Vẫn đúng ✅ |
| Multi-monitor | Phức tạp ❌ | Đơn giản ✅ |
| Bảo trì | Khó khăn ❌ | Dễ dàng ✅ |

---

## 💡 Tips & Tricks

### Tip 1: Lấy Tọa Độ Chính Xác
```
- Di chuyển chuột vào vị trí chính xác của mục tiêu
- Đảm bảo chuột ở giữa đối tượng (không quá bên cạnh)
- Bấm ENTER khi chuột ở vị trí chính xác
```

### Tip 2: Sử Dụng Phần Trăm Cho Responsive Targets
```
Ví dụ: Nút ở 50%, 50% (giữa cửa sổ game)
- Kể cả game resize, nút vẫn ở giữa ✅
- Dùng phần trăm thay vì pixel tuyệt đối
```

### Tip 3: Lưu Tất Cả Tọa Độ
```
Tạo danh sách:
- Nút "Chơi": (500, 300)
- Nút "Shop": (400, 150)
- NPC A: (200, 400)
- NPC B: (700, 350)

Sau đó dùng lại:
- Click (500, 300) để bấm "Chơi"
- Click (400, 150) để mở "Shop"
- v.v...
```

### Tip 4: Kiểm Tra Tọa Độ
```
1. Lấy tọa độ
2. Dùng "🖱️ Test Click" để thử
3. Nếu sai, lấy lại tọa độ khác
4. Lặp lại cho đến khi đúng
```

---

## ⚠️ Lưu Ý Quan Trọng

### Khi Sử Dụng:

1. **Cửa Sổ Game Phải Visible**
   - Game window không được ẩn hoặc minimize
   - Phải có thể nhìn thấy cửa sổ trên màn hình

2. **Chuột Phải Ở Trong Game**
   - Khi bấm ENTER, chuột phải nằm TRONG cửa sổ game
   - Không phải ở ngoài hay trên taskbar

3. **Phải Bấm ENTER**
   - Không phải bấm chuột, bấm **ENTER** (phím Enter trên bàn phím)
   - Nếu không bấm ENTER, tọa độ sẽ không được lưu

4. **Game Handle Được Lưu**
   - Bot sẽ nhớ cửa sổ game nào được lấy tọa độ
   - Khi click sau này, dùng tọa độ tương đối với cửa sổ đó

---

## 🔧 Sử Dụng Trong Code (Advanced)

### Lấy Tọa Độ Tương Đối Từ Code:
```python
from core.relative_capture import RelativeCoordinateCapture

# Lấy thông tin cửa sổ game
window_info = RelativeCoordinateCapture.get_game_window_info()

# Lấy tọa độ hiện tại
screen_x, screen_y = pyautogui.position()

# Chuyển sang tọa độ relative
rel_x, rel_y = RelativeCoordinateCapture.screen_to_relative(
    screen_x, screen_y, window_info
)

print(f"Tọa độ tương đối: ({rel_x}, {rel_y})")
```

### Chuyển Tọa Độ Relative Sang Screen:
```python
# Biết tọa độ relative
rel_x, rel_y = 450, 200

# Lấy thông tin cửa sổ
window_info = RelativeCoordinateCapture.get_game_window_info()

# Chuyển sang screen coordinates
screen_x, screen_y = RelativeCoordinateCapture.relative_to_screen(
    rel_x, rel_y, window_info
)

print(f"Tọa độ screen: ({screen_x}, {screen_y})")
```

---

## 📋 Checklist - Sử Dụng Đúng

- [ ] Đã cài đặt pyautogui + pywin32
- [ ] Game window đang mở và visible
- [ ] Bấm nút "📍 Lấy Tọa Độ Tương Đối"
- [ ] Di chuyển chuột vào vị trí muốn lấy
- [ ] Bấm **ENTER** (phím enter trên bàn phím)
- [ ] Xem kết quả hiển thị
- [ ] Lưu tọa độ để dùng lại

---

## ✅ Status: Hoàn Thành

- [x] Chức năng capture tọa độ relative
- [x] Chuyển đổi screen ↔ relative
- [x] Hiển thị pixel + phần trăm
- [x] Lưu vào state
- [x] Nút UI thêm vào
- [x] Hướng dẫn viết xong

**Sẵn sàng sử dụng! 🎯**

---

**Hướng Dẫn Tọa Độ Tương Đối - Version 1.0**
