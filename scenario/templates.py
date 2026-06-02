import os
import time
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

import numpy as np
import pyautogui

from utils import safe_print
from core import state
from core.vision import (
    capture_screen_gray,
    multi_scale_match,
    get_search_region_screenshot,
    filter_close_points,
    imread_unicode,
)
from ui.dialogs import (
    show_image_config_dialog,
    show_coordinate_config_dialog,
    show_keyboard_config_dialog,
)
from scenario.library import SCENARIOS_ROOT, copy_image_to_stage
from ui.theme import *


def update_history():
    state.UI.history_list.delete(0, tk.END)

    # Nếu có scenario_metadata, hiển thị từng kịch bản tách riêng
    if state.scenario_metadata:
        safe_print(f"🔵 [DEBUG] update_history: displaying {len(state.scenario_metadata)} scenarios")
        for scenario_idx, metadata in enumerate(state.scenario_metadata):
            # Header cho mỗi kịch bản
            scenario_name = os.path.basename(metadata["file_path"])
            state.UI.history_list.insert(tk.END, f"{'='*60}")
            state.UI.history_list.insert(tk.END, f"📋 KỊCH BẢN {scenario_idx + 1}: {scenario_name}")
            state.UI.history_list.insert(tk.END, f"{'='*60}")

            # Hiển thị các item của kịch bản này
            templates_count = len(metadata["templates"])
            safe_print(f"🔵 [DEBUG] Scenario {scenario_idx + 1} has {templates_count} templates")

            if templates_count == 0:
                state.UI.history_list.insert(tk.END, "  (Không có item)")
            else:
                for item_idx, tpl in enumerate(metadata["templates"]):
                    if tpl["type"] == "image":
                        delay_str = f" [delay {tpl.get('delay', state.click_delay)}s]"
                        wait_str = " [⏳ CHỜ]" if tpl.get("wait_until_found", False) else ""
                        is_detection = tpl.get("is_detection", False)

                        if is_detection:
                            state.UI.history_list.insert(tk.END, f"  {item_idx+1}. 🔍 [DETECTION] {tpl['path']}{wait_str}")
                        else:
                            state.UI.history_list.insert(tk.END, f"  {item_idx+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}{wait_str}")
                    elif tpl["type"] == "key":
                        delay_str = f" [delay {tpl.get('delay', state.click_delay)}s]"
                        state.UI.history_list.insert(tk.END, f"  {item_idx+1}. ⌨️ {tpl['path']} (nhấn {tpl['repeat']} lần){delay_str}")
                    else:
                        delay_str = f" [delay {tpl.get('delay', state.click_delay)}s]"
                        state.UI.history_list.insert(tk.END, f"  {item_idx+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}")

            state.UI.history_list.insert(tk.END, "")  # Dòng trống giữa các kịch bản
    else:
        # Hiển thị templates thường (khi không có scenario_metadata)
        for i, tpl in enumerate(state.templates):
            if tpl["type"] == "image":
                delay_str = f" [delay {tpl.get('delay', state.click_delay)}s]"
                wait_str = " [⏳ CHỜ]" if tpl.get("wait_until_found", False) else ""
                is_detection = tpl.get("is_detection", False)

                if is_detection:
                    state.UI.history_list.insert(tk.END, f"{i+1}. 🔍 [DETECTION] {tpl['path']}{wait_str}")
                else:
                    state.UI.history_list.insert(tk.END, f"{i+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}{wait_str}")
            elif tpl["type"] == "key":
                delay_str = f" [delay {tpl.get('delay', state.click_delay)}s]"
                state.UI.history_list.insert(tk.END, f"{i+1}. ⌨️ {tpl['path']} (nhấn {tpl['repeat']} lần){delay_str}")
            else:
                delay_str = f" [delay {tpl.get('delay', state.click_delay)}s]"
                state.UI.history_list.insert(tk.END, f"{i+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}")

    # Cập nhật setup info
    if state.scenario_metadata:
        setup_text = f"📋 Tổng {len(state.scenario_metadata)} kịch bản"
    elif state.infinite_loop:
        setup_text = f"🔄 Vòng lặp: ∞ (Vô hạn)  |  ⚡ Tốc độ: {state.click_delay}s"
    else:
        setup_text = f"🔄 Vòng lặp: {state.process_loops}  |  ⚡ Tốc độ: {state.click_delay}s"

    # Thêm phạm vi tìm kiếm nếu được set
    if state.search_region_enabled:
        region_text = f"  |  🔎 Phạm vi: ({state.search_region['x1']},{state.search_region['y1']})→({state.search_region['x2']},{state.search_region['y2']})"
        setup_text += region_text

    state.UI.setup_info_text.set(setup_text)


def add_image():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("All files","*.*")])
    if file_path:
        img = imread_unicode(file_path)
        if img is None:
            state.UI.status_label.config(text="⚠️ Không đọc được ảnh.")
            return
        w, h = img.shape[::-1]

        config = show_image_config_dialog(is_detection=False)
        if config is None:
            return

        if state.current_library_game and state.current_library_stage:
            new_name = copy_image_to_stage(
                state.current_library_game,
                state.current_library_stage,
                file_path,
            )
            file_path = os.path.join(
                SCENARIOS_ROOT,
                state.current_library_game,
                state.current_library_stage,
                new_name,
            )

        state.templates.append({
            "type": "image",
            "img": img,
            "w": w,
            "h": h,
            "repeat": config["repeat"],
            "delay": config["delay"],
            "path": file_path,
            "wait_until_found": config["wait_until_found"],
            "wait_timeout": config.get("wait_timeout", 0),
            "is_detection": False,
            "threshold": config["threshold"],
            "click_delay": config["click_delay"],
            "click_type": config["click_type"]
        })
        update_history()


