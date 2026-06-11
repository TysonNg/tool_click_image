import cv2
import numpy as np
import threading
import time
import json
import os
import math
import random
import ctypes

# Bật DPI awareness TRƯỚC khi import tkinter / pyautogui để screenshot và toạ độ chuột
# luôn ở physical pixels — fix lỗi tool match được máy 100% scaling nhưng fail máy 125%/150%.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import win32api, win32con
import pyautogui
import keyboard
try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

start_hotkey = "f6"
stop_hotkey = "f7"

# Safe print helper to prevent thread crashes on Windows Unicode consoles
def safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(str(msg).encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            pass


def set_status(text):
    try:
        if 'status_var' in globals() and status_var is not None:
            status_var.set(text)
        if 'status_top_var' in globals() and status_top_var is not None:
            status_top_var.set(text)
        if 'root' in globals() and root is not None:
            root.title(f"AutoClick Nâng Cấp PRO — {text}")
        root.update_idletasks()
    except Exception:
        try:
            if 'status_label' in globals() and status_label is not None:
                status_label.config(text=text)
            root.update_idletasks()
        except Exception:
            pass


def capture_screen_gray():
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

def multi_scale_match(screenshot, template, scales=None):
    """
    Match template ở nhiều scale để xử lý khác độ phân giải/DPI giữa các máy.
    Trả về (res, scale_used, scaled_w, scaled_h) — `res` cùng định dạng cv2.matchTemplate
    (mảng score), tham chiếu template ĐÃ resize theo `scale_used`.
    """
    if scales is None:
        # Cover scaling 75% → 150% (gồm 1920→1366, 1920→2560, 100%→125%/150% DPI)
        scales = [1.0, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15, 0.8, 1.2, 0.75, 1.25, 1.35, 1.5]
    best_res = None
    best_score = -1.0
    best_scale = 1.0
    best_tpl = template
    sh, sw = screenshot.shape[:2]
    for s in scales:
        if s == 1.0:
            tpl = template
        else:
            nw = max(4, int(template.shape[1] * s))
            nh = max(4, int(template.shape[0] * s))
            if nw >= sw or nh >= sh:
                continue
            tpl = cv2.resize(template, (nw, nh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
        try:
            res = cv2.matchTemplate(screenshot, tpl, cv2.TM_CCOEFF_NORMED)
        except cv2.error:
            continue
        score = float(np.max(res)) if res.size else -1.0
        if score > best_score:
            best_score = score
            best_res = res
            best_scale = s
            best_tpl = tpl
    if best_res is None:  # fallback
        best_res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        best_tpl = template
    return best_res, best_scale, best_tpl.shape[1], best_tpl.shape[0]

def get_search_region_screenshot(full_screenshot):
    """Cắt screenshot theo phạm vi tìm kiếm"""
    if not search_region_enabled:
        return full_screenshot, (0, 0)  # Trả về toàn bộ + offset (0,0)
    
    x1 = search_region["x1"]
    y1 = search_region["y1"]
    x2 = search_region["x2"]
    y2 = search_region["y2"]
    
    cropped = full_screenshot[y1:y2, x1:x2]
    return cropped, (x1, y1)

def filter_close_points(points, min_dist=20):
    filtered = []
    for pt in points:
        if not filtered:
            filtered.append(pt)
        else:
            too_close = False
            for f_pt in filtered:
                if abs(pt[0] - f_pt[0]) < min_dist and abs(pt[1] - f_pt[1]) < min_dist:
                    too_close = True
                    break
            if not too_close:
                filtered.append(pt)
    return filtered

templates = []
running = False
process_loops = 1   # số vòng lặp toàn bộ quá trình
infinite_loop = False  # vòng lặp vô hạn
click_delay = 1.0   # tốc độ click (giây nghỉ giữa các click)
human_click_mode = False  # False = click tức thì (cũ), True = rê chuột human-like

# Scenario Queue - Chạy nhiều kịch bản
scenario_queue = []  # danh sách các kịch bản cần chạy
scenario_metadata = []  # danh sách metadata của từng kịch bản (tên file, số item, ...)
current_scenario_index = 0

# Search Region - Giới hạn phạm vi tìm kiếm
search_region_enabled = False
search_region = {"x1": 0, "y1": 0, "x2": 1920, "y2": 1080}  # Mặc định toàn màn hình

def imread_unicode(path):
    with open(path, "rb") as stream:
        bytes_array = bytearray(stream.read())
    numpy_array = np.asarray(bytes_array, dtype=np.uint8)
    img = cv2.imdecode(numpy_array, cv2.IMREAD_GRAYSCALE)
    return img

def human_move(x, y, duration=None):
    """Rê chuột theo Bezier + ease-in-out + jitter, giống thao tác người."""
    start_x, start_y = win32api.GetCursorPos()
    dist = math.hypot(x - start_x, y - start_y)
    if dist < 1:
        return
    if duration is None:
        duration = random.uniform(0.18, 0.38) + dist / 3500.0
    cx1 = start_x + (x - start_x) * random.uniform(0.2, 0.4) + random.randint(-40, 40)
    cy1 = start_y + (y - start_y) * random.uniform(0.2, 0.4) + random.randint(-40, 40)
    cx2 = start_x + (x - start_x) * random.uniform(0.6, 0.8) + random.randint(-40, 40)
    cy2 = start_y + (y - start_y) * random.uniform(0.6, 0.8) + random.randint(-40, 40)
    steps = max(25, int(duration * 120))
    for i in range(1, steps + 1):
        t = i / steps
        t = 0.5 - 0.5 * math.cos(math.pi * t)
        mt = 1 - t
        bx = mt**3 * start_x + 3*mt**2*t*cx1 + 3*mt*t**2*cx2 + t**3 * x
        by = mt**3 * start_y + 3*mt**2*t*cy1 + 3*mt*t**2*cy2 + t**3 * y
        bx += random.uniform(-0.6, 0.6)
        by += random.uniform(-0.6, 0.6)
        win32api.SetCursorPos((int(bx), int(by)))
        time.sleep(duration / steps)

def click(x, y):
    if human_click_mode:
        jx = x + random.randint(-3, 3)
        jy = y + random.randint(-3, 3)
        human_move(jx, jy)
        time.sleep(random.uniform(0.04, 0.12))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(random.uniform(0.05, 0.13))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def double_click(x, y, delay=0.1):
    """Double-click tại vị trí (x, y)"""
    click(x, y)
    if human_click_mode:
        time.sleep(delay * random.uniform(0.7, 1.3))
    else:
        time.sleep(delay)
    click(x, y)

def click_and_hold(x, y, hold_time=0.2):
    """Click và giữ tại vị trí (x, y)"""
    if human_click_mode:
        jx = x + random.randint(-3, 3)
        jy = y + random.randint(-3, 3)
        human_move(jx, jy)
        time.sleep(random.uniform(0.04, 0.12))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(hold_time * random.uniform(0.85, 1.15))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(hold_time)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def press_key(key_name):
    """Nhấn một phím trên bàn phím"""
    try:
        keyboard.press(key_name)
        keyboard.release(key_name)
        safe_print(f"⌨️ Pressed key: {key_name}")
    except Exception as e:
        safe_print(f"⚠️ Error pressing key {key_name}: {e}")

def add_image():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("All files","*.*")])
    if file_path:
        img = imread_unicode(file_path)
        if img is None:
            status_label.config(text="⚠️ Không đọc được ảnh.")
            return
        w, h = img.shape[::-1]
        
        config = show_image_config_dialog(is_detection=False)
        if config is None:
            return
        
        templates.append({
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

def show_coordinate_config_dialog():
    """Hiển thị dialog gộp tất cả cài đặt cho tọa độ"""
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt tọa độ")
    dialog.geometry("550x400")
    dialog.resizable(False, False)
    
    # Main frame với background trắng
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Header frame
    header_frame = tk.Frame(main_frame, bg=PKM_DARK_BLUE)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text="⚙️ Cài đặt tọa độ", font=("Segoe UI", 14, "bold"), 
                           bg=PKM_DARK_BLUE, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    # Content frame
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    fields = {}
    
    # Tọa độ X
    tk.Label(content_frame, text="📍 Tọa độ X:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    x_var = tk.StringVar(value="0")
    x_entry = tk.Entry(content_frame, textvariable=x_var, font=("Segoe UI", 11), width=40)
    x_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["x"] = x_var
    
    # Tọa độ Y
    tk.Label(content_frame, text="📍 Tọa độ Y:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    y_var = tk.StringVar(value="0")
    y_entry = tk.Entry(content_frame, textvariable=y_var, font=("Segoe UI", 11), width=40)
    y_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["y"] = y_var
    
    # Số lần lặp
    tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    repeat_entry = tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
    repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var
    
    # Delay
    tk.Label(content_frame, text="⏱️ Delay (giây):", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_var = tk.StringVar(value=str(click_delay))
    delay_entry = tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40)
    delay_entry.pack(anchor="w", pady=(0, 25), fill=tk.X)
    fields["delay"] = delay_var
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    result = {"ok": False}
    
    def on_ok():
        result["ok"] = True
        dialog.destroy()
    
    def on_cancel():
        result["ok"] = False
        dialog.destroy()
    
    ok_btn = tk.Button(button_frame, text="✅ OK", command=on_ok, 
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    
    if result["ok"]:
        try:
            return {
                "x": int(fields["x"].get()) if fields["x"].get().isdigit() else 0,
                "y": int(fields["y"].get()) if fields["y"].get().isdigit() else 0,
                "repeat": int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1,
                "delay": float(fields["delay"].get()) if fields["delay"].get() else click_delay
            }
        except:
            return None
    return None

def add_coordinate():
    config = show_coordinate_config_dialog()
    if config is None:
        return
    templates.append({
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
    status_label.config(text="⏳ Di chuột tới vị trí muốn lấy (3 giây)...")
    root.update()
    time.sleep(3)
    x, y = pyautogui.position()
    
    config = show_coordinate_config_dialog()
    if config is None:
        return
    
    # Ghi đè tọa độ X, Y từ vị trí hiện tại
    config["x"] = x
    config["y"] = y
    
    templates.append({
        "type": "coord",
        "x": config["x"],
        "y": config["y"],
        "repeat": config["repeat"],
        "click_type": config["click_type"],
        "delay_after": config["delay_after"],
        "path": f"({config['x']},{config['y']})"
    })
    update_history()
    status_label.config(text=f"✅ Đã thêm tọa độ ({config['x']},{config['y']}) ({config['click_type']}, delay {config['delay_after']}s)")

def show_keyboard_config_dialog():
    """Hiển thị dialog gộp tất cả cài đặt cho phím"""
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt phím")
    dialog.geometry("550x400")
    dialog.resizable(False, False)
    
    # Main frame với background trắng
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Header frame
    header_frame = tk.Frame(main_frame, bg=PKM_DARK_BLUE)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text="⚙️ Cài đặt phím", font=("Segoe UI", 14, "bold"), 
                           bg=PKM_DARK_BLUE, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    # Content frame
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    fields = {}
    
    # Tên phím
    tk.Label(content_frame, text="⌨️ Tên phím:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    tk.Label(content_frame, text="(ví dụ: enter, space, a, 1, f1, ctrl+c, alt+tab)", 
             font=("Segoe UI", 9), bg="white", fg=PKM_LIGHT_BLUE).pack(anchor="w", pady=(0, 5))
    key_var = tk.StringVar(value="enter")
    key_entry = tk.Entry(content_frame, textvariable=key_var, font=("Segoe UI", 11), width=40)
    key_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["key"] = key_var
    
    # Số lần nhấn
    tk.Label(content_frame, text="📍 Số lần nhấn:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    repeat_entry = tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
    repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var
    
    # Delay
    tk.Label(content_frame, text="⏱️ Delay (giây):", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_var = tk.StringVar(value=str(click_delay))
    delay_entry = tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40)
    delay_entry.pack(anchor="w", pady=(0, 25), fill=tk.X)
    fields["delay"] = delay_var
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    result = {"ok": False}
    
    def on_ok():
        result["ok"] = True
        dialog.destroy()
    
    def on_cancel():
        result["ok"] = False
        dialog.destroy()
    
    ok_btn = tk.Button(button_frame, text="✅ OK", command=on_ok, 
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    
    if result["ok"]:
        try:
            return {
                "key": fields["key"].get().strip().lower() or "enter",
                "repeat": int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1,
                "delay": float(fields["delay"].get()) if fields["delay"].get() else click_delay
            }
        except:
            return None
    return None

def add_keyboard_key():
    """Thêm hành động nhấn phím vào kịch bản"""
    config = show_keyboard_config_dialog()
    if config is None:
        return
    
    templates.append({
        "type": "key",
        "key": config["key"],
        "repeat": config["repeat"],
        "key_type": config["key_type"],
        "delay_after": config["delay_after"],
        "path": f"[KEY: {config['key']}]"
    })
    update_history()
    status_label.config(text=f"✅ Đã thêm phím: {config['key']} ({config['key_type']}, delay {config['delay_after']}s)")

def set_search_region():
    """Đặt phạm vi tìm kiếm hình ảnh bằng cách kéo chuột"""
    global search_region_enabled, search_region
    
    # Tạo cửa sổ overlay để người dùng kéo chọn phạm vi
    overlay_window = tk.Toplevel(root)
    overlay_window.attributes('-alpha', 0.3)  # Trong suốt 30%
    overlay_window.attributes('-topmost', True)
    overlay_window.configure(bg='blue')
    
    # Lấy kích thước màn hình
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
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
            search_region["x1"] = x1
            search_region["y1"] = y1
            search_region["x2"] = x2
            search_region["y2"] = y2
            status_label.config(text=f"🔍 Phạm vi tìm kiếm: ({x1},{y1}) → ({x2},{y2})")
            # Cập nhật biến toàn cục
            globals()['search_region_enabled'] = True
        else:
            status_label.config(text="🔍 Phạm vi tìm kiếm: Toàn màn hình")
            globals()['search_region_enabled'] = False
        
        update_history()  # Cập nhật Pokédex
        overlay_window.destroy()
    
    def on_escape(event):
        status_label.config(text="🔍 Phạm vi tìm kiếm: Toàn màn hình")
        globals()['search_region_enabled'] = False
        overlay_window.destroy()
    
    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    overlay_window.bind("<Escape>", on_escape)
    
    status_label.config(text="🔍 Kéo chuột để chọn phạm vi tìm kiếm (ESC để hủy)")

def set_process_loops():
    global process_loops, infinite_loop
    
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
        infinite_loop = True
        process_loops = 999999  # Set to a very large number
        status_label.config(text="🔄 Đã đặt vòng lặp: ∞ (Vô hạn - chạy cho đến khi bấm dừng)")
    else:
        try:
            loops = int(response)
            if loops < 1:
                status_label.config(text="⚠️ Số vòng lặp phải >= 1")
                return
            infinite_loop = False
            process_loops = loops
            status_label.config(text=f"� Đã đặt {process_loops} vòng lặp cho toàn bộ quá trình.")
        except ValueError:
            status_label.config(text="⚠️ Vui lòng nhập số hoặc 'vô hạn'")
    
    update_history()

def set_speed():
    global click_delay
    delay = simpledialog.askfloat("Tốc độ", "Nhập thời gian nghỉ giữa các click (giây):", minvalue=0.1, maxvalue=5.0)
    if delay is None: return
    click_delay = delay
    status_label.config(text=f"⏩ Đã đặt tốc độ: {click_delay} giây giữa các click")

def toggle_human_click():
    """Bật/tắt chế độ rê chuột human-like"""
    global human_click_mode
    human_click_mode = not human_click_mode
    label = "🧍 Rê chuột Human-like: BẬT" if human_click_mode else "🤖 Click tức thì: BẬT"
    try:
        btn_human_mode.config(text=label)
    except Exception:
        pass
    status_label.config(text=f"✅ Đã chuyển chế độ click: {'Human-like (rê chuột)' if human_click_mode else 'Click tức thì (cũ)'}")

def test_image_matching():
    """Test tìm kiếm ảnh trên màn hình hiện tại"""
    if not templates:
        status_label.config(text="⚠️ Chưa thêm ảnh nào!")
        return
    
    # Lấy ảnh cuối cùng được thêm
    tpl = templates[-1]
    if tpl["type"] != "image":
        status_label.config(text="⚠️ Mục cuối cùng không phải ảnh!")
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
        status_label.config(text=f"✅ Tìm được {len(filtered_points)} match(es)! Max score: {max_score:.4f} (scale {used_scale:.2f}x)")
        safe_print(f"🧪 [TEST] Found {len(filtered_points)} matches for {tpl['path']} at scale {used_scale:.2f}x")
        safe_print(f"🧪 [TEST] Max score: {max_score:.4f}, Threshold: {threshold}")
        for i, pt in enumerate(filtered_points):
            safe_print(f"🧪 [TEST] Match {i+1}: ({pt[0]}, {pt[1]})")
    else:
        status_label.config(text=f"❌ Không tìm được! Max score: {max_score:.4f} < Threshold: {threshold}")
        safe_print(f"🧪 [TEST] No matches found for {tpl['path']}")
        safe_print(f"🧪 [TEST] Max score: {max_score:.4f}, Threshold: {threshold}")
        safe_print(f"🧪 [TEST] Hãy thử giảm threshold hoặc kiểm tra ảnh")


def save_scenario():
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
                                             title="Lưu kịch bản AutoClick")
    if not file_path:
        return

    scenario = {
        "process_loops": process_loops,
        "infinite_loop": infinite_loop,
        "click_delay": click_delay,
        "templates": []
    }

    for tpl in templates:
        if tpl["type"] == "image":
            scenario["templates"].append({
                "type": "image",
                "path": tpl["path"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", click_delay),
                "wait_until_found": tpl.get("wait_until_found", False),
                "wait_timeout": tpl.get("wait_timeout", 0),
                "threshold": tpl.get("threshold", 0.7),
                "click_delay": tpl.get("click_delay", 0.5),
                "click_type": tpl.get("click_type", "single")
            })
        elif tpl["type"] == "key":
            scenario["templates"].append({
                "type": "key",
                "key": tpl["key"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", click_delay),
                "key_type": tpl.get("key_type", "press"),
                "delay_after": tpl.get("delay_after", 0.5)
            })
        else:
            scenario["templates"].append({
                "type": "coord",
                "x": tpl["x"],
                "y": tpl["y"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", click_delay),
                "click_type": tpl.get("click_type", "single"),
                "delay_after": tpl.get("delay_after", 0.5)
            })

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(scenario, f, ensure_ascii=False, indent=2)
        status_label.config(text=f"💾 Đã lưu kịch bản: {os.path.basename(file_path)}")
    except Exception as e:
        status_label.config(text=f"⚠️ Lưu không thành công: {e}")


def load_scenario():
    global templates, image_templates, process_loops, click_delay, infinite_loop

    file_path = filedialog.askopenfilename(filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
                                           title="Mở kịch bản AutoClick")
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            scenario = json.load(f)

        process_loops = scenario.get("process_loops", process_loops)
        infinite_loop = scenario.get("infinite_loop", False)
        click_delay = scenario.get("click_delay", click_delay)

        templates = []
        
        # Check if any image paths are missing
        missing_images = []
        for tpl in scenario.get("templates", []):
            if tpl.get("type") == "image":
                if not os.path.exists(tpl["path"]):
                    missing_images.append(tpl["path"])
        
        # If images are missing, ask user to select new base folder
        new_base_folder = None
        if missing_images:
            safe_print(f"⚠️ Không tìm thấy {len(missing_images)} ảnh mẫu")
            result = messagebox.askyesno(
                "Ảnh mẫu không tìm thấy",
                f"Không tìm thấy {len(missing_images)} ảnh mẫu.\n\n"
                f"Bạn có muốn chỉ định thư mục chứa ảnh mẫu không?\n\n"
                f"Ví dụ: {missing_images[0] if missing_images else 'image.png'}"
            )
            if result:
                new_base_folder = filedialog.askdirectory(title="Chọn thư mục chứa ảnh mẫu")
                if not new_base_folder:
                    raise ValueError("Bạn chưa chọn thư mục ảnh mẫu")

        for tpl in scenario.get("templates", []):
            if tpl.get("type") == "image":
                img_path = tpl["path"]
                
                # If path doesn't exist and we have a new base folder, try to find the image there
                if not os.path.exists(img_path) and new_base_folder:
                    img_filename = os.path.basename(img_path)
                    new_img_path = os.path.join(new_base_folder, img_filename)
                    if os.path.exists(new_img_path):
                        img_path = new_img_path
                        safe_print(f"✅ Tìm thấy ảnh tại: {new_img_path}")
                    else:
                        raise ValueError(f"Không tìm thấy ảnh: {img_filename} trong thư mục {new_base_folder}")
                
                img = imread_unicode(img_path)
                if img is None:
                    raise ValueError(f"Không đọc được ảnh mẫu: {img_path}")
                w, h = img.shape[::-1]
                templates.append({
                    "type": "image",
                    "img": img,
                    "w": w,
                    "h": h,
                    "repeat": tpl.get("repeat", 1),
                    "delay": tpl.get("delay", click_delay),
                    "path": img_path,
                    "wait_until_found": tpl.get("wait_until_found", False),
                    "wait_timeout": tpl.get("wait_timeout", 0),
                    "threshold": tpl.get("threshold", 0.7),
                    "click_delay": tpl.get("click_delay", 0.5),
                    "click_type": tpl.get("click_type", "single")
                })
            elif tpl.get("type") == "key":
                templates.append({
                    "type": "key",
                    "key": tpl.get("key", "enter"),
                    "repeat": tpl.get("repeat", 1),
                    "delay": tpl.get("delay", click_delay),
                    "key_type": tpl.get("key_type", "press"),
                    "delay_after": tpl.get("delay_after", 0.5),
                    "path": f"[KEY: {tpl.get('key', 'enter')}]"
                })
            else:
                templates.append({
                    "type": "coord",
                    "x": tpl.get("x", 0),
                    "y": tpl.get("y", 0),
                    "repeat": tpl.get("repeat", 1),
                    "delay": tpl.get("delay", click_delay),
                    "click_type": tpl.get("click_type", "single"),
                    "delay_after": tpl.get("delay_after", 0.5),
                    "path": f"({tpl.get('x',0)},{tpl.get('y',0)})"
                })

        update_history()
        status_label.config(text=f"📂 Đã tải kịch bản: {os.path.basename(file_path)}")
    except Exception as e:
        status_label.config(text=f"⚠️ Tải kịch bản thất bại: {e}")


def update_history():
    history_list.delete(0, tk.END)
    
    # Nếu có scenario_metadata, hiển thị từng kịch bản tách riêng
    if scenario_metadata:
        safe_print(f"🔵 [DEBUG] update_history: displaying {len(scenario_metadata)} scenarios")
        for scenario_idx, metadata in enumerate(scenario_metadata):
            # Header cho mỗi kịch bản
            scenario_name = os.path.basename(metadata["file_path"])
            history_list.insert(tk.END, f"{'='*60}")
            history_list.insert(tk.END, f"📋 KỊCH BẢN {scenario_idx + 1}: {scenario_name}")
            history_list.insert(tk.END, f"{'='*60}")
            
            # Hiển thị các item của kịch bản này
            templates_count = len(metadata["templates"])
            safe_print(f"🔵 [DEBUG] Scenario {scenario_idx + 1} has {templates_count} templates")
            
            if templates_count == 0:
                history_list.insert(tk.END, "  (Không có item)")
            else:
                for item_idx, tpl in enumerate(metadata["templates"]):
                    if tpl["type"] == "image":
                        delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
                        wait_str = " [⏳ CHỜ]" if tpl.get("wait_until_found", False) else ""
                        is_detection = tpl.get("is_detection", False)
                        
                        if is_detection:
                            history_list.insert(tk.END, f"  {item_idx+1}. 🔍 [DETECTION] {tpl['path']}{wait_str}")
                        else:
                            history_list.insert(tk.END, f"  {item_idx+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}{wait_str}")
                    elif tpl["type"] == "key":
                        delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
                        history_list.insert(tk.END, f"  {item_idx+1}. ⌨️ {tpl['path']} (nhấn {tpl['repeat']} lần){delay_str}")
                    else:
                        delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
                        history_list.insert(tk.END, f"  {item_idx+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}")
            
            history_list.insert(tk.END, "")  # Dòng trống giữa các kịch bản
    else:
        # Hiển thị templates thường (khi không có scenario_metadata)
        for i, tpl in enumerate(templates):
            if tpl["type"] == "image":
                delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
                wait_str = " [⏳ CHỜ]" if tpl.get("wait_until_found", False) else ""
                is_detection = tpl.get("is_detection", False)
                
                if is_detection:
                    history_list.insert(tk.END, f"{i+1}. 🔍 [DETECTION] {tpl['path']}{wait_str}")
                else:
                    history_list.insert(tk.END, f"{i+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}{wait_str}")
            elif tpl["type"] == "key":
                delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
                history_list.insert(tk.END, f"{i+1}. ⌨️ {tpl['path']} (nhấn {tpl['repeat']} lần){delay_str}")
            else:
                delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
                history_list.insert(tk.END, f"{i+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}")
    
    # Cập nhật setup info
    if scenario_metadata:
        setup_text = f"📋 Tổng {len(scenario_metadata)} kịch bản"
    elif infinite_loop:
        setup_text = f"🔄 Vòng lặp: ∞ (Vô hạn)  |  ⚡ Tốc độ: {click_delay}s"
    else:
        setup_text = f"🔄 Vòng lặp: {process_loops}  |  ⚡ Tốc độ: {click_delay}s"
    
    # Thêm phạm vi tìm kiếm nếu được set
    if search_region_enabled:
        region_text = f"  |  🔎 Phạm vi: ({search_region['x1']},{search_region['y1']})→({search_region['x2']},{search_region['y2']})"
        setup_text += region_text
    
    setup_info_text.set(setup_text)

def delete_selected():
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    selected_text = history_list.get(index)
    
    # Xóa từ templates
    if 0 <= index < len(templates):
        templates.pop(index)
        status_label.config(text="🗑️ Đã xóa mục khỏi danh sách.")
    
    update_history()

def clear_all_items():
    """Xóa toàn bộ mục trong kịch bản hiện tại"""
    global templates
    
    if not templates:
        status_label.config(text="⚠️ Không có mục nào để xóa.")
        return
    
    if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa toàn bộ mục trong kịch bản này?\n\nHành động này không thể hoàn tác!"):
        templates = []
        update_history()
        status_label.config(text="🗑️ Đã xóa toàn bộ mục khỏi kịch bản.")

def edit_delay():
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    selected_text = history_list.get(index)
    
    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        status_label.config(text="⚠️ Không thể edit delay của old detection item.")
        return
    
    # Kiểm tra xem có phải detection item trong templates không
    if "[DETECTION]" in selected_text:
        # Cho phép edit delay của detection items
        if 0 <= index < len(templates):
            new_delay = simpledialog.askfloat("Chỉnh sửa Delay", f"Nhập delay mới (hiện tại: {templates[index].get('delay', 0.5)}s):", minvalue=0.1, maxvalue=10.0)
            if new_delay is not None:
                templates[index]["delay"] = new_delay
                update_history()
                status_label.config(text=f"✍️ Đã chỉnh sửa delay thành {new_delay}s")
        return
    
    # Edit delay của templates thường
    if 0 <= index < len(templates):
        new_delay = simpledialog.askfloat("Chỉnh sửa Delay", f"Nhập delay mới (hiện tại: {templates[index].get('delay', click_delay)}s):", minvalue=0.1, maxvalue=10.0)
        if new_delay is not None:
            templates[index]["delay"] = new_delay
            update_history()
            status_label.config(text=f"✍️ Đã chỉnh sửa delay thành {new_delay}s")


def edit_image_config():
    """Chỉnh sửa tất cả thông số của ảnh, tọa độ, hoặc phím đã thêm"""
    selected = history_list.curselection()
    if not selected:
        status_label.config(text="⚠️ Vui lòng chọn một mục để chỉnh sửa.")
        return
    
    index = selected[0]
    selected_text = history_list.get(index)
    
    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        status_label.config(text="⚠️ Không thể edit old detection items. Hãy xóa và thêm lại.")
        return
    
    # Tính toán index thực tế trong templates (bỏ qua old detection items)
    actual_index = index
    for i in range(index):
        if "[OLD DETECTION]" in history_list.get(i):
            actual_index -= 1
    
    # Kiểm tra loại item
    if not (0 <= actual_index < len(templates)):
        status_label.config(text="⚠️ Không thể chỉnh sửa mục này.")
        return
    
    item_type = templates[actual_index]["type"]
    
    # Xử lý ảnh
    if item_type == "image":
        tpl = templates[actual_index]
        
        # Tạo dialog chỉnh sửa
        dialog = tk.Toplevel(root)
        dialog.title("✏️ Chỉnh sửa ảnh")
        dialog.geometry("550x650")
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(header_frame, text="✏️ Chỉnh sửa ảnh", font=("Segoe UI", 14, "bold"), 
                               bg=PKM_BG_INNER, fg=PKM_YELLOW)
        title_label.pack(pady=15)
        
        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
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
        delay_var = tk.StringVar(value=str(tpl.get("delay", click_delay)))
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
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        result = {"ok": False}
        
        def on_ok():
            result["ok"] = True
            dialog.destroy()
        
        def on_cancel():
            result["ok"] = False
            dialog.destroy()
        
        ok_btn = tk.Button(button_frame, text="✅ Lưu", command=on_ok, 
                           bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                           padx=30, pady=10, width=18)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                              padx=30, pady=10, width=18)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        dialog.transient(root)
        dialog.grab_set()
        root.wait_window(dialog)
        
        if result["ok"]:
            try:
                tpl["repeat"] = int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1
                tpl["delay"] = float(fields["delay"].get()) if fields["delay"].get() else click_delay
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
                templates[actual_index] = tpl
                update_history()
                status_label.config(text="✅ Đã cập nhật thông số ảnh")
            except Exception as e:
                status_label.config(text=f"⚠️ Lỗi: {e}")
    
    # Xử lý tọa độ
    elif item_type == "coord":
        tpl = templates[actual_index]
        config = show_coordinate_config_dialog()
        if config is not None:
            tpl["x"] = config["x"]
            tpl["y"] = config["y"]
            tpl["repeat"] = config["repeat"]
            tpl["click_type"] = config["click_type"]
            tpl["delay_after"] = config["delay_after"]
            tpl["path"] = f"({config['x']},{config['y']})"
            update_history()
            status_label.config(text=f"✅ Đã cập nhật tọa độ ({config['x']},{config['y']})")
    
    # Xử lý phím
    elif item_type == "key":
        tpl = templates[actual_index]
        config = show_keyboard_config_dialog()
        if config is not None:
            tpl["key"] = config["key"]
            tpl["repeat"] = config["repeat"]
            tpl["key_type"] = config["key_type"]
            tpl["delay_after"] = config["delay_after"]
            tpl["path"] = f"[KEY: {config['key']}]"
            update_history()
            status_label.config(text=f"✅ Đã cập nhật phím: {config['key']}")


def move_selected_up():
    global scenario_metadata
    
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    if index == 0: return
    
    selected_text = history_list.get(index)
    
    # Nếu có scenario_metadata, di chuyển kịch bản
    if scenario_metadata:
        # Tìm scenario index từ selected index
        scenario_idx = 0
        current_line = 0
        for s_idx, metadata in enumerate(scenario_metadata):
            # Header line
            current_line += 3  # 3 dòng header (===, KỊCH BẢN, ===)
            # Items
            num_items = len(metadata["templates"])
            if current_line + num_items > index:
                scenario_idx = s_idx
                break
            current_line += num_items + 1  # +1 dòng trống
        
        if scenario_idx > 0:
            scenario_metadata[scenario_idx - 1], scenario_metadata[scenario_idx] = \
                scenario_metadata[scenario_idx], scenario_metadata[scenario_idx - 1]
            scenario_queue[scenario_idx - 1], scenario_queue[scenario_idx] = \
                scenario_queue[scenario_idx], scenario_queue[scenario_idx - 1]
            update_history()
            status_label.config(text="⬆️ Đã chuyển kịch bản lên trên.")
        return
    
    # Xử lý templates thường
    selected_text = history_list.get(index)
    
    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        status_label.config(text="⚠️ Không thể di chuyển old detection items. Hãy xóa và thêm lại.")
        return
    
    # Kiểm tra xem item trước đó có phải old detection không
    prev_text = history_list.get(index - 1)
    if "[OLD DETECTION]" in prev_text:
        status_label.config(text="⚠️ Không thể di chuyển qua old detection items.")
        return
    
    # Tính toán index thực tế trong templates (bỏ qua old detection items)
    actual_index = index
    for i in range(index):
        if "[OLD DETECTION]" in history_list.get(i):
            actual_index -= 1
    
    # Swap trong templates
    if 0 <= actual_index - 1 < len(templates) and 0 <= actual_index < len(templates):
        templates[actual_index - 1], templates[actual_index] = templates[actual_index], templates[actual_index - 1]
        status_label.config(text="⬆️ Đã chuyển mục lên trên.")
        update_history()
        history_list.selection_set(index - 1)


def move_selected_down():
    global scenario_metadata
    
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    
    selected_text = history_list.get(index)
    
    # Nếu có scenario_metadata, di chuyển kịch bản
    if scenario_metadata:
        # Tìm scenario index từ selected index
        scenario_idx = 0
        current_line = 0
        for s_idx, metadata in enumerate(scenario_metadata):
            # Header line
            current_line += 3  # 3 dòng header (===, KỊCH BẢN, ===)
            # Items
            num_items = len(metadata["templates"])
            if current_line + num_items > index:
                scenario_idx = s_idx
                break
            current_line += num_items + 1  # +1 dòng trống
        
        if scenario_idx < len(scenario_metadata) - 1:
            scenario_metadata[scenario_idx], scenario_metadata[scenario_idx + 1] = \
                scenario_metadata[scenario_idx + 1], scenario_metadata[scenario_idx]
            scenario_queue[scenario_idx], scenario_queue[scenario_idx + 1] = \
                scenario_queue[scenario_idx + 1], scenario_queue[scenario_idx]
            update_history()
            status_label.config(text="⬇️ Đã chuyển kịch bản xuống dưới.")
        return
    
    # Xử lý templates thường
    selected_text = history_list.get(index)
    
    # Kiểm tra xem có phải old detection item không
    if "[OLD DETECTION]" in selected_text:
        status_label.config(text="⚠️ Không thể di chuyển old detection items. Hãy xóa và thêm lại.")
        return
    
    # Kiểm tra xem item tiếp theo có phải old detection không
    if index + 1 < history_list.size():
        next_text = history_list.get(index + 1)
        if "[OLD DETECTION]" in next_text:
            status_label.config(text="⚠️ Không thể di chuyển qua old detection items.")
            return
    
    # Tính toán index thực tế trong templates (bỏ qua old detection items)
    actual_index = index
    for i in range(index):
        if "[OLD DETECTION]" in history_list.get(i):
            actual_index -= 1
    
    # Swap trong templates
    if 0 <= actual_index < len(templates) and 0 <= actual_index + 1 < len(templates):
        templates[actual_index + 1], templates[actual_index] = templates[actual_index], templates[actual_index + 1]
        status_label.config(text="⬇️ Đã chuyển mục xuống dưới.")
        update_history()
        history_list.selection_set(index + 1)


def find_and_click():
    global running
    safe_print("🟢 [THREAD] find_and_click thread started")
    try:
        loop_count = 0
        while running and loop_count < process_loops:
            safe_print(f"🟢 [THREAD] Loop {loop_count + 1}/{process_loops}")
            for tpl in templates:
                if tpl["type"] == "image":
                    wait_until_found = tpl.get("wait_until_found", False)
                    wait_timeout = tpl.get("wait_timeout", 0)  # 0 = không chờ, 30 = 30s, -1 = vô cực
                    found = False
                    attempt = 0
                    
                    # Tính max_attempts dựa trên wait_timeout
                    if wait_timeout == -1:  # Vô cực
                        max_attempts = float('inf')
                    elif wait_until_found and wait_timeout > 0:
                        max_attempts = wait_timeout * 10  # 10 attempts per second
                    else:
                        max_attempts = 1
                    
                    while running and attempt < max_attempts and not found:
                        full_screenshot = capture_screen_gray()
                        screenshot, (offset_x, offset_y) = get_search_region_screenshot(full_screenshot)
                        res, used_scale, matched_w, matched_h = multi_scale_match(screenshot, tpl["img"])
                        threshold = tpl.get("threshold", 0.7)  # Lấy threshold từ template
                        loc = np.where(res >= threshold)

                        points = list(zip(*loc[::-1]))
                        filtered_points = filter_close_points(points, min_dist=max(10, matched_w//2))

                        if filtered_points:
                            safe_print(f"✅ Found {len(filtered_points)} match(es) for {tpl['path']} (threshold: {threshold}, scale: {used_scale:.2f}x)")
                            safe_print(f"✅ Image size (scaled): {matched_w}x{matched_h}, Offset: ({offset_x}, {offset_y})")
                            found = True

                            count = 0
                            for pt in filtered_points:
                                # Thêm offset để có tọa độ chính xác trên màn hình
                                click_x = pt[0] + matched_w//2 + offset_x
                                click_y = pt[1] + matched_h//2 + offset_y
                                safe_print(f"✅ Match at: ({pt[0]}, {pt[1]}), Center: ({pt[0] + matched_w//2}, {pt[1] + matched_h//2})")
                                safe_print(f"🖱️ Clicking at: ({click_x}, {click_y})")
                                
                                # Sử dụng click_type để xác định loại click
                                click_type = tpl.get("click_type", "single")
                                if click_type == "double":
                                    double_click(click_x, click_y)
                                    safe_print(f"🖱️ Double-clicked {tpl['path']} at: ({click_x}, {click_y})")
                                elif click_type == "hold":
                                    click_and_hold(click_x, click_y)
                                    safe_print(f"🖱️ Click-and-hold {tpl['path']} at: ({click_x}, {click_y})")
                                else:
                                    click(click_x, click_y)
                                    safe_print(f"🖱️ Clicked {tpl['path']} at: ({click_x}, {click_y})")
                                
                                # Delay sau click
                                click_delay_after = tpl.get("click_delay", 0.5)
                                time.sleep(click_delay_after)
                                count += 1
                                if count >= tpl["repeat"]:
                                    break
                                time.sleep(0.1)
                        else:
                            if wait_until_found:
                                attempt += 1
                                if attempt % 10 == 0:
                                    max_score = float(np.max(res)) if res.size else 0.0
                                    safe_print(f"⏳ Chờ tìm {tpl['path']}... ({attempt//10*1}s) [max_score={max_score:.3f}, threshold={threshold}, scale={used_scale:.2f}x]")
                                time.sleep(0.1)
                            else:
                                attempt = max_attempts
                    
                    if not found and wait_until_found:
                        if wait_timeout == -1:
                            safe_print(f"⚠️ Timeout: Không tìm được {tpl['path']} (chờ vô cực)")
                        else:
                            safe_print(f"⚠️ Timeout: Không tìm được {tpl['path']} sau {wait_timeout} giây")
                    elif not found:
                        safe_print(f"❌ Không tìm được {tpl['path']}")
                        
                elif tpl["type"] == "coord":
                    for i in range(tpl["repeat"]):
                        # Sử dụng click_type để xác định loại click
                        click_type = tpl.get("click_type", "single")
                        if click_type == "double":
                            double_click(tpl["x"], tpl["y"])
                            safe_print(f"🖱️ Double-clicked coordinate {tpl['path']}")
                        elif click_type == "hold":
                            click_and_hold(tpl["x"], tpl["y"])
                            safe_print(f"🖱️ Click-and-hold coordinate {tpl['path']}")
                        else:
                            click(tpl["x"], tpl["y"])
                            safe_print(f"🖱️ Clicked coordinate {tpl['path']}")
                        
                        # Delay sau click
                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0.1)
                
                elif tpl["type"] == "key":
                    for i in range(tpl["repeat"]):
                        key_type = tpl.get("key_type", "press")
                        if key_type == "hold":
                            # For hold, we need to press and hold for a bit
                            pyautogui.keyDown(tpl["key"])
                            time.sleep(0.2)
                            pyautogui.keyUp(tpl["key"])
                            safe_print(f"⌨️ Held key: {tpl['key']}")
                        else:
                            press_key(tpl["key"])
                            safe_print(f"⌨️ Pressed key: {tpl['key']}")
                        
                        # Delay sau nhấn
                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0.1)
                
                time.sleep(tpl.get("delay", click_delay))
            loop_count += 1
            if loop_count < process_loops:
                safe_print(f"🔄 Loop {loop_count}/{process_loops} completed")
    except Exception as e:
        safe_print(f"[AUTOCLICK THREAD ERROR] {e}")
        import traceback
        safe_print(traceback.format_exc())
        if 'status_label' in globals():
            status_label.config(text=f"⚠️ Lỗi AutoClick: {e}")
    finally:
        ended_by_stop = not running
        running = False
        safe_print(f"🟢 [THREAD] find_and_click thread ended (ended_by_stop={ended_by_stop})")
        if 'status_label' in globals():
            if ended_by_stop:
                set_status("⏹ AutoClick đã dừng.")
            else:
                set_status("✅ AutoClick đã hoàn tất!")

def start_clicking():
    global running, scenario_queue
    
    safe_print("🔵 [DEBUG] start_clicking() called")
    
    # Nếu có scenario queue, chạy nó
    if scenario_queue:
        safe_print("🔵 [DEBUG] Running scenario queue...")
        run_scenario_queue()
        return
    
    # Kiểm tra xem có bất kỳ hành động nào trong danh sách
    has_templates = len(templates) > 0
    
    safe_print(f"🔵 [DEBUG] has_templates={has_templates}")
    safe_print(f"🔵 [DEBUG] templates count={len(templates)}")
    
    if not has_templates:
        msg = "⚠️ Chưa thêm ảnh/tọa độ nào!"
        status_label.config(text=msg)
        safe_print(f"🔵 [DEBUG] {msg}")
        return
        
    running = True
    safe_print("🔵 [DEBUG] running=True, starting find_and_click thread...")
    set_status("⏺ AutoClick đang chạy...")
    
    # Khởi động find_and_click thread
    safe_print("🔵 [DEBUG] Starting find_and_click thread...")
    threading.Thread(target=find_and_click, daemon=True).start()

def stop_clicking(event=None):
    global running
    running = False
    set_status("⏹ AutoClick đã dừng.")

def load_multiple_scenarios():
    """Tải nhiều kịch bản để chạy liên tiếp"""
    global scenario_queue, scenario_metadata, templates, process_loops, infinite_loop, click_delay
    
    file_paths = filedialog.askopenfilenames(
        filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
        title="Chọn các kịch bản để chạy liên tiếp (Ctrl+Click để chọn nhiều)"
    )
    
    # Chuyển đổi tuple thành list
    if isinstance(file_paths, tuple):
        file_paths = list(file_paths)
    elif isinstance(file_paths, str):
        file_paths = [file_paths]
    else:
        file_paths = list(file_paths)
    
    if not file_paths:
        return
    
    # KHÔNG reset scenario_metadata - thêm vào danh sách hiện có
    # scenario_metadata = []  # <-- REMOVE THIS LINE
    failed_files = []
    
    safe_print(f"🔵 [DEBUG] Selected {len(file_paths)} scenario files to add")
    for fp in file_paths:
        safe_print(f"🔵 [DEBUG]   - {fp}")
    
    # Tải tất cả kịch bản vào scenario_metadata
    for file_idx, file_path in enumerate(file_paths):
        try:
            safe_print(f"🔵 [DEBUG] Loading scenario: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                scenario = json.load(f)
            
            # Check if any image paths are missing
            missing_images = []
            for tpl in scenario.get("templates", []):
                if tpl.get("type") == "image":
                    if not os.path.exists(tpl["path"]):
                        missing_images.append(tpl["path"])
            
            # If images are missing, ask user to select new base folder
            new_base_folder = None
            if missing_images:
                safe_print(f"⚠️ Không tìm thấy {len(missing_images)} ảnh mẫu trong kịch bản {os.path.basename(file_path)}")
                result = messagebox.askyesno(
                    "Ảnh mẫu không tìm thấy",
                    f"Kịch bản: {os.path.basename(file_path)}\n\n"
                    f"Không tìm thấy {len(missing_images)} ảnh mẫu.\n\n"
                    f"Bạn có muốn chỉ định thư mục chứa ảnh mẫu không?"
                )
                if result:
                    new_base_folder = filedialog.askdirectory(title="Chọn thư mục chứa ảnh mẫu")
                    if not new_base_folder:
                        raise ValueError(f"Bạn chưa chọn thư mục ảnh mẫu cho {os.path.basename(file_path)}")
                else:
                    raise ValueError(f"Không thể tải kịch bản {os.path.basename(file_path)} vì ảnh mẫu không tìm thấy")
            
            scenario_templates = []
            for tpl in scenario.get("templates", []):
                if tpl.get("type") == "image":
                    img_path = tpl["path"]
                    
                    # If path doesn't exist and we have a new base folder, try to find the image there
                    if not os.path.exists(img_path) and new_base_folder:
                        img_filename = os.path.basename(img_path)
                        new_img_path = os.path.join(new_base_folder, img_filename)
                        if os.path.exists(new_img_path):
                            img_path = new_img_path
                            safe_print(f"✅ Tìm thấy ảnh tại: {new_img_path}")
                        else:
                            raise ValueError(f"Không tìm thấy ảnh: {img_filename} trong thư mục {new_base_folder}")
                    
                    img = imread_unicode(img_path)
                    if img is not None:
                        w, h = img.shape[::-1]
                        scenario_templates.append({
                            "type": "image",
                            "img": img,
                            "w": w,
                            "h": h,
                            "repeat": tpl.get("repeat", 1),
                            "delay": tpl.get("delay", scenario.get("click_delay", 1.0)),
                            "path": img_path,
                            "wait_until_found": tpl.get("wait_until_found", False),
                            "wait_timeout": tpl.get("wait_timeout", 0),
                            "is_detection": False,
                            "threshold": tpl.get("threshold", 0.7),
                            "click_delay": tpl.get("click_delay", 0.5),
                            "click_type": tpl.get("click_type", "single")
                        })
                    else:
                        safe_print(f"⚠️ [DEBUG] Image not found: {img_path}")
                elif tpl.get("type") == "key":
                    scenario_templates.append({
                        "type": "key",
                        "key": tpl.get("key", "enter"),
                        "repeat": tpl.get("repeat", 1),
                        "delay": tpl.get("delay", scenario.get("click_delay", 1.0)),
                        "path": f"[KEY: {tpl.get('key', 'enter')}]"
                    })
                else:
                    scenario_templates.append({
                        "type": "coord",
                        "x": tpl.get("x", 0),
                        "y": tpl.get("y", 0),
                        "repeat": tpl.get("repeat", 1),
                        "delay": tpl.get("delay", scenario.get("click_delay", 1.0)),
                        "path": f"({tpl.get('x',0)},{tpl.get('y',0)})"
                    })
            
            safe_print(f"🔵 [DEBUG] Loaded scenario has {len(scenario_templates)} templates")
            
            scenario_metadata.append({
                "file_path": file_path,
                "process_loops": scenario.get("process_loops", 1),
                "infinite_loop": scenario.get("infinite_loop", False),
                "click_delay": scenario.get("click_delay", 1.0),
                "templates": scenario_templates
            })
            
            # Thêm vào scenario_queue
            scenario_queue.append(file_path)
        except Exception as e:
            failed_files.append(file_path)
            safe_print(f"⚠️ Lỗi tải kịch bản {file_path}: {e}")
            import traceback
            safe_print(traceback.format_exc())
    
    safe_print(f"🔵 [DEBUG] Total scenarios now: {len(scenario_metadata)}")

    if scenario_metadata:
        safe_print(f"🔵 [DEBUG] scenario_metadata contents:")
        for idx, meta in enumerate(scenario_metadata):
            safe_print(f"  Scenario {idx + 1}: {os.path.basename(meta['file_path'])} - {len(meta['templates'])} templates")
        
        update_history()
        status_label.config(text=f"📋 Tổng {len(scenario_metadata)} kịch bản. Bấm 'TUNG POKÉBALL!' để chạy.")
    else:
        if failed_files:
            failed_list = ", ".join([os.path.basename(p) for p in failed_files])
            status_label.config(text=f"⚠️ Không tải được kịch bản nào! File lỗi: {failed_list}.")
            messagebox.showerror("Lỗi tải kịch bản", f"Không tải được bất kỳ kịch bản nào. File lỗi:\n{failed_list}")
        else:
            status_label.config(text="⚠️ Không thể tải kịch bản nào!")


def clear_scenarios():
    """Xóa tất cả kịch bản đã tải"""
    global scenario_queue, scenario_metadata, templates
    scenario_queue = []
    scenario_metadata = []
    templates = []
    update_history()
    status_label.config(text="🗑️ Đã xóa tất cả kịch bản.")

def edit_scenario():
    """Chỉnh sửa kịch bản được chọn"""
    global scenario_metadata
    
    if not scenario_metadata:
        status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return
    
    selected = history_list.curselection()
    if not selected:
        status_label.config(text="⚠️ Vui lòng chọn một item để xác định kịch bản.")
        return
    
    index = selected[0]
    selected_text = history_list.get(index)
    
    # Tìm scenario index từ selected index
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(scenario_metadata):
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
    
    if scenario_idx >= len(scenario_metadata):
        status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return
    
    metadata = scenario_metadata[scenario_idx]
    scenario_name = os.path.basename(metadata["file_path"])
    
    # Tạo dialog chỉnh sửa kịch bản
    dialog = tk.Toplevel(root)
    dialog.title(f"✏️ Chỉnh sửa kịch bản: {scenario_name}")
    dialog.geometry("550x400")
    dialog.resizable(False, False)
    
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text=f"✏️ Chỉnh sửa kịch bản: {scenario_name}", 
                           font=("Segoe UI", 12, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
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
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    result = {"ok": False}
    
    def on_ok():
        result["ok"] = True
        dialog.destroy()
    
    def on_cancel():
        result["ok"] = False
        dialog.destroy()
    
    ok_btn = tk.Button(button_frame, text="✅ Lưu", command=on_ok, 
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    
    if result["ok"]:
        try:
            metadata["process_loops"] = int(fields["process_loops"].get()) if fields["process_loops"].get().isdigit() else 1
            metadata["infinite_loop"] = fields["infinite_loop"].get()
            metadata["click_delay"] = float(fields["click_delay"].get()) if fields["click_delay"].get() else 1.0
            
            update_history()
            status_label.config(text=f"✅ Đã cập nhật kịch bản: {scenario_name}")
        except Exception as e:
            status_label.config(text=f"⚠️ Lỗi: {e}")


def delete_selected_scenario():
    """Xóa kịch bản được chọn"""
    global scenario_metadata, scenario_queue
    
    if not scenario_metadata:
        status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return
    
    selected = history_list.curselection()
    if not selected:
        status_label.config(text="⚠️ Vui lòng chọn một item để xác định kịch bản.")
        return
    
    index = selected[0]
    
    # Tìm scenario index từ selected index
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(scenario_metadata):
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
    
    if scenario_idx >= len(scenario_metadata):
        status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return
    
    scenario_name = os.path.basename(scenario_metadata[scenario_idx]["file_path"])
    
    # Xác nhận xóa
    if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa kịch bản '{scenario_name}'?"):
        scenario_metadata.pop(scenario_idx)
        scenario_queue.pop(scenario_idx)
        update_history()
        status_label.config(text=f"🗑️ Đã xóa kịch bản: {scenario_name}")


def edit_scenario_details():
    """Edit chi tiết kịch bản - chỉnh sửa từng ảnh, thêm/xóa ảnh"""
    global scenario_metadata
    
    if not scenario_metadata:
        status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return
    
    selected = history_list.curselection()
    if not selected:
        status_label.config(text="⚠️ Vui lòng chọn một item để xác định kịch bản.")
        return
    
    index = selected[0]
    
    # Tìm scenario index từ selected index
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(scenario_metadata):
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
    
    if scenario_idx >= len(scenario_metadata):
        status_label.config(text="⚠️ Không thể xác định kịch bản.")
        return
    
    metadata = scenario_metadata[scenario_idx]
    scenario_name = os.path.basename(metadata["file_path"])
    
    # Tạo dialog chỉnh sửa chi tiết
    dialog = tk.Toplevel(root)
    dialog.title(f"✏️ Edit Kịch Bản: {scenario_name}")
    dialog.geometry("700x600")
    dialog.resizable(True, True)
    
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Header
    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text=f"✏️ Edit Kịch Bản: {scenario_name}", 
                           font=("Segoe UI", 12, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    # Content frame
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
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
    
    # Button frame
    button_frame = tk.Frame(content_frame, bg="white")
    button_frame.pack(fill=tk.X, pady=(0, 0))
    
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
        edit_dialog.geometry("550x650")
        edit_dialog.resizable(False, False)
        
        edit_main = tk.Frame(edit_dialog, bg="white")
        edit_main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        edit_header = tk.Frame(edit_main, bg=PKM_BG_INNER)
        edit_header.pack(fill=tk.X, padx=0, pady=0)
        
        edit_title = tk.Label(edit_header, text=f"✏️ Chỉnh sửa ảnh", 
                             font=("Segoe UI", 12, "bold"), bg=PKM_BG_INNER, fg=PKM_YELLOW)
        edit_title.pack(pady=15)
        
        edit_content = tk.Frame(edit_main, bg="white")
        edit_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
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
        
        # Button frame
        edit_button_frame = tk.Frame(edit_main, bg="white")
        edit_button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def on_ok():
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
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(edit_button_frame, text="❌ Hủy", command=edit_dialog.destroy, 
                              bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                              padx=30, pady=10, width=18)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
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


def run_scenario_queue():
    """Chạy tất cả kịch bản trong hàng đợi"""
    global scenario_queue, current_scenario_index, running, templates, process_loops, infinite_loop, click_delay
    
    if not scenario_metadata:
        status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return
    
    current_scenario_index = 0
    set_status(f"⏺ Chạy kịch bản 1/{len(scenario_metadata)}...")
    
    # Biến để theo dõi khi nào kịch bản hoàn tất
    scenario_completed = [False]
    
    def run_next_scenario():
        global current_scenario_index, running, templates, process_loops, infinite_loop, click_delay
        
        if current_scenario_index >= len(scenario_metadata):
            set_status(f"✅ Đã hoàn tất tất cả {len(scenario_metadata)} kịch bản!")
            running = False
            return
        
        # Lấy kịch bản từ scenario_metadata
        metadata = scenario_metadata[current_scenario_index]
        file_path = metadata["file_path"]
        
        try:
            process_loops = metadata.get("process_loops", 1)
            infinite_loop = metadata.get("infinite_loop", False)
            click_delay = metadata.get("click_delay", 1.0)
            
            # Copy templates từ metadata
            templates = []
            for tpl in metadata.get("templates", []):
                templates.append(tpl.copy())
            
            update_history()
            set_status(f"⏺ Chạy kịch bản {current_scenario_index + 1}/{len(scenario_metadata)}: {os.path.basename(file_path)}")
            
            safe_print(f"🔵 [DEBUG] Starting scenario {current_scenario_index + 1}/{len(scenario_metadata)}")
            
            # Reset scenario_completed flag
            scenario_completed[0] = False
            
            # QUAN TRỌNG: Set running = True trước khi chạy thread
            running = True
            
            # Chạy kịch bản này
            def run_scenario_thread():
                global running
                try:
                    find_and_click()
                finally:
                    scenario_completed[0] = True
            
            threading.Thread(target=run_scenario_thread, daemon=True).start()
            
            # Sau khi hoàn tất, chạy kịch bản tiếp theo
            def check_and_run_next():
                global current_scenario_index, running
                if scenario_completed[0]:
                    safe_print(f"🔵 [DEBUG] Scenario {current_scenario_index + 1} completed, moving to next")
                    current_scenario_index += 1
                    root.after(500, run_next_scenario)
                else:
                    root.after(200, check_and_run_next)
            
            root.after(200, check_and_run_next)
            
        except Exception as e:
            safe_print(f"⚠️ Lỗi tải kịch bản: {e}")
            import traceback
            safe_print(traceback.format_exc())
            current_scenario_index += 1
            root.after(500, run_next_scenario)
    
    run_next_scenario()

# --- Global Hotkeys Support ---
TK_TO_KEYBOARD = {
    "Escape": "esc",
    "space": "space",
    "Return": "enter",
    "BackSpace": "backspace",
    "Tab": "tab",
    "Caps_Lock": "caps lock",
    "Control_L": "ctrl",
    "Control_R": "ctrl",
    "Alt_L": "alt",
    "Alt_R": "alt",
    "Shift_L": "shift",
    "Shift_R": "shift",
    "period": ".",
    "comma": ",",
    "slash": "/",
    "backslash": "\\",
    "minus": "-",
    "equal": "=",
    "semicolon": ";",
    "apostrophe": "'",
    "bracketleft": "[",
    "bracketright": "]",
    "Up": "up",
    "Down": "down",
    "Left": "left",
    "Right": "right",
    "Prior": "page up",
    "Next": "page down",
    "End": "end",
    "Home": "home",
    "Insert": "insert",
    "Delete": "delete",
    "Num_Lock": "num lock",
    "Scroll_Lock": "scroll lock",
    "Pause": "pause",
}

def translate_key(keysym):
    if keysym.startswith("F") and keysym[1:].isdigit():
        return keysym.lower()
    if keysym in TK_TO_KEYBOARD:
        return TK_TO_KEYBOARD[keysym]
    if len(keysym) == 1:
        return keysym.lower()
    return keysym.lower()

def register_global_hotkeys():
    global start_hotkey, stop_hotkey
    try:
        keyboard.unhook_all()
    except Exception:
        pass
        
    try:
        if start_hotkey:
            keyboard.add_hotkey(start_hotkey, start_clicking)
    except Exception:
        if 'status_label' in globals():
            status_label.config(text=f"⚠️ Phím Start '{start_hotkey.upper()}' không hợp lệ hoặc bị trùng!")
        start_hotkey = ""
        
    try:
        if stop_hotkey:
            keyboard.add_hotkey(stop_hotkey, stop_clicking)
    except Exception:
        if 'status_label' in globals():
            status_label.config(text=f"⚠️ Phím Stop '{stop_hotkey.upper()}' không hợp lệ hoặc bị trùng!")
        stop_hotkey = ""

def change_start_hotkey():
    btn_hotkey_start.config(text="⏳ Nhấn phím...", bg="#fab387", fg="#11111b")
    status_label.config(text="⌨️ Hãy nhấn một phím trên bàn phím để gán làm phím Bắt đầu...")
    root.bind("<KeyPress>", capture_start_key)

def capture_start_key(event):
    global start_hotkey
    root.unbind("<KeyPress>")
    keysym = event.keysym
    key = translate_key(keysym)
    start_hotkey = key
    register_global_hotkeys()
    btn_hotkey_start.config(text=f"⌨️ Phím Start: {start_hotkey.upper()}", bg="#45475a", fg="#cdd6f4")
    status_label.config(text=f"✅ Đã đặt phím tắt Bắt đầu là: {start_hotkey.upper()}")

def change_stop_hotkey():
    btn_hotkey_stop.config(text="⏳ Nhấn phím...", bg="#fab387", fg="#11111b")
    status_label.config(text="⌨️ Hãy nhấn một phím trên bàn phím để gán làm phím Dừng...")
    root.bind("<KeyPress>", capture_stop_key)

def capture_stop_key(event):
    global stop_hotkey
    root.unbind("<KeyPress>")
    keysym = event.keysym
    key = translate_key(keysym)
    stop_hotkey = key
    register_global_hotkeys()
    btn_hotkey_stop.config(text=f"⌨️ Phím Stop: {stop_hotkey.upper()}", bg="#45475a", fg="#cdd6f4")
    status_label.config(text=f"✅ Đã đặt phím tắt Dừng là: {stop_hotkey.upper()}")

# ============================================================
# POKEMON THEMED GUI
# ============================================================

# === Pokemon Color Palette (Professional Theme)
PKM_BG_DARK   = "#0d0d0d"   # Nền tối nhất
PKM_BG_MAIN   = "#1a1a2e"   # Nền chính (xanh đen)
PKM_BG_CARD   = "#16213e"   # Nền card (xanh đậm)
PKM_BG_INNER  = "#0f3460"   # Listbox / inner (xanh sâu)
PKM_RED       = "#e94560"   # Pokéball đỏ (sáng hơn)
PKM_RED_LIGHT = "#ff6b7a"   # Red hover
PKM_RED_DARK  = "#c41e3a"   # Red dark
PKM_YELLOW    = "#ffd60a"   # Pikachu vàng (sáng)
PKM_YELLOW_DK = "#ffc300"   # Yellow hover/dark
PKM_BLUE      = "#457b9d"   # Pokéball xanh (chuyên nghiệp)
PKM_BLUE_LT   = "#6ba3d4"   # Blue hover
PKM_BLUE_DARK = "#1d3557"   # Blue dark
PKM_WHITE     = "#f1faee"   # Chữ chính (trắng ấm)
PKM_GRAY      = "#a8dadc"   # Text phụ
PKM_GREEN     = "#2a9d8f"   # Màu HP / active (xanh lá)
PKM_GREEN_LT  = "#52b788"   # Green hover
PKM_GOLD      = "#e76f51"   # Tiêu đề (cam)
PKM_BORDER    = "#ffd60a"   # Border highlight (vàng)

# ════════════════════════════════════════════════════════════
# DIALOG FUNCTIONS - Phải định nghĩa TRƯỚC khi root được tạo
# ════════════════════════════════════════════════════════════

def show_image_config_dialog(is_detection=False):
    """Hiển thị dialog gộp tất cả cài đặt cho ảnh"""
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt ảnh")
    dialog.geometry("550x650")
    dialog.resizable(False, False)
    
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text="⚙️ Cài đặt ảnh", font=("Segoe UI", 14, "bold"), 
                           bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    fields = {}
    
    tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    repeat_entry = tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
    repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["repeat"] = repeat_var
    
    tk.Label(content_frame, text="⏱️ Delay trước (giây):", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    delay_var = tk.StringVar(value=str(click_delay))
    delay_entry = tk.Entry(content_frame, textvariable=delay_var, font=("Segoe UI", 11), width=40)
    delay_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay"] = delay_var
    
    tk.Label(content_frame, text="🖱️ Loại click:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_type_var = tk.StringVar(value="single")
    click_type_combo = tk.OptionMenu(content_frame, click_type_var, "single", "double", "hold")
    click_type_combo.config(font=("Segoe UI", 11), bg="white", fg="black", 
                           activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    click_type_combo.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_type"] = click_type_var
    
    tk.Label(content_frame, text="⏳ Delay sau click (giây):", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    click_delay_var = tk.StringVar(value="0.5")
    click_delay_entry = tk.Entry(content_frame, textvariable=click_delay_var, font=("Segoe UI", 11), width=40)
    click_delay_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["click_delay"] = click_delay_var
    
    tk.Label(content_frame, text="🎯 Threshold (0.0-1.0):", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    threshold_var = tk.StringVar(value="0.7")
    threshold_entry = tk.Entry(content_frame, textvariable=threshold_var, font=("Segoe UI", 11), width=40)
    threshold_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["threshold"] = threshold_var
    
    tk.Label(content_frame, text="⏳ Chờ tìm được?:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    wait_var = tk.StringVar(value="không")
    wait_combo = tk.OptionMenu(content_frame, wait_var, "không", "có (30s)", "vô cực")
    wait_combo.config(font=("Segoe UI", 11), bg="white", fg="black", 
                     activebackground=PKM_BLUE_LT, activeforeground="white", width=37)
    wait_combo.pack(anchor="w", pady=(0, 25), fill=tk.X)
    fields["wait_until_found"] = wait_var
    
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    result = {"ok": False}
    
    def on_ok():
        result["ok"] = True
        dialog.destroy()
    
    def on_cancel():
        result["ok"] = False
        dialog.destroy()
    
    ok_btn = tk.Button(button_frame, text="✅ OK", command=on_ok, 
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    
    if result["ok"]:
        try:
            repeat = int(fields["repeat"].get()) if fields["repeat"].get().isdigit() else 1
            delay = float(fields["delay"].get()) if fields["delay"].get() else click_delay
            click_type = fields["click_type"].get()
            click_delay_after = float(fields["click_delay"].get()) if fields["click_delay"].get() else 0.5
            threshold = float(fields["threshold"].get()) if fields["threshold"].get() else 0.7
            wait_choice = fields["wait_until_found"].get()
            
            # Xử lý tùy chọn chờ
            if wait_choice == "vô cực":
                wait_until_found = True
                wait_timeout = -1  # -1 = vô cực
            elif wait_choice == "có (30s)":
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
                "wait_timeout": wait_timeout
            }
        except:
            return None
    return None

def show_coordinate_config_dialog():
    """Hiển thị dialog gộp tất cả cài đặt cho tọa độ"""
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt tọa độ")
    dialog.geometry("550x550")
    dialog.resizable(False, False)
    
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text="⚙️ Cài đặt tọa độ", font=("Segoe UI", 14, "bold"), 
                           bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    fields = {}
    
    tk.Label(content_frame, text="📍 Tọa độ X:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    x_var = tk.StringVar(value="0")
    x_entry = tk.Entry(content_frame, textvariable=x_var, font=("Segoe UI", 11), width=40)
    x_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["x"] = x_var
    
    tk.Label(content_frame, text="📍 Tọa độ Y:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    y_var = tk.StringVar(value="0")
    y_entry = tk.Entry(content_frame, textvariable=y_var, font=("Segoe UI", 11), width=40)
    y_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["y"] = y_var
    
    tk.Label(content_frame, text="📍 Số lần click:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    repeat_entry = tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
    repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
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
    delay_after_entry = tk.Entry(content_frame, textvariable=delay_after_var, font=("Segoe UI", 11), width=40)
    delay_after_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay_after"] = delay_after_var
    
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    result = {"ok": False}
    
    def on_ok():
        result["ok"] = True
        dialog.destroy()
    
    def on_cancel():
        result["ok"] = False
        dialog.destroy()
    
    ok_btn = tk.Button(button_frame, text="✅ OK", command=on_ok, 
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
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
    """Hiển thị dialog gộp tất cả cài đặt cho phím"""
    dialog = tk.Toplevel(root)
    dialog.title("⚙️ Cài đặt phím")
    dialog.geometry("550x550")
    dialog.resizable(False, False)
    
    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    title_label = tk.Label(header_frame, text="⚙️ Cài đặt phím", font=("Segoe UI", 14, "bold"), 
                           bg=PKM_BG_INNER, fg=PKM_YELLOW)
    title_label.pack(pady=15)
    
    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    fields = {}
    
    tk.Label(content_frame, text="⌨️ Tên phím:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    tk.Label(content_frame, text="(ví dụ: enter, space, a, 1, f1, ctrl+c, alt+tab)", 
             font=("Segoe UI", 9), bg="white", fg=PKM_BLUE_LT).pack(anchor="w", pady=(0, 5))
    key_var = tk.StringVar(value="enter")
    key_entry = tk.Entry(content_frame, textvariable=key_var, font=("Segoe UI", 11), width=40)
    key_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["key"] = key_var
    
    tk.Label(content_frame, text="📍 Số lần nhấn:", font=("Segoe UI", 11, "bold"), 
             bg="white", fg="black").pack(anchor="w", pady=(10, 3))
    repeat_var = tk.StringVar(value="1")
    repeat_entry = tk.Entry(content_frame, textvariable=repeat_var, font=("Segoe UI", 11), width=40)
    repeat_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
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
    delay_after_entry = tk.Entry(content_frame, textvariable=delay_after_var, font=("Segoe UI", 11), width=40)
    delay_after_entry.pack(anchor="w", pady=(0, 15), fill=tk.X)
    fields["delay_after"] = delay_after_var
    
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    result = {"ok": False}
    
    def on_ok():
        result["ok"] = True
        dialog.destroy()
    
    def on_cancel():
        result["ok"] = False
        dialog.destroy()
    
    ok_btn = tk.Button(button_frame, text="✅ OK", command=on_ok, 
                       bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), 
                       padx=30, pady=10, width=18)
    ok_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="❌ Hủy", command=on_cancel, 
                          bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=30, pady=10, width=18)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
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


# GUI Root Window - Responsive Design
root = tk.Tk()
root.title("⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu")

# Get screen dimensions for responsive sizing
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate optimal window size (70% of screen, min 800x600, max 1400x1000)
window_width = max(800, min(1400, int(screen_width * 0.7)))
window_height = max(600, min(1000, int(screen_height * 0.75)))

root.geometry(f"{window_width}x{window_height}")
root.resizable(True, True)  # Enable resizing
root.configure(bg=PKM_BG_MAIN)

# Store window dimensions for responsive scaling
root.base_width = window_width
root.base_height = window_height

bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pokemon_bg.png")
if not os.path.exists(bg_path):
    pass
else:
    try:
        # Resize background to match window size
        img = Image.open(bg_path).resize((window_width, window_height), Image.LANCZOS)
        # Làm tối thêm một chút để chữ dễ đọc trên background
        img = ImageEnhance.Brightness(img).enhance(0.45)
        # Thêm blur nhẹ tạo hiệu ứng depth
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        _bg_photo = ImageTk.PhotoImage(img)
        bg_canvas = tk.Canvas(root, width=window_width, height=window_height,
                              highlightthickness=0, bd=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        bg_canvas.create_image(0, 0, anchor="nw", image=_bg_photo)
        bg_canvas.lower()  # Đẩy xuống dưới tất cả widget
        
        # Update background when window is resized
        def on_window_resize(event=None):
            try:
                if hasattr(root, '_resize_timer'):
                    root.after_cancel(root._resize_timer)
                root._resize_timer = root.after(500, update_bg_on_resize)
            except:
                pass
        
        def update_bg_on_resize():
            try:
                new_width = root.winfo_width()
                new_height = root.winfo_height()
                if new_width > 1 and new_height > 1:
                    img_resized = Image.open(bg_path).resize((new_width, new_height), Image.LANCZOS)
                    img_resized = ImageEnhance.Brightness(img_resized).enhance(0.45)
                    img_resized = img_resized.filter(ImageFilter.GaussianBlur(radius=2))
                    new_photo = ImageTk.PhotoImage(img_resized)
                    bg_canvas.create_image(0, 0, anchor="nw", image=new_photo)
                    bg_canvas.image = new_photo
            except:
                pass
        
        root.bind("<Configure>", on_window_resize)
    except Exception as e:
        pass  # Nếu load thất bại thì bỏ qua, dùng màu nền thường

# ─── Helper: Responsive font sizing ─────────────────────────────────────
def get_responsive_font(base_size, style="normal"):
    """Calculate responsive font size based on window width"""
    try:
        scale_factor = max(0.8, min(1.2, root.winfo_width() / 1000.0))
        size = max(7, int(base_size * scale_factor))
        if style == "bold":
            return ("Segoe UI", size, "bold")
        else:
            return ("Segoe UI", size)
    except:
        if style == "bold":
            return ("Segoe UI", base_size, "bold")
        else:
            return ("Segoe UI", base_size)

# ─── Helper: tạo nút theo phong cách Pokemon battle menu ────────────────
def create_btn(parent, text, command, bg=PKM_RED, fg=PKM_WHITE,
               hover_bg=None, font=("Segoe UI", 9, "bold"), **kwargs):
    _hover = hover_bg or bg
    btn = tk.Button(
        parent, text=text, command=command, font=font,
        bg=bg, fg=fg, activebackground=_hover, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2", padx=6, pady=3,
        highlightthickness=2, highlightbackground=PKM_BORDER,
        highlightcolor=PKM_YELLOW, **kwargs
    )
    def on_enter(e):
        if btn["state"] != "disabled":
            btn.config(bg=_hover)
    def on_leave(e):
        if btn["state"] != "disabled":
            btn.config(bg=bg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    # Store original properties for responsive adjustment
    btn._original_padx = 6
    btn._original_pady = 3
    btn._original_font = font
    btn._base_font_size = font[1] if len(font) > 1 else 9
    btn._bg = bg
    btn._hover_bg = _hover
    
    return btn

# ─── Helper: tạo Card kiểu Pokédex ──────────────────────────────────────
def create_card(parent, title, title_color=PKM_YELLOW):
    # Outer border frame (giả lập viền Pokédex) - NO PADDING
    border = tk.Frame(parent, bg=title_color, bd=0)
    border.pack(fill="both", expand=True, pady=(0, 6), padx=0)

    # Pokéball accent dot + title bar
    title_bar = tk.Frame(border, bg=PKM_BG_CARD, pady=4, padx=6)
    title_bar.pack(fill="x", side="top")

    dot_canvas = tk.Canvas(title_bar, width=14, height=14,
                           bg=PKM_BG_CARD, highlightthickness=0)
    dot_canvas.pack(side="left", padx=(0, 6))
    dot_canvas.create_oval(1, 1, 13, 13, fill=title_color, outline=PKM_WHITE, width=2)
    dot_canvas.create_line(1, 7, 13, 7, fill=PKM_WHITE, width=2)

    # Responsive font size for title
    title_font_size = 10
    try:
        if root.winfo_width() < 900:
            title_font_size = 8
        elif root.winfo_width() < 1200:
            title_font_size = 9
    except:
        pass

    title_label = tk.Label(title_bar, text=title, font=("Segoe UI", title_font_size, "bold"),
             bg=PKM_BG_CARD, fg=title_color)
    title_label.pack(side="left")
    
    # Store for responsive scaling
    title_label._base_size = 10
    title_label._title_color = title_color

    # Divider line giả viền ngang Pokédex
    tk.Frame(border, bg=title_color, height=2).pack(fill="x")

    # Card inner content area - FULL WIDTH, NO PADDING
    inner = tk.Frame(border, bg=PKM_BG_CARD, padx=0, pady=0)
    inner.pack(fill="both", expand=True)
    
    # Store original padding for scaling
    inner._original_padx = 0
    inner._original_pady = 0
    
    return inner

# ════════════════════════════════════════════════════════════
#  HEADER — Pokédex Style Banner (Responsive)
# ════════════════════════════════════════════════════════════
header_frame = tk.Frame(root, bg=PKM_RED)
header_frame.pack(fill="x", side="top")

# Left side decoration: Pokéball design
left_deco = tk.Canvas(header_frame, width=100, height=85,
                      bg=PKM_RED, highlightthickness=0)
left_deco.pack(side="left", padx=5)
# Main circle
left_deco.create_oval(15, 15, 75, 75, fill=PKM_RED, outline=PKM_WHITE, width=3)
# Horizontal line
left_deco.create_line(15, 45, 75, 45, fill=PKM_WHITE, width=3)
# Top circle (blue)
left_deco.create_oval(25, 25, 65, 45, fill=PKM_BLUE, outline="", width=0)
# Bottom circle (white)
left_deco.create_oval(25, 45, 65, 65, fill=PKM_WHITE, outline="", width=0)
# Center dot
left_deco.create_oval(40, 40, 50, 50, fill=PKM_BG_DARK, outline=PKM_WHITE, width=2)

# Title text
title_frame = tk.Frame(header_frame, bg=PKM_RED)
title_frame.pack(side="left", padx=15, fill="both", expand=True)
tk.Label(title_frame, text="⚡ POKÉCLICK PRO",
         font=("Segoe UI", 16, "bold"), bg=PKM_RED, fg=PKM_YELLOW).pack(anchor="w")
tk.Label(title_frame, text="Hệ thống Tự Động Chiến Đấu · Image Recognition · Win32",
         font=("Segoe UI", 8), bg=PKM_RED, fg=PKM_WHITE).pack(anchor="w")

# Right: HP bar decoration
hp_frame = tk.Frame(header_frame, bg=PKM_RED)
hp_frame.pack(side="right", padx=25)
tk.Label(hp_frame, text="TRAINER HP", font=("Segoe UI", 8, "bold"),
         bg=PKM_RED, fg=PKM_WHITE).pack(anchor="e")
hp_bar_bg = tk.Frame(hp_frame, bg=PKM_BG_DARK, height=12, width=140)
hp_bar_bg.pack(anchor="e", pady=(2, 0))
hp_bar_bg.pack_propagate(False)
hp_bar_fill = tk.Frame(hp_bar_bg, bg=PKM_GREEN, height=12, width=120)
hp_bar_fill.place(x=0, y=0)
tk.Label(hp_frame, text="110 / 130",
         font=("Segoe UI", 8), bg=PKM_RED, fg=PKM_GREEN_LT).pack(anchor="e")

# Thin separator line
tk.Frame(root, bg=PKM_GOLD, height=2).pack(fill="x")

# ════════════════════════════════════════════════════════════
#  BODY LAYOUT - RESPONSIVE GRID SYSTEM
# ════════════════════════════════════════════════════════════
body_frame = tk.Frame(root, bg=PKM_BG_MAIN)
body_frame.pack(fill="both", expand=True, padx=0, pady=0)

# Configure grid weights for responsive behavior - EQUAL EXPANSION
body_frame.grid_rowconfigure(0, weight=1)
body_frame.grid_columnconfigure(0, weight=1)  # Left panel - EXPAND
body_frame.grid_columnconfigure(1, weight=0)  # Separator - FIXED
body_frame.grid_columnconfigure(2, weight=1)  # Right panel - EXPAND

# LEFT PANEL with scrollbar
left_panel_outer = tk.Frame(body_frame, bg=PKM_BG_MAIN)
left_panel_outer.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

left_canvas = tk.Canvas(left_panel_outer, bg=PKM_BG_MAIN, highlightthickness=0)
left_scrollbar = tk.Scrollbar(left_panel_outer, orient="vertical", command=left_canvas.yview)
left_panel = tk.Frame(left_canvas, bg=PKM_BG_MAIN)

left_panel.bind(
    "<Configure>",
    lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
)

left_canvas.configure(yscrollcommand=left_scrollbar.set)

left_canvas_window = left_canvas.create_window((0, 0), window=left_panel, anchor="nw")

# Force left_panel to expand to canvas width ONLY if content is smaller
def _on_left_canvas_configure(event):
    canvas_width = event.width
    # Get the required width of the panel content
    left_panel.update_idletasks()
    panel_width = left_panel.winfo_reqwidth()
    # Only expand if canvas is wider than content
    if canvas_width > panel_width:
        left_canvas.itemconfig(left_canvas_window, width=canvas_width)
    else:
        left_canvas.itemconfig(left_canvas_window, width=panel_width)

left_canvas.pack(side="left", fill="both", expand=True)
left_scrollbar.pack(side="right", fill="y")

left_canvas.bind("<Configure>", _on_left_canvas_configure)

# SEPARATOR LINE
separator = tk.Frame(body_frame, bg=PKM_GOLD, width=2)
separator.grid(row=0, column=1, sticky="ns", padx=0, pady=0)

# RIGHT PANEL with scrollbar
right_panel_outer = tk.Frame(body_frame, bg=PKM_BG_MAIN)
right_panel_outer.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)

right_canvas = tk.Canvas(right_panel_outer, bg=PKM_BG_MAIN, highlightthickness=0)
right_scrollbar = tk.Scrollbar(right_panel_outer, orient="vertical", command=right_canvas.yview)
right_panel = tk.Frame(right_canvas, bg=PKM_BG_MAIN)

right_panel.bind(
    "<Configure>",
    lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
)

right_canvas.configure(yscrollcommand=right_scrollbar.set)

right_canvas_window = right_canvas.create_window((0, 0), window=right_panel, anchor="nw")

# Force right_panel to expand to canvas width ONLY if content is smaller
def _on_right_canvas_configure(event):
    canvas_width = event.width
    # Get the required width of the panel content
    right_panel.update_idletasks()
    panel_width = right_panel.winfo_reqwidth()
    # Only expand if canvas is wider than content
    if canvas_width > panel_width:
        right_canvas.itemconfig(right_canvas_window, width=canvas_width)
    else:
        right_canvas.itemconfig(right_canvas_window, width=panel_width)

right_canvas.pack(side="left", fill="both", expand=True)
right_scrollbar.pack(side="right", fill="y")

right_canvas.bind("<Configure>", _on_right_canvas_configure)

# Bind mousewheel to right canvas as well
right_canvas.bind("<MouseWheel>", lambda e: right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
right_panel.bind("<MouseWheel>", lambda e: right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

# Smart mouse wheel scrolling
def _on_mousewheel(event):
    try:
        # Try to scroll the canvas that the mouse is over
        try:
            if left_canvas.winfo_containing(event.x_root, event.y_root):
                left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                return
        except:
            pass
        
        try:
            if right_canvas.winfo_containing(event.x_root, event.y_root):
                right_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                return
        except:
            pass
    except:
        pass

left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ════════════════════════════════════════════════════════════
#  LEFT PANEL — Controls
# ════════════════════════════════════════════════════════════

# ── SECTION 1: Kỹ năng tuần tự ──────────────────────────────
act_inner = create_card(left_panel, "⚔️  KỸ NĂNG CHIẾN ĐẤU (Tuần tự)", PKM_GOLD)

btn_add_img = create_btn(act_inner, "🖼️  Thêm Pokémon mục tiêu (Ảnh)",
                         add_image, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT)
btn_add_img.pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

btn_add_coord = create_btn(act_inner, "📍  Thêm tọa độ chiến trường (XY)",
                           add_coordinate, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT)
btn_add_coord.pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

btn_add_pos = create_btn(act_inner, "🎯  Ghi nhớ vị trí chuột hiện tại  [⏳ 3s]",
                         add_current_position, bg=PKM_GREEN, fg=PKM_BG_DARK, hover_bg=PKM_GREEN_LT)
btn_add_pos.pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

btn_add_key = create_btn(act_inner, "⌨️  Thêm phím bàn phím",
                         add_keyboard_key, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT)
btn_add_key.pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

# ── SECTION 2: Túi đồ Trainer ────────────────────────────────
settings_inner = create_card(left_panel, "🎒  TÚI ĐỒ TRAINER (Cấu hình)", PKM_GOLD)

settings_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
settings_row.pack(fill="both", expand=True, pady=2, padx=0)

btn_loop = create_btn(settings_row, "🔄 Số trận đấu",
                      set_process_loops, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_loop.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

btn_speed = create_btn(settings_row, "⚡ Tốc độ tấn công",
                       set_speed, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_speed.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

human_mode_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
human_mode_row.pack(fill="both", expand=True, pady=(4, 2), padx=0)

btn_human_mode = create_btn(human_mode_row, "🤖 Click tức thì: BẬT",
                            toggle_human_click, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_human_mode.pack(fill="both", expand=True, ipady=5)

hotkey_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
hotkey_row.pack(fill="both", expand=True, pady=(4, 2), padx=0)

btn_hotkey_start = create_btn(hotkey_row, f"⌨️ Phím Chiến Đấu: {start_hotkey.upper()}",
                              change_start_hotkey,
                              bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE)
btn_hotkey_start.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

btn_hotkey_stop = create_btn(hotkey_row, f"⌨️ Phím Rút Lui: {stop_hotkey.upper()}",
                             change_stop_hotkey,
                             bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE)
btn_hotkey_stop.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
scenario_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

btn_save_scenario = create_btn(scenario_row, "💾 Lưu dữ liệu Trainer",
                               save_scenario, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_save_scenario.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

btn_load_scenario = create_btn(scenario_row, "📂 Tải dữ liệu Trainer",
                               load_scenario, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_load_scenario.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

multi_scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
multi_scenario_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

btn_load_multi = create_btn(multi_scenario_row, "📚 Tải nhiều kịch bản",
                            load_multiple_scenarios, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_load_multi.pack(fill="both", expand=True, ipady=5, padx=0)

clear_scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
clear_scenario_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

btn_clear_scenarios = create_btn(clear_scenario_row, "🗑️ Xóa tất cả kịch bản",
                                 clear_scenarios, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT)
btn_clear_scenarios.pack(fill="both", expand=True, ipady=5, padx=0)

search_region_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
search_region_row.pack(fill="both", expand=True, pady=(4, 0), padx=0)

btn_search_region = create_btn(search_region_row, "🔎 Giới hạn phạm vi tìm kiếm",
                               set_search_region, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_search_region.pack(fill="both", expand=True, ipady=5, padx=0)

# ── SECTION 3: Chiến đấu! ───────────────────────────────────
exec_inner = create_card(left_panel, "⚡  CHIẾN ĐẤU!", PKM_GREEN)

exec_row = tk.Frame(exec_inner, bg=PKM_BG_CARD)
exec_row.pack(fill="both", expand=True, pady=4, padx=0)

btn_start = create_btn(exec_row, "  ⚡  TUNG POKÉBALL!  ",
                       start_clicking, bg=PKM_GREEN, fg=PKM_BG_DARK,
                       hover_bg=PKM_GREEN_LT, font=("Segoe UI", 11, "bold"))
btn_start.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=7)

btn_stop = create_btn(exec_row, "  🏃  RÚT LUI!  ",
                      stop_clicking, bg=PKM_RED, fg=PKM_WHITE,
                      hover_bg=PKM_RED_LIGHT, font=("Segoe UI", 11, "bold"))
btn_stop.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=7)

status_top_var = tk.StringVar(value="❓ Wild AutoClick appeared!  Chờ lệnh Trainer...")
status_top_display = tk.Label(exec_inner, textvariable=status_top_var,
                              font=("Segoe UI", 8), bg=PKM_BG_CARD,
                              fg=PKM_GRAY, wraplength=320, justify="left", pady=4)
status_top_display.pack(fill="x", pady=(6, 0), padx=0)

# Separator line
tk.Frame(exec_inner, bg=PKM_GREEN, height=1).pack(fill="x", pady=(6, 0))

# ════════════════════════════════════════════════════════════
#  RIGHT PANEL — Pokédex Danh Sách
# ════════════════════════════════════════════════════════════
queue_inner = create_card(right_panel, "📜  POKÉDEX KỊCH BẢN", PKM_YELLOW)

# Lucario background decoration with image - RESPONSIVE
lucario_bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HD-wallpaper-lucario-pokemon-thumbnail.jpg")
lucario_container = tk.Frame(queue_inner, bg=PKM_BG_CARD)
lucario_container.pack(fill="x", pady=(0, 8))

# Responsive height based on window size
def update_lucario_height():
    try:
        window_width = root.winfo_width()
        if window_width < 900:
            lucario_container.pack_configure(pady=(0, 0))
            lucario_container.pack_propagate(True)
            # Hide by setting height to 0
            for child in lucario_container.winfo_children():
                child.pack_forget()
        else:
            lucario_container.pack_configure(pady=(0, 8))
            lucario_container.pack_propagate(False)
            # Show content
            for child in lucario_container.winfo_children():
                child.pack(fill="both", expand=True)
    except:
        pass

lucario_container.pack_propagate(False)

if os.path.exists(lucario_bg_path) and PIL_AVAILABLE:
    try:
        lucario_img = Image.open(lucario_bg_path)
        # Resize to fit container (380x120)
        lucario_img = lucario_img.resize((380, 120), Image.LANCZOS)
        # Darken slightly for better text visibility
        lucario_img = ImageEnhance.Brightness(lucario_img).enhance(0.7)
        _lucario_photo = ImageTk.PhotoImage(lucario_img)
        
        lucario_canvas = tk.Canvas(lucario_container, width=380, height=120,
                                   bg=PKM_BG_CARD, highlightthickness=0)
        lucario_canvas.pack(fill="both", expand=True)
        lucario_canvas.create_image(0, 0, anchor="nw", image=_lucario_photo)
        
        # Add semi-transparent overlay with text
        overlay = tk.Label(lucario_container, text="Lucario Ready for Battle! ⚡",
                          font=("Segoe UI", 12, "bold"), bg=PKM_BG_CARD, fg=PKM_YELLOW,
                          relief="flat", bd=0)
        overlay.place(x=10, y=50, anchor="w")
    except Exception as e:
        safe_print(f"Error loading Lucario image: {e}")
        # Fallback to canvas drawing
        lucario_canvas = tk.Canvas(lucario_container, width=380, height=120,
                                   bg=PKM_BG_CARD, highlightthickness=0)
        lucario_canvas.pack(fill="both", expand=True)
        lucario_canvas.create_text(190, 60, text="Lucario Ready for Battle!", 
                                  font=("Segoe UI", 14, "bold"), fill=PKM_YELLOW)
else:
    # Fallback to canvas drawing if image not found
    lucario_canvas = tk.Canvas(lucario_container, width=380, height=120,
                               bg=PKM_BG_CARD, highlightthickness=0)
    lucario_canvas.pack(fill="both", expand=True)
    lucario_canvas.create_text(190, 60, text="Lucario Ready for Battle!", 
                              font=("Segoe UI", 14, "bold"), fill=PKM_YELLOW)

# Setup Info Section - Hiển thị cấu hình kịch bản
setup_info_frame = tk.Frame(queue_inner, bg=PKM_BG_CARD, relief="flat", bd=0)
setup_info_frame.pack(fill="x", pady=(4, 4), padx=0)

setup_info_text = tk.StringVar(value="🔄 Vòng lặp: 1  |  ⚡ Tốc độ: 1.0s")
setup_info_label = tk.Label(setup_info_frame, textvariable=setup_info_text,
                            font=("Segoe UI", 8), bg=PKM_BG_CARD, fg=PKM_YELLOW,
                            anchor="center", justify="center", wraplength=360)
setup_info_label.pack(fill="x", padx=4, pady=2)

# Listbox container với viền vàng giả màn hình Pokédex
list_border = tk.Frame(queue_inner, bg=PKM_GOLD, padx=2, pady=2)
list_border.pack(fill="both", expand=True, pady=2)

list_frame = tk.Frame(list_border, bg=PKM_BG_INNER)
list_frame.pack(fill="both", expand=True)

# Vertical scrollbar
scrollbar_v = tk.Scrollbar(list_frame, orient="vertical", bg=PKM_GOLD, width=12)
scrollbar_v.pack(side="right", fill="y")

# Horizontal scrollbar
scrollbar_h = tk.Scrollbar(list_frame, orient="horizontal", bg=PKM_GOLD, width=12)
scrollbar_h.pack(side="bottom", fill="x")

history_list = tk.Listbox(
    list_frame,
    bg=PKM_BG_INNER, fg=PKM_WHITE,
    selectbackground=PKM_GOLD, selectforeground=PKM_BG_DARK,
    font=("Segoe UI", 9), relief="flat", bd=0,
    highlightthickness=0, yscrollcommand=scrollbar_v.set,
    xscrollcommand=scrollbar_h.set,
    height=15, activestyle="dotbox"
)
history_list.pack(side="left", fill="both", expand=True)
scrollbar_v.config(command=history_list.yview)
scrollbar_h.config(command=history_list.xview)

# Nút điều khiển danh sách
list_ops_frame = tk.Frame(queue_inner, bg=PKM_BG_CARD)
list_ops_frame.pack(fill="x", pady=(4, 0), padx=0)

tk.Frame(list_ops_frame, bg=PKM_GOLD, height=2).pack(fill="x", pady=(0, 4))

row1 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row1.pack(fill="both", expand=True, pady=1, padx=0)

btn_up = create_btn(row1, "▲  Di Chuyển Lên",
                    move_selected_up, bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE)
btn_up.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

btn_down = create_btn(row1, "▼  Di Chuyển Xuống",
                      move_selected_down, bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE)
btn_down.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

row2 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row2.pack(fill="both", expand=True, pady=1, padx=0)

btn_delete = create_btn(row2, "🗑️  Xóa Mục",
                        delete_selected, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT)
btn_delete.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

btn_clear_all = create_btn(row2, "🗑️  Xóa Tất Cả",
                           clear_all_items, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT)
btn_clear_all.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

row3 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row3.pack(fill="both", expand=True, pady=1, padx=0)

btn_edit_config = create_btn(row3, "⚙️  Chỉnh Sửa Toàn Bộ Thông Số",
                             edit_image_config, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_edit_config.pack(fill="both", expand=True, ipady=5, padx=0)

row4 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row4.pack(fill="both", expand=True, pady=1, padx=0)

btn_edit_scenario = create_btn(row4, "📋 Chỉnh Sửa Kịch Bản",
                               edit_scenario, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_edit_scenario.pack(fill="both", expand=True, ipady=5, padx=0)

row5 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row5.pack(fill="both", expand=True, pady=1, padx=0)

btn_edit_scenario_details = create_btn(row5, "✏️ Edit Chi Tiết Kịch Bản",
                                       edit_scenario_details, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_edit_scenario_details.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 2), ipady=5)

btn_delete_scenario = create_btn(row5, "🗑️ Xóa Kịch Bản",
                                 delete_selected_scenario, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT)
btn_delete_scenario.pack(side=tk.RIGHT, fill="both", expand=True, padx=(2, 0), ipady=5)

# ════════════════════════════════════════════════════════════
#  STATUS BAR — Pokemon Dialogue Box (Responsive)
# ════════════════════════════════════════════════════════════
# Outer border (vàng dày — giả khung hộp thoại Pokemon)
tk.Frame(root, bg=PKM_GOLD, height=2).pack(fill="x", side="bottom")
status_frame = tk.Frame(root, bg=PKM_BG_DARK)
status_frame.pack(fill="x", side="bottom")



# Pokéball icon bên trái status
poke_icon = tk.Canvas(status_frame, width=32, height=32,
                      bg=PKM_BG_DARK, highlightthickness=0)
poke_icon.pack(side="left", padx=(14, 10), pady=9)
poke_icon.create_oval(2, 2, 30, 30, fill=PKM_RED, outline=PKM_WHITE, width=2)
poke_icon.create_line(2, 16, 30, 16, fill=PKM_WHITE, width=2)
poke_icon.create_oval(10, 10, 22, 22, fill=PKM_WHITE, outline=PKM_RED, width=2)

status_var = tk.StringVar(value="❓ Wild AutoClick appeared!  Chờ lệnh Trainer...")
status_label = tk.Label(status_frame, textvariable=status_var,
                        font=("Segoe UI", 8),
                        bg=PKM_BG_DARK, fg=PKM_GRAY, anchor="w", wraplength=400, justify="left")
status_label.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=9)

# PATCH: cập nhật capture key buttons text sang Pokemon theme
_orig_capture_start = capture_start_key
def capture_start_key(event):
    global start_hotkey
    root.unbind("<KeyPress>")
    keysym = event.keysym
    key = translate_key(keysym)
    start_hotkey = key
    register_global_hotkeys()
    btn_hotkey_start.config(text=f"⌨️ Phím Chiến Đấu: {start_hotkey.upper()}")
    set_status(f"✅ Đã đặt phím Chiến Đấu: {start_hotkey.upper()}")

_orig_capture_stop = capture_stop_key
def capture_stop_key(event):
    global stop_hotkey
    root.unbind("<KeyPress>")
    keysym = event.keysym
    key = translate_key(keysym)
    stop_hotkey = key
    register_global_hotkeys()
    btn_hotkey_stop.config(text=f"⌨️ Phím Rút Lui: {stop_hotkey.upper()}")
    set_status(f"✅ Đã đặt phím Rút Lui: {stop_hotkey.upper()}")

def change_start_hotkey():
    btn_hotkey_start.config(text="⏳ Nhấn phím...", bg=PKM_GOLD, fg=PKM_BG_DARK)
    set_status("⌨️ Hãy nhấn một phím để gán làm phím Chiến Đấu (Start)...")
    root.bind("<KeyPress>", capture_start_key)

def change_stop_hotkey():
    btn_hotkey_stop.config(text="⏳ Nhấn phím...", bg=PKM_GOLD, fg=PKM_BG_DARK)
    set_status("⌨️ Hãy nhấn một phím để gán làm phím Rút Lui (Stop)...")
    root.bind("<KeyPress>", capture_stop_key)

btn_hotkey_start.config(command=change_start_hotkey)
btn_hotkey_stop.config(command=change_stop_hotkey)

# ════════════════════════════════════════════════════════════
#  RESPONSIVE LAYOUT HANDLERS - PROFESSIONAL OPTIMIZATION
# ════════════════════════════════════════════════════════════
def on_window_configure(event=None):
    """Handle window resize events for truly responsive layout"""
    try:
        # Update minimum window size
        root.minsize(700, 500)
        
        current_width = root.winfo_width()
        current_height = root.winfo_height()
        
        if current_width > 1 and current_height > 1:
            # Update status label wraplength
            status_label.config(wraplength=max(300, current_width - 100))
            
            # CALCULATE SCALE FACTOR based on window width
            # Reference width is 1000px (default comfortable size)
            scale_factor = current_width / 1000.0
            scale_factor = max(0.7, min(1.3, scale_factor))  # Clamp between 0.7 and 1.3
            
            # PROFESSIONAL RESPONSIVE DESIGN
            # NO padding on panel outer frames - content stretches full width
            # Padding is inside cards only
            left_panel_outer.grid_configure(padx=0, pady=0)
            right_panel_outer.grid_configure(padx=0, pady=0)
            
            # Update Lucario image visibility
            try:
                update_lucario_height()
            except:
                pass
            
            # Adjust all elements based on scale factor
            try:
                _scale_all_elements(root, scale_factor)
            except:
                pass
                
    except:
        pass

def _scale_all_elements(widget, scale_factor):
    """Recursively scale all buttons, labels, and frames"""
    try:
        # Scale buttons
        if isinstance(widget, tk.Button) and hasattr(widget, '_original_padx'):
            # Scale padding
            new_padx = max(3, int(widget._original_padx * scale_factor))
            new_pady = max(2, int(widget._original_pady * scale_factor))
            widget.config(padx=new_padx, pady=new_pady)
            
            # Scale font
            if hasattr(widget, '_base_font_size'):
                new_size = max(7, int(widget._base_font_size * scale_factor))
                widget.config(font=("Segoe UI", new_size, "bold"))
        
        # Scale labels
        elif isinstance(widget, tk.Label):
            try:
                current_font = widget.cget("font")
                if current_font and isinstance(current_font, tuple) and len(current_font) > 1:
                    base_size = int(current_font[1])
                    new_size = max(7, int(base_size * scale_factor))
                    widget.config(font=(current_font[0], new_size) + current_font[2:])
            except:
                pass
        
        # Scale frames padding
        elif isinstance(widget, tk.Frame):
            try:
                # Try to get current padding
                padx = widget.cget("padx")
                pady = widget.cget("pady")
                if padx and pady:
                    new_padx = max(4, int(int(padx) * scale_factor))
                    new_pady = max(4, int(int(pady) * scale_factor))
                    widget.config(padx=new_padx, pady=new_pady)
            except:
                pass
        
        # Recursively scale children
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                _scale_all_elements(child, scale_factor)
    except:
        pass

# Bind window resize event
root.bind("<Configure>", on_window_configure)

# ════════════════════════════════════════════════════════════
#  INIT
# ════════════════════════════════════════════════════════════
root.bind("<Escape>", stop_clicking)
register_global_hotkeys()
update_history()
root.mainloop()

