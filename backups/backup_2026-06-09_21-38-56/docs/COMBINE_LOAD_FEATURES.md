# ✅ Combine Load Scenario Features - HOÀN THÀNH (v2)

## Tóm Tắt Thay Đổi

**Trước**: 2 nút riêng biệt
- 📂 Tải dữ liệu Trainer (1 file - thay thế)
- 📚 Tải nhiều kịch bản (nhiều files - queue)

**Sau**: 1 nút duy nhất  
- 📂 Tải dữ liệu Trainer (**LUÔN** tải vào queue - gộp và chạy liên tiếp)

## Cách Hoạt Động

Nút **📂 Tải dữ liệu Trainer** giờ sử dụng hàm `load_scenario_combo()`:

- **Chọn 1 file** → Load vào queue (chạy 1 kịch bản)
- **Chọn 2+ files** → Load tất cả vào queue (chạy liên tiếp)

✨ **Chính là chức năng "Tải nhiều kịch bản" nhưng tên gọn hơn!**

## Thay Đổi Files

### `scenario/io.py`
- ✅ Cập nhật hàm `load_scenario_combo()` - **LUÔN load vào queue**
- ✅ Giữ `load_scenario()` và `load_multiple_scenarios()` (backup)

### `autoclick_gui.py`
- ✅ Import `load_scenario_combo` (thay cho 2 hàm cũ)
- ✅ Gỡ bỏ `multi_scenario_row` (frame "📚 Tải nhiều kịch bản")
- ✅ Cập nhật callback: `load_scenario` → `load_scenario_combo`

## UI Mới

### Trước (3 nút):
```
[💾 Lưu dữ liệu] [📂 Tải dữ liệu]
[📚 Tải nhiều kịch bản]
[🗑️ Xóa tất cả]
```

### Sau (2 nút - gọn gàng):
```
[💾 Lưu dữ liệu] [📂 Tải dữ liệu *]
[🗑️ Xóa tất cả]
```

*Nút tải LUÔN tải vào queue, có thể chọn 1 hoặc nhiều files

## Test

```bash
python autoclick_gui.py
```

Kiểm tra:
- Chọn 1 file → Hiện "Tổng 1 kịch bản" ✅
- Chọn 2+ files → Hiện "Tổng X kịch bản" ✅
- Bấm "TUNG POKÉBALL!" → Chạy tuần tự ✅
- Hủy dialog → Không có lỗi ✅

## Status
✅ **HOÀN THÀNH** - UI gọn gàng, luôn tải vào queue
