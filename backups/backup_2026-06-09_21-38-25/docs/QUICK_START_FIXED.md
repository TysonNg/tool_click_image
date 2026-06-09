# 🚀 Hướng Dẫn Nhanh - Khắc Phục Lỗi Window Handle

## ⚡ Vấn Đề & Giải Pháp

### ❌ Lỗi Gốc:
```
Window handle 1051690 is no longer valid, clearing...
🖱️ Double-clicked coordinate (512,451)
đã nhập cửa sổ đích r vẫn ko chạy được?
```

### ✅ Nguyên Nhân:
Cửa sổ game bị **mất, tối thiểu hóa, ẩn, hoặc bị đóng** trong khi script đang chạy

### ✅ Giải Pháp:
Hệ thống đã được cập nhật với **WindowGuard** - tự động khôi phục & bảo vệ cửa sổ!

---

## 📋 Các Bước Để Chạy Thành Công

### 1️⃣ Chuẩn Bị Game

```
1. Mở game MapleStory (hoặc game khác)
2. Đảm bảo cửa sổ KHÔNG bị minimize
3. Đặt cửa sổ game ở nơi bạn có thể nhìn thấy
```

### 2️⃣ Xác Định Cửa Sổ Đích

```
1. Mở ứng dụng PokéClick PRO
2. Bấm nút: "🎯 Xác Định Cửa Sổ Đích"
3. Nhập tên game: "MapleStory" (hoặc tên khác)
4. Bấm OK
```

**Kết quả dự kiến:**
```
✅ Đã xác định cửa sổ đích: MapleStory | Kích thước: 1024x768
✅ Window validated and protected successfully
```

### 3️⃣ Thêm Hành Động

Chọn một trong các tùy chọn:

```
🖼️ Thêm Pokémon mục tiêu (Ảnh)
   → Chụp ảnh chiến pháp/NPC bạn muốn tấn công

📍 Thêm tọa độ chiến trường (XY)
   → Thêm tọa độ click tĩnh (ví dụ: 512, 300)

📍 Lấy Tọa Độ Tương Đối (Relative)
   → Capture tọa độ theo cửa sổ (khác với tuyệt đối)

⌨️ Thêm phím bàn phím
   → Bấm phím tự động (ví dụ: phím tấn công)
```

### 4️⃣ Kiểm Tra Trước Khi Chạy

```
✅ Cửa sổ game đang mở
✅ Cửa sổ game KHÔNG bị minimize (không ở taskbar)
✅ Cửa sổ game KHÔNG bị ẩn
✅ Status bar hiển thị: "✅ Đã xác định cửa sổ đích: [Tên Game]"
✅ Đã thêm ít nhất 1 hành động
```

### 5️⃣ Chạy Script!

```
Bấm: "⚡ TUNG POKÉBALL!"

Hệ thống sẽ:
1. Kiểm tra cửa sổ còn hợp lệ
2. Khôi phục nếu bị minimize
3. Đưa lên foreground
4. Thực hiện các hành động
5. Giữ cửa sổ active trong quá trình chạy
```

---

## 🛡️ Tính Năng Bảo Vệ Cửa Sổ Mới

### ✨ Tự Động Xảy Ra:

```
✅ PRE-FLIGHT CHECK
   → Kiểm tra cửa sổ trước khi bắt đầu
   → Cảnh báo nếu có vấn đề

✅ AUTO-RESTORE
   → Nếu cửa sổ bị minimize → tự động hiển thị
   → Nếu cửa sổ bị ẩn → tự động show
   
✅ CONTINUOUS MONITORING
   → Kiểm tra cửa sổ sau mỗi hành động
   → Tự động đưa lên foreground
   → Dừng script nếu cửa sổ mất
   
✅ SMART WARNINGS
   → Thông báo chi tiết nếu có vấn đề
   → Cho phép chọn "tiếp tục" hoặc "chọn lại"
```

---

## 🎯 Ví Dụ Thực Tế

### Tình Huống 1: Minimize Ngoài Ý Muốn

```
❌ CÓ: Đang chạy script, bạn vô tình bấm nút minimize
❌ CÓ: Script dừng lại, lỗi "Window handle invalid"

✅ SAU CẬP NHẬT: 
   ✅ Hệ thống tự động detect
   ✅ Tự động hiển thị cửa sổ
   ✅ Tiếp tục chạy script!
```

### Tình Huống 2: Alt-Tab

```
❌ CÓ: Đang chạy script, bạn alt-tab sang app khác
❌ CÓ: Script dừng lại, lỗi "Window handle invalid"

✅ SAU CẬP NHẬT:
   ✅ Hệ thống detect cửa sổ mất
   ✅ Tự động đưa game lên foreground
   ✅ Tiếp tục chạy script!
```

### Tình Huống 3: Cửa Sổ Bị Đóng

