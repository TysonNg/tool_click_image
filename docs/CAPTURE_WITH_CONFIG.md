# 📍 Lấy Tọa Độ Tương Đối + Cấu Hình - Hướng Dẫn Hoàn Chỉnh

## ✨ Chức Năng Mới

**Nút: "📍 Lấy Tọa Độ Tương Đối (Relative)"**

Quy trình hoàn chỉnh:
1. **Chọn cửa sổ game** - Hỏi người dùng nhập tên cửa sổ
2. **Lấy tọa độ** - Di chuyển chuột + bấm ENTER
3. **Tự động cấu hình** - Mở dialog "Cài đặt tọa độ" với X, Y đã filled
4. **Cài đặt thông số** - Click_type, delay, repeat, v.v...
5. **Tự động thêm** - Lưu vào danh sách kịch bản

---

## 🎯 Quy Trình Chi Tiết

### Bước 1: Bấm Nút "📍 Lấy Tọa Độ Tương Đối"

```
Giao diện chính
  ↓ Tìm phần "⚔️ KỸ NĂNG CHIẾN ĐẤU" (bên trái)
  ↓ Bấm nút tím: "📍 Lấy Tọa Độ Tương Đối (Relative)"
```

### Bước 2: Chọn Cửa Sổ Game

```
Popup xuất hiện:
┌─────────────────────────────────────┐
│ 📍 Xác Định Cửa Sổ Game            │
├─────────────────────────────────────┤
│ Nhập tên cửa sổ game                │
│ (ví dụ: 'Notepad', 'Chrome',       │
│  'My Game')                         │
│                                     │
│ (Bạn có thể nhập tên riêng phần,   │
│  không cần đầy đủ)                  │
│                                     │
│ [  Chrome  ____________________]    │
│                                     │
│ [  OK  ]  [ Cancel ]               │
└─────────────────────────────────────┘
```

**Ví dụ:**
- Nhập: "Chrome" → Tìm cửa sổ chứa "Chrome"
- Nhập: "note" → Tìm "Notepad"
- Nhập: "game" → Tìm cửa sổ game

### Bước 3: Xác Nhận Cửa Sổ

```
Status bar cập nhật:
✅ Đã xác định: Chrome | Vị trí: (1920, 1000) | Kích thước: 1024x768

(Người dùng biết là đã chọn đúng cửa sổ)
```

### Bước 4: Popup Hướng Dẫn Capture

```
╔════════════════════════════════════════╗
║ 📍 Lấy Tọa Độ Tương Đối              ║
╠════════════════════════════════════════╣
║ 📋 Hướng Dẫn:                          ║
║                                        ║
║ 1️⃣ Di chuyển con chuột vào vị trí     ║
║    muốn lấy tọa độ                    ║
║                                        ║
║ 2️⃣ Bấm phím ENTER để lấy tọa độ       ║
║                                        ║
║ 3️⃣ Kết quả sẽ được tự động lưu vào   ║
║    danh sách kịch bản                 ║
║                                        ║
║ ⏳ Chờ... Di chuyển chuột và bấm ENTER║
╚════════════════════════════════════════╝
```

### Bước 5: Di Chuyển Chuột + Bấm ENTER

```
- Đưa chuột vào game window
- Di chuyển đến vị trí muốn lấy tọa độ
- Bấm ENTER trên bàn phím
- Popup tự động đóng
```

### Bước 6: Tự Động Mở Dialog Cấu Hình

```
┌──────────────────────────────────────────┐
│ ⚙️ Cài đặt tọa độ                       │
├──────────────────────────────────────────┤
│ 📍 Tọa độ X:        [450__________]      │ ← Đã filled!
│ 📍 Tọa độ Y:        [200__________]      │ ← Đã filled!
│ 📍 Số lần click:    [1____________]      │
│ 🖱️ Loại click:      ◉ single ○ double   │
│ ⏱️ Delay sau click:  [0.5_________]      │
│                                          │
│        [OK]  [Cancel]                   │
└──────────────────────────────────────────┘
```

**Đặc điểm:**
- X, Y đã được điền từ tọa độ vừa lấy
- Người dùng có thể điều chỉnh các thông số khác
- Có thể thay đổi click_type (single/double/hold)
- Có thể điều chỉnh delay

### Bước 7: Cài Đặt Tham Số (Optional)

```
Ví dụ các cài đặt:

Tọa độ X: 450 (từ capture)
Tọa độ Y: 200 (từ capture)
Số lần click: 1
Loại click: single (click thường)
Delay sau click: 0.5 giây

Hoặc có thể cài đặt:
- Số lần click: 2 (click 2 lần)
- Loại click: double (click đôi)
- Delay: 1.0 (chờ 1 giây sau click)
```

### Bước 8: Bấm OK

```
Dialog đóng → Tự động thêm vào kịch bản
```

### Bước 9: Xem Kết Quả

```
Status bar cập nhật:
✅ Đã thêm: Tọa độ (450, 200) | Click: single | Delay: 0.5s

Bảng kịch bản (phải):
┌─────────────────────────────────────────────┐
│ 📍 (450, 200) [56.3%, 33.3%] (single, 0.5s)│ ← Vừa thêm!
│ (có thể edit, xóa, di chuyển)              │
└─────────────────────────────────────────────┘
```

---

## 📊 Thông Tin Hiển Thị Trong Bảng

### Một Hàng Action:

```
📍 (450, 200) [56.3%, 33.3%] (single, 0.5s)
```

**Ý Nghĩa:**
- `📍` = Loại action là tọa độ
- `(450, 200)` = Tọa độ pixel
- `[56.3%, 33.3%]` = Tọa độ phần trăm
- `(single, 0.5s)` = Loại click + delay

