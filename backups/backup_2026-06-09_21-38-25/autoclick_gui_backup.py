import cv2
import numpy as np
import threading
import time
import json
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
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
click_delay = 1.0   # tốc độ click (giây nghỉ giữa các click)

# Image Detection Option
image_detection_enabled = False
image_templates = []  # danh sách ảnh riêng cho image detection
image_detection_running = False

def imread_unicode(path):
    with open(path, "rb") as stream:
        bytes_array = bytearray(stream.read())
    numpy_array = np.asarray(bytes_array, dtype=np.uint8)
    img = cv2.imdecode(numpy_array, cv2.IMREAD_GRAYSCALE)
    return img

def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def add_image():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("All files","*.*")])
    if file_path:
        img = imread_unicode(file_path)
        if img is None:
            status_label.config(text="⚠️ Không đọc được ảnh.")
            return
        w, h = img.shape[::-1]
        repeat = simpledialog.askinteger("Số lần lặp", "Nhập số lần click cho ảnh này:", minvalue=1, maxvalue=100)
        if repeat is None: return
        delay = simpledialog.askfloat("Delay", "Nhập thời gian delay cho ảnh này (giây):", minvalue=0.1, maxvalue=10.0)
        if delay is None: delay = click_delay
        templates.append({"type":"image","img": img, "w": w, "h": h, "repeat": repeat, "delay": delay, "path": file_path})
        update_history()

def add_coordinate():
    x = simpledialog.askinteger("Tọa độ X", "Nhập X:", minvalue=0)
    if x is None: return
    y = simpledialog.askinteger("Tọa độ Y", "Nhập Y:", minvalue=0)
    if y is None: return
    repeat = simpledialog.askinteger("Số lần lặp", "Nhập số lần click cho tọa độ này:", minvalue=1, maxvalue=100)
    if repeat is None: return
    delay = simpledialog.askfloat("Delay", "Nhập thời gian delay cho tọa độ này (giây):", minvalue=0.1, maxvalue=10.0)
    if delay is None: delay = click_delay
    templates.append({"type":"coord","x": x, "y": y, "repeat": repeat, "delay": delay, "path": f"({x},{y})"})
    update_history()

def add_current_position():
    status_label.config(text="⏳ Di chuột tới vị trí muốn lấy (3 giây)...")
    root.update()
    time.sleep(3)
    x, y = pyautogui.position()
    repeat = simpledialog.askinteger("Số lần lặp", "Nhập số lần click cho tọa độ này:", minvalue=1, maxvalue=100)
    if repeat is None: return
    delay = simpledialog.askfloat("Delay", "Nhập thời gian delay cho tọa độ này (giây):", minvalue=0.1, maxvalue=10.0)
    if delay is None: delay = click_delay
    templates.append({"type":"coord","x": x, "y": y, "repeat": repeat, "delay": delay, "path": f"({x},{y})"})
    update_history()
    status_label.config(text=f"✅ Đã thêm tọa độ ({x},{y}) (lặp {repeat} lần, delay {delay}s)")

def set_process_loops():
    global process_loops
    loops = simpledialog.askinteger("Vòng lặp", "Nhập số vòng lặp cho toàn bộ quá trình:", minvalue=1, maxvalue=100)
    if loops is None: return
    process_loops = loops
    status_label.config(text=f"🔁 Đã đặt {process_loops} vòng lặp cho toàn bộ quá trình.")

def set_speed():
    global click_delay
    delay = simpledialog.askfloat("Tốc độ", "Nhập thời gian nghỉ giữa các click (giây):", minvalue=0.1, maxvalue=5.0)
    if delay is None: return
    click_delay = delay
    status_label.config(text=f"⏩ Đã đặt tốc độ: {click_delay} giây giữa các click")

