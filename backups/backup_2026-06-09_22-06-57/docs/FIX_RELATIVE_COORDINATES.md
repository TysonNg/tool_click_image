# ✅ Fix Lỗi Tọa Độ Tương Đối (Relative Coordinates)

## 🐛 Vấn Đề

Khi dùng "📍 Lấy Tọa Độ Tương Đối":
```
1. Nhập tên cửa sổ ✅
2. Lấy tọa độ tương đối (100, 200) ✅
3. Nhưng khi click lại → Click vào chỗ khác ❌
```

**Nguyên Nhân:**
- Tọa độ được capture là **relative** (100, 200 trong window)
- Nhưng khi runner click, nó click vào **absolute** (100, 200 trên screen)
- Nếu window di chuyển hoặc không ở vị trí gốc → click sai chỗ

## ✅ Giải Pháp

### 1. Lưu Window Handle + Mark Relative

**File: `autoclick_gui.py`** - Hàm `capture_relative_coordinates()`

Template được lưu với thông tin window:
```python
template = {
    'type': 'coord',
    'x': 100,  # Relative X
    'y': 200,  # Relative Y
    'is_relative': True,  # ← Mark as RELATIVE
    'game_hwnd': state.game_hwnd,  # ← Save window handle
    'window_title': window_info['title'],  # ← For reference
    'click_type': 'single',
    'delay_after': 0.5,
    'path': '📍 (100, 200) [50.0%, 50.0%] (single, 0.5s)'
}
```

### 2. Calculate Absolute When Clicking

**File: `core/runner.py`** - Xử lý `type == "coord"`

Khi runner click, nó tính toán absolute:
```python
elif tpl["type"] == "coord":
    click_x = tpl["x"]
    click_y = tpl["y"]
    
    if tpl.get("is_relative", False):
        # Get window position
        win_info = RelativeCoordinateCapture.get_game_window_info()
        
        # Convert: absolute = relative + window_offset
        click_x = win_info['client_left'] + tpl["x"]  # e.g., 800 + 100 = 900
        click_y = win_info['client_top'] + tpl["y"]   # e.g., 600 + 200 = 800
        
        # Then click at (900, 800)
        click(click_x, click_y)
```

### 3. Backward Compatibility

Các tọa độ thường (không dùng "Lấy Tương Đối") được đánh dấu:
```python
template = {
    'type': 'coord',
    'x': 100,
    'y': 200,
    'is_relative': False,  # ← Mark as ABSOLUTE
    # ... no game_hwnd
}
```

Khi click, nếu `is_relative = False`, dùng tọa độ trực tiếp.

## 📋 Files Đã Sửa

1. ✅ `autoclick_gui.py`
   - Thêm `'is_relative': True`
   - Thêm `'game_hwnd': state.game_hwnd`
   - Thêm `'window_title'` cho reference

2. ✅ `core/runner.py`
   - Thêm logic tính offset khi `is_relative = True`
   - Log output cho debug

3. ✅ `scenario/templates.py`
   - Thêm `'is_relative': False` cho `add_coordinate()`
   - Thêm `'is_relative': False` cho `add_current_position()`

## 🧪 Testing

### Test 1: Lấy Tọa Độ Tương Đối

```bash
1. Mở game/app bất kỳ (e.g., Chrome)
   - Để window ở vị trí (500, 300)
   
2. Bấm "📍 Lấy Tọa Độ Tương Đối"
   - Nhập: "Chrome"
   - Di chuột đến nút cần click (e.g., trong window)
   - Tọa độ relative = (100, 150) [Tính từ góc trái-trên của window]
   - Bấm OK
   
3. Bấm "⚡ TUNG POKÉBALL!" → Click vào tọa độ đúng ✅
   - Absolute = (500+100, 300+150) = (600, 450) ✅

4. Di chuyển window đến (1000, 400)
   - Bấm "⚡ TUNG POKÉBALL!" lại
   - Nó vẫn click vào nút đúng ✅
   - Vì absolute = (1000+100, 400+150) = (1100, 550) ✅
```

### Test 2: Tọa Độ Thường (Absolute)

```bash
1. Bấm "📍 Thêm tọa độ chiến trường (XY)"
   - Nhập: X=100, Y=200
   - Bấm OK
   
2. Bấm "⚡ TUNG POKÉBALL!" → Click vào (100, 200) ✅
   - Không tính offset (như cũ)
```

## 📊 So Sánh

| Loại | Lưu Trữ | Khi Click | Window Move |
|------|---------|----------|------------|
| Relative | relative (x, y) + hwnd | absolute = rel + offset | ✅ Theo window |
| Absolute | absolute (x, y) | dùng trực tiếp | ❌ Cố định |

## 🔍 Debug Output

Khi chạy với relative coordinates:
```
📍 Relative→Absolute: (100, 200) + (500, 300) = (600, 500)
🖱️ Clicked coordinate 📍 (100, 200) [50.0%, 50.0%] (single, 0.5s)
```

## 📝 Quy Ước Tọa Độ

### Format Path

**Relative:**
```
📍 (100, 200) [50.0%, 50.0%] (single, 0.5s)
   ↑ Relative X,Y
             ↑ Percent of window
                           ↑ Click type + delay
```

**Absolute:**
```
📍 (800, 600)
   ↑ Absolute X,Y (screen coords)
```

---

**Status: ✅ Fix hoàn tất - Tọa độ tương đối hoạt động chính xác!**

