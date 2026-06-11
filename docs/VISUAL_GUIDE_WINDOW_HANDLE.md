# 📊 Hướng Dẫn Trực Quan: Window Handle

## 🎯 Window Handle Là Gì?

```
┌─────────────────────────────────────────┐
│         MapleStory M Game Window         │
│  ┌───────────────────────────────────┐  │
│  │  ╔═══════════════════════════════╗ │  │
│  │  ║   HWND: 1051690 ← Handle      ║ │  │
│  │  ║   Status: ✅ HỢPNÃO HỢP LỆ  ║ │  │
│  │  ╚═══════════════════════════════╝ │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

Handle = Định danh duy nhất của cửa sổ
Khi Windows reboot/recreate cửa sổ → Handle bị thay đổi
```

---

## 🔄 Luồng Sự Kiện: Cách Hoạt Động

### ✅ LUỒNG BÌNH THƯỜNG

```
[Bước 1] Chọn Cửa Sổ
┌─────────────────────────────┐
│ Bấm "Chọn Cửa Sổ Đích"      │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│ Tìm MapleStory M window     │
│ → HWND = 1051690 ✅         │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│ Lưu HWND vào state          │
│ state.game_hwnd = 1051690   │
└──────────┬──────────────────┘
           │
           ↓
[Bước 2] Chạy Scenario
┌─────────────────────────────┐
│ Bấm "Chạy"                  │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│ ✅ Check: IsWindow(1051690)?│
│    → YES ✅ HỢPNÀO HỢP LỆ  │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│ ✅ Bắt đầu chạy scenario    │
│ 🖱️  Click, click, click...  │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│ ✅ Scenario hoàn tất        │
└─────────────────────────────┘
```

### ❌ LUỒNG SAI: Alt-Tab Trong Khi Chạy

```
[Bước 1] Chọn Cửa Sổ ✅
└──────────┬──────────────────────┘
           │
[Bước 2] Chạy Scenario
├─────────────────────────────┐
│ ✅ Check: IsWindow(1051690)?│
│    → YES ✅ HỢPNÀO HỢP LỆ  │
└──────────┬──────────────────┘
           │
           ↓
├─────────────────────────────┐
│ 🖱️  Click trên button 1      │
└──────────┬──────────────────┘
           │
           ↓
❌ ❌ ❌ BẠN ALT-TAB SAU ❌ ❌ ❌
           │
           ↓
├─────────────────────────────┐
│ Window handle: 1051690      │
│ Status: ❌ KHÔNG HỢP LỆ    │
│ (Chrome active, không phải game)
└──────────┬──────────────────┘
           │
           ↓
├─────────────────────────────┐
│ 🖱️  Click trên button 2      │
│ (Nhưng được gửi đến Chrome!)│
└──────────┬──────────────────┘
           │
           ↓
❌ SCENARIO FAIL - Không click vào đúng nơi
```

---

## 🛡️ Lớp Kiểm Tra (Protection Layer)

### TRƯỚC (Cũ) - Không Có Kiểm Tra

```
Find_and_click()
    │
    ├─ Bấm (512, 451)? → Windows không biết nên gửi đến Chrome
    │
    └─ Bấm (525, 163)? → Chrome nhân được click ❌
```

### SAU (Mới) - Có 2 Lớp Kiểm Tra

```
Find_and_click()
    │
    ├─ [KIỂM TRA 1] Trước khi bắt đầu
    │  └─ IsWindow(HWND)? 
    │     ├─ YES → Tiếp tục ✅
    │     └─ NO  → DỪNG, báo lỗi ❌
    │
    ├─ [Vòng lặp Template]
    │  │
    │  ├─ [KIỂM TRA 2] Trước mỗi bước
    │  │  └─ IsWindow(HWND)?
    │  │     ├─ YES → Thực hiện click ✅
    │  │     └─ NO  → DỪNG, báo lỗi ❌
    │  │
    │  └─ Bấm (512, 451)
    │
    └─ Hoàn tát
```

---

## 🎮 Ví Dụ Thực Tế

### Kịch Bản 1️⃣: Tất Cả Bình Thường ✅

