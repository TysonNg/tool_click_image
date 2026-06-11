# ✅ Fix Lỗi Reset Thông Tin Khi Bấm Sửa

## 🐛 Vấn Đề

Khi bấm "✏️ Sửa" để chỉnh sửa một mục trong list:
```
1. Mục có thông tin: X=100, Y=200, Repeat=5, Delay=1.0s
2. Bấm "✏️ Sửa"
3. Dialog mở ra nhưng fields bị reset:
   - X: 0 (thay vì 100) ❌
   - Y: 0 (thay vì 200) ❌
   - Repeat: 1 (thay vì 5) ❌
   - Delay: 0.5s (thay vì 1.0s) ❌
```

**Nguyên Nhân:**
- Hàm `_edit_template_in_list()` gọi dialog mà **không pass giá trị cũ**
- Dialog fields được init với default value thay vì giá trị từ template

## ✅ Giải Pháp

### 1. Pass Giá Trị Cũ Khi Edit Coordinate

**File: `scenario/templates.py`** - Hàm `_edit_template_in_list()`

```python
# ❌ CŨ - Không pass giá trị
config = show_coordinate_config_dialog()

# ✅ MỚI - Pass giá trị cũ
config = show_coordinate_config_dialog(
    initial_x=tpl.get("x", 0),
    initial_y=tpl.get("y", 0)
)
```

### 2. Pass Giá Trị Cũ Khi Edit Keyboard

**File: `scenario/templates.py`** - Hàm `_edit_template_in_list()`

```python
# ❌ CŨ
config = show_keyboard_config_dialog()

# ✅ MỚI
config = show_keyboard_config_dialog(
    initial_key=tpl.get("key", "enter"),
    initial_repeat=tpl.get("repeat", 1),
    initial_key_type=tpl.get("key_type", "press"),
    initial_delay=tpl.get("delay_after", 0.5)
)
```

### 3. Update Dialog Signature Để Nhận Initial Values

**File: `ui/dialogs.py`** - Các hàm dialog:

```python
# show_coordinate_config_dialog
def show_coordinate_config_dialog(initial_x=None, initial_y=None):
    # ... setup ...
    x_var = tk.StringVar(value=str(initial_x) if initial_x is not None else "0")
    y_var = tk.StringVar(value=str(initial_y) if initial_y is not None else "0")

# show_keyboard_config_dialog
def show_keyboard_config_dialog(initial_key="enter", initial_repeat=1, 
                                initial_key_type="press", initial_delay=0.5):
    # ... setup ...
    key_var = tk.StringVar(value=str(initial_key))
    repeat_var = tk.StringVar(value=str(initial_repeat))

# show_image_config_dialog
def show_image_config_dialog(is_detection=False, initial_repeat=None, 
                              initial_delay=None, ...):
    # ... setup ...
    repeat_var = tk.StringVar(value=str(initial_repeat if initial_repeat is not None else 1))
```

### 4. Image Edit Dialog Đã Hỗ Trợ

Hàm `_open_image_edit_dialog()` **đã có** logic lấy giá trị cũ:
```python
repeat_var = tk.StringVar(value=str(tpl.get("repeat", 1)))
delay_var = tk.StringVar(value=str(tpl.get("delay", state.click_delay)))
# ... etc
```

Không cần thay đổi gì vì nó mutate template in-place.

## 📋 Files Đã Sửa

1. ✅ `scenario/templates.py`
   - Pass `initial_x`, `initial_y` cho `show_coordinate_config_dialog()`
   - Pass `initial_key`, `initial_repeat`, ... cho `show_keyboard_config_dialog()`

2. ✅ `ui/dialogs.py`
   - Update signature `show_coordinate_config_dialog(initial_x=None, initial_y=None)`
   - Update signature `show_keyboard_config_dialog(initial_key=..., initial_repeat=..., ...)`
   - Update signature `show_image_config_dialog(..., initial_repeat=None, initial_delay=None, ...)`
   - Fields được init với initial values thay vì hardcoded defaults

## 🧪 Testing

### Test 1: Edit Coordinate

```bash
1. Thêm tọa độ: X=150, Y=250
   - Display: "📍 (150,250)"
   
2. Bấm "✏️ Sửa"
   - X field: 150 ✅ (thay vì 0)
   - Y field: 250 ✅ (thay vì 0)
   
3. Sửa thành X=200, Y=300
   - Bấm OK
   - Display: "📍 (200,300)" ✅
```

### Test 2: Edit Keyboard

```bash
1. Thêm phím: enter, 3 lần, press, 0.8s delay
   - Display: "[KEY: enter]"
   
2. Bấm "✏️ Sửa"
   - Key field: "enter" ✅
   - Repeat: 3 ✅
   - Type: "press" ✅
   - Delay: 0.8 ✅
   
3. Sửa thành: space, 5 lần
   - Bấy OK
   - Display: "[KEY: space]" ✅
```

### Test 3: Edit Image

```bash
1. Thêm ảnh với: repeat=2, delay=0.7s, threshold=0.8
   - Display: "🖼️ (image_name)"
   
2. Bấm "✏️ Sửa"
   - Repeat: 2 ✅
   - Delay trước: 0.7 ✅
   - Threshold: 0.8 ✅
   
3. Sửa thành: repeat=3, threshold=0.9
   - Bấm OK ✅
```

## 🔍 Debug

Khi edit, debug log sẽ show:
```
✅ Đã cập nhật tọa độ (200,300)
✅ Đã cập nhật phím: space
✅ Đã cập nhật thông số ảnh
```

Nếu reset fields vẫn xảy ra → check:
1. Dialog function nhận initial values?
2. `_edit_template_in_list()` pass giá trị?
3. `tpl.get("key")` có return giá trị?

---

**Status: ✅ Fix hoàn tất - Edit fields sẽ giữ giá trị cũ!**