def toggle_image_detection():
    global image_detection_enabled
    image_detection_enabled = not image_detection_enabled
    if image_detection_enabled:
        detection_btn.config(text="Image Detection (✅ BẬT)", bg="#a6e3a1", activebackground="#94e2d5")
        status_label.config(text="🔍 Image Detection ✅ BẬT")
    else:
        detection_btn.config(text="Image Detection (❌ TẮT)", bg="#f38ba8", activebackground="#eba0ac")
        status_label.config(text="🔍 Image Detection ❌ TẮT")

def add_image_for_detection():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("All files","*.*")])
    if file_path:
        img = imread_unicode(file_path)
        if img is None:
            status_label.config(text="⚠️ Không đọc được ảnh.")
            return
        w, h = img.shape[::-1]
        image_templates.append({"img": img, "w": w, "h": h, "path": file_path})
        update_history()
        status_label.config(text=f"✅ Đã thêm ảnh detection: {file_path}")


def save_scenario():
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
                                             title="Lưu kịch bản AutoClick")
    if not file_path:
        return

    scenario = {
        "process_loops": process_loops,
        "click_delay": click_delay,
        "templates": [],
        "image_templates": []
    }

    for tpl in templates:
        if tpl["type"] == "image":
            scenario["templates"].append({
                "type": "image",
                "path": tpl["path"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", click_delay)
            })
        else:
            scenario["templates"].append({
                "type": "coord",
                "x": tpl["x"],
                "y": tpl["y"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", click_delay)
            })

    for tpl in image_templates:
        scenario["image_templates"].append({
            "path": tpl["path"],
            "w": tpl["w"],
            "h": tpl["h"]
        })

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(scenario, f, ensure_ascii=False, indent=2)
        status_label.config(text=f"💾 Đã lưu kịch bản: {os.path.basename(file_path)}")
    except Exception as e:
        status_label.config(text=f"⚠️ Lưu không thành công: {e}")


def load_scenario():
    global templates, image_templates, process_loops, click_delay

    file_path = filedialog.askopenfilename(filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
                                           title="Mở kịch bản AutoClick")
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            scenario = json.load(f)

        process_loops = scenario.get("process_loops", process_loops)
        click_delay = scenario.get("click_delay", click_delay)

        templates = []
        image_templates = []

        for tpl in scenario.get("templates", []):
            if tpl.get("type") == "image":
                img = imread_unicode(tpl["path"])
                if img is None:
                    raise ValueError(f"Không đọc được ảnh mẫu: {tpl['path']}")
                w, h = img.shape[::-1]
                templates.append({
                    "type": "image",
                    "img": img,
                    "w": w,
                    "h": h,
                    "repeat": tpl.get("repeat", 1),
                    "delay": tpl.get("delay", click_delay),
                    "path": tpl["path"]
                })
            else:
                templates.append({
                    "type": "coord",
                    "x": tpl.get("x", 0),
                    "y": tpl.get("y", 0),
                    "repeat": tpl.get("repeat", 1),
                    "delay": tpl.get("delay", click_delay),
                    "path": f"({tpl.get('x',0)},{tpl.get('y',0)})"
                })

        for tpl in scenario.get("image_templates", []):
            img = imread_unicode(tpl["path"])
            if img is None:
                raise ValueError(f"Không đọc được ảnh detection: {tpl['path']}")
            image_templates.append({
                "img": img,
                "w": tpl.get("w", img.shape[1]),
                "h": tpl.get("h", img.shape[0]),
                "path": tpl["path"]
            })

        update_history()
        status_label.config(text=f"📂 Đã tải kịch bản: {os.path.basename(file_path)}")
    except Exception as e:
        status_label.config(text=f"⚠️ Tải kịch bản thất bại: {e}")


def update_history():
    history_list.delete(0, tk.END)
    # Hiển thị templates thường
    for i, tpl in enumerate(templates):
        if tpl["type"] == "image":
            delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
            history_list.insert(tk.END, f"{i+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}")
        else:
            delay_str = f" [delay {tpl.get('delay', click_delay)}s]"
            history_list.insert(tk.END, f"{i+1}. {tpl['path']} (lặp {tpl['repeat']} lần){delay_str}")
    # Hiển thị detection templates với dấu [DETECTION]
    for i, tpl in enumerate(image_templates):
        history_list.insert(tk.END, f"🔍 [DETECTION] {tpl['path']}")

def delete_selected():
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    selected_text = history_list.get(index)
    
    # Kiểm tra xem có phải detection item không
    if "[DETECTION]" in selected_text:
        # Xóa từ image_templates
        detection_index = index - len(templates)
        if 0 <= detection_index < len(image_templates):
            image_templates.pop(detection_index)
            status_label.config(text="🗑️ Đã xóa ảnh detection khỏi danh sách.")
    else:
        # Xóa từ templates
        templates.pop(index)
        status_label.config(text="🗑️ Đã xóa mục khỏi danh sách.")
    
    update_history()

def edit_delay():
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    selected_text = history_list.get(index)
    
    # Chỉ cho edit delay của templates thường (không phải detection)
    if "[DETECTION]" in selected_text:
        status_label.config(text="⚠️ Không thể edit delay của detection item.")
        return
    
    if 0 <= index < len(templates):
        new_delay = simpledialog.askfloat("Chỉnh sửa Delay", f"Nhập delay mới (hiện tại: {templates[index].get('delay', click_delay)}s):", minvalue=0.1, maxvalue=10.0)
        if new_delay is not None:
            templates[index]["delay"] = new_delay
            update_history()
            status_label.config(text=f"✍️ Đã chỉnh sửa delay thành {new_delay}s")


def move_selected_up():
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    if index == 0: return
    
    selected_text = history_list.get(index)
    prev_text = history_list.get(index - 1)
    
    # Kiểm tra cả hai đều là detection
    if "[DETECTION]" in selected_text and "[DETECTION]" in prev_text:
        detection_index = index - len(templates)
        prev_detection_index = (index - 1) - len(templates)
        if 0 <= detection_index < len(image_templates) and 0 <= prev_detection_index < len(image_templates):
            image_templates[prev_detection_index], image_templates[detection_index] = image_templates[detection_index], image_templates[prev_detection_index]
            status_label.config(text="⬆️ Đã chuyển detection lên trên.")
    # Kiểm tra cả hai đều không phải detection
    elif "[DETECTION]" not in selected_text and "[DETECTION]" not in prev_text:
        templates[index - 1], templates[index] = templates[index], templates[index - 1]
        status_label.config(text="⬆️ Đã chuyển mục lên trên.")
    else:
        status_label.config(text="⚠️ Không thể di chuyển giữa detection và template.")
        return
    
    update_history()
    history_list.selection_set(index - 1)


def move_selected_down():
    selected = history_list.curselection()
    if not selected: return
    index = selected[0]
    total_items = len(templates) + len(image_templates)
    if index == total_items - 1: return
    
    selected_text = history_list.get(index)
    next_text = history_list.get(index + 1)
    
    # Kiểm tra cả hai đều là detection
    if "[DETECTION]" in selected_text and "[DETECTION]" in next_text:
        detection_index = index - len(templates)
        next_detection_index = (index + 1) - len(templates)
        if 0 <= detection_index < len(image_templates) and 0 <= next_detection_index < len(image_templates):
            image_templates[next_detection_index], image_templates[detection_index] = image_templates[detection_index], image_templates[next_detection_index]
            status_label.config(text="⬇️ Đã chuyển detection xuống dưới.")
    # Kiểm tra cả hai đều không phải detection
    elif "[DETECTION]" not in selected_text and "[DETECTION]" not in next_text:
        templates[index + 1], templates[index] = templates[index], templates[index + 1]
        status_label.config(text="⬇️ Đã chuyển mục xuống dưới.")
    else:
        status_label.config(text="⚠️ Không thể di chuyển giữa detection và template.")
        return
    
    update_history()
    history_list.selection_set(index + 1)


def image_detection_loop():
    """Kiểm tra ảnh trên màn hình liên tục (chạy song song với logic cũ)"""
    global image_detection_running
    try:
        while image_detection_running and image_detection_enabled:
            screenshot = capture_screen_gray()
            
            for tpl in image_templates:
                res = cv2.matchTemplate(screenshot, tpl["img"], cv2.TM_CCOEFF_NORMED)
                threshold = 0.8
                loc = np.where(res >= threshold)
                
                points = list(zip(*loc[::-1]))
                # Group close points using a minimum distance equal to template width/2
                filtered_points = filter_close_points(points, min_dist=max(10, tpl["w"]//2))
                
                for pt in filtered_points:
                    click(pt[0] + tpl["w"]//2, pt[1] + tpl["h"]//2)
                    safe_print(f"[DETECTION] Click: {tpl['path']} at: {pt[0]}, {pt[1]}")
                    time.sleep(0.5)  # delay nhỏ sau mỗi click detection
            
            time.sleep(0.3)  # kiểm tra ảnh liên tục
    except Exception as e:
        safe_print(f"[DETECTION THREAD ERROR] {e}")
        if 'status_label' in globals():
            status_label.config(text=f"⚠️ Lỗi detection: {e}")
    finally:
        image_detection_running = False

def find_and_click():
    global running
    try:
        loop_count = 0
        while running and loop_count < process_loops:
            for tpl in templates:
                if tpl["type"] == "image":
                    screenshot = capture_screen_gray()
                    res = cv2.matchTemplate(screenshot, tpl["img"], cv2.TM_CCOEFF_NORMED)
                    threshold = 0.8
                    loc = np.where(res >= threshold)
                    
                    points = list(zip(*loc[::-1]))
                    filtered_points = filter_close_points(points, min_dist=max(10, tpl["w"]//2))
                    
                    count = 0
                    for pt in filtered_points:
                        click(pt[0] + tpl["w"]//2, pt[1] + tpl["h"]//2)
                        safe_print(f"Clicked {tpl['path']} at: {pt[0]}, {pt[1]}")
                        count += 1
                        if count >= tpl["repeat"]:
                            break
                elif tpl["type"] == "coord":
                    for i in range(tpl["repeat"]):
                        click(tpl["x"], tpl["y"])
                        safe_print(f"Clicked coordinate {tpl['path']}")
                        time.sleep(tpl.get("delay", click_delay))
                time.sleep(tpl.get("delay", click_delay))
            loop_count += 1
    except Exception as e:
        safe_print(f"[AUTOCLICK THREAD ERROR] {e}")
        if 'status_label' in globals():
            status_label.config(text=f"⚠️ Lỗi AutoClick: {e}")
    finally:
        ended_by_stop = not running and loop_count < process_loops
        running = False
        if 'status_label' in globals():
            if ended_by_stop:
                status_label.config(text="⏹ AutoClick đã dừng.")
            else:
                status_label.config(text="⏹ AutoClick đã hoàn tất.")

def start_clicking():
    global running, image_detection_running
    
    # Kiểm tra xem có bất kỳ hành động nào trong danh sách tuần tự hoặc danh sách nhận dạng song song không
    has_templates = len(templates) > 0
    has_detection = image_detection_enabled and len(image_templates) > 0
    
    if not has_templates and not has_detection:
        if len(image_templates) > 0 and not image_detection_enabled:
            status_label.config(text="⚠️ Hãy nhấn bật nút 'Image Detection' để quét ảnh!")
        else:
            status_label.config(text="⚠️ Chưa thêm ảnh/tọa độ nào hoặc chưa bật quét ảnh!")
        return
        
    running = True
    set_status("⏺ AutoClick đang chạy...")
    
    if has_templates:
        threading.Thread(target=find_and_click, daemon=True).start()
    
    # Khởi động luồng quét ảnh song song nếu được bật và có ảnh quét
    if has_detection:
        image_detection_running = True
        threading.Thread(target=image_detection_loop, daemon=True).start()

def stop_clicking(event=None):
    global running, image_detection_running
    running = False
    image_detection_running = False
    set_status("⏹ AutoClick đã dừng.")

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

# GUI Root Window
root = tk.Tk()
root.title("⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu")
root.geometry("1000x750")
root.resizable(False, False)
root.configure(bg=PKM_BG_MAIN)

bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pokemon_bg.png")
if not os.path.exists(bg_path):
    pass
else:
    try:
        img = Image.open(bg_path).resize((1000, 750), Image.LANCZOS)
        # Làm tối thêm một chút để chữ dễ đọc trên background
        img = ImageEnhance.Brightness(img).enhance(0.45)
        # Thêm blur nhẹ tạo hiệu ứng depth
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        _bg_photo = ImageTk.PhotoImage(img)
        bg_canvas = tk.Canvas(root, width=1000, height=750,
                              highlightthickness=0, bd=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        bg_canvas.create_image(0, 0, anchor="nw", image=_bg_photo)
        bg_canvas.lower()  # Đẩy xuống dưới tất cả widget
    except Exception as e:
        pass  # Nếu load thất bại thì bỏ qua, dùng màu nền thường

# ─── Helper: tạo nút theo phong cách Pokemon battle menu ────────────────
def create_btn(parent, text, command, bg=PKM_RED, fg=PKM_WHITE,
               hover_bg=None, font=("Segoe UI", 9, "bold"), **kwargs):
    _hover = hover_bg or bg
    btn = tk.Button(
        parent, text=text, command=command, font=font,
        bg=bg, fg=fg, activebackground=_hover, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2", padx=8, pady=4,
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
    return btn

# ─── Helper: tạo Card kiểu Pokédex ──────────────────────────────────────
def create_card(parent, title, title_color=PKM_YELLOW):
    # Outer border frame (giả lập viền Pokédex)
    border = tk.Frame(parent, bg=title_color, bd=0)
    border.pack(fill="x", pady=(0, 12), padx=0)

    # Pokéball accent dot + title bar
    title_bar = tk.Frame(border, bg=PKM_BG_CARD, pady=8, padx=12)
    title_bar.pack(fill="x", side="top")

    dot_canvas = tk.Canvas(title_bar, width=16, height=16,
                           bg=PKM_BG_CARD, highlightthickness=0)
    dot_canvas.pack(side="left", padx=(0, 8))
    dot_canvas.create_oval(1, 1, 15, 15, fill=title_color, outline=PKM_WHITE, width=2)
    dot_canvas.create_line(1, 8, 15, 8, fill=PKM_WHITE, width=2)

    tk.Label(title_bar, text=title, font=("Segoe UI", 10, "bold"),
             bg=PKM_BG_CARD, fg=title_color).pack(side="left")

    # Divider line giả viền ngang Pokédex
    tk.Frame(border, bg=title_color, height=3).pack(fill="x")

    # Card inner content area
    inner = tk.Frame(border, bg=PKM_BG_CARD, padx=12, pady=10)
    inner.pack(fill="both", expand=True)
    return inner

# ════════════════════════════════════════════════════════════
#  HEADER — Pokédex Style Banner
# ════════════════════════════════════════════════════════════
header_frame = tk.Frame(root, bg=PKM_RED, height=85)
header_frame.pack(fill="x", side="top")
header_frame.pack_propagate(False)

# Left side decoration: Pokéball design
left_deco = tk.Canvas(header_frame, width=100, height=85,
                      bg=PKM_RED, highlightthickness=0)
left_deco.pack(side="left")
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
title_frame.pack(side="left", padx=15)
tk.Label(title_frame, text="⚡ POKÉCLICK PRO",
         font=("Segoe UI", 18, "bold"), bg=PKM_RED, fg=PKM_YELLOW).pack(anchor="w")
tk.Label(title_frame, text="Hệ thống Tự Động Chiến Đấu · Image Recognition · Win32",
         font=("Segoe UI", 9), bg=PKM_RED, fg=PKM_WHITE).pack(anchor="w")

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
#  BODY LAYOUT
# ════════════════════════════════════════════════════════════
body_frame = tk.Frame(root, bg=PKM_BG_MAIN)
body_frame.pack(fill="both", expand=True, padx=16, pady=12)

left_panel = tk.Frame(body_frame, bg=PKM_BG_MAIN)
left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

right_panel = tk.Frame(body_frame, bg=PKM_BG_MAIN)
right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

# ════════════════════════════════════════════════════════════
#  LEFT PANEL — Controls
# ════════════════════════════════════════════════════════════

# ── SECTION 1: Kỹ năng tuần tự ──────────────────────────────
act_inner = create_card(left_panel, "⚔️  KỸ NĂNG CHIẾN ĐẤU (Tuần tự)", PKM_YELLOW)

btn_add_img = create_btn(act_inner, "🖼️  Thêm Pokémon mục tiêu (Ảnh)",
                         add_image, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT)
btn_add_img.pack(fill="x", pady=3, ipady=3)

btn_add_coord = create_btn(act_inner, "📍  Thêm tọa độ chiến trường (XY)",
                           add_coordinate, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT)
btn_add_coord.pack(fill="x", pady=3, ipady=3)

btn_add_pos = create_btn(act_inner, "🎯  Ghi nhớ vị trí chuột hiện tại  [⏳ 3s]",
                         add_current_position, bg="#1a6b2a", fg=PKM_YELLOW, hover_bg=PKM_GREEN)
btn_add_pos.pack(fill="x", pady=3, ipady=3)

# ── SECTION 2: Túi đồ Trainer ────────────────────────────────
settings_inner = create_card(left_panel, "🎒  TÚI ĐỒ TRAINER (Cấu hình)", PKM_GOLD)

settings_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
settings_row.pack(fill="x", pady=3)

btn_loop = create_btn(settings_row, "🔄 Số trận đấu",
                      set_process_loops, bg="#7a5c00", fg=PKM_YELLOW, hover_bg=PKM_YELLOW_DK)
btn_loop.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=3)

btn_speed = create_btn(settings_row, "⚡ Tốc độ tấn công",
                       set_speed, bg="#7a5c00", fg=PKM_YELLOW, hover_bg=PKM_YELLOW_DK)
btn_speed.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=3)

hotkey_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
hotkey_row.pack(fill="x", pady=(8, 3))

btn_hotkey_start = create_btn(hotkey_row, f"⌨️ Phím Chiến Đấu: {start_hotkey.upper()}",
                              change_start_hotkey,
                              bg="#1e1e3a", fg=PKM_WHITE, hover_bg="#2d2d50")
btn_hotkey_start.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=3)

btn_hotkey_stop = create_btn(hotkey_row, f"⌨️ Phím Rút Lui: {stop_hotkey.upper()}",
                             change_stop_hotkey,
                             bg="#1e1e3a", fg=PKM_WHITE, hover_bg="#2d2d50")
btn_hotkey_stop.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=3)

scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
scenario_row.pack(fill="x", pady=(3, 0))

btn_save_scenario = create_btn(scenario_row, "💾 Lưu dữ liệu Trainer",
                               save_scenario, bg="#7a5c00", fg=PKM_YELLOW, hover_bg=PKM_YELLOW_DK)
btn_save_scenario.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=3)

btn_load_scenario = create_btn(scenario_row, "📂 Tải dữ liệu Trainer",
                               load_scenario, bg="#7a5c00", fg=PKM_YELLOW, hover_bg=PKM_YELLOW_DK)
btn_load_scenario.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=3)

# ── SECTION 3: PokéRadar ─────────────────────────────────────
detect_inner = create_card(left_panel, "🔍  POKÉRADAR (Nhận dạng song song)", "#b07eff")

btn_detect_img = create_btn(detect_inner, "📸 Thêm Pokémon cần Radar",
                            add_image_for_detection, bg="#4a1a7a", fg="#d4aaff", hover_bg="#6b2aaa")
btn_detect_img.pack(fill="x", pady=3, ipady=3)

detection_btn = create_btn(detect_inner, "POKÉRADAR  ❌  TẮT",
                           toggle_image_detection, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT)
detection_btn.pack(fill="x", pady=3, ipady=3)

# ── SECTION 4: Chiến đấu! ───────────────────────────────────
exec_inner = create_card(left_panel, "⚡  CHIẾN ĐẤU!", PKM_GREEN)

exec_row = tk.Frame(exec_inner, bg=PKM_BG_CARD)
exec_row.pack(fill="x", pady=4)

btn_start = create_btn(exec_row, "  ⚡  TUNG POKÉBALL!  ",
                       start_clicking, bg=PKM_GREEN, fg="#002200",
                       hover_bg=PKM_GREEN_LT, font=("Consolas", 11, "bold"))
btn_start.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=6)

btn_stop = create_btn(exec_row, "  🏃  RÚT LUI!  ",
                      stop_clicking, bg=PKM_RED, fg=PKM_WHITE,
                      hover_bg=PKM_RED_LIGHT, font=("Consolas", 11, "bold"))
btn_stop.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=6)

status_top_var = tk.StringVar(value="❓ Wild AutoClick appeared!  Chờ lệnh Trainer...")
status_top_display = tk.Label(exec_inner, textvariable=status_top_var,
                              font=("Consolas", 8, "bold"), bg=PKM_BG_CARD,
                              fg=PKM_WHITE, wraplength=320, justify="left", pady=4)
status_top_display.pack(fill="x", pady=(8, 0))

# ════════════════════════════════════════════════════════════
#  RIGHT PANEL — Pokédex Danh Sách
# ════════════════════════════════════════════════════════════
queue_inner = create_card(right_panel, "📜  POKÉDEX KỊCH BẢN", PKM_YELLOW)

# Listbox container với viền đỏ giả màn hình Pokédex
list_border = tk.Frame(queue_inner, bg=PKM_RED, padx=2, pady=2)
list_border.pack(fill="both", expand=True, pady=4)

list_frame = tk.Frame(list_border, bg=PKM_BG_INNER)
list_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                         troughcolor=PKM_BG_INNER, bg=PKM_RED, width=10)
scrollbar.pack(side="right", fill="y")

history_list = tk.Listbox(
    list_frame,
    bg=PKM_BG_INNER, fg=PKM_WHITE,
    selectbackground=PKM_RED, selectforeground=PKM_YELLOW,
    font=("Consolas", 9), relief="flat", bd=0,
    highlightthickness=0, yscrollcommand=scrollbar.set,
    height=17, activestyle="dotbox"
)
history_list.pack(side="left", fill="both", expand=True)
scrollbar.config(command=history_list.yview)

# Nút điều khiển danh sách
list_ops_frame = tk.Frame(queue_inner, bg=PKM_BG_CARD)
list_ops_frame.pack(fill="x", pady=(8, 0))

tk.Frame(list_ops_frame, bg=PKM_YELLOW, height=1).pack(fill="x", pady=(0, 6))

row1 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row1.pack(fill="x", pady=2)

btn_up = create_btn(row1, "▲  Di Chuyển Lên",
                    move_selected_up, bg="#1e1e3a", fg=PKM_WHITE, hover_bg="#2d2d50")
btn_up.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=3)

