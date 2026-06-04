import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import os
import sys
import tkinter as tk

# Ensure project root is on sys.path so submodules resolve
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from core import state
from core.state import set_status
from core.runner import start_clicking, stop_clicking, smart_start
from scenario.io import save_scenario, load_scenario, load_multiple_scenarios, clear_scenarios
from scenario.templates import (
    add_image, add_coordinate, add_current_position, add_keyboard_key,
    set_search_region, clear_search_region, set_process_loops, set_speed, toggle_human_click, toggle_precision_mode,
    test_image_matching, update_history,
    delete_selected, clear_all_items, edit_delay, edit_image_config,
    move_selected_up, move_selected_down,
)
from scenario.details_editor import edit_scenario_details
from ui.theme import *
from ui.widgets import create_btn, create_card
from ui.library_panel import create_library_panel
from ui.hotkeys import (
    register_global_hotkeys, change_start_hotkey, change_stop_hotkey,
    capture_start_key, capture_stop_key,
)
from ui.layout import on_window_configure
from utils import safe_print

# ════════════════════════════════════════════════════════════
#  ROOT WINDOW
# ════════════════════════════════════════════════════════════
root = tk.Tk()
root.title("⚡ PokéClick PRO — Hệ thống Tự Động Chiến Đấu")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = max(800, min(1400, int(screen_width * 0.7)))
window_height = max(600, min(1000, int(screen_height * 0.75)))
root.geometry(f"{window_width}x{window_height}")
root.resizable(True, True)
root.configure(bg=PKM_BG_MAIN)
root.base_width = window_width
root.base_height = window_height

# Register root in state
state.UI.root = root

