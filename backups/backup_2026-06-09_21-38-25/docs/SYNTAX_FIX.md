# 🔧 FIX: IndentationError trong vision.py

## 🐛 LỖI
```
File "core\vision.py", line 215
    except cv2.error:
IndentationError: unexpected indent
```

## 🔍 NGUYÊN NHÂN
Khi thêm function `_compute_edge_similarity()`, có một đoạn code bị **duplicate** và **sai indentation**:

```python
def _compute_edge_similarity(...):
    ...
    return 1.0  # Nếu lỗi, không penalty
            except cv2.error:  # ← LỖI: Indent sai + code duplicate
                continue
        
        return best_score, best_loc, best_method  # ← Code duplicate
```

Đoạn code `except cv2.error:` này thuộc về function `match_single()` nhưng bị duplicate xuống dưới `_compute_edge_similarity()`.

---

## ✅ GIẢI PHÁP
Xóa toàn bộ đoạn code duplicate sau function `_compute_edge_similarity()`.

**Code SAU KHI FIX:**
```python
def _compute_edge_similarity(template: np.ndarray, matched_region: np.ndarray) -> float:
    """
    Tính similarity giữa edges của template và matched region.
    Return: 0.0-1.0, càng cao càng giống.
    """
    try:
        # Detect edges bằng Canny
        template_edges = cv2.Canny(template, 50, 150)
        matched_edges = cv2.Canny(matched_region, 50, 150)
        
        # Normalize
        template_edges = template_edges.astype(float) / 255.0
        matched_edges = matched_edges.astype(float) / 255.0
        
        # Compute correlation
        correlation = np.corrcoef(template_edges.flatten(), matched_edges.flatten())[0, 1]
        
        # Handle NaN (khi edges rỗng)
        if np.isnan(correlation):
            return 0.5
        
        return max(0.0, min(1.0, correlation))
    except:
        return 1.0  # Nếu lỗi, không penalty


def _build_match_result(  # ← Function tiếp theo, KHÔNG có code duplicate
    score: float,
    ...
```

---

## 🧪 KIỂM TRA

### **Test 1: Import modules**
```python
from core import vision
from core import runner
from core import state
# ✅ Tất cả import thành công
```

### **Test 2: Check constants**
```python
print(vision.DEFAULT_THRESHOLD)  # 0.85
print(vision.RECOMMENDED_MIN_THRESHOLD)  # 0.75
# ✅ Constants đúng
```

### **Test 3: Run GUI**
```bash
python autoclick_gui.py
# ✅ GUI chạy không lỗi
```

---

## 📊 KẾT QUẢ TEST

```
Testing imports...
1. Importing core.vision...
   ✅ core.vision OK
2. Importing core.runner...
   ✅ core.runner OK
3. Importing core.state...
   ✅ core.state OK

✅ ALL IMPORTS SUCCESSFUL!
DEFAULT_THRESHOLD = 0.85
RECOMMENDED_MIN_THRESHOLD = 0.75
```

---

## 📝 FILE ĐÃ SỬA
- ✅ `core/vision.py` - Xóa code duplicate

---

**Status:** ✅ **FIXED**  
**Date:** June 4, 2026  
**Issue:** IndentationError: unexpected indent  
**Solution:** Removed duplicate code block after _compute_edge_similarity()  
