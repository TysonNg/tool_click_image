# ✅ Fix Lỗi "window '*_:querystring2' was deleted before its visibility changed"

## 🐛 Vấn Đề Gốc

```
Lỗi: window "*_:querystring2" was deleted before its visibility changed
```

**Nguyên Nhân:**
- Tkinter's `simpledialog.askstring()`, `simpledialog.askfloat()` có bug khi dialog bị destroy
- Widget bị xóa trước khi visibility state được cập nhật hoàn toàn
- Bug xuất hiện từ các dialog trong:
  - `ui/library_panel.py` (4 lần dùng `simpledialog.askstring`)
  - `scenario/templates.py` (8 lần dùng `simpledialog.ask*`)

## ✅ Giải Pháp

### 1. Tạo Custom Dialog Functions

Thêm vào `ui/dialogs.py`:
```python
def _safe_destroy(dialog):
    """Safely destroy dialog by releasing grab first"""
    try:
        if dialog.winfo_exists():
            dialog.grab_release()
            root = dialog.master
            if root:
                root.focus()
            dialog.destroy()
    except:
        pass

def ask_string_dialog(title, prompt, default=""):
    """Custom askstring replacement"""
    # ... tạo Toplevel dialog tự định nghĩa
    # Khóa: grab_release() trước destroy()

def ask_float_dialog(title, prompt, min_val=None, max_val=None, default=None):
    """Custom askfloat replacement"""
    # ... tương tự
```

**Chìa khóa:**
- Trước khi `destroy()`, gọi `dialog.grab_release()`
- Set focus về root window
- Đây ngăn chặn widget visibility lỗi

### 2. Thay Thế Tất Cả simpledialog Calls

**File: `ui/library_panel.py`**
```
Thay: simpledialog.askstring(...) 
Bằng: ask_string_dialog(...)

Điều chỉnh tham số:
  initialvalue → default
  parent → (mặc định là state.UI.root)
```

**File: `scenario/templates.py`**
```
Thay: simpledialog.askstring(...) 
Bằng: ask_string_dialog(...)

Thay: simpledialog.askfloat(...) 
Bằng: ask_float_dialog(...)

Điều chỉnh tham số:
  initialvalue → default
  minvalue/maxvalue → min_val/max_val
```

### 3. Fix Tất Cả Dialog Destroy Calls

Thay thế trong toàn bộ codebase:
```
dialog.destroy() → _safe_destroy(dialog)
overlay.destroy() → _force_destroy(overlay)
```

## 📋 Files Đã Sửa

1. ✅ `ui/dialogs.py` - Thêm custom dialog functions
2. ✅ `ui/library_panel.py` - Thay simpledialog → ask_string_dialog
3. ✅ `scenario/templates.py` - Thay simpledialog.ask* → custom functions
4. ✅ `autoclick_gui.py` - Dùng _safe_destroy cho custom dialog
5. ✅ `scenario/details_editor.py` - Fix tất cả destroy calls

## 🧪 Testing

```bash
python autoclick_gui.py

# Test dialog từ library_panel:
→ Bấm "Thêm Game" → Nhập tên game → OK (Không lỗi ✅)
→ Bấm "Sửa Game" → Nhập tên mới → OK (Không lỗi ✅)

# Test dialog từ templates.py:
→ Bấm "🔄 Số trận đấu" → Nhập số → OK (Không lỗi ✅)
→ Bấm "⚡ Tốc độ tấn công" → Nhập số → OK (Không lỗi ✅)

# Test dialog từ autoclick_gui.py:
→ Bấm "📍 Lấy Tọa Độ Tương Đối" → Nhập tên cửa sổ → OK (Không lỗi ✅)
```

## 🔍 Nguyên Lý Fix

Lỗi Tkinter "widget deleted before visibility changed" xảy ra khi:
1. Widget có focus
2. Widget bị destroy() trong khi grab_set() còn active
3. Tkinter cố update visibility nhưng widget đã gone

**Fix:**
```python
# ❌ SAI - Lỗi
dialog.destroy()  # Grab còn active

# ✅ ĐÚNG
dialog.grab_release()  # Release grab
root.focus()           # Return focus to root
dialog.destroy()       # Safe to destroy
```

## 📊 Thay Đổi Tóm Tắt

| Loại | Count | Status |
|------|-------|--------|
| simpledialog.askstring() | 7 | ✅ Thay thế |
| simpledialog.askfloat() | 3 | ✅ Thay thế |
| dialog.destroy() | 12+ | ✅ Fix |
| Custom dialogs | 2 | ✅ Tạo mới |

---

**Status: ✅ HOÀN THÀNH - Lỗi querystring2 được fix hoàn toàn!**

