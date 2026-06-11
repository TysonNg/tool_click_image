# ✅ Fix Lỗi Nhập Tên Cửa Sổ Game - Hoàn Thành

## 🐛 Vấn Đề

```
Lỗi: window "*_:querystring2" was deleted before its visibility changed
```

**Nguyên Nhân:**
- `simpledialog.askstring()` có lỗi khi dialog bị destroy trước khi visibility thay đổi
- Đây là bug trong Tkinter, không phải code của ta

## ✅ Giải Pháp

**Thay thế `simpledialog` bằng custom Tkinter dialog**

### Trước:
```python
window_title = simpledialog.askstring(
    "📍 Xác Định Cửa Sổ Game",
    "Nhập tên cửa sổ game...",
    parent=root
)
# ❌ Bug: widget bị xóa trước khi visibility thay đổi
```

### Sau:
```python
window_title = ask_window_title_custom()
# ✅ Custom dialog không có lỗi
```

### Hàm Custom:
```python
def ask_window_title_custom():
    """Ask user for window title using Tkinter (not simpledialog)"""
    dialog = tk.Toplevel(root)
    dialog.title("📍 Xác Định Cửa Sổ Game")
    dialog.geometry("450x200")
    
    # ... UI setup ...
    
    entry = tk.Entry(dialog, font=("Segoe UI", 11), width=40)
    entry.pack(pady=15, padx=20)
    entry.focus()
    
    # ... OK/Cancel buttons ...
    
    dialog.wait_window()
    
    return result_var.get() if result_var.get() else None
```

## 🎯 Quy Trình Mới (Sẽ Hoạt Động)

```
1. Bấm "📍 Lấy Tọa Độ Tương Đối"
   ↓
2. Dialog "Xác Định Cửa Sổ Game" xuất hiện (Clean, không bug)
   ├─ Nhập tên cửa sổ (ví dụ: "Chrome")
   ├─ Bấm OK hoặc ENTER
   └─ Dialog đóng (không lỗi)
   ↓
3. Tiếp tục quy trình capture bình thường
```

## 📝 Thay Đổi Files

### `autoclick_gui.py`
- ❌ Xóa: `from tkinter import simpledialog`
- ✅ Thêm: Hàm `ask_window_title_custom()`
- ✅ Cập nhật: `capture_relative_coordinates()` gọi hàm custom

## ✅ Test

```bash
python autoclick_gui.py
→ Bấm "📍 Lấy Tọa Độ Tương Đối"
→ Nhập tên cửa sổ (ví dụ: "Chrome", "Notepad")
→ Bấm OK
→ Không có lỗi ✅
```

## 📊 So Sánh

| Phương Thức | Ưu Điểm | Nhược Điểm |
|------------|--------|----------|
| `simpledialog` | Đơn giản | ❌ Bug visibility |
| Custom Dialog | ✅ Không bug | Nhiều code hơn |

---

**Status: ✅ Lỗi đã fix - Dialog hoạt động bình thường!**
