import os
import time
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

import numpy as np
import pyautogui
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

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
    show_image_source_dialog,
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


def _autosave_to_library():
    """Khi editor đang gắn với 1 stage trong library, tự ghi state.templates vào JSON của stage đó."""
    if state.scenario_metadata:
        return  # queue mode - không autosave
    if not (state.current_library_game and state.current_library_stage):
        return
    try:
        from scenario.io import save_scenario_to_stage
        save_scenario_to_stage(state.current_library_game, state.current_library_stage)
    except Exception as exc:
        safe_print(f"⚠️ Auto-save thất bại: {exc}")


def _create_scrollable_form(parent, bg="white"):
    """Tạo vùng cuộn dọc trong parent. Trả về (container, inner_frame).
    Pack `container` bằng side=TOP/fill=BOTH/expand=True; thêm widget vào `inner_frame`."""
    container = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)

    def _on_inner_configure(_event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner.bind("<Configure>", _on_inner_configure)

    def _on_canvas_configure(event):
        canvas.itemconfig(inner_id, width=event.width)
    canvas.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))

    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return container, inner


def _resolve_selection_context(index):
    """Map line index trong history_list về context:
      ('scenario_header', s_idx)
      ('scenario_item', s_idx, t_idx)
      ('editor_item', t_idx)
      ('none',)
    """
    if state.scenario_metadata:
        cursor = 0
        for s_idx, metadata in enumerate(state.scenario_metadata):
            # 3 dòng header: === / KỊCH BẢN N / ===
            if cursor <= index < cursor + 3:
                return ("scenario_header", s_idx)
            cursor += 3
            num_items = len(metadata["templates"])
            if num_items == 0:
                if index == cursor:
                    return ("scenario_header", s_idx)
                cursor += 1
            else:
                if cursor <= index < cursor + num_items:
                    return ("scenario_item", s_idx, index - cursor)
                cursor += num_items
            # blank line
            if index == cursor:
                return ("none",)
            cursor += 1
        return ("none",)
    if 0 <= index < len(state.templates):
        return ("editor_item", index)
    return ("none",)


def _get_template_storage_dir(metadata=None):
    if metadata and metadata.get("file_path"):
        return os.path.dirname(metadata["file_path"])
    if state.current_library_game and state.current_library_stage:
        return os.path.join(SCENARIOS_ROOT, state.current_library_game, state.current_library_stage)
    return os.path.join(SCENARIOS_ROOT, "_captured")


def _next_capture_path(storage_dir):
    os.makedirs(storage_dir, exist_ok=True)
    index = 1
    while True:
        candidate = os.path.join(storage_dir, f"capture_{index}.png")
        if not os.path.exists(candidate):
            return candidate
        index += 1


def _choose_import_image_path():
    return filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])


def _prepare_imported_image_path(file_path, metadata=None):
    if not file_path:
        return None
    if metadata is not None:
        return file_path
    if state.current_library_game and state.current_library_stage:
        new_name = copy_image_to_stage(
            state.current_library_game,
            state.current_library_stage,
            file_path,
        )
        return os.path.join(
            SCENARIOS_ROOT,
            state.current_library_game,
            state.current_library_stage,
            new_name,
        )
    return file_path


def _default_search_region():
    return {"x1": 0, "y1": 0, "x2": 0, "y2": 0}


