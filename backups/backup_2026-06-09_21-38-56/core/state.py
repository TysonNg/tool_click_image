start_hotkey = "f6"
stop_hotkey = "f7"

templates = []
running = False
process_loops = 1
infinite_loop = False
click_delay = 1.0
human_click_mode = False
precision_mode = True

scenario_queue = []
scenario_metadata = []
current_scenario_index = 0
queue_stopped = False
last_run_result = None

current_library_game = None
current_library_stage = None
run_library_selection = None  # set by ui.library_panel — fn that builds queue from ticked stages and starts

search_region_enabled = False
search_region = {"x1": 0, "y1": 0, "x2": 1920, "y2": 1080}

# Relative coordinate capture
game_hwnd = None
game_window_title = None  # Store window title for reference
captured_relative_x = 0
captured_relative_y = 0
captured_relative_percent_x = 0
captured_relative_percent_y = 0


class UI:
    """Widget references — populated after UI is created in main."""
    root = None
    status_var = None
    status_top_var = None
    status_label = None
    history_list = None
    setup_info_text = None
    target_window_text = None
    btn_hotkey_start = None
    btn_hotkey_stop = None
    btn_human_mode = None
    btn_precision_mode = None


def set_status(text):
    from utils import safe_print
    try:
        if UI.status_var is not None:
            UI.status_var.set(text)
        if UI.status_top_var is not None:
            UI.status_top_var.set(text)
        if UI.root is not None:
            UI.root.title(f"AutoClick Nâng Cấp PRO — {text}")
            UI.root.update_idletasks()
    except Exception:
        try:
            if UI.status_label is not None:
                UI.status_label.config(text=text)
                UI.root.update_idletasks()
        except Exception:
            pass