btn_down = create_btn(row1, "▼  Di Chuyển Xuống",
                      move_selected_down, bg="#1e1e3a", fg=PKM_WHITE, hover_bg="#2d2d50")
btn_down.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=3)

row2 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row2.pack(fill="x", pady=2)

btn_edit = create_btn(row2, "✏️  Chỉnh Sửa Delay",
                      edit_delay, bg="#7a5c00", fg=PKM_YELLOW, hover_bg=PKM_YELLOW_DK)
btn_edit.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=3)

btn_delete = create_btn(row2, "🗑️  Xóa Mục",
                        delete_selected, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT)
btn_delete.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=3)

# ════════════════════════════════════════════════════════════
#  STATUS BAR — Pokemon Dialogue Box
# ════════════════════════════════════════════════════════════
# Outer border (trắng dày — giả khung hộp thoại Pokemon)
tk.Frame(root, bg=PKM_WHITE, height=3).pack(fill="x", side="bottom")
status_frame = tk.Frame(root, bg=PKM_BG_DARK, height=45)
status_frame.pack(fill="x", side="bottom")
status_frame.pack_propagate(False)
tk.Frame(root, bg=PKM_RED, height=3).pack(fill="x", side="bottom")

# Pokéball icon bên trái status
poke_icon = tk.Canvas(status_frame, width=30, height=30,
                      bg=PKM_BG_DARK, highlightthickness=0)