def _normalize_search_region(region):
    if not region:
        return _default_search_region()
    try:
        x1 = int(region.get("x1", 0))
        y1 = int(region.get("y1", 0))
        x2 = int(region.get("x2", 0))
        y2 = int(region.get("y2", 0))
    except (AttributeError, TypeError, ValueError):
        return _default_search_region()
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def _get_click_point_defaults(tpl, width, height):
    click_x = int(tpl.get("click_x", width // 2) or width // 2)
    click_y = int(tpl.get("click_y", height // 2) or height // 2)
    click_x = max(0, min(click_x, max(0, width - 1)))
    click_y = max(0, min(click_y, max(0, height - 1)))
    return click_x, click_y


def _template_image_flags(tpl):
    flags = [f"threshold:{tpl.get('threshold', 0.7)}"]
    if tpl.get("wait_until_found", False):
        flags.append("wait")
    if tpl.get("search_region_enabled", False):
        flags.append("region")
    click_mode = tpl.get("click_point_mode", "center")
    flags.append(f"click:{'custom' if click_mode == 'custom' else 'center'}")
    return " | ".join(flags)


def capture_region_with_overlay(min_width=8, min_height=8, instruction_text="Keo chuot de cat anh mau. ESC de huy."):
    root = state.UI.root
    root.withdraw()
    root.update_idletasks()
    time.sleep(0.2)
    screenshot = pyautogui.screenshot()

    overlay = None
    result = {"bbox": None, "cancelled": True, "error": None}
    try:
        overlay = tk.Toplevel(root)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        screen_width, screen_height = screenshot.size
        overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        overlay.configure(bg="black")

        canvas = tk.Canvas(
            overlay,
            width=screen_width,
            height=screen_height,
            highlightthickness=0,
            cursor="crosshair",
        )
        canvas.pack(fill="both", expand=True)

        if ImageTk is not None:
            photo = ImageTk.PhotoImage(screenshot)
            canvas.create_image(0, 0, anchor="nw", image=photo)
            canvas.image = photo
        else:
            canvas.create_rectangle(0, 0, screen_width, screen_height, fill="black", outline="")

        canvas.create_rectangle(0, 0, screen_width, screen_height, fill="black", stipple="gray50", outline="")
        canvas.create_text(
            24,
            24,
            text=instruction_text,
            anchor="nw",
            fill="yellow",
            font=("Segoe UI", 14, "bold"),
        )

        coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0, "rect": None, "label": None}

        def _clear_label():
            if coords["label"] is not None:
                canvas.delete(coords["label"])
                coords["label"] = None

        def on_mouse_down(event):
            coords["x1"] = event.x
            coords["y1"] = event.y
            coords["x2"] = event.x
            coords["y2"] = event.y
            if coords["rect"] is not None:
                canvas.delete(coords["rect"])
            _clear_label()
            coords["rect"] = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="yellow", width=3)

        def on_mouse_drag(event):
            coords["x2"] = min(max(event.x, 0), screen_width)
            coords["y2"] = min(max(event.y, 0), screen_height)
            x1, y1 = min(coords["x1"], coords["x2"]), min(coords["y1"], coords["y2"])
            x2, y2 = max(coords["x1"], coords["x2"]), max(coords["y1"], coords["y2"])
            if coords["rect"] is None:
                coords["rect"] = canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
            else:
                canvas.coords(coords["rect"], x1, y1, x2, y2)
            _clear_label()
            coords["label"] = canvas.create_text(
                x1 + 8,
                max(8, y1 - 18),
                text=f"{x2 - x1}x{y2 - y1}",
                anchor="nw",
                fill="yellow",
                font=("Segoe UI", 11, "bold"),
            )

        def finish_selection():
            x1, y1 = min(coords["x1"], coords["x2"]), min(coords["y1"], coords["y2"])
            x2, y2 = max(coords["x1"], coords["x2"]), max(coords["y1"], coords["y2"])
            width = x2 - x1
            height = y2 - y1
            if width < min_width or height < min_height:
                result["error"] = f"Vung chup qua nho ({width}x{height}). Toi thieu {min_width}x{min_height}."
            else:
                result["bbox"] = (x1, y1, x2, y2)
                result["cancelled"] = False
            overlay.destroy()

        def on_mouse_up(_event):
            finish_selection()

        def on_escape(_event=None):
            result["cancelled"] = True
            overlay.destroy()

        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        overlay.bind("<Escape>", on_escape)
        overlay.focus_force()
        root.wait_window(overlay)
    finally:
        if overlay is not None and overlay.winfo_exists():
            overlay.destroy()
        root.deiconify()
        root.lift()
        root.focus_force()
        root.update_idletasks()

    if result["bbox"] is None:
        return None, None, result["error"]
    return screenshot.crop(result["bbox"]), result["bbox"], None


def _capture_image_to_path(metadata=None):
    cropped_image, _bbox, error = capture_region_with_overlay()
    if cropped_image is None:
        return None, error
    output_path = _next_capture_path(_get_template_storage_dir(metadata))
    try:
        cropped_image.save(output_path, format="PNG")
    except Exception as exc:
        return None, f"Khong luu duoc anh mau: {exc}"
    return output_path, None


def _pick_search_region_for_step(initial_region=None):
    _cropped_image, bbox, error = capture_region_with_overlay(
        min_width=20,
        min_height=20,
        instruction_text="Keo chuot de chon vung tim cho step. ESC de huy.",
    )
    if bbox is None:
        return _normalize_search_region(initial_region), error or "cancelled"
    return _normalize_search_region({"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]}), None


def _pick_click_point_in_template(file_path, initial_point=None):
    if Image is None or ImageTk is None:
        return initial_point, "Pillow khong kha dung de preview diem click."

    image = Image.open(file_path)
    width, height = image.size
    start_x = width // 2
    start_y = height // 2
    if initial_point:
        start_x = max(0, min(int(initial_point[0]), max(0, width - 1)))
        start_y = max(0, min(int(initial_point[1]), max(0, height - 1)))

    max_preview_w = 700
    max_preview_h = 520
    scale = min(max_preview_w / max(1, width), max_preview_h / max(1, height), 1.0)
    preview_w = max(1, int(round(width * scale)))
    preview_h = max(1, int(round(height * scale)))
    preview_image = image.resize((preview_w, preview_h), Image.LANCZOS) if scale != 1.0 else image.copy()

    dialog = tk.Toplevel(state.UI.root)
    dialog.title("Dat diem click trong anh")
    dialog.geometry(f"{max(420, preview_w + 40)}x{max(220, preview_h + 140)}")
    dialog.resizable(False, False)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        main_frame,
        text="Bam vao vi tri can click trong anh mau",
        font=("Segoe UI", 12, "bold"),
        bg="white",
        fg="black",
    ).pack(pady=(14, 8))

    canvas = tk.Canvas(main_frame, width=preview_w, height=preview_h, highlightthickness=1, highlightbackground="gray70", cursor="crosshair")
    canvas.pack(padx=20, pady=(0, 10))
    photo = ImageTk.PhotoImage(preview_image)
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo

    current = {"x": start_x, "y": start_y, "marker": None, "ok": False}
    info_var = tk.StringVar()

    def draw_marker():
        scaled_x = int(round(current["x"] * scale))
        scaled_y = int(round(current["y"] * scale))
        canvas.delete("click_marker")
        canvas.create_line(scaled_x - 10, scaled_y, scaled_x + 10, scaled_y, fill="red", width=2, tags="click_marker")
        canvas.create_line(scaled_x, scaled_y - 10, scaled_x, scaled_y + 10, fill="red", width=2, tags="click_marker")
        canvas.create_oval(scaled_x - 4, scaled_y - 4, scaled_x + 4, scaled_y + 4, outline="white", width=2, tags="click_marker")
        info_var.set(f"Diem click: ({current['x']}, {current['y']}) / {width}x{height}")

    def on_canvas_click(event):
        current["x"] = max(0, min(int(round(event.x / max(scale, 1e-9))), width - 1))
        current["y"] = max(0, min(int(round(event.y / max(scale, 1e-9))), height - 1))
        draw_marker()

    def use_center():
        current["x"] = width // 2
        current["y"] = height // 2
        draw_marker()

    def on_ok(event=None):
        current["ok"] = True
        dialog.destroy()

    def on_cancel(event=None):
        current["ok"] = False
        dialog.destroy()

    canvas.bind("<Button-1>", on_canvas_click)
    draw_marker()

    tk.Label(main_frame, textvariable=info_var, font=("Segoe UI", 10), bg="white", fg="black").pack(pady=(0, 10))

    button_row = tk.Frame(main_frame, bg="white")
    button_row.pack(fill=tk.X, padx=20, pady=(0, 16))
    tk.Button(button_row, text="Dat ve tam", command=use_center, bg=PKM_BLUE_DARK, fg=PKM_WHITE, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
    tk.Button(button_row, text="Luu", command=on_ok, bg=PKM_GREEN, fg="white", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
    tk.Button(button_row, text="Huy", command=on_cancel, bg=PKM_RED, fg="white", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    dialog.transient(state.UI.root)
    dialog.grab_set()
    state.UI.root.wait_window(dialog)

    if not current["ok"]:
        return initial_point, "cancelled"
    return (current["x"], current["y"]), None


def _show_step_image_config_dialog(file_path, initial=None):
    initial = initial or {}
    img = imread_unicode(file_path)
    if img is None:
        raise ValueError("Khong doc duoc anh.")
    width, height = img.shape[::-1]
    click_x, click_y = _get_click_point_defaults(initial, width, height)
    search_region = _normalize_search_region(initial.get("search_region"))
    click_point_mode = initial.get("click_point_mode", "center")
    search_region_enabled = bool(initial.get("search_region_enabled", False))

    root = state.UI.root
    dialog = tk.Toplevel(root)
    dialog.title("Cai dat anh")
    dialog.geometry("560x760")
    dialog.minsize(520, 680)
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X)
    tk.Label(header_frame, text="Cai dat anh", font=("Segoe UI", 14, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW).pack(pady=15)

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

    content_container, content_frame = _create_scrollable_form(main_frame)
    content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = {}
    click_state = {"mode": click_point_mode, "x": click_x, "y": click_y}
    region_state = {"enabled": search_region_enabled, "region": search_region}

    def add_entry(label, key, value):
        tk.Label(content_frame, text=label, font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(10, 3))
        var = tk.StringVar(value=str(value))
        tk.Entry(content_frame, textvariable=var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
        fields[key] = var

    add_entry("So lan click:", "repeat", initial.get("repeat", 1))
    add_entry("Delay truoc (giay):", "delay", initial.get("delay", state.click_delay))

    tk.Label(content_frame, text="Loai click:", font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_type_var = tk.StringVar(value=initial.get("click_type", "single"))
    click_type_combo = tk.OptionMenu(content_frame, click_type_var, "single", "double", "hold")
    click_type_combo.config(font=("Segoe UI", 11), bg="white", fg="black", activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    click_type_combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_type"] = click_type_var

    add_entry("Delay sau click (giay):", "click_delay", initial.get("click_delay", 0.5))
    add_entry("Threshold (0.0-1.0):", "threshold", initial.get("threshold", 0.7))

    tk.Label(content_frame, text="Cho tim duoc?:", font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    wait_timeout = initial.get("wait_timeout", 0)
    if wait_timeout == -1:
        wait_choice = "vo cuc"
    elif wait_timeout > 0:
        wait_choice = "co (30s)"
    else:
        wait_choice = "khong"
    wait_var = tk.StringVar(value=wait_choice)
    wait_combo = tk.OptionMenu(content_frame, wait_var, "khong", "co (30s)", "vo cuc")
    wait_combo.config(font=("Segoe UI", 11), bg="white", fg="black", activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    wait_combo.pack(anchor="w", pady=(0, 18), fill=tk.X)
    fields["wait_until_found"] = wait_var

    tk.Label(content_frame, text="Diem click:", font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(8, 3))
    click_info_var = tk.StringVar()

    def refresh_click_info():
        click_info_var.set(
            f"Mode: {'custom' if click_state['mode'] == 'custom' else 'center'} | "
            f"Point: ({click_state['x']}, {click_state['y']}) / {width}x{height}"
        )

    tk.Label(content_frame, textvariable=click_info_var, font=("Segoe UI", 10), bg="white", fg="gray25").pack(anchor="w", pady=(0, 8))
    click_button_row = tk.Frame(content_frame, bg="white")
    click_button_row.pack(fill=tk.X, pady=(0, 15))

    def on_pick_click_point():
        point, error = _pick_click_point_in_template(file_path, (click_state["x"], click_state["y"]))
        if error:
            if error == "cancelled":
                return
            messagebox.showerror("Loi", error)
            return
        if point is None:
            return
        click_state["x"], click_state["y"] = point
        click_state["mode"] = "custom"
        refresh_click_info()

    def on_use_center():
        click_state["x"] = width // 2
        click_state["y"] = height // 2
        click_state["mode"] = "center"
        refresh_click_info()

    tk.Button(click_button_row, text="Dat diem click", command=on_pick_click_point, bg=PKM_BLUE_DARK, fg=PKM_WHITE, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
    tk.Button(click_button_row, text="Dung tam anh", command=on_use_center, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    tk.Label(content_frame, text="Vung tim rieng cho step:", font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(8, 3))
    region_info_var = tk.StringVar()

    def refresh_region_info():
        if region_state["enabled"]:
            r = region_state["region"]
            region_info_var.set(f"Bat | ({r['x1']}, {r['y1']}) -> ({r['x2']}, {r['y2']})")
        else:
            region_info_var.set("Tat | Dang dung global/full screen")

    tk.Label(content_frame, textvariable=region_info_var, font=("Segoe UI", 10), bg="white", fg="gray25").pack(anchor="w", pady=(0, 8))
    region_button_row = tk.Frame(content_frame, bg="white")
    region_button_row.pack(fill=tk.X, pady=(0, 15))

    def on_pick_region():
        region, error = _pick_search_region_for_step(region_state["region"])
        if error:
            if error == "cancelled":
                return
            if "qua nho" in error:
                messagebox.showwarning("Canh bao", error)
            return
        region_state["region"] = region
        region_state["enabled"] = True
        refresh_region_info()

    def on_clear_region():
        region_state["enabled"] = False
        region_state["region"] = _default_search_region()
        refresh_region_info()

    tk.Button(region_button_row, text="Dat vung tim", command=on_pick_region, bg=PKM_BLUE_DARK, fg=PKM_WHITE, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
    tk.Button(region_button_row, text="Bo vung rieng", command=on_clear_region, bg=PKM_RED, fg=PKM_WHITE, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    refresh_click_info()
    refresh_region_info()

    result = {"ok": False}

    def on_ok(event=None):
        result["ok"] = True
        dialog.destroy()

    def on_cancel(event=None):
        result["ok"] = False
        dialog.destroy()

    tk.Button(button_frame, text="Luu", command=on_ok, bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)
    tk.Button(button_frame, text="Huy", command=on_cancel, bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    if not result["ok"]:
        return None

    repeat = int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1
    delay = float(fields["delay"].get()) if fields["delay"].get() else state.click_delay
    click_type = fields["click_type"].get()
    click_delay_after = float(fields["click_delay"].get()) if fields["click_delay"].get() else 0.5
    threshold = float(fields["threshold"].get()) if fields["threshold"].get() else 0.7
    wait_choice = fields["wait_until_found"].get()
    if wait_choice == "vo cuc":
        wait_until_found = True
        wait_timeout = -1
    elif wait_choice == "co (30s)":
        wait_until_found = True
        wait_timeout = 30
    else:
        wait_until_found = False
        wait_timeout = 0

    return {
        "repeat": repeat,
        "delay": delay,
        "click_type": click_type,
        "click_delay": click_delay_after,
        "threshold": threshold,
        "wait_until_found": wait_until_found,
        "wait_timeout": wait_timeout,
        "search_region_enabled": region_state["enabled"],
        "search_region": _normalize_search_region(region_state["region"]),
        "click_point_mode": click_state["mode"],
        "click_x": click_state["x"],
        "click_y": click_state["y"],
    }


def _build_image_template(file_path, config):
    img = imread_unicode(file_path)
    if img is None:
        raise ValueError("Khong doc duoc anh.")
    w, h = img.shape[::-1]
    click_x = int(config.get("click_x", w // 2))
    click_y = int(config.get("click_y", h // 2))
    click_x = max(0, min(click_x, max(0, w - 1)))
    click_y = max(0, min(click_y, max(0, h - 1)))
    return {
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
        "click_type": config["click_type"],
        "search_region_enabled": bool(config.get("search_region_enabled", False)),
        "search_region": _normalize_search_region(config.get("search_region")),
        "click_point_mode": config.get("click_point_mode", "center"),
        "click_x": click_x,
        "click_y": click_y,
    }


def create_image_template_via_user_flow(metadata=None):
    source = show_image_source_dialog()
    if not source:
        return None

    file_path = None
    from_capture = False
    if source == "capture":
        file_path, error = _capture_image_to_path(metadata)
        if error:
            state.UI.status_label.config(text=f"⚠️ {error}")
            return None
        from_capture = True
    else:
        selected_path = _choose_import_image_path()
        if not selected_path:
            return None
        file_path = _prepare_imported_image_path(selected_path, metadata=metadata)

    try:
        config = _show_step_image_config_dialog(file_path)
    except Exception as exc:
        if from_capture and file_path and os.path.exists(file_path):
            os.remove(file_path)
        state.UI.status_label.config(text=f"⚠️ {exc}")
        return None
    if config is None:
        if from_capture and file_path and os.path.exists(file_path):
            os.remove(file_path)
        return None

    try:
        return _build_image_template(file_path, config)
    except Exception as exc:
        if from_capture and file_path and os.path.exists(file_path):
            os.remove(file_path)
        state.UI.status_label.config(text=f"⚠️ {exc}")
        return None


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
        _autosave_to_library()


def add_image():
    template = create_image_template_via_user_flow()
    if template is None:
        return
    state.templates.append(template)
    update_history()
    _autosave_to_library()
    state.UI.status_label.config(text=f"✅ Đã thêm ảnh mẫu: {os.path.basename(template['path'])}")


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
    _autosave_to_library()
    _autosave_to_library()


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
    _autosave_to_library()
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
    _autosave_to_library()
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


def clear_search_region():
    """Bo gioi han pham vi tim kiem global, quay ve full screen."""
    state.search_region_enabled = False
    state.search_region = {"x1": 0, "y1": 0, "x2": 1920, "y2": 1080}
    update_history()
    state.UI.status_label.config(text="🔍 Đã bỏ giới hạn phạm vi tìm kiếm. Đang dùng toàn màn hình.")


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
        state.process_loops = 1
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
    _autosave_to_library()


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


def toggle_precision_mode():
    """Bật/tắt precision mode cho image matching."""
    state.precision_mode = not getattr(state, "precision_mode", True)
    label = "🎯 Precision Mode: BẬT" if state.precision_mode else "🌐 Match Rộng: BẬT"
    try:
        state.UI.btn_precision_mode.config(text=label)
    except Exception:
        pass
    state.UI.status_label.config(
        text=(
            "✅ Precision mode: dải scale hẹp, ưu tiên match chặt"
            if state.precision_mode
            else "✅ Match rộng: dải scale rộng, dễ bắt hơn nhưng dễ match nhầm hơn"
        )
    )


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
    """Unified delete: xóa template trong editor, xóa ảnh trong scenario queue,
    hoặc xóa cả scenario khỏi queue tùy vị trí đang chọn."""
    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="⚠️ Vui lòng chọn một mục để xóa.")
        return
    ctx = _resolve_selection_context(selected[0])
    kind = ctx[0]
    if kind == "editor_item":
        state.templates.pop(ctx[1])
        update_history()
        _autosave_to_library()
        state.UI.status_label.config(text="🗑️ Đã xóa mục.")
    elif kind == "scenario_item":
        s_idx, t_idx = ctx[1], ctx[2]
        state.scenario_metadata[s_idx]["templates"].pop(t_idx)
        update_history()
        state.UI.status_label.config(text="🗑️ Đã xóa ảnh khỏi kịch bản.")
    elif kind == "scenario_header":
        s_idx = ctx[1]
        scenario_name = os.path.basename(state.scenario_metadata[s_idx]["file_path"])
        if not messagebox.askyesno("Xác nhận xóa", f"Xóa kịch bản '{scenario_name}' khỏi queue?"):
            return
        state.scenario_metadata.pop(s_idx)
        state.scenario_queue.pop(s_idx)
        update_history()
        state.UI.status_label.config(text=f"🗑️ Đã xóa kịch bản: {scenario_name}")
    else:
        state.UI.status_label.config(text="⚠️ Không thể xóa mục này.")


def clear_all_items():
    """Unified clear: xóa toàn bộ queue (queue mode) hoặc xóa toàn bộ templates (editor mode)."""
    if state.scenario_metadata:
        if not messagebox.askyesno("Xác nhận xóa", "Xóa toàn bộ kịch bản khỏi queue?"):
            return
        state.scenario_metadata = []
        state.scenario_queue = []
        update_history()
        state.UI.status_label.config(text="🗑️ Đã xóa toàn bộ kịch bản khỏi queue.")
        return
    if not state.templates:
        state.UI.status_label.config(text="⚠️ Không có mục nào để xóa.")
        return
    if not messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa toàn bộ mục trong kịch bản này?\n\nHành động này không thể hoàn tác!"):
        return
    state.templates = []
    update_history()
    _autosave_to_library()
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
    """Unified edit: dispatch theo context.
       - scenario_header → sửa metadata của kịch bản (loops/delay)
       - scenario_item   → sửa template trong scenario_metadata
       - editor_item     → sửa template trong state.templates + autosave
    """
    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="⚠️ Vui lòng chọn một mục để chỉnh sửa.")
        return
    ctx = _resolve_selection_context(selected[0])
    kind = ctx[0]
    if kind == "scenario_header":
        _edit_scenario_metadata(ctx[1])
    elif kind == "scenario_item":
        s_idx, t_idx = ctx[1], ctx[2]
        _edit_template_in_list(state.scenario_metadata[s_idx]["templates"], t_idx, persist=False)
    elif kind == "editor_item":
        _edit_template_in_list(state.templates, ctx[1], persist=True)
    else:
        state.UI.status_label.config(text="⚠️ Không thể chỉnh sửa mục này.")


def _edit_template_in_list(template_list, idx, persist):
    """Mở dialog phù hợp với type của template (image/coord/key) và mutate in-place.
       Nếu persist=True và editor đang gắn library stage → autosave JSON."""
    if not (0 <= idx < len(template_list)):
        return
    tpl = template_list[idx]
    item_type = tpl["type"]

    if item_type == "image":
        _open_image_edit_dialog(tpl)
        update_history()
        if persist:
            _autosave_to_library()
    elif item_type == "coord":
        config = show_coordinate_config_dialog()
        if config is not None:
            tpl["x"] = config["x"]
            tpl["y"] = config["y"]
            tpl["repeat"] = config["repeat"]
            tpl["click_type"] = config["click_type"]
            tpl["delay_after"] = config["delay_after"]
            tpl["path"] = f"({config['x']},{config['y']})"
            update_history()
            if persist:
                _autosave_to_library()
            state.UI.status_label.config(text=f"✅ Đã cập nhật tọa độ ({config['x']},{config['y']})")
    elif item_type == "key":
        config = show_keyboard_config_dialog()
        if config is not None:
            tpl["key"] = config["key"]
            tpl["repeat"] = config["repeat"]
            tpl["key_type"] = config["key_type"]
            tpl["delay_after"] = config["delay_after"]
            tpl["path"] = f"[KEY: {config['key']}]"
            update_history()
            if persist:
                _autosave_to_library()
            state.UI.status_label.config(text=f"✅ Đã cập nhật phím: {config['key']}")


def _open_image_edit_dialog(tpl):
    """Mở dialog chỉnh sửa template ảnh, mutate tpl in-place."""
    dialog = tk.Toplevel(state.UI.root)
    dialog.title("✏️ Chỉnh sửa ảnh")
    dialog.geometry("560x650")
    dialog.minsize(520, 500)
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

    content_container, content_frame = _create_scrollable_form(main_frame)
    content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = {}

    tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value=str(tpl.get("repeat", 1)))
    tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var

    tk.Label(content_frame, text="⏱️ Delay trước (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_var = tk.StringVar(value=str(tpl.get("delay", state.click_delay)))
    tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay"] = delay_var

    tk.Label(content_frame, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_type_var = tk.StringVar(value=tpl.get("click_type", "single"))
    click_type_combo = tk.OptionMenu(content_frame, click_type_var, "single", "double", "hold")
    click_type_combo.config(font=("Segoe UI", 11), bg="white", fg="black",
                            activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    click_type_combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_type"] = click_type_var

    tk.Label(content_frame, text="⏳ Delay sau click (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_delay_var = tk.StringVar(value=str(tpl.get("click_delay", 0.5)))
    tk.Entry(content_frame, textvariable=click_delay_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_delay"] = click_delay_var

    tk.Label(content_frame, text="🎯 Threshold (0.0-1.0):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    threshold_var = tk.StringVar(value=str(tpl.get("threshold", 0.7)))
    tk.Entry(content_frame, textvariable=threshold_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["threshold"] = threshold_var

    tk.Label(content_frame, text="⏳ Chờ tìm được?:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
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

    tk.Button(button_frame, text="✅ Lưu", command=on_ok,
              bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)
    tk.Button(button_frame, text="❌ Hủy", command=on_cancel,
              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)

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

            state.UI.status_label.config(text="✅ Đã cập nhật thông số ảnh")
        except Exception as e:
            state.UI.status_label.config(text=f"⚠️ Lỗi: {e}")


def _swap(lst, i, j):
    lst[i], lst[j] = lst[j], lst[i]


def move_selected_up():
    selected = state.UI.history_list.curselection()
    if not selected:
        return
    ctx = _resolve_selection_context(selected[0])
    kind = ctx[0]
    if kind == "scenario_header":
        s_idx = ctx[1]
        if s_idx == 0:
            return
        _swap(state.scenario_metadata, s_idx, s_idx - 1)
        _swap(state.scenario_queue, s_idx, s_idx - 1)
        update_history()
        state.UI.status_label.config(text="⬆️ Đã chuyển kịch bản lên trên.")
    elif kind == "scenario_item":
        s_idx, t_idx = ctx[1], ctx[2]
        if t_idx == 0:
            return
        _swap(state.scenario_metadata[s_idx]["templates"], t_idx, t_idx - 1)
        update_history()
        state.UI.status_label.config(text="⬆️ Đã chuyển ảnh lên trên.")
    elif kind == "editor_item":
        t_idx = ctx[1]
        if t_idx == 0:
            return
        _swap(state.templates, t_idx, t_idx - 1)
        update_history()
        _autosave_to_library()
        state.UI.history_list.selection_set(t_idx - 1)
        state.UI.status_label.config(text="⬆️ Đã chuyển mục lên trên.")


def move_selected_down():
    selected = state.UI.history_list.curselection()
    if not selected:
        return
    ctx = _resolve_selection_context(selected[0])
    kind = ctx[0]
    if kind == "scenario_header":
        s_idx = ctx[1]
        if s_idx >= len(state.scenario_metadata) - 1:
            return
        _swap(state.scenario_metadata, s_idx, s_idx + 1)
        _swap(state.scenario_queue, s_idx, s_idx + 1)
        update_history()
        state.UI.status_label.config(text="⬇️ Đã chuyển kịch bản xuống dưới.")
    elif kind == "scenario_item":
        s_idx, t_idx = ctx[1], ctx[2]
        if t_idx >= len(state.scenario_metadata[s_idx]["templates"]) - 1:
            return
        _swap(state.scenario_metadata[s_idx]["templates"], t_idx, t_idx + 1)
        update_history()
        state.UI.status_label.config(text="⬇️ Đã chuyển ảnh xuống dưới.")
    elif kind == "editor_item":
        t_idx = ctx[1]
        if t_idx >= len(state.templates) - 1:
            return
        _swap(state.templates, t_idx, t_idx + 1)
        update_history()
        _autosave_to_library()
        state.UI.history_list.selection_set(t_idx + 1)
        state.UI.status_label.config(text="⬇️ Đã chuyển mục xuống dưới.")


def _edit_scenario_metadata(scenario_idx):
    """Sửa metadata kịch bản (process_loops/infinite_loop/click_delay) cho s_idx đã biết."""
    if not (0 <= scenario_idx < len(state.scenario_metadata)):
        state.UI.status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return

    metadata = state.scenario_metadata[scenario_idx]
    scenario_name = os.path.basename(metadata["file_path"])

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
            from scenario.io import save_scenario_metadata

            loops_text = fields["process_loops"].get().strip()
            infinite_loop = fields["infinite_loop"].get()
            process_loops = int(loops_text) if loops_text.isdigit() else 1
            if process_loops < 1:
                raise ValueError("Số vòng lặp phải >= 1")

            click_delay_text = fields["click_delay"].get().strip()
            click_delay = float(click_delay_text) if click_delay_text else 1.0
            if click_delay <= 0:
                raise ValueError("Tốc độ click phải > 0")

            metadata["process_loops"] = 1 if infinite_loop else process_loops
            metadata["infinite_loop"] = infinite_loop
            metadata["click_delay"] = click_delay
            save_scenario_metadata(metadata)

            update_history()
            state.UI.status_label.config(text=f"✅ Đã cập nhật kịch bản: {scenario_name}")
        except Exception as e:
            state.UI.status_label.config(text=f"⚠️ Lỗi: {e}")


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
        edit_dialog.geometry("560x650")
        edit_dialog.minsize(520, 500)
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

        edit_content_container, edit_content = _create_scrollable_form(edit_main)
        edit_content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

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

        edit_dialog.transient(dialog)
        edit_dialog.grab_set()

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


def _apply_image_template_config(tpl, config):
    tpl["repeat"] = config["repeat"]
    tpl["delay"] = config["delay"]
    tpl["click_type"] = config["click_type"]
    tpl["click_delay"] = config["click_delay"]
    tpl["threshold"] = config["threshold"]
    tpl["wait_until_found"] = config["wait_until_found"]
    tpl["wait_timeout"] = config["wait_timeout"]
    tpl["search_region_enabled"] = bool(config.get("search_region_enabled", False))
    tpl["search_region"] = _normalize_search_region(config.get("search_region"))
    tpl["click_point_mode"] = config.get("click_point_mode", "center")
    tpl["click_x"] = int(config.get("click_x", tpl.get("w", 1) // 2))
    tpl["click_y"] = int(config.get("click_y", tpl.get("h", 1) // 2))


def edit_existing_image_template(tpl):
    try:
        config = _show_step_image_config_dialog(tpl["path"], initial=tpl)
    except Exception as exc:
        messagebox.showerror("Loi", f"Loi: {exc}")
        return False
    if config is None:
        return False
    _apply_image_template_config(tpl, config)
    return True


def _open_image_edit_dialog(tpl):
    if edit_existing_image_template(tpl):
        state.UI.status_label.config(text="✅ Đã cập nhật thông số ảnh")


def test_image_matching():
    """Test tìm kiếm ảnh trên màn hình hiện tại với region/click point thực tế."""
    if not state.templates:
        state.UI.status_label.config(text="⚠️ Chưa thêm ảnh nào!")
        return

    tpl = state.templates[-1]
    if tpl["type"] != "image":
        state.UI.status_label.config(text="⚠️ Mục cuối cùng không phải ảnh!")
        return

    full_screenshot = capture_screen_gray()
    screenshot, (offset_x, offset_y), region_source = get_search_region_screenshot(full_screenshot, template=tpl)
    res, used_scale, tpl_w, tpl_h = multi_scale_match(screenshot, tpl["img"])
    threshold = tpl.get("threshold", 0.7)

    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))
    filtered_points = filter_close_points(points, min_dist=max(10, tpl_w // 2))
    max_score = np.max(res) if res.size > 0 else 0

    if filtered_points:
        state.UI.status_label.config(
            text=f"✅ Tìm được {len(filtered_points)} match(es)! Max score: {max_score:.4f} (scale {used_scale:.2f}x)"
        )
        safe_print(f"🧪 [TEST] Found {len(filtered_points)} matches for {tpl['path']} at scale {used_scale:.2f}x")
        safe_print(f"🧪 [TEST] Max score: {max_score:.4f}, Threshold: {threshold}, Region source: {region_source}")
        for i, pt in enumerate(filtered_points):
            click_mode = tpl.get("click_point_mode", "center")
            base_w = max(1, int(tpl.get("w", tpl_w) or tpl_w))
            base_h = max(1, int(tpl.get("h", tpl_h) or tpl_h))
            if click_mode == "custom":
                raw_click_x = int(tpl.get("click_x", base_w // 2))
                raw_click_y = int(tpl.get("click_y", base_h // 2))
                if 0 <= raw_click_x < base_w and 0 <= raw_click_y < base_h:
                    scaled_click_x = int(round(raw_click_x * tpl_w / base_w))
                    scaled_click_y = int(round(raw_click_y * tpl_h / base_h))
                else:
                    click_mode = "center"
                    scaled_click_x = tpl_w // 2
                    scaled_click_y = tpl_h // 2
            else:
                scaled_click_x = tpl_w // 2
                scaled_click_y = tpl_h // 2
            click_x = pt[0] + scaled_click_x + offset_x
            click_y = pt[1] + scaled_click_y + offset_y
            safe_print(
                f"🧪 [TEST] Match {i+1}: origin=({pt[0]}, {pt[1]}), "
                f"size={tpl_w}x{tpl_h}, offset=({offset_x}, {offset_y}), "
                f"click_mode={click_mode}, final_click=({click_x}, {click_y})"
            )
    else:
        state.UI.status_label.config(text=f"❌ Không tìm được! Max score: {max_score:.4f} < Threshold: {threshold}")
        safe_print(f"🧪 [TEST] No matches found for {tpl['path']}")
        safe_print(f"🧪 [TEST] Max score: {max_score:.4f}, Threshold: {threshold}, Region source: {region_source}")
        safe_print("🧪 [TEST] Hãy thử tăng context ảnh, đổi vùng tìm hoặc chỉnh threshold")
def test_image_matching():
    """Debug helper using the same best-match pipeline as runtime."""
    from core.vision import find_best_match

    if not state.templates:
        state.UI.status_label.config(text="âš ï¸ ChÆ°a thÃªm áº£nh nÃ o!")
        return

    tpl = state.templates[-1]
    if tpl["type"] != "image":
        state.UI.status_label.config(text="âš ï¸ Má»¥c cuá»‘i cÃ¹ng khÃ´ng pháº£i áº£nh!")
        return

    full_screenshot = capture_screen_gray()
    screenshot, (offset_x, offset_y), region_source = get_search_region_screenshot(full_screenshot, template=tpl)
    threshold = tpl.get("threshold", 0.7)
    candidate_images = tpl.get("imgs") or [tpl["img"]]
    candidate_masks = tpl.get("masks") or [tpl.get("mask")]
    candidate_names = tpl.get("paths") or [tpl["path"]]
    match = find_best_match(
        screenshot,
        candidate_images,
        threshold=threshold,
        template_names=candidate_names,
        masks=candidate_masks,
    )

    if match.found:
        click_mode = tpl.get("click_point_mode", "center")
        base_w = max(1, int(tpl.get("w", match.matched_w) or match.matched_w))
        base_h = max(1, int(tpl.get("h", match.matched_h) or match.matched_h))
        if click_mode == "custom":
            raw_click_x = int(tpl.get("click_x", base_w // 2))
            raw_click_y = int(tpl.get("click_y", base_h // 2))
            if 0 <= raw_click_x < base_w and 0 <= raw_click_y < base_h:
                scaled_click_x = int(round(raw_click_x * match.matched_w / base_w))
                scaled_click_y = int(round(raw_click_y * match.matched_h / base_h))
            else:
                click_mode = "center"
                scaled_click_x = match.matched_w // 2
                scaled_click_y = match.matched_h // 2
        else:
            scaled_click_x = match.matched_w // 2
            scaled_click_y = match.matched_h // 2

        click_x = match.top_left_x + scaled_click_x + offset_x
        click_y = match.top_left_y + scaled_click_y + offset_y
        state.UI.status_label.config(text=f"âœ… Best match! Score: {match.score:.4f} (scale {match.scale:.2f}x)")
        safe_print(
            f"ðŸ§ª [TEST] Best match for {tpl['path']} => {match.template_name} "
            f"(score={match.score:.4f}, threshold={threshold}, scale={match.scale:.2f}x, method={match.method})"
        )
        safe_print(
            f"ðŸ§ª [TEST] Match origin=({match.top_left_x}, {match.top_left_y}), "
            f"size={match.matched_w}x{match.matched_h}, region_offset=({offset_x}, {offset_y}), "
            f"region_source={region_source}, click_mode={click_mode}, final_click=({click_x}, {click_y})"
        )
    else:
        state.UI.status_label.config(
            text=f"âŒ KhÃ´ng tÃ¬m Ä‘Æ°á»£c! Best score: {match.score:.4f} < Threshold: {threshold}"
        )
        safe_print(f"ðŸ§ª [TEST] No matches found for {tpl['path']}")
        safe_print(
            f"ðŸ§ª [TEST] Best score: {match.score:.4f}, Threshold: {threshold}, "
            f"Region source: {region_source}, Best template: {match.template_name}"
        )
        safe_print("ðŸ§ª [TEST] HÃ£y thá»­ tÄƒng context áº£nh, Ä‘á»•i vÃ¹ng tÃ¬m hoáº·c chá»‰nh threshold")
