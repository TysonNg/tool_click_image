# Plan: Thư viện kịch bản (Scenario Library)

## Mục tiêu

Thêm tính năng quản lý kịch bản theo cây thư mục **Game → Ải** vào tool AutoClick. Hiện tại user phải dùng file dialog chọn file JSON thủ công mỗi lần — feature mới cho phép chọn game, tick ải, bấm chạy.

## Cấu trúc thư mục

```
D:\autoclick_image\scenarios\          ← root cố định, tạo nếu chưa có
├── maple\                              ← folder = 1 game
│   ├── Cooking\                        ← folder = 1 ải (scenario)
│   │   ├── 1.png, 2.png, ...          ← ảnh template
│   │   └── Cooking.json               ← scenario JSON
│   ├── Daily Dungeon\
│   │   ├── 1.png ... 5.png
│   │   └── Daily_Dungeon.json
│   ├── Elite\
│   ├── Evo\
│   └── Monster_Park\
├── genshin\
│   └── ...
└── settings.json                       ← nhớ game/ải đã chọn lần cuối
```

Mỗi ải chứa ảnh + 1 file `.json` scenario. Ảnh nằm cùng folder với JSON.

## Codebase hiện tại

Project đã refactor thành module:

```
autoclick_gui.py          ← entry point (UI layout + mainloop)
core/
  state.py                ← global vars + UI widget refs (state.UI.root, state.UI.status_label, ...)
  input.py                ← click, human_move, press_key
  vision.py               ← screenshot, matchTemplate, multi_scale_match
  runner.py               ← find_and_click, start/stop_clicking, run_scenario_queue
scenario/
  io.py                   ← save_scenario, load_scenario, load_multiple_scenarios, clear_scenarios
  templates.py            ← add/edit/delete templates, update_history, dialogs
ui/
  theme.py                ← PKM_* color constants
  widgets.py              ← create_btn, create_card helpers
  dialogs.py              ← show_image_config_dialog, show_coordinate_config_dialog, show_keyboard_config_dialog
  hotkeys.py              ← hotkey binding
  layout.py               ← responsive scaling
utils.py                  ← safe_print
```

### Quy ước code

- Global state truy cập qua `from core import state` → `state.templates`, `state.click_delay`, ...
- Widget refs qua `state.UI.root`, `state.UI.status_label`, `state.UI.history_list`, ...
- Theme colors dùng `from ui.theme import *` (PKM_RED, PKM_BLUE_DARK, PKM_YELLOW, ...)
- Tạo nút dùng `from ui.widgets import create_btn, create_card`
- `from utils import safe_print`

### Scenario JSON format hiện tại

```json
{
  "process_loops": 1,
  "infinite_loop": false,
  "click_delay": 1.0,
  "templates": [
    {
      "type": "image",
      "path": "D:/Program Files/maple/Cooking/1.png",   ← ABSOLUTE path (cũ)
      "repeat": 1,
      "delay": 1.0,
      "wait_until_found": true,
      "wait_timeout": 30,
      "threshold": 0.7,
      "click_delay": 1.0,
      "click_type": "single"
    },
    {
      "type": "coord",
      "x": 500, "y": 300,
      "repeat": 1,
      "delay": 1.0,
      "click_type": "single",
      "delay_after": 0.5
    },
    {
      "type": "key",
      "key": "enter",
      "repeat": 1,
      "delay": 1.0,
      "key_type": "press",
      "delay_after": 0.5
    }
  ]
}
```

## Các thay đổi cần làm

### 1. Tạo file `scenario/library.py` — Helper functions

