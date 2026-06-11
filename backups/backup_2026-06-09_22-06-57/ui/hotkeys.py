import keyboard
from core import state
from core.state import set_status
from utils import safe_print

TK_TO_KEYBOARD = {
    "Escape": "esc", "space": "space", "Return": "enter",
    "BackSpace": "backspace", "Tab": "tab", "Caps_Lock": "caps lock",
    "Control_L": "ctrl", "Control_R": "ctrl",
    "Alt_L": "alt", "Alt_R": "alt",
    "Shift_L": "shift", "Shift_R": "shift",
    "period": ".", "comma": ",", "slash": "/", "backslash": "\\",
    "minus": "-", "equal": "=", "semicolon": ";", "apostrophe": "'",
    "bracketleft": "[", "bracketright": "]",
    "Up": "up", "Down": "down", "Left": "left", "Right": "right",
    "Prior": "page up", "Next": "page down",
    "End": "end", "Home": "home", "Insert": "insert", "Delete": "delete",
    "Num_Lock": "num lock", "Scroll_Lock": "scroll lock", "Pause": "pause",
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
    from core.runner import smart_start as start_clicking, stop_clicking
    try:
        keyboard.unhook_all()
    except Exception:
        pass
    try:
        if state.start_hotkey:
            keyboard.add_hotkey(state.start_hotkey, start_clicking)
    except Exception:
        if state.UI.status_label is not None:
            state.UI.status_label.config(text=f"⚠️ Phím Start '{state.start_hotkey.upper()}' không hợp lệ hoặc bị trùng!")
        state.start_hotkey = ""
    try:
        if state.stop_hotkey:
            keyboard.add_hotkey(state.stop_hotkey, stop_clicking)
    except Exception:
        if state.UI.status_label is not None:
            state.UI.status_label.config(text=f"⚠️ Phím Stop '{state.stop_hotkey.upper()}' không hợp lệ hoặc bị trùng!")
        state.stop_hotkey = ""


def capture_start_key(event):
    root = state.UI.root
    root.unbind("<KeyPress>")
    keysym = event.keysym
    key = translate_key(keysym)
    state.start_hotkey = key
    register_global_hotkeys()
    state.UI.btn_hotkey_start.config(text=f"⌨️ Phím Chiến Đấu: {state.start_hotkey.upper()}")
    set_status(f"✅ Đã đặt phím Chiến Đấu: {state.start_hotkey.upper()}")


def capture_stop_key(event):
    root = state.UI.root
    root.unbind("<KeyPress>")
    keysym = event.keysym
    key = translate_key(keysym)
    state.stop_hotkey = key
    register_global_hotkeys()
    state.UI.btn_hotkey_stop.config(text=f"⌨️ Phím Rút Lui: {state.stop_hotkey.upper()}")
    set_status(f"✅ Đã đặt phím Rút Lui: {state.stop_hotkey.upper()}")


def change_start_hotkey():
    from ui.theme import PKM_GOLD, PKM_BG_DARK
    state.UI.btn_hotkey_start.config(text="⏳ Nhấn phím...", bg=PKM_GOLD, fg=PKM_BG_DARK)
    set_status("⌨️ Hãy nhấn một phím để gán làm phím Chiến Đấu (Start)...")
    state.UI.root.bind("<KeyPress>", capture_start_key)


def change_stop_hotkey():
    from ui.theme import PKM_GOLD, PKM_BG_DARK
    state.UI.btn_hotkey_stop.config(text="⏳ Nhấn phím...", bg=PKM_GOLD, fg=PKM_BG_DARK)
    set_status("⌨️ Hãy nhấn một phím để gán làm phím Rút Lui (Stop)...")
    state.UI.root.bind("<KeyPress>", capture_stop_key)