poke_icon.pack(side="left", padx=(12, 6), pady=8)
poke_icon.create_oval(2, 2, 28, 28, fill=PKM_RED, outline=PKM_WHITE, width=2)
poke_icon.create_line(2, 15, 28, 15, fill=PKM_WHITE, width=2)
poke_icon.create_oval(10, 10, 20, 20, fill=PKM_WHITE, outline=PKM_RED, width=2)

status_var = tk.StringVar(value="❓ Wild AutoClick appeared!  Chờ lệnh Trainer...")
status_label = tk.Label(status_frame, textvariable=status_var,
                        font=("Consolas", 9, "bold"),
                        bg=PKM_BG_DARK, fg=PKM_WHITE, anchor="w")
status_label.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=8)

# ════════════════════════════════════════════════════════════
#  PATCH: cập nhật lại hàm toggle_image_detection để dùng text Pokemon
# ════════════════════════════════════════════════════════════
_orig_toggle = toggle_image_detection
def toggle_image_detection():
    global image_detection_enabled
    image_detection_enabled = not image_detection_enabled
    if image_detection_enabled:
        detection_btn.config(text="POKÉRADAR  ✅  BẬT",
                             bg=PKM_GREEN, fg="#002200",
                             activebackground=PKM_GREEN_LT)
        set_status("🔍 PokéRadar ✅ BẬT — Đang quét màn hình...")
    else:
        detection_btn.config(text="POKÉRADAR  ❌  TẮT",
                             bg=PKM_RED, fg=PKM_WHITE,
                             activebackground=PKM_RED_LIGHT)
        set_status("🔍 PokéRadar ❌ TẮT")

detection_btn.config(command=toggle_image_detection)

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
    btn_hotkey_start.config(text="⏳ Nhấn phím...", bg="#cc6600", fg=PKM_WHITE)
    set_status("⌨️ Hãy nhấn một phím để gán làm phím Chiến Đấu (Start)...")
    root.bind("<KeyPress>", capture_start_key)

def change_stop_hotkey():
    btn_hotkey_stop.config(text="⏳ Nhấn phím...", bg="#cc6600", fg=PKM_WHITE)
    set_status("⌨️ Hãy nhấn một phím để gán làm phím Rút Lui (Stop)...")
    root.bind("<KeyPress>", capture_stop_key)

btn_hotkey_start.config(command=change_start_hotkey)
btn_hotkey_stop.config(command=change_stop_hotkey)

# ════════════════════════════════════════════════════════════
#  INIT
# ════════════════════════════════════════════════════════════
root.bind("<Escape>", stop_clicking)
register_global_hotkeys()
update_history()
root.mainloop()