```python
SCENARIOS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scenarios")

def ensure_scenarios_root():
    """Tạo D:\autoclick_image\scenarios\ nếu chưa có."""

def list_games() -> list[str]:
    """Trả về danh sách tên folder con trong scenarios/. Mỗi folder = 1 game."""

def list_stages(game: str) -> list[str]:
    """Trả về danh sách folder con của scenarios/<game>/. Mỗi folder = 1 ải. Sort A→Z."""

def get_stage_json(game: str, stage: str) -> str | None:
    """Tìm file .json đầu tiên trong scenarios/<game>/<stage>/. Trả None nếu ko có."""

def resolve_image_path(json_dir: str, path: str) -> str:
    """
    Nếu path là relative (vd '1.png' hoặc 'images/1.png') → join với json_dir.
    Nếu path là absolute → giữ nguyên (backward compat).
    """

def create_game(name: str):
    """Tạo folder scenarios/<name>/."""

def rename_game(old_name: str, new_name: str):
    """Rename folder."""

def delete_game(name: str):
    """shutil.rmtree sau khi confirm."""

def create_stage(game: str, stage_name: str):
    """Tạo folder scenarios/<game>/<stage_name>/."""

def delete_stage(game: str, stage_name: str):
    """shutil.rmtree sau khi confirm."""

def copy_stage(game: str, stage_name: str, new_name: str):
    """shutil.copytree."""

def copy_image_to_stage(game: str, stage: str, src_path: str) -> str:
    """
    Copy ảnh vào scenarios/<game>/<stage>/.
    Nếu trùng tên → đổi thành 1_2.png, 1_3.png, ...
    Trả về tên file mới (relative).
    """

def save_settings(last_game: str, last_stages: list[str]):
    """Lưu vào scenarios/settings.json."""

def load_settings() -> dict:
    """Đọc scenarios/settings.json. Trả {"last_game": "", "last_stages": []}."""

def import_old_scenario(json_path: str, game: str, stage_name: str):
    """
    Import scenario cũ (path absolute) vào thư viện mới:
    1. Tạo folder scenarios/<game>/<stage_name>/
    2. Copy tất cả ảnh được reference trong JSON vào folder đó
    3. Sửa path trong JSON thành relative
    4. Lưu JSON mới vào folder đó
    """
```

### 2. Tạo file `ui/library_panel.py` — UI panel

Panel này thêm vào **LEFT PANEL** trong `autoclick_gui.py`, ngay trước section "🎒 TÚI ĐỒ TRAINER".

#### UI Layout

```
┌─ 📚 THƯ VIỆN KỊCH BẢN ────────────────────────┐
│ 🎮 Game: [ maple          ▼ ] [➕] [✏️] [🗑️]  │
│ ─────────────────────────────────────────────── │
│ 📋 Danh sách Ải:                                │
│ ☑ Cooking                                      │
│ ☐ Daily Dungeon                                │
│ ☑ Elite                                        │
│ ☐ Evo                                          │
│ ☐ Monster_Park                                 │
│ ─────────────────────────────────────────────── │
│ [➕ Ải mới] [📋 Copy] [🗑️ Xóa ải]              │
│ [▶️ Chạy ải đã chọn] [📂 Mở folder]            │
│ [📥 Import scenario cũ]                         │
└────────────────────────────────────────────────┘
```

#### Hành vi

- **Game dropdown**: `list_games()`. Khi chọn game → refresh checkbox list bằng `list_stages(game)`.
- **➕ Game mới**: `simpledialog.askstring` → `create_game(name)` → refresh dropdown.
- **✏️ Sửa tên game**: `simpledialog.askstring` → `rename_game()` → refresh.
- **🗑️ Xóa game**: `messagebox.askyesno` confirm 2 lần → `delete_game()` → refresh.
- **Checkbox list**: Mỗi ải 1 `tk.Checkbutton`. Dùng dict `{stage_name: BooleanVar}`.
- **➕ Ải mới**: Hỏi tên → `create_stage()` → refresh list.
- **📋 Copy ải**: Copy ải đang selected → hỏi tên mới → `copy_stage()`.
- **🗑️ Xóa ải**: Confirm → `delete_stage()` → refresh.
- **▶️ Chạy ải đã chọn**: Lấy các ải có checkbox = True, sort A→Z, load JSON + ảnh cho mỗi ải, đưa vào `state.scenario_metadata` + `state.scenario_queue`, rồi gọi `start_clicking()`.
- **📂 Mở folder**: `os.startfile(scenarios/<game>/)` để mở Explorer.
- **📥 Import scenario cũ**: Hỏi chọn file JSON cũ + chọn game đích + nhập tên ải → gọi `import_old_scenario()` → refresh.

#### Load ải vào runner

Khi bấm "▶️ Chạy ải đã chọn":

```python
selected_stages = [name for name, var in stage_vars.items() if var.get()]
selected_stages.sort()  # A→Z

state.scenario_metadata = []
state.scenario_queue = []

for stage_name in selected_stages:
    json_path = get_stage_json(current_game, stage_name)
    if not json_path:
        continue
    json_dir = os.path.dirname(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        scenario = json.load(f)

    # Load templates, resolve image paths
    scenario_templates = []
    for tpl in scenario.get("templates", []):
        if tpl["type"] == "image":
            img_path = resolve_image_path(json_dir, tpl["path"])
            img = imread_unicode(img_path)
            if img is not None:
                w, h = img.shape[::-1]
                scenario_templates.append({
                    "type": "image", "img": img, "w": w, "h": h,
                    "path": img_path, ...các field khác...
                })
        elif tpl["type"] == "key":
            scenario_templates.append({...})
        else:  # coord
            scenario_templates.append({...})

    state.scenario_metadata.append({
        "file_path": json_path,
        "process_loops": scenario.get("process_loops", 1),
        "infinite_loop": scenario.get("infinite_loop", False),
        "click_delay": scenario.get("click_delay", 1.0),
        "templates": scenario_templates
    })
    state.scenario_queue.append(json_path)

update_history()
start_clicking()
```

