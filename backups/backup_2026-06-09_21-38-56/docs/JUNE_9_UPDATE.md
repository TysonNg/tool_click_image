# 🎯 AutoClick Bản Cập Nhật: June 9, 2026

## 📝 Tóm Tắt Cập Nhật

### 🔧 Vấn đề Được Giải Quyết
**"Window handle không hợp lệ" khi chạy kịch bản sau khi alt-tab hoặc tối thiểu hóa cửa sổ**

### ✅ Giải Pháp Được Triển Khai

#### 1. **Kiểm Tra Window Handle Trước Khi Bắt Đầu**
- Trước khi chạy kịch bản, hệ thống sẽ kiểm tra xem window handle còn hợp lệ không
- Nếu **không hợp lệ** → Báo lỗi rõ ràng và **dừng ngay**
- Thông báo: `❌ Cửa sổ đích không còn hợp lệ. Vui lòng chọn lại.`

#### 2. **Kiểm Tra Window Handle Trong Quá Trình Chạy**
- Sau mỗi bước (template) trong vòng lặp, kiểm tra window handle
- Nếu cửa sổ **bị đóng/tối thiểu hóa/mất focus** → Dừng ngay
- Thông báo: `❌ Cửa sổ đích bị mất trong quá trình chạy`

---

## 📋 Chi Tiết Kỹ Thuật

### Tệp Được Sửa
**`core/runner.py`**

### Các Thay Đổi

#### ✅ Thêm Import
```python
import win32gui  # Để kiểm tra tính hợp lệ của window handle
```

#### ✅ Kiểm Tra Tại Đầu `find_and_click()`
```python
def find_and_click(queue_mode=False):
    # ...
    try:
        # VALIDATE WINDOW BEFORE STARTING
        if state.game_hwnd:
            if not win32gui.IsWindow(state.game_hwnd):
                safe_print(f"❌ FATAL: Window handle không còn hợp lệ!")
                state.game_hwnd = None
                state.running = False
                # Báo lỗi giao diện
                if state.UI and state.UI.status_label:
                    state.UI.status_label.config(
                        text="❌ Cửa sổ đích không còn hợp lệ. Vui lòng chọn lại.",
                        fg="#ff3333"
                    )
                return "failed"
```

#### ✅ Kiểm Tra Trong Vòng Lặp Template
```python
for tpl_index, tpl in enumerate(state.templates):
    if not state.running:
        break
    
    # Check window is still valid
    if state.game_hwnd and not win32gui.IsWindow(state.game_hwnd):
        safe_print(f"❌ FATAL: Window handle bị mất!")
        state.game_hwnd = None
        state.running = False
        # Báo lỗi
        break
```

---

## 🎯 Cách Sử Dụng (Đúng Cách)

### ✅ Quy Trình Chuẩn

1. **Mở AutoClick**
   ```
   ✅ AutoClick Giao Diện chính
   ```

2. **Chọn Cửa Sổ Đích**
   ```
   ✅ Bấm "Chọn Cửa Sổ Đích"
   ✅ Chọn cửa sổ game
   ✅ Window sẽ được highlight (xanh dương)
   ```

3. **Chuẩn Bị Game**
   ```
   ✅ Mở game window
   ✅ Giữ game window ở trạng thái ACTIVE (đang có focus)
   ✅ Đừng alt-tab hoặc tối thiểu hóa
   ```

4. **Chạy Kịch Bản**
   ```
   ✅ Bấm "Chạy" 
   ✅ Chờ scenario hoàn tất (KHÔNG NHẤC MẮT)
   ✅ Hoàn tất → Thông báo ✅
   ```

### ❌ Sai Lầm Phổ Biến

| ❌ KHÔNG NÊN | ✅ NÊN |
|------------|------|
| Chọn cửa sổ → Alt-tab → Chạy | Chọn cửa sổ → Giữ focus → Chạy |
| Chọn cửa sổ → Tối thiểu hóa → Chạy | Chọn cửa sổ → Mở game → Chạy |
| Chạy trong khi alt-tab | Alt-tab SAU khi scenario kết thúc |
| Click đi click lại trong quá trình chạy | Để scenario chạy tự động |

---

## 🚨 Xử Lý Lỗi

### Nếu thấy: `❌ Cửa sổ đích không còn hợp lệ`

**Nguyên nhân Có Thể:**
- ❌ Game đã bị đóng
- ❌ Game đã bị tối thiểu hóa
- ❌ Bạn alt-tab sang ứng dụng khác
- ❌ Bạn mới bật lại máy

**Cách Khắc Phục:**
1. ✅ Mở game (hoặc khôi phục nếu tối thiểu hóa)
2. ✅ Bấm "Chọn Cửa Sổ Đích" lại
3. ✅ Giữ game active
4. ✅ Chạy lại

---

### Nếu thấy: `❌ Cửa sổ đích bị mất trong quá trình chạy`

**Nguyên nhân:**
- ❌ Bạn alt-tab TRONG khi scenario chạy
- ❌ Bạn tối thiểu hóa TRONG khi scenario chạy
- ❌ Bạn đóng game TRONG khi scenario chạy

**Cách Khắc Phục:**
1. ✅ Scenario sẽ **tự động dừng** (an toàn)
2. ✅ Bấm "Chọn Cửa Sổ Đích" lại
3. ✅ **ĐỢI** cho đến khi scenario hoàn tất lần này
4. ✅ Không alt-tab hoặc tối thiểu hóa
5. ✅ Chạy lại

---

## 💡 Mẹo & Lưu Ý

### 🎮 Khi Chạy Game Scenario
- **ĐỦ NHỎ ĐỂ NHÌN THẤY GAME**
  ```
  ✅ Để game window ở vị trí có thể nhìn thấy hoàn toàn
  ✅ Để AutoClick window ở một góc (tối thiểu hóa)
  ✅ Chuột sẽ tự động click trong game
  ```

- **KHÔNG BẤMVÁOCH trong khi scenario chạy**
  ```
  ✅ Để scenario chạy tự động
  ❌ KHÔNG SPAM CLICK trong game
  ❌ KHÔNG NHẤN PHÍM while running
  ```

- **NẾU CẦN DỪNG**
  ```
  ✅ Bấm "STOP" button trong AutoClick
  ✅ KHÔNG FORCE QUIT game
  ```

### 📝 Cách Tạo Scenario An Toàn
1. Mở game và chuẩn bị trạng thái
2. Chọn cửa sổ game với AutoClick
3. Bắt đầu capture coordinates
4. Lưu scenario
5. Test chạy với số vòng nhỏ (1-2 vòng)
6. Từ từ tăng số vòng khi chắc chắn

---

## 📊 Thay Đổi Hành Vi

### Trước (cũ)
```
❌ Window handle không hợp lệ (lặng lẽ)
→ Double-click (512,451)
→ Không xảy ra gì
→ Người dùng confused
```

### Sau (mới)
```
❌ Window handle không hợp lệ
→ [NGAY LẬP TỨC] Báo lỗi rõ ràng
→ Status: "❌ Cửa sổ đích không còn hợp lệ"
→ Scenario dừng
→ Người dùng biết là sao
```

---

## 📚 Tài Liệu Liên Quan
- `docs/WINDOW_HANDLE_FIX.md` - Chi tiết kỹ thuật
- `docs/QUICK_FIX_CHECKLIST.md` - Checklist nhanh

---

**Ngày Cập Nhật:** June 9, 2026  
**Phiên Bản:** 2.0.1  
**Trang Thái:** ✅ Production Ready