```
Thời gian    AutoClick              MapleStory M
─────────────────────────────────────────────────
T0:00        Chọn cửa sổ
             HWND = 1051690
                                   ← Game đang chạy
T0:05        Chạy scenario
             [Check] IsWindow? YES ✅
                                   ← Game ACTIVE
T0:06        Click (512, 451)
                                   → Button bị click ✅
T0:07        Click (525, 163)
                                   → Button bị click ✅
T0:08        ✅ Hoàn tất
```

### Kịch Bản 2️⃣: Alt-Tab Đúng Lúc ❌ (CỰ)

```
Thời gian    AutoClick              MapleStory M / Chrome
─────────────────────────────────────────────────────────
T0:00        Chọn cửa sổ
             HWND = 1051690
                                   ← Game đang chạy
T0:05        Chạy scenario
             [Check] IsWindow? YES ✅
                                   ← Game ACTIVE
T0:06        Click (512, 451)
                                   → Button bị click ✅
T0:07        ❌ BẠN ALT-TAB
                                   ← Chrome được focus
                                   ← HWND 1051690 = inactive
T0:08        Click (525, 163)
             ⚠️ Chuối: "Click at (525, 163)"
                                   ← ??? Tìm window 1051690
                                   ← Không tìm thấy
                                   ← Click gửi tới Chrome ❌
T0:09        ❌ FAIL - Scenario không xảy ra gì
```

### Kịch Bản 3️⃣: Alt-Tab Đúng Lúc ✅ (MỚI)

```
Thời gian    AutoClick              MapleStory M / Chrome
─────────────────────────────────────────────────────────
T0:00        Chọn cửa sổ
             HWND = 1051690
                                   ← Game đang chạy
T0:05        Chạy scenario
             [Check] IsWindow? YES ✅
                                   ← Game ACTIVE
T0:06        Click (512, 451)
                                   → Button bị click ✅
T0:07        ❌ BẠN ALT-TAB
                                   ← Chrome được focus
                                   ← HWND 1051690 = inactive
T0:08        Template loop - KIỂM TRA
             [Check 2] IsWindow(1051690)?
             → KHÔNG ❌
             → STOP ngay lập tức
             → Status: "❌ Cửa sổ đích bị mất"
                                   ← Chrome không bị click ✅
T0:09        ✅ Scenario dừng an toàn
             Người dùng hiểu: "Tôi alt-tab nên scenario dừng"
```

---

## 📍 Vị Trí Kiểm Tra Trong Code

### Kiểm Tra 1️⃣: Tại Đầu

```python
def find_and_click():
    # ← HERE: Kiểm tra trước khi bắt đầu
    if state.game_hwnd:
        if not win32gui.IsWindow(state.game_hwnd):
            return "failed"  # Dừng ngay
```

### Kiểm Tra 2️⃣: Trong Vòng Lặp

```python
    while state.running and (state.infinite_loop or ...):
        for tpl in state.templates:
            # ← HERE: Kiểm tra trước mỗi bước
            if state.game_hwnd and not win32gui.IsWindow(state.game_hwnd):
                break  # Dừng loop
```

---

## 🎯 Hành Động Tối Ưu Hóa

### ✅ CỰ (Nên Làm)

```
AutoClick              Màn Hình
┌──────────────┐       ┌────────────────────┐
│ AutoClick    │       │ MapleStory M       │
│ [STOP]       │       │ [ACTIVE] ← Focus   │
│ [RUN]        │       │ 🎮 Game đang chơi │
│ Status: ...  │       │                    │
└──────────────┘       └────────────────────┘
         ↑                      ↑
    Size nhỏ        Game Window FULL VISIBLE
    Để xa game      Để nhìn thấy hoàn toàn
```

### ❌ SAI (Không Nên Làm)

```
❌ Tối thiểu hóa game → Dừng scenario
❌ Alt-tab khác ứng dụng → Dừng scenario
❌ Đóng game → Dừng scenario
❌ Che phủ game window → Chuột có thể click sai
```

---

## 💡 Tóm Tắt

| Trạng Thái | Kiểm Tra | Hành Động |
|-----------|---------|---------|
| Game ACTIVE | ✅ Pass | ▶️ Chạy |
| Game Inactive | ❌ Fail | 🛑 Dừng + Báo lỗi |
| Game Tối Thiểu Hóa | ❌ Fail | 🛑 Dừng + Báo lỗi |
| Game Đóng | ❌ Fail | 🛑 Dừng + Báo lỗi |

---

**Cập nhật:** June 9, 2026