def add_coordinate():
    config = show_coordinate_config_dialog()
    if config is None:
        return
    state.templates.append({
        "type": "coord",
        "x": config["x"],
        "y": config["y"],
        "repeat": config["repeat"],
        "click_type": config["click_type"],
        "delay_after": config["delay_after"],
        "path": f"({config['x']},{config['y']})"
    })
    update_history()


def add_current_position():
    state.UI.status_label.config(text="⏳ Di chuột tới vị trí muốn lấy (3 giây)...")
    state.UI.root.update()
    time.sleep(3)
    x, y = pyautogui.position()

    config = show_coordinate_config_dialog()
    if config is None:
        return

    # Ghi đè tọa độ X, Y từ vị trí hiện tại
    config["x"] = x
    config["y"] = y

    state.templates.append({
        "type": "coord",
        "x": config["x"],
        "y": config["y"],
        "repeat": config["repeat"],
        "click_type": config["click_type"],
        "delay_after": config["delay_after"],
        "path": f"({config['x']},{config['y']})"
    })
    update_history()
    state.UI.status_label.config(text=f"✅ Đã thêm tọa độ ({config['x']},{config['y']}) ({config['click_type']}, delay {config['delay_after']}s)")


def add_keyboard_key():
    """Thêm hành động nhấn phím vào kịch bản"""
    config = show_keyboard_config_dialog()
    if config is None:
        return

    state.templates.append({
        "type": "key",
        "key": config["key"],
        "repeat": config["repeat"],
        "key_type": config["key_type"],
        "delay_after": config["delay_after"],
        "path": f"[KEY: {config['key']}]"
    })
    update_history()
    state.UI.status_label.config(text=f"✅ Đã thêm phím: {config['key']} ({config['key_type']}, delay {config['delay_after']}s)")


def set_search_region():
    """Đặt phạm vi tìm kiếm hình ảnh bằng cách kéo chuột"""
    # Tạo cửa sổ overlay để người dùng kéo chọn phạm vi
    overlay_window = tk.Toplevel(state.UI.root)
    overlay_window.attributes('-alpha', 0.3)  # Trong suốt 30%
    overlay_window.attributes('-topmost', True)
    overlay_window.configure(bg='blue')

    # Lấy kích thước màn hình
    screen_width = state.UI.root.winfo_screenwidth()
    screen_height = state.UI.root.winfo_screenheight()
    overlay_window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Canvas để vẽ hình chữ nhật
    canvas = tk.Canvas(overlay_window, bg='blue', highlightthickness=0, cursor="crosshair")
    canvas.pack(fill="both", expand=True)

    # Biến lưu tọa độ
    coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0, "rect": None}

    def on_mouse_down(event):
        coords["x1"] = event.x
        coords["y1"] = event.y

    def on_mouse_drag(event):
        coords["x2"] = event.x
        coords["y2"] = event.y

        # Xóa hình chữ nhật cũ
        if coords["rect"]:
            canvas.delete(coords["rect"])

        # Vẽ hình chữ nhật mới
        x1, y1 = min(coords["x1"], coords["x2"]), min(coords["y1"], coords["y2"])
        x2, y2 = max(coords["x1"], coords["x2"]), max(coords["y1"], coords["y2"])
        coords["rect"] = canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)

        # Hiển thị tọa độ
        canvas.delete("text")
        canvas.create_text(x1 + 10, y1 + 10, text=f"({x1},{y1}) → ({x2},{y2})",
                          fill="yellow", font=("Arial", 12, "bold"), anchor="nw", tags="text")

    def on_mouse_up(event):
        x1, y1 = min(coords["x1"], coords["x2"]), min(coords["y1"], coords["y2"])
        x2, y2 = max(coords["x1"], coords["x2"]), max(coords["y1"], coords["y2"])

        if x1 != x2 and y1 != y2:
            state.search_region["x1"] = x1
            state.search_region["y1"] = y1
            state.search_region["x2"] = x2
            state.search_region["y2"] = y2
            state.UI.status_label.config(text=f"🔍 Phạm vi tìm kiếm: ({x1},{y1}) → ({x2},{y2})")
            # Cập nhật biến toàn cục
            state.search_region_enabled = True
        else:
            state.UI.status_label.config(text="🔍 Phạm vi tìm kiếm: Toàn màn hình")
            state.search_region_enabled = False

        update_history()  # Cập nhật Pokédex
        overlay_window.destroy()

    def on_escape(event):
        state.UI.status_label.config(text="🔍 Phạm vi tìm kiếm: Toàn màn hình")
        state.search_region_enabled = False
        overlay_window.destroy()

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    overlay_window.bind("<Escape>", on_escape)

    state.UI.status_label.config(text="🔍 Kéo chuột để chọn phạm vi tìm kiếm (ESC để hủy)")


def set_process_loops():
    # Hỏi người dùng có muốn vòng lặp vô hạn không
    response = simpledialog.askstring(
        "Vòng lặp",
        "Nhập số vòng lặp (hoặc 'vô hạn' / '∞' để lặp cho đến khi bấm dừng):",
        initialvalue="1"
    )

    if response is None:
        return

    response = response.strip().lower()

    if response in ['vô hạn', '∞', 'infinite', 'inf']:
        state.infinite_loop = True
        state.process_loops = 999999  # Set to a very large number
        state.UI.status_label.config(text="🔄 Đã đặt vòng lặp: ∞ (Vô hạn - chạy cho đến khi bấm dừng)")
    else:
        try:
            loops = int(response)
            if loops < 1:
                state.UI.status_label.config(text="⚠️ Số vòng lặp phải >= 1")
                return
            state.infinite_loop = False
            state.process_loops = loops
            state.UI.status_label.config(text=f"🔄 Đã đặt {state.process_loops} vòng lặp cho toàn bộ quá trình.")
        except ValueError:
            state.UI.status_label.config(text="⚠️ Vui lòng nhập số hoặc 'vô hạn'")

    update_history()


