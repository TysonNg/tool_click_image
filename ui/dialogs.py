import tkinter as tk
from ui.theme import *
from core import state


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
        dialog.destroy()

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

    dialog.bind("<Escape>", lambda _event: dialog.destroy())
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    return result["value"]


def show_image_config_dialog(is_detection=False):
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
    repeat_var = tk.StringVar(value="1")
    tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var

    tk.Label(content_frame, text="⏱️ Delay trước (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_var = tk.StringVar(value=str(state.click_delay))
    tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay"] = delay_var

    tk.Label(content_frame, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_type_var = tk.StringVar(value="single")
    combo = tk.OptionMenu(content_frame, click_type_var, "single", "double", "hold")
    combo.config(font=("Segoe UI", 11), bg="white", fg="black",
                 activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_type"] = click_type_var

    tk.Label(content_frame, text="⏳ Delay sau click (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_delay_var = tk.StringVar(value="0.5")
    tk.Entry(content_frame, textvariable=click_delay_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_delay"] = click_delay_var

    tk.Label(content_frame, text="🎯 Threshold (0.0-1.0):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    threshold_var = tk.StringVar(value="0.7")
    tk.Entry(content_frame, textvariable=threshold_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["threshold"] = threshold_var

    tk.Label(content_frame, text="⏳ Chờ tìm được?:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    wait_var = tk.StringVar(value="không")
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


def show_coordinate_config_dialog():
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
    x_var = tk.StringVar(value="0")
    tk.Entry(content_frame, textvariable=x_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["x"] = x_var

    tk.Label(content_frame, text="📍 Tọa độ Y:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    y_var = tk.StringVar(value="0")
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
        dialog.destroy()

    def on_cancel(event=None):
        result["ok"] = False
        dialog.destroy()

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


def show_keyboard_config_dialog():
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
    key_var = tk.StringVar(value="enter")
    tk.Entry(content_frame, textvariable=key_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["key"] = key_var

    tk.Label(content_frame, text="📍 Số lần nhấn:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var

    tk.Label(content_frame, text="🖱️ Loại nhấn:", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    key_type_var = tk.StringVar(value="press")
    key_type_frame = tk.Frame(content_frame, bg="white")
    key_type_frame.pack(anchor="w", pady=(0, 15), fill=tk.X)
    for opt in ["press", "hold"]:
        tk.Radiobutton(key_type_frame, text=opt, variable=key_type_var, value=opt,
                       bg="white", fg="black", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)
    fields["key_type"] = key_type_var

    tk.Label(content_frame, text="⏱️ Delay sau nhấn (giây):", font=("Segoe UI", 11, "bold"),
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_after_var = tk.StringVar(value="0.5")
    tk.Entry(content_frame, textvariable=delay_after_var, font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay_after"] = delay_after_var

    result = {"ok": False}

    def on_ok(event=None):
        result["ok"] = True
        dialog.destroy()

    def on_cancel(event=None):
        result["ok"] = False
        dialog.destroy()

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