# Background image
bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pokemon_bg.png")
if os.path.exists(bg_path) and PIL_AVAILABLE:
    try:
        img = Image.open(bg_path).resize((window_width, window_height), Image.LANCZOS)
        img = ImageEnhance.Brightness(img).enhance(0.45)
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        _bg_photo = ImageTk.PhotoImage(img)
        bg_canvas = tk.Canvas(root, width=window_width, height=window_height,
                              highlightthickness=0, bd=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        bg_canvas.create_image(0, 0, anchor="nw", image=_bg_photo)
        bg_canvas.lower()

        def on_window_resize(event=None):
            try:
                if hasattr(root, '_resize_timer'):
                    root.after_cancel(root._resize_timer)
                root._resize_timer = root.after(500, _update_bg)
            except:
                pass

        def _update_bg():
            try:
                nw = root.winfo_width()
                nh = root.winfo_height()
                if nw > 1 and nh > 1:
                    img_r = Image.open(bg_path).resize((nw, nh), Image.LANCZOS)
                    img_r = ImageEnhance.Brightness(img_r).enhance(0.45)
                    img_r = img_r.filter(ImageFilter.GaussianBlur(radius=2))
                    new_photo = ImageTk.PhotoImage(img_r)
                    bg_canvas.create_image(0, 0, anchor="nw", image=new_photo)
                    bg_canvas.image = new_photo
            except:
                pass

        root.bind("<Configure>", on_window_resize)
    except:
        pass

# ════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════
header_frame = tk.Frame(root, bg=PKM_RED)
header_frame.pack(fill="x", side="top")

left_deco = tk.Canvas(header_frame, width=100, height=85, bg=PKM_RED, highlightthickness=0)
left_deco.pack(side="left", padx=5)
left_deco.create_oval(15, 15, 75, 75, fill=PKM_RED, outline=PKM_WHITE, width=3)
left_deco.create_line(15, 45, 75, 45, fill=PKM_WHITE, width=3)
left_deco.create_oval(25, 25, 65, 45, fill=PKM_BLUE, outline="", width=0)
left_deco.create_oval(25, 45, 65, 65, fill=PKM_WHITE, outline="", width=0)
left_deco.create_oval(40, 40, 50, 50, fill=PKM_BG_DARK, outline=PKM_WHITE, width=2)

title_frame = tk.Frame(header_frame, bg=PKM_RED)
title_frame.pack(side="left", padx=15, fill="both", expand=True)
tk.Label(title_frame, text="⚡ POKÉCLICK PRO",
         font=("Segoe UI", 16, "bold"), bg=PKM_RED, fg=PKM_YELLOW).pack(anchor="w")
tk.Label(title_frame, text="Hệ thống Tự Động Chiến Đấu · Image Recognition · Win32",
         font=("Segoe UI", 8), bg=PKM_RED, fg=PKM_WHITE).pack(anchor="w")

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

tk.Frame(root, bg=PKM_GOLD, height=2).pack(fill="x")

# ════════════════════════════════════════════════════════════
#  BODY LAYOUT
# ════════════════════════════════════════════════════════════
body_frame = tk.Frame(root, bg=PKM_BG_MAIN)
body_frame.pack(fill="both", expand=True, padx=0, pady=0)
body_frame.grid_rowconfigure(0, weight=1)
body_frame.grid_columnconfigure(0, weight=1)
body_frame.grid_columnconfigure(1, weight=0)
body_frame.grid_columnconfigure(2, weight=1)

# LEFT PANEL
left_panel_outer = tk.Frame(body_frame, bg=PKM_BG_MAIN)
left_panel_outer.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

left_canvas = tk.Canvas(left_panel_outer, bg=PKM_BG_MAIN, highlightthickness=0)
left_scrollbar = tk.Scrollbar(left_panel_outer, orient="vertical", command=left_canvas.yview)
left_panel = tk.Frame(left_canvas, bg=PKM_BG_MAIN)
left_panel.bind("<Configure>",
                lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
left_canvas.configure(yscrollcommand=left_scrollbar.set)
left_canvas_window = left_canvas.create_window((0, 0), window=left_panel, anchor="nw")

def _on_left_canvas_configure(event):
    cw = event.width
    left_panel.update_idletasks()
    pw = left_panel.winfo_reqwidth()
    left_canvas.itemconfig(left_canvas_window, width=max(cw, pw))

left_canvas.pack(side="left", fill="both", expand=True)
left_scrollbar.pack(side="right", fill="y")
left_canvas.bind("<Configure>", _on_left_canvas_configure)

# SEPARATOR
tk.Frame(body_frame, bg=PKM_GOLD, width=2).grid(row=0, column=1, sticky="ns")

# RIGHT PANEL
right_panel_outer = tk.Frame(body_frame, bg=PKM_BG_MAIN)
right_panel_outer.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)

right_canvas = tk.Canvas(right_panel_outer, bg=PKM_BG_MAIN, highlightthickness=0)
right_scrollbar = tk.Scrollbar(right_panel_outer, orient="vertical", command=right_canvas.yview)
right_panel = tk.Frame(right_canvas, bg=PKM_BG_MAIN)
right_panel.bind("<Configure>",
                 lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
right_canvas.configure(yscrollcommand=right_scrollbar.set)
right_canvas_window = right_canvas.create_window((0, 0), window=right_panel, anchor="nw")

def _on_right_canvas_configure(event):
    cw = event.width
    right_panel.update_idletasks()
    pw = right_panel.winfo_reqwidth()
    right_canvas.itemconfig(right_canvas_window, width=max(cw, pw))

right_canvas.pack(side="left", fill="both", expand=True)
right_scrollbar.pack(side="right", fill="y")
right_canvas.bind("<Configure>", _on_right_canvas_configure)

# Mousewheel
def _on_mousewheel(event):
    try:
        try:
            if left_canvas.winfo_containing(event.x_root, event.y_root):
                left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return
        except:
            pass
        try:
            if right_canvas.winfo_containing(event.x_root, event.y_root):
                right_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return
        except:
            pass
    except:
        pass

left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ════════════════════════════════════════════════════════════
#  LEFT PANEL — Controls
# ════════════════════════════════════════════════════════════

# SECTION 1: Skills
act_inner = create_card(left_panel, "⚔️  KỸ NĂNG CHIẾN ĐẤU (Tuần tự)", PKM_GOLD)

create_btn(act_inner, "🖼️  Thêm Pokémon mục tiêu (Ảnh)",
           add_image, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT
           ).pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

create_btn(act_inner, "📍  Thêm tọa độ chiến trường (XY)",
           add_coordinate, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT
           ).pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

create_btn(act_inner, "🎯  Ghi nhớ vị trí chuột hiện tại  [⏳ 3s]",
           add_current_position, bg=PKM_GREEN, fg=PKM_BG_DARK, hover_bg=PKM_GREEN_LT
           ).pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

create_btn(act_inner, "⌨️  Thêm phím bàn phím",
           add_keyboard_key, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT
           ).pack(fill="both", expand=True, pady=2, ipady=5, padx=0)

# SECTION 2: Trainer bag
create_library_panel(left_panel)

settings_inner = create_card(left_panel, "🎒  TÚI ĐỒ TRAINER (Cấu hình)", PKM_GOLD)

settings_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
settings_row.pack(fill="both", expand=True, pady=2, padx=0)

create_btn(settings_row, "🔄 Số trận đấu",
           set_process_loops, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

create_btn(settings_row, "⚡ Tốc độ tấn công",
           set_speed, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

human_mode_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
human_mode_row.pack(fill="both", expand=True, pady=(4, 2), padx=0)

btn_human_mode = create_btn(human_mode_row, "🤖 Click tức thì: BẬT",
                            toggle_human_click, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE)
btn_human_mode.pack(fill="both", expand=True, ipady=5)
state.UI.btn_human_mode = btn_human_mode

precision_mode_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
precision_mode_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

btn_precision_mode = create_btn(
    precision_mode_row,
    "🎯 Precision Mode: BẬT",
    toggle_precision_mode,
    bg=PKM_BLUE_DARK,
    fg=PKM_YELLOW,
    hover_bg=PKM_BLUE,
)
btn_precision_mode.pack(fill="both", expand=True, ipady=5)
state.UI.btn_precision_mode = btn_precision_mode

hotkey_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
hotkey_row.pack(fill="both", expand=True, pady=(4, 2), padx=0)

btn_hotkey_start = create_btn(hotkey_row, f"⌨️ Phím Chiến Đấu: {state.start_hotkey.upper()}",
                              change_start_hotkey, bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE)
btn_hotkey_start.pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)
state.UI.btn_hotkey_start = btn_hotkey_start

btn_hotkey_stop = create_btn(hotkey_row, f"⌨️ Phím Rút Lui: {state.stop_hotkey.upper()}",
                             change_stop_hotkey, bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE)
btn_hotkey_stop.pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)
state.UI.btn_hotkey_stop = btn_hotkey_stop

scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
scenario_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

create_btn(scenario_row, "💾 Lưu dữ liệu Trainer",
           save_scenario, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)

create_btn(scenario_row, "📂 Tải dữ liệu Trainer",
           load_scenario, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

multi_scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
multi_scenario_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

create_btn(multi_scenario_row, "📚 Tải nhiều kịch bản",
           load_multiple_scenarios, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(fill="both", expand=True, ipady=5, padx=0)

clear_scenario_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
clear_scenario_row.pack(fill="both", expand=True, pady=(0, 2), padx=0)

create_btn(clear_scenario_row, "🗑️ Xóa tất cả kịch bản",
           clear_scenarios, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT
           ).pack(fill="both", expand=True, ipady=5, padx=0)

search_region_row = tk.Frame(settings_inner, bg=PKM_BG_CARD)
search_region_row.pack(fill="both", expand=True, pady=(4, 0), padx=0)

create_btn(search_region_row, "🔎 Giới hạn phạm vi tìm kiếm",
           set_search_region, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(fill="both", expand=True, ipady=5, padx=0)

create_btn(search_region_row, "Clear Search Region",
           clear_search_region, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT
           ).pack(fill="both", expand=True, ipady=5, padx=0, pady=(4, 0))

# SECTION 3: Battle
exec_inner = create_card(left_panel, "⚡  CHIẾN ĐẤU!", PKM_GREEN)

exec_row = tk.Frame(exec_inner, bg=PKM_BG_CARD)
exec_row.pack(fill="both", expand=True, pady=4, padx=0)

create_btn(exec_row, "  ⚡  TUNG POKÉBALL!  ",
           smart_start, bg=PKM_GREEN, fg=PKM_BG_DARK,
           hover_bg=PKM_GREEN_LT, font=("Segoe UI", 11, "bold")
           ).pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=7)

create_btn(exec_row, "  🏃  RÚT LUI!  ",
           stop_clicking, bg=PKM_RED, fg=PKM_WHITE,
           hover_bg=PKM_RED_LIGHT, font=("Segoe UI", 11, "bold")
           ).pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=7)

status_top_var = tk.StringVar(value="❓ Wild AutoClick appeared!  Chờ lệnh Trainer...")
state.UI.status_top_var = status_top_var
tk.Label(exec_inner, textvariable=status_top_var,
         font=("Segoe UI", 8), bg=PKM_BG_CARD,
         fg=PKM_GRAY, wraplength=320, justify="left", pady=4
         ).pack(fill="x", pady=(6, 0), padx=0)
tk.Frame(exec_inner, bg=PKM_GREEN, height=1).pack(fill="x", pady=(6, 0))

# ════════════════════════════════════════════════════════════
#  RIGHT PANEL — Pokédex
# ════════════════════════════════════════════════════════════
queue_inner = create_card(right_panel, "📜  POKÉDEX KỊCH BẢN", PKM_YELLOW)

# Lucario decoration
lucario_bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "HD-wallpaper-lucario-pokemon-thumbnail.jpg")
lucario_container = tk.Frame(queue_inner, bg=PKM_BG_CARD)
lucario_container.pack(fill="x", pady=(0, 8))
lucario_container.pack_propagate(False)

if os.path.exists(lucario_bg_path) and PIL_AVAILABLE:
    try:
        lucario_img = Image.open(lucario_bg_path).resize((380, 120), Image.LANCZOS)
        lucario_img = ImageEnhance.Brightness(lucario_img).enhance(0.7)
        _lucario_photo = ImageTk.PhotoImage(lucario_img)
        lucario_canvas = tk.Canvas(lucario_container, width=380, height=120,
                                   bg=PKM_BG_CARD, highlightthickness=0)
        lucario_canvas.pack(fill="both", expand=True)
        lucario_canvas.create_image(0, 0, anchor="nw", image=_lucario_photo)
        overlay = tk.Label(lucario_container, text="Lucario Ready for Battle! ⚡",
                           font=("Segoe UI", 12, "bold"), bg=PKM_BG_CARD, fg=PKM_YELLOW)
        overlay.place(x=10, y=50, anchor="w")
    except:
        lucario_canvas = tk.Canvas(lucario_container, width=380, height=120,
                                   bg=PKM_BG_CARD, highlightthickness=0)
        lucario_canvas.pack(fill="both", expand=True)
        lucario_canvas.create_text(190, 60, text="Lucario Ready for Battle!",
                                   font=("Segoe UI", 14, "bold"), fill=PKM_YELLOW)
else:
    lucario_canvas = tk.Canvas(lucario_container, width=380, height=120,
                               bg=PKM_BG_CARD, highlightthickness=0)
    lucario_canvas.pack(fill="both", expand=True)
    lucario_canvas.create_text(190, 60, text="Lucario Ready for Battle!",
                               font=("Segoe UI", 14, "bold"), fill=PKM_YELLOW)

# Setup info
setup_info_frame = tk.Frame(queue_inner, bg=PKM_BG_CARD, relief="flat", bd=0)
setup_info_frame.pack(fill="x", pady=(4, 4), padx=0)

setup_info_text = tk.StringVar(value="🔄 Vòng lặp: 1  |  ⚡ Tốc độ: 1.0s")
state.UI.setup_info_text = setup_info_text
tk.Label(setup_info_frame, textvariable=setup_info_text,
         font=("Segoe UI", 8), bg=PKM_BG_CARD, fg=PKM_YELLOW,
         anchor="center", justify="center", wraplength=360).pack(fill="x", padx=4, pady=2)

# History listbox
list_border = tk.Frame(queue_inner, bg=PKM_GOLD, padx=2, pady=2)
list_border.pack(fill="both", expand=True, pady=2)

list_frame = tk.Frame(list_border, bg=PKM_BG_INNER)
list_frame.pack(fill="both", expand=True)

scrollbar_v = tk.Scrollbar(list_frame, orient="vertical", bg=PKM_GOLD, width=12)
scrollbar_v.pack(side="right", fill="y")
scrollbar_h = tk.Scrollbar(list_frame, orient="horizontal", bg=PKM_GOLD, width=12)
scrollbar_h.pack(side="bottom", fill="x")

history_list = tk.Listbox(
    list_frame, bg=PKM_BG_INNER, fg=PKM_WHITE,
    selectbackground=PKM_GOLD, selectforeground=PKM_BG_DARK,
    font=("Segoe UI", 9), relief="flat", bd=0,
    highlightthickness=0, yscrollcommand=scrollbar_v.set,
    xscrollcommand=scrollbar_h.set, height=15, activestyle="dotbox"
)
history_list.pack(side="left", fill="both", expand=True)
scrollbar_v.config(command=history_list.yview)
scrollbar_h.config(command=history_list.xview)
state.UI.history_list = history_list

# List controls
list_ops_frame = tk.Frame(queue_inner, bg=PKM_BG_CARD)
list_ops_frame.pack(fill="x", pady=(4, 0), padx=0)
tk.Frame(list_ops_frame, bg=PKM_GOLD, height=2).pack(fill="x", pady=(0, 4))

row1 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row1.pack(fill="both", expand=True, pady=1, padx=0)
create_btn(row1, "▲  Lên", move_selected_up,
           bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE
           ).pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)
create_btn(row1, "▼  Xuống", move_selected_down,
           bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE
           ).pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

row2 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row2.pack(fill="both", expand=True, pady=1, padx=0)
create_btn(row2, "✏️  Sửa", edit_image_config,
           bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)
create_btn(row2, "🗑️  Xóa", delete_selected,
           bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT
           ).pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

row3 = tk.Frame(list_ops_frame, bg=PKM_BG_CARD)
row3.pack(fill="both", expand=True, pady=1, padx=0)
create_btn(row3, "📋  Quản Lý Kịch Bản", edit_scenario_details,
           bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE
           ).pack(side="left", fill="both", expand=True, padx=(0, 2), ipady=5)
create_btn(row3, "🗑️  Xóa Sạch", clear_all_items,
           bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT
           ).pack(side="right", fill="both", expand=True, padx=(2, 0), ipady=5)

# ════════════════════════════════════════════════════════════
#  STATUS BAR
# ════════════════════════════════════════════════════════════
tk.Frame(root, bg=PKM_GOLD, height=2).pack(fill="x", side="bottom")
status_frame = tk.Frame(root, bg=PKM_BG_DARK)
status_frame.pack(fill="x", side="bottom")

poke_icon = tk.Canvas(status_frame, width=32, height=32, bg=PKM_BG_DARK, highlightthickness=0)
poke_icon.pack(side="left", padx=(14, 10), pady=9)
poke_icon.create_oval(2, 2, 30, 30, fill=PKM_RED, outline=PKM_WHITE, width=2)
poke_icon.create_line(2, 16, 30, 16, fill=PKM_WHITE, width=2)
poke_icon.create_oval(10, 10, 22, 22, fill=PKM_WHITE, outline=PKM_RED, width=2)

status_var = tk.StringVar(value="❓ Wild AutoClick appeared!  Chờ lệnh Trainer...")
state.UI.status_var = status_var
status_label = tk.Label(status_frame, textvariable=status_var,
                        font=("Segoe UI", 8), bg=PKM_BG_DARK, fg=PKM_GRAY,
                        anchor="w", wraplength=400, justify="left")
status_label.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=9)
state.UI.status_label = status_label

# ════════════════════════════════════════════════════════════
#  RESPONSIVE + INIT
# ════════════════════════════════════════════════════════════
root.bind("<Configure>", on_window_configure)
root.bind("<Escape>", stop_clicking)
register_global_hotkeys()
update_history()
root.mainloop()