def set_speed():
    delay = simpledialog.askfloat("Tốc độ", "Nhập thời gian nghỉ giữa các click (giây):", minvalue=0.1, maxvalue=5.0)
    if delay is None: return
    state.click_delay = delay
    state.UI.status_label.config(text=f"⏩ Đã đặt tốc độ: {state.click_delay} giây giữa các click")


def toggle_human_click():
    """Bật/tắt chế độ rê chuột human-like"""
    state.human_click_mode = not state.human_click_mode
    label = "🧍 Rê chuột Human-like: BẬT" if state.human_click_mode else "🤖 Click tức thì: BẬT"
    try:
        state.UI.btn_human_mode.config(text=label)
    except Exception:
        pass
    state.UI.status_label.config(text=f"✅ Đã chuyển chế độ click: {'Human-like (rê chuột)' if state.human_click_mode else 'Click tức thì (cũ)'}")


def test_image_matching():
    """Test tìm kiếm ảnh trên màn hình hiện tại"""
    if not state.templates:
        state.UI.status_label.config(text="⚠️ Chưa thêm ảnh nào!")
        return

    # Lấy ảnh cuối cùng được thêm
    tpl = state.templates[-1]
    if tpl["type"] != "image":
        state.UI.status_label.config(text="⚠️ Mục cuối cùng không phải ảnh!")
        return

    full_screenshot = capture_screen_gray()
    screenshot, (offset_x, offset_y) = get_search_region_screenshot(full_screenshot)
    res, used_scale, tpl_w, tpl_h = multi_scale_match(screenshot, tpl["img"])
    threshold = tpl.get("threshold", 0.7)

    # Tìm tất cả matches
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))
    filtered_points = filter_close_points(points, min_dist=max(10, tpl_w//2))

    # Tìm max score
    max_score = np.max(res) if res.size > 0 else 0

    if filtered_points:
        state.UI.status_label.config(text=f"✅ Tìm được {len(filtered_points)} match(es)! Max score: {max_score:.4f} (scale {used_scale:.2f}x)")
        safe_print(f"🧪 [TEST] Found {len(filtered_points)} matches for {tpl['path']} at scale {used_scale:.2f}x")
        safe_print(f"🧪 [TEST] Max score: {max_score:.4f}, Threshold: {threshold}")
        for i, pt in enumerate(filtered_points):
            safe_print(f"🧪 [TEST] Match {i+1}: ({pt[0]}, {pt[1]})")
    else:
        state.UI.status_label.config(text=f"❌ Không tìm được! Max score: {max_score:.4f} < Threshold: {threshold}")
        safe_print(f"🧪 [TEST] No matches found for {tpl['path']}")
        safe_print(f"🧪 [TEST] Max score: {max_score:.4f}, Threshold: {threshold}")
        safe_print(f"🧪 [TEST] Hãy thử giảm threshold hoặc kiểm tra ảnh")


def delete_selected():
    selected = state.UI.history_list.curselection()
    if not selected: return
    index = selected[0]
    selected_text = state.UI.history_list.get(index)

    # Xóa từ templates
    if 0 <= index < len(state.templates):
        state.templates.pop(index)
        state.UI.status_label.config(text="🗑️ Đã xóa mục khỏi danh sách.")

    update_history()


def clear_all_items():
    """Xóa toàn bộ mục trong kịch bản hiện tại"""
    if not state.templates:
        state.UI.status_label.config(text="⚠️ Không có mục nào để xóa.")
        return

    if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa toàn bộ mục trong kịch bản này?\n\nHành động này không thể hoàn tác!"):
        state.templates = []
        update_history()
        state.UI.status_label.config(text="🗑️ Đã xóa toàn bộ mục khỏi kịch bản.")


def edit_delay():
    selected = state.UI.history_list.curselection()
    if not selected: return
    index = selected[0]
    selected_text = state.UI.history_list.get(index)

    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        state.UI.status_label.config(text="⚠️ Không thể edit delay của old detection item.")
        return

    # Kiểm tra xem có phải detection item trong templates không
    if "[DETECTION]" in selected_text:
        # Cho phép edit delay của detection items
        if 0 <= index < len(state.templates):
            new_delay = simpledialog.askfloat("Chỉnh sửa Delay", f"Nhập delay mới (hiện tại: {state.templates[index].get('delay', 0.5)}s):", minvalue=0.1, maxvalue=10.0)
            if new_delay is not None:
                state.templates[index]["delay"] = new_delay
                update_history()
                state.UI.status_label.config(text=f"✍️ Đã chỉnh sửa delay thành {new_delay}s")
        return

    # Edit delay của templates thường
    if 0 <= index < len(state.templates):
        new_delay = simpledialog.askfloat("Chỉnh sửa Delay", f"Nhập delay mới (hiện tại: {state.templates[index].get('delay', state.click_delay)}s):", minvalue=0.1, maxvalue=10.0)
        if new_delay is not None:
            state.templates[index]["delay"] = new_delay
            update_history()
            state.UI.status_label.config(text=f"✍️ Đã chỉnh sửa delay thành {new_delay}s")


def edit_image_config():
    """Chỉnh sửa tất cả thông số của ảnh, tọa độ, hoặc phím đã thêm"""
    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="⚠️ Vui lòng chọn một mục để chỉnh sửa.")
        return

    index = selected[0]
    selected_text = state.UI.history_list.get(index)

    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        state.UI.status_label.config(text="⚠️ Không thể edit old detection items. Hãy xóa và thêm lại.")
        return

    # Tính toán index thực tế trong templates (bỏ qua old detection items)
    actual_index = index
    for i in range(index):
        if "[OLD DETECTION]" in state.UI.history_list.get(i):
            actual_index -= 1

    # Kiểm tra loại item
    if not (0 <= actual_index < len(state.templates)):
        state.UI.status_label.config(text="⚠️ Không thể chỉnh sửa mục này.")
        return

    item_type = state.templates[actual_index]["type"]

    # Xử lý ảnh
    if item_type == "image":
        tpl = state.templates[actual_index]

        # Tạo dialog chỉnh sửa
        dialog = tk.Toplevel(state.UI.root)
        dialog.title("✏️ Chỉnh sửa ảnh")
        dialog.geometry("550x700")
        dialog.minsize(500, 600)
        dialog.resizable(True, True)

        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        title_label = tk.Label(header_frame, text="✏️ Chỉnh sửa ảnh", font=("Segoe UI", 14, "bold"),
                               bg=PKM_BG_INNER, fg=PKM_YELLOW)
        title_label.pack(pady=15)

        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        fields = {}

        # Số lần lặp
        tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        repeat_var = tk.StringVar(value=str(tpl.get("repeat", 1)))
        repeat_entry = tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
        repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["repeat"] = repeat_var

        # Delay trước
        tk.Label(content_frame, text="⏱️ Delay trước (giây):", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        delay_var = tk.StringVar(value=str(tpl.get("delay", state.click_delay)))
        delay_entry = tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40)
        delay_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["delay"] = delay_var

        # Loại click
        tk.Label(content_frame, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        click_type_var = tk.StringVar(value=tpl.get("click_type", "single"))
        click_type_combo = tk.OptionMenu(content_frame, click_type_var, "single", "double", "hold")
        click_type_combo.config(font=("Segoe UI", 11), bg="white", fg="black",
                               activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
        click_type_combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["click_type"] = click_type_var

        # Delay sau click
        tk.Label(content_frame, text="⏳ Delay sau click (giây):", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        click_delay_var = tk.StringVar(value=str(tpl.get("click_delay", 0.5)))
        click_delay_entry = tk.Entry(content_frame, textvariable=click_delay_var, font=("Segoe UI", 11), width=40)
        click_delay_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["click_delay"] = click_delay_var

        # Threshold
        tk.Label(content_frame, text="🎯 Threshold (0.0-1.0):", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        threshold_var = tk.StringVar(value=str(tpl.get("threshold", 0.7)))
        threshold_entry = tk.Entry(content_frame, textvariable=threshold_var, font=("Segoe UI", 11), width=40)
        threshold_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["threshold"] = threshold_var

        # Chờ cho đến khi tìm được
        tk.Label(content_frame, text="⏳ Chờ tìm được?:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))

        # Xác định giá trị hiện tại
        wait_timeout = tpl.get("wait_timeout", 0)
        if wait_timeout == -1:
            wait_choice = "vô cực"
        elif wait_timeout > 0:
            wait_choice = "có (30s)"
        else:
            wait_choice = "không"

        wait_var = tk.StringVar(value=wait_choice)
        wait_combo = tk.OptionMenu(content_frame, wait_var, "không", "có (30s)", "vô cực")
        wait_combo.config(font=("Segoe UI", 11), bg="white", fg="black",
                         activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
        wait_combo.pack(anchor="w", pady=(0, 25), fill=tk.X)
        fields["wait_until_found"] = wait_var

        result = {"ok": False}

        def on_ok(event=None):
            result["ok"] = True
            dialog.destroy()

        def on_cancel(event=None):
            result["ok"] = False
            dialog.destroy()

        ok_btn = tk.Button(button_frame, text="✅ Lưu", command=on_ok,
                           bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                           padx=30, pady=10, width=18)
        ok_btn.pack(side=tk.LEFT, padx=5, expand=True)

        cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel,
                              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
                              padx=30, pady=10, width=18)
        cancel_btn.pack(side=tk.LEFT, padx=5, expand=True)

        dialog.bind("<Return>", on_ok)
        dialog.bind("<Escape>", on_cancel)
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        dialog.transient(state.UI.root)
        dialog.grab_set()
        state.UI.root.wait_window(dialog)

        if result["ok"]:
            try:
                tpl["repeat"] = int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1
                tpl["delay"] = float(fields["delay"].get()) if fields["delay"].get() else state.click_delay
                tpl["click_type"] = fields["click_type"].get()
                tpl["click_delay"] = float(fields["click_delay"].get()) if fields["click_delay"].get() else 0.5
                tpl["threshold"] = float(fields["threshold"].get()) if fields["threshold"].get() else 0.7

                wait_choice = fields["wait_until_found"].get()
                if wait_choice == "vô cực":
                    tpl["wait_until_found"] = True
                    tpl["wait_timeout"] = -1
                elif wait_choice == "có (30s)":
                    tpl["wait_until_found"] = True
                    tpl["wait_timeout"] = 30
                else:
                    tpl["wait_until_found"] = False
                    tpl["wait_timeout"] = 0

                # Cập nhật lại template trong danh sách
                state.templates[actual_index] = tpl
                update_history()
                state.UI.status_label.config(text="✅ Đã cập nhật thông số ảnh")
            except Exception as e:
                state.UI.status_label.config(text=f"⚠️ Lỗi: {e}")

    # Xử lý tọa độ
    elif item_type == "coord":
        tpl = state.templates[actual_index]
        config = show_coordinate_config_dialog()
        if config is not None:
            tpl["x"] = config["x"]
            tpl["y"] = config["y"]
            tpl["repeat"] = config["repeat"]
            tpl["click_type"] = config["click_type"]
            tpl["delay_after"] = config["delay_after"]
            tpl["path"] = f"({config['x']},{config['y']})"
            update_history()
            state.UI.status_label.config(text=f"✅ Đã cập nhật tọa độ ({config['x']},{config['y']})")

    # Xử lý phím
    elif item_type == "key":
        tpl = state.templates[actual_index]
        config = show_keyboard_config_dialog()
        if config is not None:
            tpl["key"] = config["key"]
            tpl["repeat"] = config["repeat"]
            tpl["key_type"] = config["key_type"]
            tpl["delay_after"] = config["delay_after"]
            tpl["path"] = f"[KEY: {config['key']}]"
            update_history()
            state.UI.status_label.config(text=f"✅ Đã cập nhật phím: {config['key']}")


def move_selected_up():
    selected = state.UI.history_list.curselection()
    if not selected: return
    index = selected[0]
    if index == 0: return

    selected_text = state.UI.history_list.get(index)

    # Nếu có scenario_metadata, di chuyển kịch bản
    if state.scenario_metadata:
        # Tìm scenario index từ selected index
        scenario_idx = 0
        current_line = 0
        for s_idx, metadata in enumerate(state.scenario_metadata):
            # Header line
            current_line += 3  # 3 dòng header (===, KỊCH BẢN, ===)
            # Items
            num_items = len(metadata["templates"])
            if current_line + num_items > index:
                scenario_idx = s_idx
                break
            current_line += num_items + 1  # +1 dòng trống

        if scenario_idx > 0:
            state.scenario_metadata[scenario_idx - 1], state.scenario_metadata[scenario_idx] = \
                state.scenario_metadata[scenario_idx], state.scenario_metadata[scenario_idx - 1]
            state.scenario_queue[scenario_idx - 1], state.scenario_queue[scenario_idx] = \
                state.scenario_queue[scenario_idx], state.scenario_queue[scenario_idx - 1]
            update_history()
            state.UI.status_label.config(text="⬆️ Đã chuyển kịch bản lên trên.")
        return

    # Xử lý templates thường
    selected_text = state.UI.history_list.get(index)

    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        state.UI.status_label.config(text="⚠️ Không thể di chuyển old detection items. Hãy xóa và thêm lại.")
        return

    # Kiểm tra xem item trước đó có phải old detection không
    prev_text = state.UI.history_list.get(index - 1)
    if "[OLD DETECTION]" in prev_text:
        state.UI.status_label.config(text="⚠️ Không thể di chuyển qua old detection items.")
        return

    # Tính toán index thực tế trong templates (bỏ qua old detection items)
    actual_index = index
    for i in range(index):
        if "[OLD DETECTION]" in state.UI.history_list.get(i):
            actual_index -= 1

    # Swap trong templates
    if 0 <= actual_index - 1 < len(state.templates) and 0 <= actual_index < len(state.templates):
        state.templates[actual_index - 1], state.templates[actual_index] = state.templates[actual_index], state.templates[actual_index - 1]
        state.UI.status_label.config(text="⬆️ Đã chuyển mục lên trên.")
        update_history()
        state.UI.history_list.selection_set(index - 1)


def move_selected_down():
    selected = state.UI.history_list.curselection()
    if not selected: return
    index = selected[0]

    selected_text = state.UI.history_list.get(index)

    # Nếu có scenario_metadata, di chuyển kịch bản
    if state.scenario_metadata:
        # Tìm scenario index từ selected index
        scenario_idx = 0
        current_line = 0
        for s_idx, metadata in enumerate(state.scenario_metadata):
            # Header line
            current_line += 3  # 3 dòng header (===, KỊCH BẢN, ===)
            # Items
            num_items = len(metadata["templates"])
            if current_line + num_items > index:
                scenario_idx = s_idx
                break
            current_line += num_items + 1  # +1 dòng trống

        if scenario_idx < len(state.scenario_metadata) - 1:
            state.scenario_metadata[scenario_idx], state.scenario_metadata[scenario_idx + 1] = \
                state.scenario_metadata[scenario_idx + 1], state.scenario_metadata[scenario_idx]
            state.scenario_queue[scenario_idx], state.scenario_queue[scenario_idx + 1] = \
                state.scenario_queue[scenario_idx + 1], state.scenario_queue[scenario_idx]
            update_history()
            state.UI.status_label.config(text="⬇️ Đã chuyển kịch bản xuống dưới.")
        return

    # Xử lý templates thường
    selected_text = state.UI.history_list.get(index)

    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        state.UI.status_label.config(text="⚠️ Không thể di chuyển old detection items. Hãy xóa và thêm lại.")
        return

    # Kiểm tra xem item tiếp theo có phải old detection không
    if index + 1 < state.UI.history_list.size():
        next_text = state.UI.history_list.get(index + 1)
        if "[OLD DETECTION]" in next_text:
            state.UI.status_label.config(text="⚠️ Không thể di chuyển qua old detection items.")
            return

    # Tính toán index thực tế trong templates (bỏ qua old detection items)
    actual_index = index
    for i in range(index):
        if "[OLD DETECTION]" in state.UI.history_list.get(i):
            actual_index -= 1

    # Swap trong templates
    if 0 <= actual_index < len(state.templates) and 0 <= actual_index + 1 < len(state.templates):
        state.templates[actual_index + 1], state.templates[actual_index] = state.templates[actual_index], state.templates[actual_index + 1]
        state.UI.status_label.config(text="⬇️ Đã chuyển mục xuống dưới.")
        update_history()
        state.UI.history_list.selection_set(index + 1)


def edit_scenario():
    """Chỉnh sửa kịch bản được chọn"""
    if not state.scenario_metadata:
        state.UI.status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return

    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="⚠️ Vui lòng chọn một item để xác định kịch bản.")
        return

    index = selected[0]
    selected_text = state.UI.history_list.get(index)

    # Tìm scenario index từ selected index
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(state.scenario_metadata):
        # Header line: 3 dòng (===, KỊCH BẢN, ===)
        current_line += 3
        # Items
        num_items = len(metadata["templates"])
        if num_items == 0:
            current_line += 1  # "(Không có item)"
        else:
            current_line += num_items
        # Dòng trống
        current_line += 1

        if current_line > index:
            scenario_idx = s_idx
            break

    if scenario_idx >= len(state.scenario_metadata):
        state.UI.status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return

    metadata = state.scenario_metadata[scenario_idx]
    scenario_name = os.path.basename(metadata["file_path"])

    # Tạo dialog chỉnh sửa kịch bản
    dialog = tk.Toplevel(state.UI.root)
    dialog.title(f"✏️ Chỉnh sửa kịch bản: {scenario_name}")
    dialog.geometry("550x450")
    dialog.minsize(500, 400)
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

    title_label = tk.Label(header_frame, text=f"✏️ Chỉnh sửa kịch bản: {scenario_name}",
                           font=("Segoe UI", 12, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = {}

    # Số vòng lặp
    tk.Label(content_frame, text="🔄 Số vòng lặp:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    loops_var = tk.StringVar(value=str(metadata.get("process_loops", 1)))
    loops_entry = tk.Entry(content_frame, textvariable=loops_var, font=("Segoe UI", 11), width=40)
    loops_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["process_loops"] = loops_var

    # Vòng lặp vô hạn
    infinite_var = tk.BooleanVar(value=metadata.get("infinite_loop", False))
    infinite_check = tk.Checkbutton(content_frame, text="∞ Vòng lặp vô hạn",
                                    variable=infinite_var, font=("Segoe UI", 11),
                                    bg="white", fg="black", activebackground="white", activeforeground="black")
    infinite_check.pack(anchor="w", pady=(0, 15))
    fields["infinite_loop"] = infinite_var

    # Tốc độ click
    tk.Label(content_frame, text="⚡ Tốc độ click (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    speed_var = tk.StringVar(value=str(metadata.get("click_delay", 1.0)))
    speed_entry = tk.Entry(content_frame, textvariable=speed_var, font=("Segoe UI", 11), width=40)
    speed_entry.pack(anchor="w", pady=(0, 25), fill=tk.X)
    fields["click_delay"] = speed_var

    result = {"ok": False}

    def on_ok(event=None):
        result["ok"] = True
        dialog.destroy()

    def on_cancel(event=None):
        result["ok"] = False
        dialog.destroy()

    ok_btn = tk.Button(button_frame, text="✅ Lưu", command=on_ok,
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5, expand=True)

    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel,
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5, expand=True)

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    dialog.transient(state.UI.root)
    dialog.grab_set()
    state.UI.root.wait_window(dialog)

    if result["ok"]:
        try:
            metadata["process_loops"] = int(fields["process_loops"].get()) if fields["process_loops"].get().isdigit() else 1
            metadata["infinite_loop"] = fields["infinite_loop"].get()
            metadata["click_delay"] = float(fields["click_delay"].get()) if fields["click_delay"].get() else 1.0

            update_history()
            state.UI.status_label.config(text=f"✅ Đã cập nhật kịch bản: {scenario_name}")
        except Exception as e:
            state.UI.status_label.config(text=f"⚠️ Lỗi: {e}")


def delete_selected_scenario():
    """Xóa kịch bản được chọn"""
    if not state.scenario_metadata:
        state.UI.status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return

    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="⚠️ Vui lòng chọn một item để xác định kịch bản.")
        return

    index = selected[0]

    # Tìm scenario index từ selected index
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(state.scenario_metadata):
        # Header line: 3 dòng (===, KỊCH BẢN, ===)
        current_line += 3
        # Items
        num_items = len(metadata["templates"])
        if num_items == 0:
            current_line += 1  # "(Không có item)"
        else:
            current_line += num_items
        # Dòng trống
        current_line += 1

        if current_line > index:
            scenario_idx = s_idx
            break

    if scenario_idx >= len(state.scenario_metadata):
        state.UI.status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return

    scenario_name = os.path.basename(state.scenario_metadata[scenario_idx]["file_path"])

    # Xác nhận xóa
    if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa kịch bản '{scenario_name}'?"):
        state.scenario_metadata.pop(scenario_idx)
        state.scenario_queue.pop(scenario_idx)
        update_history()
        state.UI.status_label.config(text=f"🗑️ Đã xóa kịch bản: {scenario_name}")


def edit_scenario_details():
    """Edit chi tiết kịch bản - chỉnh sửa từng ảnh, thêm/xóa ảnh"""
    if not state.scenario_metadata:
        state.UI.status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return

    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="⚠️ Vui lòng chọn một item để xác định kịch bản.")
        return

    index = selected[0]

    # Tìm scenario index từ selected index
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(state.scenario_metadata):
        current_line += 3  # Header
        num_items = len(metadata["templates"])
        if num_items == 0:
            current_line += 1
        else:
            current_line += num_items
        current_line += 1  # Dòng trống

        if current_line > index:
            scenario_idx = s_idx
            break

    if scenario_idx >= len(state.scenario_metadata):
        state.UI.status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return

    metadata = state.scenario_metadata[scenario_idx]
    scenario_name = os.path.basename(metadata["file_path"])

    # Tạo dialog chỉnh sửa chi tiết
    dialog = tk.Toplevel(state.UI.root)
    dialog.title(f"✏️ Edit Kịch Bản: {scenario_name}")
    dialog.geometry("700x600")
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    # Header
    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

    title_label = tk.Label(header_frame, text=f"✏️ Edit Kịch Bản: {scenario_name}",
                           font=("Segoe UI", 12, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)

    # Button frame (đặt ở đáy trước để không bị content đẩy ra ngoài)
    button_frame = tk.Frame(main_frame, bg=PKM_BG_CARD)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 15))

    # Content frame
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Danh sách ảnh
    tk.Label(content_frame, text="📋 Danh sách ảnh trong kịch bản:",
             font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(0, 10))

    # Listbox với scrollbar
    list_frame = tk.Frame(content_frame, bg="white")
    list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    scrollbar = tk.Scrollbar(list_frame, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    template_list = tk.Listbox(list_frame, font=("Segoe UI", 9),
                               bg=PKM_BG_INNER, fg=PKM_WHITE,
                               selectbackground=PKM_GOLD, selectforeground=PKM_BG_DARK,
                               yscrollcommand=scrollbar.set, height=12)
    template_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=template_list.yview)

    # Populate listbox
    for idx, tpl in enumerate(metadata["templates"]):
        if tpl["type"] == "image":
            display_text = f"{idx+1}. 🖼️ {os.path.basename(tpl['path'])} (threshold: {tpl.get('threshold', 0.7)})"
        elif tpl["type"] == "key":
            display_text = f"{idx+1}. ⌨️ {tpl['path']}"
        else:
            display_text = f"{idx+1}. 📍 {tpl['path']}"
        template_list.insert(tk.END, display_text)

    def edit_selected_template():
        sel = template_list.curselection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một ảnh để chỉnh sửa.")
            return

        tpl_idx = sel[0]
        tpl = metadata["templates"][tpl_idx]

        if tpl["type"] != "image":
            messagebox.showinfo("Thông báo", "Chỉ có thể chỉnh sửa ảnh.")
            return

        # Tạo dialog chỉnh sửa ảnh
        edit_dialog = tk.Toplevel(dialog)
        edit_dialog.title(f"✏️ Chỉnh sửa ảnh: {os.path.basename(tpl['path'])}")
        edit_dialog.geometry("550x700")
        edit_dialog.minsize(500, 600)
        edit_dialog.resizable(True, True)

        edit_main = tk.Frame(edit_dialog, bg="white")
        edit_main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        edit_header = tk.Frame(edit_main, bg=PKM_BG_INNER)
        edit_header.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        edit_title = tk.Label(edit_header, text=f"✏️ Chỉnh sửa ảnh",
                             font=("Segoe UI", 12, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW)
        edit_title.pack(pady=15)

        edit_button_frame = tk.Frame(edit_main, bg="white")
        edit_button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

        edit_content = tk.Frame(edit_main, bg="white")
        edit_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        fields = {}

        # Số lần click
        tk.Label(edit_content, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        repeat_var = tk.StringVar(value=str(tpl.get("repeat", 1)))
        repeat_entry = tk.Entry(edit_content, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
        repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["repeat"] = repeat_var

        # Delay trước
        tk.Label(edit_content, text="⏱️ Delay trước (giây):", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        delay_var = tk.StringVar(value=str(tpl.get("delay", 1.0)))
        delay_entry = tk.Entry(edit_content, textvariable=delay_var, font=("Segoe UI", 11), width=40)
        delay_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["delay"] = delay_var

        # Loại click
        tk.Label(edit_content, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        click_type_var = tk.StringVar(value=tpl.get("click_type", "single"))
        click_type_combo = tk.OptionMenu(edit_content, click_type_var, "single", "double", "hold")
        click_type_combo.config(font=("Segoe UI", 11), bg="white", fg="black", width=37)
        click_type_combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["click_type"] = click_type_var

        # Delay sau click
        tk.Label(edit_content, text="⏳ Delay sau click (giây):", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        click_delay_var = tk.StringVar(value=str(tpl.get("click_delay", 0.5)))
        click_delay_entry = tk.Entry(edit_content, textvariable=click_delay_var, font=("Segoe UI", 11), width=40)
        click_delay_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["click_delay"] = click_delay_var

        # Threshold
        tk.Label(edit_content, text="🎯 Threshold (0.0-1.0):", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        threshold_var = tk.StringVar(value=str(tpl.get("threshold", 0.7)))
        threshold_entry = tk.Entry(edit_content, textvariable=threshold_var, font=("Segoe UI", 11), width=40)
        threshold_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields["threshold"] = threshold_var

        # Chờ tìm được
        tk.Label(edit_content, text="⏳ Chờ tìm được?:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="black").pack(anchor="w", pady=(10, 3))

        wait_timeout = tpl.get("wait_timeout", 0)
        if wait_timeout == -1:
            wait_choice = "vô cực"
        elif wait_timeout > 0:
            wait_choice = "có (30s)"
        else:
            wait_choice = "không"

        wait_var = tk.StringVar(value=wait_choice)
        wait_combo = tk.OptionMenu(edit_content, wait_var, "không", "có (30s)", "vô cực")
        wait_combo.config(font=("Segoe UI", 11), bg="white", fg="black", width=37)
        wait_combo.pack(anchor="w", pady=(0, 25), fill=tk.X)
        fields["wait_until_found"] = wait_var

        def on_ok(event=None):
            try:
                tpl["repeat"] = int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1
                tpl["delay"] = float(fields["delay"].get()) if fields["delay"].get() else 1.0
                tpl["click_type"] = fields["click_type"].get()
                tpl["click_delay"] = float(fields["click_delay"].get()) if fields["click_delay"].get() else 0.5
                tpl["threshold"] = float(fields["threshold"].get()) if fields["threshold"].get() else 0.7

                wait_choice = fields["wait_until_found"].get()
                if wait_choice == "vô cực":
                    tpl["wait_until_found"] = True
                    tpl["wait_timeout"] = -1
                elif wait_choice == "có (30s)":
                    tpl["wait_until_found"] = True
                    tpl["wait_timeout"] = 30
                else:
                    tpl["wait_until_found"] = False
                    tpl["wait_timeout"] = 0

                # Cập nhật listbox
                display_text = f"{tpl_idx+1}. 🖼️ {os.path.basename(tpl['path'])} (threshold: {tpl.get('threshold', 0.7)})"
                template_list.delete(tpl_idx)
                template_list.insert(tpl_idx, display_text)

                edit_dialog.destroy()
                messagebox.showinfo("Thành công", "Đã cập nhật ảnh.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {e}")

        ok_btn = tk.Button(edit_button_frame, text="✅ Lưu", command=on_ok,
                          bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                          padx=30, pady=10, width=18)
        ok_btn.pack(side=tk.LEFT, padx=5, expand=True)

        cancel_btn = tk.Button(edit_button_frame, text="❌ Hủy", command=edit_dialog.destroy,
                              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
                              padx=30, pady=10, width=18)
        cancel_btn.pack(side=tk.LEFT, padx=5, expand=True)

        edit_dialog.bind("<Return>", on_ok)
        edit_dialog.bind("<Escape>", lambda e: edit_dialog.destroy())
        edit_dialog.protocol("WM_DELETE_WINDOW", edit_dialog.destroy)

    def delete_selected_template():
        sel = template_list.curselection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một ảnh để xóa.")
            return

        tpl_idx = sel[0]
        if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa ảnh này?"):
            metadata["templates"].pop(tpl_idx)
            template_list.delete(tpl_idx)
            messagebox.showinfo("Thành công", "Đã xóa ảnh.")

    def add_new_template():
        file_path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("All files","*.*")])
        if file_path:
            img = imread_unicode(file_path)
            if img is None:
                messagebox.showerror("Lỗi", "Không đọc được ảnh.")
                return

            w, h = img.shape[::-1]
            metadata["templates"].append({
                "type": "image",
                "img": img,
                "w": w,
                "h": h,
                "repeat": 1,
                "delay": 1.0,
                "path": file_path,
                "wait_until_found": False,
                "wait_timeout": 0,
                "is_detection": False,
                "threshold": 0.7,
                "click_delay": 0.5,
                "click_type": "single"
            })

            idx = len(metadata["templates"]) - 1
            display_text = f"{idx+1}. 🖼️ {os.path.basename(file_path)} (threshold: 0.7)"
            template_list.insert(tk.END, display_text)
            messagebox.showinfo("Thành công", "Đã thêm ảnh.")

    # Định nghĩa các hàm di chuyển trước
    def move_template_up():
        sel = template_list.curselection()
        if not sel or sel[0] == 0:
            messagebox.showwarning("Cảnh báo", "Không thể di chuyển lên.")
            return

        idx = sel[0]
        metadata["templates"][idx-1], metadata["templates"][idx] = metadata["templates"][idx], metadata["templates"][idx-1]

        # Cập nhật listbox
        item1 = template_list.get(idx-1)
        item2 = template_list.get(idx)
        template_list.delete(idx-1, idx)
        template_list.insert(idx-1, item2)
        template_list.insert(idx, item1)
        template_list.selection_set(idx-1)
        messagebox.showinfo("Thành công", "Đã di chuyển lên.")

    def move_template_down():
        sel = template_list.curselection()
        if not sel or sel[0] == template_list.size() - 1:
            messagebox.showwarning("Cảnh báo", "Không thể di chuyển xuống.")
            return

        idx = sel[0]
        metadata["templates"][idx], metadata["templates"][idx+1] = metadata["templates"][idx+1], metadata["templates"][idx]

        # Cập nhật listbox
        item1 = template_list.get(idx)
        item2 = template_list.get(idx+1)
        template_list.delete(idx, idx+1)
        template_list.insert(idx, item2)
        template_list.insert(idx+1, item1)
        template_list.selection_set(idx+1)
        messagebox.showinfo("Thành công", "Đã di chuyển xuống.")

    # Buttons - Sắp xếp thành 2 hàng để đều cỡ
    button_row1 = tk.Frame(button_frame, bg=PKM_BG_CARD)
    button_row1.pack(fill="x", pady=5)

    btn_edit = tk.Button(button_row1, text="✏️ Edit Ảnh", command=edit_selected_template,
                        bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"),
                        padx=15, pady=8)
    btn_edit.pack(side=tk.LEFT, fill="x", expand=True, padx=3)

    btn_up = tk.Button(button_row1, text="⬆️ Lên", command=move_template_up,
                      bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"),
                      padx=15, pady=8)
    btn_up.pack(side=tk.LEFT, fill="x", expand=True, padx=3)

    btn_down = tk.Button(button_row1, text="⬇️ Xuống", command=move_template_down,
                        bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"),
                        padx=15, pady=8)
    btn_down.pack(side=tk.LEFT, fill="x", expand=True, padx=3)

    btn_delete = tk.Button(button_row1, text="🗑️ Xóa Ảnh", command=delete_selected_template,
                          bg=PKM_RED, fg=PKM_WHITE, font=("Segoe UI", 10, "bold"),
                          padx=15, pady=8)
    btn_delete.pack(side=tk.LEFT, fill="x", expand=True, padx=3)

    button_row2 = tk.Frame(button_frame, bg=PKM_BG_CARD)
    button_row2.pack(fill="x", pady=5)

    btn_add = tk.Button(button_row2, text="➕ Thêm Ảnh", command=add_new_template,
                       bg=PKM_GREEN, fg=PKM_BG_DARK, font=("Segoe UI", 10, "bold"),
                       padx=15, pady=8)
    btn_add.pack(side=tk.LEFT, fill="x", expand=True, padx=3)

    # Close button
    close_btn = tk.Button(button_row2, text="✅ Đóng", command=lambda: [dialog.destroy(), update_history()],
                         bg=PKM_BLUE, fg=PKM_WHITE, font=("Segoe UI", 10, "bold"),
                         padx=15, pady=8)
    close_btn.pack(side=tk.RIGHT, fill="x", expand=True, padx=3)