```
❌ CÓ: Bạn đóng cửa sổ game khi script chạy
❌ CÓ: Script dừng lại, lỗi "Window handle invalid"

✅ SAU CẬP NHẬT:
   ✅ Hệ thống detect cửa sổ mất
   ✅ Dừng script ngay lập tức (an toàn)
   ✅ Thông báo rõ ràng: "Cửa sổ game đã bị đóng"
   ✅ Cho phép mở game lại và bắt đầu lại
```

---

## 🔍 Kiểm Tra Logs

### Khi Chạy Thành Công:

```
🟢 [THREAD] find_and_click thread started
✅ Window validated and protected successfully
🔧 [WINDOW_GUARD] Window is healthy
✅ Best match for pokemon_target.png => pokemon_target.png (score: 0.87)
🖱️ Clicked pokemon_target.png at: (512, 451)
✅ AutoClick đã hoàn tất!
```

### Khi Có Cảnh Báo:

```
⚠️ Target window is minimized

Bạn có muốn:
- 'Có' để tiếp tục và tự động khôi phục cửa sổ
- 'Không' để chọn cửa sổ khác

[Bấm 'Có']

🔧 [WINDOW_GUARD] Restoring minimized window...
✅ Window restored and brought to foreground
⚡ Proceeding with script execution...
```

### Khi Có Lỗi:

```
❌ FATAL: Window handle became invalid during execution!
   The game window was closed, minimized, or lost focus

❌ Cửa sổ đích bị mất trong quá trình chạy

[Giải pháp:]
1. Mở lại game
2. Bấm "🎯 Xác Định Cửa Sổ Đích"
3. Chọn cửa sổ game
4. Bấm "⚡ TUNG POKÉBALL!" lần nữa
```

---

## 🆘 Troubleshooting

### ❓ Script vẫn không chạy?

```
1️⃣ Kiểm tra: Cửa sổ game có ở foreground không?
2️⃣ Kiểm tra: Có thông báo lỗi nào không?
3️⃣ Thử: Bấm "🎯 Xác Định Cửa Sổ Đích" lần nữa
4️⃣ Thử: Bấm "❌ Xóa Giới hạn" nếu bạn đã đặt vùng tìm kiếm
5️⃣ Thử: Khởi động lại ứng dụng
```

### ❓ Cửa sổ bị minimize liên tục?

```
1️⃣ Kiểm tra: Có app khác tự động activate không?
2️⃣ Tắt: Các app không cần thiết
3️⃣ Đặt: Cửa sổ game ở nơi an toàn (không bị click)
4️⃣ Khóa: Không bấm Alt-Tab trong khi script chạy
```

### ❓ Tọa độ click sai?

```
1️⃣ Kiểm tra: Kích thước cửa sổ thay đổi sau khi xác định?
   → Nếu có, bấm "🎯 Xác Định Cửa Sổ Đích" lần nữa

2️⃣ Thử: Sử dụng "📍 Lấy Tọa Độ Tương Đối" thay vì tuyệt đối
   → Tọa độ tương đối thích ứng với vị trí cửa sổ

3️⃣ Thử: Tăng threshold matching (nếu ảnh khó nhận diện)
   → Chỉnh độ nhạy trong "🔄 Số trận đấu"
```

---

## 📊 Status Indicators

### 🟢 Tất Cả Tốt:
```
✅ Đã xác định cửa sổ đích: MapleStory | Kích thước: 1024x768
```

### 🟡 Cảnh Báo:
```
⚠️ Target window is minimized
⚠️ Không tìm được pokemon.png (waiting...)
```

### 🔴 Lỗi:
```
❌ Cửa sổ đích không còn hợp lệ
❌ Cửa sổ đích bị mất trong quá trình chạy
```

---

## 🎓 Tìm Hiểu Thêm

### 📖 Tài Liệu Chi Tiết:
- `WINDOW_HANDLE_FIX.md` - Giải thích chi tiết về lỗi và cách khắc phục
- `AUTOCLICK_CHEATSHEET.md` - Bảng ghi nhanh tất cả tính năng
- `AUTOCLICK_PRO_COMPLETE.md` - Hướng dẫn đầy đủ

### 🧪 Kiểm Tra Hệ Thống:
```
Chạy: python TEST_WINDOW_GUARD.py

Kết quả:
✅ ALL TESTS PASSED!
Window Guard is working correctly!
```

---

## ✨ Recap - 5 Bước Đơn Giản

```
1. 🎮 Mở game (không minimize)
2. 🎯 Bấm "🎯 Xác Định Cửa Sổ Đích" → Nhập tên game
3. ➕ Thêm ảnh/tọa độ/phím
4. ✅ Kiểm tra: Status bar xanh, không minimize
5. ⚡ Bấm "⚡ TUNG POKÉBALL!" → Xong!
```

**Hệ thống sẽ tự động:**
- ✅ Bảo vệ cửa sổ
- ✅ Khôi phục nếu cần
- ✅ Dừng an toàn nếu cửa sổ mất

---

🎉 **Bây giờ bạn đã sẵn sàng!** Hãy chạy thử xem! 🚀
