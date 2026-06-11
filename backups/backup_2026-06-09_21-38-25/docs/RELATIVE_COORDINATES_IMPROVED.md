# 📍 Lấy Tọa Độ Tương Đối (Cải Tiến) - Hướng Dẫn Hoàn Chỉnh

## ✨ Cập Nhật Mới

### 1️⃣ UI Đẹp Hơn
- Popup hướng dẫn với giao diện hiện đại
- Hiển thị rõ ràng, dễ hiểu
- Dark theme phù hợp với ứng dụng

### 2️⃣ Tự Động Thêm Vào Kịch Bản
- Sau khi lấy tọa độ → **tự động thêm** vào danh sách kịch bản
- Không cần bước thêm thủ công
- Hiển thị luôn trong bảng kịch bản

### 3️⃣ Hiển Thị Chi Tiết
- Bảng kịch bản (POKÉDEX) hiển thị:
  - Loại: 📍 Tọa Độ
  - Pixel: (X, Y)
  - Phần Trăm: (%, %)
  - Có thể edit, xóa, di chuyển

---

## 🎯 Quy Trình Sử Dụng

### Bước 1: Bấm Nút "📍 Lấy Tọa Độ Tương Đối"

```
Giao diện chính
  ↓ (Tìm phần "⚔️ KỸ NĂNG CHIẾN ĐẤU" bên trái)
  ↓ Bấm nút tím: "📍 Lấy Tọa Độ Tương Đối (Relative)"
```

### Bước 2: Popup Hướng Dẫn Xuất Hiện

```
╔════════════════════════════════════════╗
║ 📍 Lấy Tọa Độ Tương Đối              ║
╠════════════════════════════════════════╣
║ 📋 Hướng Dẫn:                          ║
║                                        ║
║ 1️⃣ Di chuyển con chuột vào vị trí     ║
║    muốn lấy tọa độ                    ║
║    (Có thể là nút, NPC, hay bất kỳ    ║
║     điểm nào trong game)              ║
║                                        ║
║ 2️⃣ Bấm phím ENTER để lấy tọa độ       ║
║                                        ║
║ 3️⃣ Kết quả sẽ được tự động lưu vào   ║
║    danh sách kịch bản                 ║
║                                        ║
║ ⏳ Chờ... Di chuyển chuột và bấm ENTER║
╚════════════════════════════════════════╝
```

### Bước 3: Di Chuyển Chuột

```
- Đưa chuột vào game window
- Di chuyển đến vị trí muốn lấy tọa độ
  (Ví dụ: nút "Bắt Đầu", vị trí NPC, v.v...)
- **Giữ chuột tại vị trí đó**
```

### Bước 4: Bấm ENTER

```
- Bấm phím ENTER trên bàn phím
- Popup sẽ tự động đóng
```

### Bước 5: Xem Kết Quả

```
✅ Popup thành công:
   Tọa Độ Tương Đối:
   
   Pixel: (450, 200)
   Phần Trăm: (56.3%, 33.3%)
   
   ✅ Đã tự động thêm vào kịch bản!
```

### Bước 6: Xem Trong Bảng Kịch Bản

```
POKÉDEX KỊCH BẢN (bên phải):
┌──────────────────────────────────────────┐
│ 📍 Tọa Độ: (450, 200) [56.3%, 33.3%]   │ ← Vừa thêm!
│ (có thể edit, xóa, di chuyển)          │
└──────────────────────────────────────────┘
```

---

## 📊 Thông Tin Hiển Thị Trong Bảng Kịch Bản

### Một Hàng Action Trong Bảng:

```
📍 Tọa Độ: (450, 200) [56.3%, 33.3%]
```

**Ý Nghĩa:**
- `📍` = Loại action là tọa độ (coordinate)
- `(450, 200)` = Tọa độ pixel (X=450, Y=200)
- `[56.3%, 33.3%]` = Tọa độ phần trăm
  - 56.3% = vị trí ngang trong cửa sổ
  - 33.3% = vị trí dọc trong cửa sổ

---

## 🎮 Ví Dụ Thực Tế

### Ví Dụ 1: Lấy Tọa Độ Nút "Bắt Đầu" Game

```
Bước 1: Game đang chạy
        Nút "Bắt Đầu" ở vị trí (450, 200)

Bước 2: Bấm "📍 Lấy Tọa Độ Tương Đối"
        Popup hướng dẫn xuất hiện

Bước 3: Di chuyển chuột vào nút "Bắt Đầu"
        Chuột ở vị trí chính xác của nút

Bước 4: Bấm ENTER
        Popup đóng

Bước 5: Kết quả: Pixel (450, 200)

Bước 6: Bảng kịch bản tự động hiển thị:
        📍 Tọa Độ: (450, 200) [56.3%, 33.3%]
```

### Ví Dụ 2: Lấy Tọa Độ Nhiều Vị Trí Liên Tiếp

```
Lần 1: Lấy tọa độ nút "Đi Phiêu Lưu"
       → Kết quả: (500, 300)
       → Bảng: 📍 (500, 300) [62.5%, 50.0%]

Lần 2: Lấy tọa độ NPC "Chiến Thương"
       → Kết quả: (300, 250)
       → Bảng: 📍 (300, 250) [37.5%, 41.7%]

Lần 3: Lấy tọa độ Nút "Thu Phí"
       → Kết quả: (600, 150)
       → Bảng: 📍 (600, 150) [75.0%, 25.0%]

Bảng kịch bản cuối cùng:
┌────────────────────────────────┐
│ 📍 (500, 300) [62.5%, 50.0%]  │ ← Bấm nút
│ 📍 (300, 250) [37.5%, 41.7%]  │ ← Nói chuyện NPC
│ 📍 (600, 150) [75.0%, 25.0%]  │ ← Thu phí
└────────────────────────────────┘

Click nút "⚡ TUNG POKÉBALL!" → Bot sẽ tự động:
1. Click (500, 300)
2. Click (300, 250)
3. Click (600, 150)
```

