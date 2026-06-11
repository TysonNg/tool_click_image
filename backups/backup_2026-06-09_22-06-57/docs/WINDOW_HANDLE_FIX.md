# 🪟 Khắc Phục Lỗi Window Handle Invalid

**Vấn đề:** "Window handle 1051690 is no longer valid"

## 🔍 Nguyên Nhân

Lỗi này xảy ra khi:
1. **Cửa sổ game bị đóng** (closed)
2. **Cửa sổ bị tối thiểu hóa** (minimized)
3. **Cửa sổ bị ẩn** (hidden)
4. **Alt-Tab ra khỏi cửa sổ** game
5. **Cửa sổ bị thay đổi** hoặc mất focus

## ✅ Các Cải Tiến Đã Thực Hiện

### 1. **WindowGuard Module** (`core/window_guard.py`)
Tạo module riêng để quản lý cửa sổ:
- `validate_window()` - Kiểm tra handle còn hợp lệ
- `protect_window()` - Khôi phục cửa sổ nếu tối thiểu hóa/ẩn
- `bring_to_foreground_safe()` - Đưa cửa sổ lên foreground an toàn
- `check_and_warn()` - Cảnh báo tình trạng cửa sổ

### 2. **Runner.py Enhancements** 
Cập nhật `find_and_click()`:
- ✅ Xác thực cửa sổ **trước khi bắt đầu**
- ✅ Khôi phục cửa sổ nếu cần
- ✅ Kiểm tra **trong mỗi vòng lặp template**
- ✅ Tự động bảo vệ cửa sổ giữa các click
- ✅ Thông báo chi tiết khi cửa sổ mất

### 3. **Smart Start Pre-flight Checks**
`smart_start()` giờ:
- Kiểm tra cửa sổ được xác định
- Cảnh báo nếu cửa sổ có vấn đề
- Cho phép người dùng chọn "tiếp tục & khôi phục" hoặc "chọn cửa sổ khác"
- Tự động khôi phục trước khi chạy

### 4. **Relative Coordinate Capture Fixes**
- Xóa duplicate decorator
- Thêm xác thực handle trong `get_game_window_info()`

## 🛠️ Cách Sử Dụng

### Khi Bắt Đầu Chạy Script:

```
1. Bấm "🎯 Xác Định Cửa Sổ Đích" để chọn game
2. Thêm ảnh/tọa độ mong muốn
3. Bấm "⚡ TUNG POKÉBALL!" để bắt đầu
```

**Hệ thống sẽ tự động:**
- ✅ Kiểm tra cửa sổ còn hợp lệ
- ✅ Khôi phục nếu bị minimize
- ✅ Đưa cửa sổ lên foreground
- ✅ Giữ cửa sổ hoạt động trong quá trình chạy

### Nếu Gặp Cảnh Báo:

```
⚠️ Target window is minimized

Bạn có muốn:
- 'Có' để tiếp tục và tự động khôi phục cửa sổ
- 'Không' để chọn cửa sổ khác
```

**Chọn "Có"** → Hệ thống sẽ khôi phục và tiếp tục

## 📋 Best Practices

### ✅ LÀM ĐIỀU NÀY:
1. **Giữ cửa sổ game trong tầm nhìn** trước khi bắt đầu
2. **Đừng minimize/hide cửa sổ** trong quá trình chạy
3. **Đừng Alt-Tab** ra khỏi game
4. **Để game ở foreground** (không click cửa sổ khác)
5. **Xác định cửa sổ lại** nếu game bị khởi động lại

### ❌ TRÁNH ĐIỀU NÀY:
- ❌ Minimize cửa sổ game khi script đang chạy
- ❌ Alt-Tab sang ứng dụng khác
- ❌ Đóng cửa sổ game
- ❌ Thay đổi kích thước cửa sổ (lớn/nhỏ)
- ❌ Khởi động lại game trong khi script chạy

## 🔧 Troubleshooting

### Lỗi: "Window handle is no longer valid"

**Giải Pháp:**
```
1. Bấm "❌ Xóa" hoặc chọn cửa sổ mới với "🎯 Xác Định Cửa Sổ Đích"
2. Đảm bảo cửa sổ game không bị minimize/ẩn
3. Bấm "⚡ TUNG POKÉBALL!" để chạy lại
```

### Lỗi: "Target window is minimized"

**Giải Pháp Tự Động:**
```
Hệ thống sẽ tự động hiển thị:
1. Cửa sổ sẽ được khôi phục
2. Cửa sổ sẽ được đưa lên foreground
3. Script sẽ tiếp tục chạy
```

**Hoặc chủ động:**
```
1. Nhấp vào game window để làm nó active
2. Bấm "⚡ TUNG POKÉBALL!" để chạy lại
```

### Lỗi: "Window was closed"

**Giải Pháp:**
```
1. Mở lại game
2. Bấm "🎯 Xác Định Cửa Sổ Đích"
3. Chọn cửa sổ game mới
4. Bấm "⚡ TUNG POKÉBALL!" để chạy
```

## 📊 Log Messages

### ✅ Thành Công:
```
✅ Window validated and protected successfully
🔧 [WINDOW_GUARD] Restoring minimized window...
✅ Final click point: (512, 451)
```

### ⚠️ Cảnh Báo:
```
⚠️ Target window is minimized
⚠️ Target window is hidden
⚠️ No target window set
```

### ❌ Lỗi:
```
❌ FATAL: Window handle became invalid during execution!
❌ Window no longer valid, clearing...
❌ Cửa sổ đích bị mất trong quá trình chạy
```

## 🎯 Kiểm Tra Trước Khi Chạy

Trước khi bấm "⚡ TUNG POKÉBALL!":

```
□ Cửa sổ game đang mở
□ Cửa sổ game không bị minimize
□ Cửa sổ game không bị ẩn
□ Game không bị minimize
□ Màn hình ứng dụng đang hiển thị game
□ Status bar hiển thị: "✅ Đã xác định cửa sổ đích: [Tên Game]"
```

Nếu tất cả những điều trên ✅, bạn đã sẵn sàng!

## 📝 Changelog

**v2.0 - Window Guard System:**
- ✅ Tạo WindowGuard module
- ✅ Thêm pre-flight checks
- ✅ Tự động khôi phục cửa sổ
- ✅ Kiểm tra cửa sổ trong vòng lặp
- ✅ Thông báo lỗi chi tiết

**v1.0 - Cơ bản:**
- Window handle validation
- Error messages

---

**Để được hỗ trợ:** Kiểm tra logs hoặc thực hiện các bước troubleshooting ở trên! 🚀