---

## 🎮 Ví Dụ Thực Tế

### Ví Dụ 1: Lấy Tọa Độ Nút "Bắt Đầu"

```
Bước 1: Bấm "📍 Lấy Tọa Độ Tương Đối"

Bước 2: Nhập tên cửa sổ: "Chrome"
        ✅ Xác định: Chrome

Bước 3: Popup hướng dẫn → Di chuyển chuột vào nút "Bắt Đầu" → ENTER
        Popup đóng

Bước 4: Dialog cấu hình mở:
        X: 450
        Y: 200
        Số lần: 1
        Click: single
        Delay: 0.5s
        → Bấm OK

Bước 5: Bảng kịch bản tự động cập nhật:
        📍 (450, 200) [56.3%, 33.3%] (single, 0.5s)
```

### Ví Dụ 2: Lấy Tọa Độ Với Click Đôi + Delay Lâu

```
Bước 1: Bấm nút → Chọn cửa sổ → Lấy tọa độ: (300, 250)

Bước 2: Dialog cấu hình mở:
        X: 300
        Y: 250
        Số lần: 1
        Click: ◉ double (chọn double)
        Delay: 1.5 (sửa từ 0.5)
        → Bấm OK

Bước 3: Bảng hiển thị:
        📍 (300, 250) [37.5%, 41.7%] (double, 1.5s)
```

### Ví Dụ 3: Lấy Nhiều Tọa Độ Liên Tiếp

```
Lần 1: Lấy nút "Bắt Đầu" → (500, 300) → (single, 0.5s)
Lần 2: Lấy NPC "NPC A" → (300, 250) → (single, 0.5s)
Lần 3: Lấy nút "Thu Phí" → (600, 150) → (double, 1.0s)

Bảng kịch bản cuối cùng:
📍 (500, 300) [62.5%, 50.0%] (single, 0.5s)
📍 (300, 250) [37.5%, 41.7%] (single, 0.5s)
📍 (600, 150) [75.0%, 25.0%] (double, 1.0s)

Bấm "⚡ TUNG POKÉBALL!" → Bot sẽ:
1. Click (500, 300) once
2. Chờ 0.5s
3. Click (300, 250) once
4. Chờ 0.5s
5. Click (600, 150) twice
6. Chờ 1.0s
```

---

## 🔧 Tương Tác Với Bảng Kịch Bản

### Edit Action

```
1. Click chọn hàng:
   📍 (450, 200) [56.3%, 33.3%] (single, 0.5s)

2. Bấm nút "✏️ Sửa"

3. Dialog edit xuất hiện
   (Có thể sửa X, Y, click_type, delay, v.v...)

4. Bấm OK → Lưu thay đổi
```

### Xóa Action

```
1. Click chọn hàng
2. Bấm nút "🗑️ Xóa"
3. Action bị xóa
```

### Di Chuyển Thứ Tự

```
1. Click chọn hàng
2. Bấm "▲ Lên" hoặc "▼ Xuống"
3. Thứ tự action thay đổi
```

---

## ⚙️ Cấu Hình Chi Tiết

### Tọa Độ X, Y
```
Tự động filled từ lần capture
Có thể sửa lại nếu cần
```

### Số Lần Click
```
1 = Click 1 lần (mặc định)
2 = Click 2 lần
N = Click N lần
```

### Loại Click
```
◉ single (Click 1 lần - mặc định)
○ double (Click 2 lần nhanh)
○ hold   (Giữ chuột)
```

### Delay Sau Click
```
0.5 = Chờ 0.5 giây sau click (mặc định)
1.0 = Chờ 1.0 giây
2.0 = Chờ 2.0 giây
```

---

## 💡 Tips

### Tip 1: Lấy Tọa Độ Chính Xác
```
- Chọn cửa sổ game trước
- Di chuyển chuột vào **tâm** đối tượng
- Bấm ENTER khi ở vị trí chính xác
```

### Tip 2: Cài Đặt Delay Phù Hợp
```
Nút bình thường: 0.5s
Hành động phức tạp: 1.0-2.0s
Click liên tiếp: 0.2-0.3s
```

### Tip 3: Sử Dụng Click Đôi Khi Cần
```
Double click: Mở file, bật tính năng
Single click: Thông thường (mặc định)
Hold: Kéo, giữ đối tượng
```

### Tip 4: Test Trước
```
1. Lấy tọa độ
2. Cấu hình
3. Bấm "⚡ TUNG POKÉBALL!" để test 1 lần
4. Xác nhận click đúng vị trí
5. Nếu sai → Edit lại
```

---

## ✅ Checklist

- [ ] Cài đặt pyautogui + pywin32
- [ ] Game window đang mở
- [ ] Bấm nút capture
- [ ] Nhập tên cửa sổ game
- [ ] Đợi xác nhận cửa sổ
- [ ] Di chuyển chuột vào vị trí
- [ ] Bấm ENTER
- [ ] Dialog cấu hình mở với X, Y đã filled
- [ ] Cài đặt các thông số (click_type, delay, v.v...)
- [ ] Bấm OK
- [ ] Xem trong bảng kịch bản
- [ ] Có thể edit/xóa nếu cần

---

## 🎉 Status: Hoàn Thành

- [x] Chọn cửa sổ game
- [x] Lấy tọa độ tương đối
- [x] Tự động mở dialog cấu hình
- [x] X, Y đã filled
- [x] Cài đặt thông số linh hoạt
- [x] Tự động thêm vào kịch bản
- [x] Hiển thị chi tiết trong bảng

**Sẵn sàng sử dụng!** ✨

---

**Hướng Dẫn Lấy Tọa Độ + Cấu Hình - Version 3.0**