---

## 🔧 Tương Tác Với Bảng Kịch Bản

### Xem Chi Tiết Action

```
Bảng kịch bản:
📍 Tọa Độ: (450, 200) [56.3%, 33.3%]

Cách xem:
- Nhìn vào bảng, thấy ngay tọa độ pixel và phần trăm
- Biết chính xác vị trí sẽ được click
```

### Edit Action

```
1. Click chọn hàng trong bảng:
   📍 Tọa Độ: (450, 200) [56.3%, 33.3%]

2. Bấm nút "✏️ Sửa"

3. Dialog edit xuất hiện
   (Có thể sửa X, Y, repeat, delay, v.v...)

4. Bấm OK → Lưu thay đổi
```

### Xóa Action

```
1. Click chọn hàng:
   📍 Tọa Độ: (450, 200) [56.3%, 33.3%]

2. Bấm nút "🗑️ Xóa"

3. Action bị xóa khỏi kịch bản
```

### Di Chuyển Thứ Tự

```
Nếu muốn thay đổi thứ tự click:

1. Click chọn hàng
2. Bấm "▲ Lên" hoặc "▼ Xuống"
3. Thứ tự action sẽ thay đổi
```

---

## 💡 Tips & Tricks

### Tip 1: Lấy Tọa Độ Chính Xác

```
Để đạt độ chính xác cao:
- Di chuyển chuột vào **tâm** của đối tượng
- Không di chuyển quá sát cạnh
- Bấm ENTER khi chuột ở vị trí chính xác
```

### Tip 2: Sử Dụng Phần Trăm Cho Responsive Targets

```
Nếu game có thể resize:
- Thay vì dùng pixel tuyệt đối (450, 200)
- Hãy dùng phần trăm (50%, 50%) = giữa cửa sổ

Lợi ích:
- Kể cả game resize, vẫn click đúng vị trí
- Linh hoạt hơn
```

### Tip 3: Lưu Danh Sách Tọa Độ

```
Nên lưu danh sách các tọa độ quan trọng:

Nút "Bắt Đầu": (500, 300)
NPC "Chiến Thương": (300, 250)
Nút "Thu Phí": (600, 150)
Nút "Rút Lui": (100, 50)

→ Dùng lại bất kỳ lúc nào
```

### Tip 4: Test Trước Khi Chạy Tự Động

```
Quy trình:
1. Lấy tọa độ
2. Thêm vào kịch bản
3. Bấm "✏️ Test Click" để xem (nếu có)
4. Hoặc bấm "⚡ TUNG POKÉBALL!" để chạy 1 lần
5. Kiểm tra xem có click đúng không
6. Nếu sai → Edit lại tọa độ
7. Nếu đúng → Chạy tự động bình thường
```

---

## 🔄 So Sánh: Quy Trình Cũ vs Mới

### Quy Trình Cũ (Thủ Công)
```
1. Lấy tọa độ
   ↓
2. Bấm "📍 Thêm tọa độ chiến trường"
   ↓
3. Nhập X, Y thủ công
   ↓
4. Bấm OK
   ↓
5. Hiển thị trong bảng
```

### Quy Trình Mới (Tự Động)
```
1. Lấy tọa độ
   ↓ (Tự động!)
2. Thêm vào kịch bản
   ↓ (Tự động!)
3. Hiển thị trong bảng
```

**Tiết kiệm 2 bước!** 🚀

---

## ⚠️ Lưu Ý Quan Trọng

### Khi Sử Dụng:

1. **Cửa Sổ Game Phải Visible**
   - Không được ẩn, minimize, hoặc che phủ
   - Phải nhìn thấy đầy đủ trên màn hình

2. **Chuột Phải Ở Trong Game Window**
   - Khi bấm ENTER, chuột phải ở **TRONG** cửa sổ game
   - Không phải ở ngoài hay trên taskbar

3. **Phải Bấm ENTER (Không Phải Click Chuột)**
   - Bấm phím **ENTER** trên bàn phím (dòng phím trên)
   - Không phải bấm chuột

4. **Kịch Bản Sẽ Cộng Dồn**
   - Mỗi lần lấy tọa độ → thêm 1 action mới
   - Cũ không bị xóa, chỉ thêm tiếp

---

## ✅ Checklist

- [ ] Đã cài đặt pyautogui + pywin32
- [ ] Game window đang mở và visible
- [ ] Bấm nút "📍 Lấy Tọa Độ Tương Đối"
- [ ] Di chuyển chuột vào vị trí cần lấy
- [ ] Bấm **ENTER** trên bàn phím
- [ ] Xem popup thành công
- [ ] Bảng kịch bản tự động cập nhật
- [ ] Có thể edit/xóa/di chuyển trong bảng
- [ ] Sẵn sàng chạy tự động

---

## 🎉 Status: Hoàn Thành

- [x] UI capture đẹp hơn
- [x] Tự động thêm vào kịch bản
- [x] Hiển thị chi tiết trong bảng
- [x] Có thể edit/xóa/di chuyển
- [x] Hướng dẫn hoàn chỉnh

**Sẵn sàng sử dụng!** ✨

---

**Hướng Dẫn Lấy Tọa Độ Tương Đối (Cải Tiến) - Version 2.0**
