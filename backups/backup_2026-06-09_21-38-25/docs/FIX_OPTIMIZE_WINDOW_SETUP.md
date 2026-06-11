# ✅ Tối Ưu Setup Cửa Sổ - Chỉ Cần Nhập 1 Lần

## 🎯 Vấn Đề Gốc

Trước: Mỗi lần dùng relative click phải:
```
1. Bấm "📍 Lấy Tọa Độ Tương Đối"
   → Nhập tên cửa sổ (Chrome)
2. Lấy tọa độ
3. Lần sau lại phải nhập lại (Chrome)
   → Nhập lại (Chrome)
4. ... cứ lặp lại
```

**Vấn đề:** Lặp lại nhập window 5-10 lần cho 1 kịch bản ❌

## ✅ Giải Pháp

Tách riêng button **"🎯 Xác Định Cửa Sổ Đích"** để:

```
1. Bấm "🎯 Xác Định Cửa Sổ Đích"
   → Nhập tên cửa sổ 1 lần (Chrome)
   → Lưu vào state.game_hwnd + state.game_window_title

2. Sau đó tất cả action tự động dùng window này:
   ├─ "📍 Lấy Tọa Độ Tương Đối" → Không cần nhập lại
   ├─ "⌨️ Thêm phím" → Tự apply vào window đó
   └─ "🖼️ Thêm ảnh" → Cũng tự dùng window đó
```

## 📋 Thay Đổi

### 1. Thêm Nút "🎯 Xác Định Cửa Sổ Đích"

**File: `autoclick_gui.py`**

```python
def set_target_window():
    """Set target window for all relative operations"""
    # Nhập tên window
    window_title = ask_window_title_custom()
    
    # Tìm window
    hwnd = win32gui.FindWindow(None, window_title)  # or partial match
    
    # Lưu vào state
    state.game_hwnd = hwnd
    state.game_window_title = window_info['title']
    
    # Show status
    state.UI.status_label.config(
        text=f"✅ Đã xác định cửa sổ đích: {window_info['title']}"
    )
```

**UI Layout:**
```
⚔️ KỸ NĂNG CHIẾN ĐẤU
├─ 🎯 Xác Định Cửa Sổ Đích  ← NEW
├─ 🖼️ Thêm Pokémon mục tiêu
├─ 📍 Thêm tọa độ chiến trường
├─ 🎯 Ghi nhớ vị trí chuột
├─ 📍 Lấy Tọa Độ Tương Đối  ← Simplified
└─ ⌨️ Thêm phím bàn phím
```

### 2. Simplify "📍 Lấy Tọa Độ Tương Đối"

**File: `autoclick_gui.py`**

```python
def capture_relative_coordinates():
    # Check if window already set
    if not state.game_hwnd:
        messagebox.showwarning("⚠️ Cảnh báo", 
                              "Vui lòng bấm '🎯 Xác Định Cửa Sổ Đích' trước!")
        return
    
    # ✅ Use pre-set window - NO need to ask again
    window_info = RelativeCoordinateCapture.get_game_window_info()
    
    # Capture UI (user clicks to select coordinate)
    RelativeCoordinateCapture.start_capture_ui(root, on_capture_complete)
```

**Trước (4 steps):**
```
1. Nhập tên window
2. Tìm window
3. Di chuột chọn tọa độ
4. Cấu hình click type/delay
```

**Sau (2 steps):**
```
1. Di chuột chọn tọa độ
2. Cấu hình click type/delay
```

### 3. Add state variables

**File: `core/state.py`**

```python
game_hwnd = None
game_window_title = None  # Store title for reference
```

### 4. Same logic for keyboard & image

Không cần sửa gì - chúng cũng tự dùng `state.game_hwnd`:

```python
# Keyboard operations
→ Tự apply vào window đó

# Image recognition
→ Tự dùng search region của window đó
```

## 🧪 Testing

### Test Workflow

```
Setup Phase (1 lần):
1. Bấm "🎯 Xác Định Cửa Sổ Đích"
2. Nhập: "Chrome" → OK
   Status: "✅ Đã xác định cửa sổ đích: Chrome"

Repeat Phase (mỗi action):
3. Bấm "📍 Lấy Tọa Độ Tương Đối"
   → Chọn điểm trong Chrome
   → Cấu hình
   → OK ✅
   
4. Bấm "📍 Lấy Tọa Độ Tương Đối" lại
   → Chọn điểm khác
   → OK ✅
   
5. Bấm "⌨️ Thêm phím"
   → Chọn phím
   → OK ✅
   
❌ Không cần nhập "Chrome" lại!
```

### Fallback

Nếu chưa set window:
```
Bấm "📍 Lấy Tọa Độ Tương Đối" mà không set window
→ Warning: "Vui lòng bấm '🎯 Xác Định Cửa Sổ Đích' trước!"
```

## 📊 So Sánh

| Bước | Cũ | Mới |
|------|-------|--------|
| Setup Window | Mỗi action nhập | 1 lần duy nhất |
| Capture Tọa Độ 1 | Nhập + Chọn | Chỉ chọn |
| Capture Tọa Độ 2 | Nhập + Chọn | Chỉ chọn |
| Capture Tọa Độ 3 | Nhập + Chọn | Chỉ chọn |
| **Tổng cộng** | **~12 nhập** | **~3 nhập** |

## 🎯 UX Improvement

**Trước:**
```
Setup 1 kịch bản 5 action
= Nhập window 5 lần + Chọn 5 lần
= Rất loằng ngoằng
```

**Sau:**
```
Setup 1 kịch bản 5 action
= Nhập window 1 lần + Chọn 5 lần
= Nhanh + Clean! ✅
```

## 🔄 Tương Lai

Có thể extend thêm:
- ☐ Preset cho multiple windows
- ☐ Window auto-detect (focus trên game)
- ☐ Recent windows list

Nhưng hiện tại solution này đã **giảm 80% input** 🚀

---

**Status: ✅ Optimization hoàn tất!**

