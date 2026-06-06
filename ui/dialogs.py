import tkinter as tk
from ui.theme import *
from core import state


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


def _force_destroy(dialog):
    """Force destroy dialog even without grab (for emergency cases)"""
    try:
        if dialog.winfo_exists():
            try:
                dialog.grab_release()
            except:
                pass
            try:
                root = dialog.master
                if root:
                    root.focus()
            except:
                pass
            dialog.destroy()
    except:
        pass


def ask_string_dialog(title, prompt, default="", parent=None, initialvalue=None):
    """Custom askstring replacement - compatible with simpledialog
    
    Supports both 'default' and 'initialvalue' parameters for compatibility
    """
    if parent is None:
        parent = state.UI.root
    
    # Support both 'default' and 'initialvalue' parameters
    initial_val = initialvalue if initialvalue is not None else default
    
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.resizable(False, False)
    
    result = {"value": None}
    
    tk.Label(dialog, text=prompt, font=("Segoe UI", 10)).pack(pady=10)
    
    entry_var = tk.StringVar(value=initial_val)
    entry = tk.Entry(dialog, textvariable=entry_var, font=("Segoe UI", 11), width=40)
    entry.pack(pady=10, padx=20)
    entry.focus()
    
    def on_ok():
        result["value"] = entry_var.get()
        _safe_destroy(dialog)
    
    def on_cancel():
        result["value"] = None
        _safe_destroy(dialog)
    
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
    
    entry.bind("<Return>", lambda e: on_ok())
    dialog.bind("<Escape>", lambda e: on_cancel())
    
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)
    
    return result["value"]


def ask_float_dialog(title, prompt, min_val=None, max_val=None, default=None, parent=None):
    """Custom askfloat replacement"""
    if parent is None:
        parent = state.UI.root
    
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.resizable(False, False)
    
    result = {"value": None}
    
    tk.Label(dialog, text=prompt, font=("Segoe UI", 10)).pack(pady=10)
    
    entry_var = tk.StringVar(value=str(default) if default else "")
    entry = tk.Entry(dialog, textvariable=entry_var, font=("Segoe UI", 11), width=40)
    entry.pack(pady=10, padx=20)
    entry.focus()
    
    def on_ok():
        try:
            val = float(entry_var.get())
            if min_val is not None and val < min_val:
                tk.messagebox.showerror("Error", f"Value must be >= {min_val}")
                return
            if max_val is not None and val > max_val:
                tk.messagebox.showerror("Error", f"Value must be <= {max_val}")
                return
            result["value"] = val
            _safe_destroy(dialog)
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a valid number")
    
    def on_cancel():
        result["value"] = None
        _safe_destroy(dialog)
    
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
    
    entry.bind("<Return>", lambda e: on_ok())
    dialog.bind("<Escape>", lambda e: on_cancel())
    
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)
    
    return result["value"]


def show_image_source_dialog():
    root = state.UI.root
    dialog = tk.Toplevel(root)
    dialog.title("Nguon anh mau")
    dialog.geometry("460x300")
    dialog.minsize(420, 280)
    dialog.resizable(False, False)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X)
    tk.Label(
        header_frame,
        text="Chon nguon anh mau",
        font=("Segoe UI", 14, "bold"),
        bg=PKM_BG_INNER,
        fg=PKM_YELLOW,
    ).pack(pady=15)

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

    tk.Label(
        content_frame,
        text="Nen uu tien chup tren man hinh de tranh lech ti le/DPI.",
        font=("Segoe UI", 10),
        bg="white",
        fg="black",
        wraplength=380,
        justify="left",
    ).pack(anchor="w", pady=(0, 16))

    result = {"value": None}

    def choose(value):
        result["value"] = value
        _safe_destroy(dialog)

    action_frame = tk.Frame(content_frame, bg="white")
    action_frame.pack(fill=tk.X, pady=(0, 10))

    tk.Button(
        action_frame,
        text="Chup tren man hinh",
        command=lambda: choose("capture"),
        bg=PKM_GREEN,
        fg=PKM_BG_DARK,
        font=("Segoe UI", 11, "bold"),
        padx=20,
        pady=10,
    ).pack(fill=tk.X, pady=(0, 10))

    tk.Button(
        action_frame,
        text="Chon file PNG co san",
        command=lambda: choose("file"),
        bg=PKM_BLUE_DARK,
        fg=PKM_WHITE,
        font=("Segoe UI", 11, "bold"),
        padx=20,
        pady=10,
    ).pack(fill=tk.X)

    footer_frame = tk.Frame(main_frame, bg="white")
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=(0, 20))

    tk.Button(
        footer_frame,
        text="Huy",
        command=dialog.destroy,
        bg=PKM_RED,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        padx=20,
        pady=8,
    ).pack(fill=tk.X)

    dialog.bind("<Escape>", lambda _event: _safe_destroy(dialog))
    dialog.protocol("WM_DELETE_WINDOW", lambda: _safe_destroy(dialog))
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    return result["value"]