### 3. Sửa `scenario/io.py` — save với relative path

Khi save scenario từ thư viện (biết folder ải):

```python
def save_scenario_to_stage(game, stage):
    """Lưu state.templates vào scenarios/<game>/<stage>/<stage>.json với path ảnh relative."""
    stage_dir = os.path.join(SCENARIOS_ROOT, game, stage)
    json_path = os.path.join(stage_dir, f"{stage}.json")

    scenario = {...}
    for tpl in state.templates:
        if tpl["type"] == "image":
            # Convert absolute path to relative
            rel_path = os.path.relpath(tpl["path"], stage_dir)
            scenario["templates"].append({"type": "image", "path": rel_path, ...})
    ...
```

Giữ nguyên `save_scenario()` và `load_scenario()` cũ làm fallback (user vẫn có nút "💾 Lưu / 📂 Tải" trong TÚI ĐỒ TRAINER).

### 4. Sửa `scenario/templates.py` — add_image copy ảnh

Khi đang trong context 1 ải (biến `state.current_library_game` và `state.current_library_stage` khác None):

```python
def add_image():
    file_path = filedialog.askopenfilename(...)
    if file_path:
        # Nếu đang trong context thư viện → copy ảnh vào folder ải
        if state.current_library_game and state.current_library_stage:
            new_name = copy_image_to_stage(
                state.current_library_game,
                state.current_library_stage,
                file_path
            )
            file_path = os.path.join(SCENARIOS_ROOT, state.current_library_game,
                                      state.current_library_stage, new_name)
        ...  # phần còn lại giữ nguyên
```

### 5. Thêm vào `core/state.py`

```python
# Library context — set khi user đang thao tác trong thư viện
current_library_game = None
current_library_stage = None
```

### 6. Sửa `autoclick_gui.py` — đặt panel vào layout

Trong LEFT PANEL, thêm trước section "🎒 TÚI ĐỒ TRAINER":

```python
from ui.library_panel import create_library_panel
create_library_panel(left_panel)
```

### 7. `scenarios/settings.json`

```json
{
  "last_game": "maple",
  "last_stages": ["Cooking", "Elite"]
}
```

Đọc lúc startup, ghi lại mỗi khi user thay đổi game hoặc tick/untick ải.

## Thứ tự thực hiện

| # | File | Việc | Phụ thuộc |
|---|------|------|-----------|
| 1 | `core/state.py` | Thêm `current_library_game`, `current_library_stage` | — |
| 2 | `scenario/library.py` | Viết tất cả helper functions | — |
| 3 | `ui/library_panel.py` | Viết toàn bộ UI panel + event handlers | #1, #2 |
| 4 | `scenario/io.py` | Thêm `save_scenario_to_stage()` | #2 |
| 5 | `scenario/templates.py` | Sửa `add_image()` để auto copy khi trong context thư viện | #1, #2 |
| 6 | `autoclick_gui.py` | Thêm `create_library_panel(left_panel)` vào layout | #3 |
| 7 | Test | Load scenario cũ từ `D:\maple\*`, import vào thư viện, chạy thử | All |

## Quy tắc

- **KHÔNG đụng logic runner** (`core/runner.py`, `find_and_click`). Chỉ chuẩn bị `state.scenario_metadata` + `state.scenario_queue` đúng format rồi gọi `start_clicking()`.
- **Backward compatible**: scenario JSON cũ (path absolute) vẫn load được. `resolve_image_path()` check absolute trước.
- **Trùng tên ảnh khi copy**: tự đổi tên `1.png` → `1_2.png` → `1_3.png`, không ghi đè, không hỏi user.
- **Giữ nguyên 2 nút cũ** "💾 Lưu dữ liệu Trainer" / "📂 Tải dữ liệu Trainer" trong TÚI ĐỒ TRAINER làm fallback.
- **Thứ tự chạy**: khi tick nhiều ải → sort tên A→Z.
- **UI style**: dùng `create_btn`, `create_card` từ `ui/widgets.py`, màu từ `ui/theme.py`.

## User hiện có

Folder `D:\maple\` chứa 7 game scenarios (Cooking, Daily Dungeon, Dimension, Elite, Evo, Monster_Park, Mulung). Mỗi folder chứa ảnh PNG + 1 file JSON. Cần test import folder này vào thư viện.