def show_image_config_dialog(is_detection=False, initial_repeat=None, initial_delay=None, initial_click_type=None, 
                              initial_click_delay=None, initial_threshold=None, initial_wait_timeout=None):
    root = state.UI.root
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt ảnh")
    dialog.geometry("550x700")
    dialog.minsize(500, 600)
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

    tk.Label(header_frame, text="⚙️ Cài đặt ảnh", font=("Segoe UI", 14, "bold"),
             bg=PKM_BG_INNER, fg=PKM_YELLOW).pack(pady=15)

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = {}

    tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value=str(initial_repeat if initial_repeat is not None else 1))
    tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var

    tk.Label(content_frame, text="⏱️ Delay trước (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_var = tk.StringVar(value=str(initial_delay if initial_delay is not None else state.click_delay))
    tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay"] = delay_var

    tk.Label(content_frame, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_type_var = tk.StringVar(value=str(initial_click_type if initial_click_type is not None else "single"))
    combo = tk.OptionMenu(content_frame, click_type_var, "single", "double", "hold")
    combo.config(font=("Segoe UI", 11), bg="white", fg="black",
                 activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_type"] = click_type_var

    tk.Label(content_frame, text="⏳ Delay sau click (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_delay_var = tk.StringVar(value=str(initial_click_delay if initial_click_delay is not None else 0.5))
    tk.Entry(content_frame, textvariable=click_delay_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_delay"] = click_delay_var

    tk.Label(content_frame, text="🎯 Threshold (0.0-1.0):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    threshold_var = tk.StringVar(value=str(initial_threshold if initial_threshold is not None else 0.7))
    tk.Entry(content_frame, textvariable=threshold_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["threshold"] = threshold_var

    tk.Label(content_frame, text="⏳ Chờ tìm được?:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    
    # Determine wait choice from initial_wait_timeout
    if initial_wait_timeout == -1:
        wait_choice = "vô cực"
    elif initial_wait_timeout and initial_wait_timeout > 0:
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
        _safe_destroy(dialog)

    def on_cancel(event=None):
        result["ok"] = False
        _safe_destroy(dialog)

    tk.Button(button_frame, text="✅ OK", command=on_ok,
              bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)

    tk.Button(button_frame, text="❌ Hủy", command=on_cancel,
              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    if result["ok"]:
        try:
            repeat = int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1
            delay = float(fields["delay"].get()) if fields["delay"].get() else state.click_delay
            click_type = fields["click_type"].get()
            click_delay_after = float(fields["click_delay"].get()) if fields["click_delay"].get() else 0.5
            threshold = float(fields["threshold"].get()) if fields["threshold"].get() else 0.7
            wait_choice = fields["wait_until_found"].get()

            if wait_choice == "vô cực":
                wait_until_found = True
                wait_timeout = -1
            elif wait_choice == "có (30s)":
                wait_until_found = True
                wait_timeout = 30
            else:
                wait_until_found = False
                wait_timeout = 0

            return {
                "repeat": repeat, "delay": delay, "click_type": click_type,
                "click_delay": click_delay_after, "threshold": threshold,
                "wait_until_found": wait_until_found, "wait_timeout": wait_timeout
            }
        except:
            return None
    return None


def show_coordinate_config_dialog(initial_x=None, initial_y=None):
    root = state.UI.root
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt tọa độ")
    dialog.geometry("550x600")
    dialog.minsize(500, 520)
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
    tk.Label(header_frame, text="⚙️ Cài đặt tọa độ", font=("Segoe UI", 14, "bold"),
             bg=PKM_BG_INNER, fg=PKM_YELLOW).pack(pady=15)

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = {}

    tk.Label(content_frame, text="📍 Tọa độ X:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    x_var = tk.StringVar(value=str(initial_x) if initial_x is not None else "0")
    tk.Entry(content_frame, textvariable=x_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["x"] = x_var

    tk.Label(content_frame, text="📍 Tọa độ Y:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    y_var = tk.StringVar(value=str(initial_y) if initial_y is not None else "0")
    tk.Entry(content_frame, textvariable=y_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["y"] = y_var

    tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var

    tk.Label(content_frame, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_type_var = tk.StringVar(value="single")
    click_type_frame = tk.Frame(content_frame, bg="white")
    click_type_frame.pack(anchor="w", pady=(0, 15), fill=tk.X)
    for opt in ["single", "double", "hold"]:
        tk.Radiobutton(click_type_frame, text=opt, variable=click_type_var, value=opt,
                       bg="white", fg="black", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)
    fields["click_type"] = click_type_var

    tk.Label(content_frame, text="⏱️ Delay sau click (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_after_var = tk.StringVar(value="0.5")
    tk.Entry(content_frame, textvariable=delay_after_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay_after"] = delay_after_var

    result = {"ok": False}

    def on_ok(event=None):
        result["ok"] = True
        _safe_destroy(dialog)

    def on_cancel(event=None):
        result["ok"] = False
        _safe_destroy(dialog)

    tk.Button(button_frame, text="✅ OK", command=on_ok,
              bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)
    tk.Button(button_frame, text="❌ Hủy", command=on_cancel,
              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    if result["ok"]:
        try:
            return {
                "x": int(fields["x"].get()) if fields["x"].get().isdigit() else 0,
                "y": int(fields["y"].get()) if fields["y"].get().isdigit() else 0,
                "repeat": int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1,
                "click_type": fields["click_type"].get(),
                "delay_after": float(fields["delay_after"].get()) if fields["delay_after"].get() else 0.5
            }
        except:
            return None
    return None


def show_keyboard_config_dialog(initial_key="enter", initial_repeat=1, initial_key_type="press", initial_delay=0.5):
    root = state.UI.root
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt phím")
    dialog.geometry("550x600")
    dialog.minsize(500, 520)
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
    tk.Label(header_frame, text="⚙️ Cài đặt phím", font=("Segoe UI", 14, "bold"),
             bg=PKM_BG_INNER, fg=PKM_YELLOW).pack(pady=15)

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = {}

    tk.Label(content_frame, text="⌨️ Tên phím:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    tk.Label(content_frame, text="(ví dụ: enter, space, a, 1, f1, ctrl+c, alt+tab)",
             font=("Segoe UI", 9), bg="white", fg=PKM_LIGHT_BLUE).pack(anchor="w", pady=(0, 5))
    key_var = tk.StringVar(value=str(initial_key))
    tk.Entry(content_frame, textvariable=key_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["key"] = key_var

    tk.Label(content_frame, text="📍 Số lần nhấn:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value=str(initial_repeat))
    tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var

    tk.Label(content_frame, text="🖱️ Loại nhấn:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    key_type_var = tk.StringVar(value=str(initial_key_type))
    key_type_frame = tk.Frame(content_frame, bg="white")
    key_type_frame.pack(anchor="w", pady=(0, 15), fill=tk.X)
    for opt in ["press", "hold"]:
        tk.Radiobutton(key_type_frame, text=opt, variable=key_type_var, value=opt,
                       bg="white", fg="black", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)
    fields["key_type"] = key_type_var

    tk.Label(content_frame, text="⏱️ Delay sau nhấn (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_after_var = tk.StringVar(value=str(initial_delay))
    tk.Entry(content_frame, textvariable=delay_after_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay_after"] = delay_after_var

    result = {"ok": False}

    def on_ok(event=None):
        result["ok"] = True
        _safe_destroy(dialog)

    def on_cancel(event=None):
        result["ok"] = False
        _safe_destroy(dialog)

    tk.Button(button_frame, text="✅ OK", command=on_ok,
              bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)
    tk.Button(button_frame, text="❌ Hủy", command=on_cancel,
              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"),
              padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    if result["ok"]:
        try:
            return {
                "key": fields["key"].get().strip().lower() or "enter",
                "repeat": int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1,
                "key_type": fields["key_type"].get(),
                "delay_after": float(fields["delay_after"].get()) if fields["delay_after"].get() else 0.5
            }
        except:
            return None
    return None


def show_speed_multiplier_dialog(parent=None):
    """Show speed multiplier slider dialog (0.0 = max speed, 1.0 = normal)"""
    if parent is None:
        parent = state.UI.root
    
    dialog = tk.Toplevel(parent)
    dialog.title("⚡ Cài Đặt Tốc Độ")
    dialog.geometry("450x200")
    dialog.resizable(False, False)
    dialog.grab_set()
    
    result = {"value": None}
    
    # Title
    tk.Label(
        dialog, 
        text="Tốc Độ Chạy Kịch Bản", 
        font=("Segoe UI", 12, "bold"),
        bg=PKM_BLUE_DARK if "PKM_BLUE_DARK" in globals() else "#1e3a8a",
        fg=PKM_YELLOW if "PKM_YELLOW" in globals() else "#fbbf24"
    ).pack(fill="x", pady=10, padx=10, ipady=5)
    
    # Info frame
    info_frame = tk.Frame(dialog, bg="white")
    info_frame.pack(fill="x", pady=5, padx=10)
    
    tk.Label(
        info_frame,
        text="0% = Tốc độ TỐI ĐA (không chờ)  |  100% = Bình thường",
        font=("Segoe UI", 9),
        bg="white",
        fg="#666"
    ).pack(anchor="w")
    
    # Slider frame
    slider_frame = tk.Frame(dialog, bg="white")
    slider_frame.pack(fill="x", pady=10, padx=20)
    
    # Current value label
    current_value_label = tk.Label(
        slider_frame,
        text="100%",
        font=("Segoe UI", 10, "bold"),
        bg="white",
        fg="#2563eb"
    )
    current_value_label.pack(side="left", padx=(0, 10))
    
    # Slider
    speed_var = tk.IntVar(value=100)
    
    def on_slider_change(*args):
        percentage = speed_var.get()
        current_value_label.config(text=f"{percentage}%")
        if percentage == 0:
            current_value_label.config(text="0% (TỐI ĐA)", fg="#ef4444")
        elif percentage == 100:
            current_value_label.config(text="100% (Bình thường)", fg="#2563eb")
        else:
            current_value_label.config(text=f"{percentage}% ({round(100/percentage, 1)}x nhanh)", fg="#f59e0b")
    
    slider = tk.Scale(
        slider_frame,
        from_=0,
        to=100,
        orient="horizontal",
        variable=speed_var,
        command=on_slider_change,
        bg="white",
        fg="#2563eb",
        length=350,
        troughcolor="#e5e7eb",
        highlightthickness=0
    )
    slider.pack(side="left", fill="x", expand=True)
    
    # Button frame
    button_frame = tk.Frame(dialog, bg="white")
    button_frame.pack(fill="x", pady=10, padx=10)
    
    def ok_clicked():
        percentage = speed_var.get()
        result["value"] = percentage / 100.0
        _safe_destroy(dialog)
    
    def cancel_clicked():
        result["value"] = None
        _safe_destroy(dialog)
    
    tk.Button(
        button_frame,
        text="✅ OK",
        command=ok_clicked,
        font=("Segoe UI", 10),
        bg="#10b981",
        fg="white",
        padx=20
    ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame,
        text="❌ Hủy",
        command=cancel_clicked,
        font=("Segoe UI", 10),
        bg="#ef4444",
        fg="white",
        padx=20
    ).pack(side="left", padx=5)
    
    dialog.transient(parent)
    dialog.wait_window()
    
    return result["value"]


def show_final_step_mode_dialog(parent=None):
    """Show dropdown to select final step behavior"""
    if parent is None:
        parent = state.UI.root
    
    dialog = tk.Toplevel(parent)
    dialog.title("🎯 Cách Xử Lý Bước Cuối")
    dialog.geometry("450x200")
    dialog.resizable(False, False)
    dialog.grab_set()
    
    result = {"value": None}
    
    # Title
    tk.Label(
        dialog, 
        text="Khi Bước Cuối Không Tìm Thấy", 
        font=("Segoe UI", 12, "bold"),
        bg=PKM_BLUE_DARK if "PKM_BLUE_DARK" in globals() else "#1e3a8a",
        fg=PKM_YELLOW if "PKM_YELLOW" in globals() else "#fbbf24"
    ).pack(fill="x", pady=10, padx=10, ipady=5)
    
    # Info frame
    info_frame = tk.Frame(dialog, bg="white")
    info_frame.pack(fill="x", pady=5, padx=10)
    
    tk.Label(
        info_frame,
        text="Chọn cách xử lý nếu ảnh cuối cùng không được tìm thấy",
        font=("Segoe UI", 9),
        bg="white",
        fg="#666"
    ).pack(anchor="w")
    
    # Options frame
    options_frame = tk.Frame(dialog, bg="white")
    options_frame.pack(fill="both", expand=True, pady=15, padx=20)
    
    mode_var = tk.StringVar(value="wait_3s")
    
    # Option 1: Skip now
    tk.Radiobutton(
        options_frame,
        text="⚡ Skip ngay (không chờ) - Nhanh nhất",
        variable=mode_var,
        value="skip_now",
        font=("Segoe UI", 10),
        bg="white",
        fg="#ef4444"
    ).pack(anchor="w", pady=8)
    
    # Option 2: Wait 1s
    tk.Radiobutton(
        options_frame,
        text="⏳ Chờ 1 giây - Cân bằng",
        variable=mode_var,
        value="wait_1s",
        font=("Segoe UI", 10),
        bg="white",
        fg="#f59e0b"
    ).pack(anchor="w", pady=8)
    
    # Option 3: Wait 3s (default)
    tk.Radiobutton(
        options_frame,
        text="⏳ Chờ 3 giây - Bình thường (mặc định)",
        variable=mode_var,
        value="wait_3s",
        font=("Segoe UI", 10),
        bg="white",
        fg="#2563eb"
    ).pack(anchor="w", pady=8)
    
    # Button frame
    button_frame = tk.Frame(dialog, bg="white")
    button_frame.pack(fill="x", pady=10, padx=10)
    
    def ok_clicked():
        result["value"] = mode_var.get()
        _safe_destroy(dialog)
    
    def cancel_clicked():
        result["value"] = None
        _safe_destroy(dialog)
    
    tk.Button(
        button_frame,
        text="✅ OK",
        command=ok_clicked,
        font=("Segoe UI", 10),
        bg="#10b981",
        fg="white",
        padx=20
    ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame,
        text="❌ Hủy",
        command=cancel_clicked,
        font=("Segoe UI", 10),
        bg="#ef4444",
        fg="white",
        padx=20
    ).pack(side="left", padx=5)
    
    dialog.transient(parent)
    dialog.wait_window()
    
    return result["value"]
