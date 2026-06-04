import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from core import state
from core.runner import start_clicking
from core.state import set_status
from scenario.io import load_templates_from_file, save_scenario_to_stage
from scenario.library import (
    SCENARIOS_ROOT,
    copy_stage,
    create_game,
    create_stage,
    delete_game,
    delete_stage,
    ensure_scenarios_root,
    get_stage_json,
    import_old_scenario,
    list_games,
    list_stages,
    load_settings,
    rename_game,
    save_settings,
)
from scenario.templates import update_history
from ui.theme import *
from ui.widgets import create_btn, create_card


def create_library_panel(parent):
    ensure_scenarios_root()
    inner = create_card(parent, "SCENARIO LIBRARY", PKM_YELLOW)

    game_var = tk.StringVar()
    stage_vars = {}
    stage_checks_frame = tk.Frame(inner, bg=PKM_BG_CARD)
    option_holder = {"widget": None}
    sync_state = {"mute_game_change": False}

    def get_current_game():
        value = game_var.get().strip()
        return value or None

    def get_selected_stages():
        return sorted(
            [name for name, var in stage_vars.items() if var.get()],
            key=str.lower,
        )

    def persist_settings():
        save_settings(get_current_game() or "", get_selected_stages())

    def update_library_context():
        current_game = get_current_game()
        selected_stages = get_selected_stages()
        if current_game and len(selected_stages) == 1:
            state.current_library_game = current_game
            state.current_library_stage = selected_stages[0]
        else:
            state.current_library_game = None
            state.current_library_stage = None

    def rebuild_stage_list(selected_stages=None):
        for child in stage_checks_frame.winfo_children():
            child.destroy()
        stage_vars.clear()

        current_game = get_current_game()
        selected_stages = set(selected_stages or [])
        stages = list_stages(current_game) if current_game else []
        if not stages:
            tk.Label(
                stage_checks_frame,
                text="Chua co ai nao trong game nay.",
                bg=PKM_BG_CARD,
                fg=PKM_WHITE,
                anchor="w",
                justify="left",
                font=("Segoe UI", 9),
            ).pack(fill="x", pady=2)
            update_library_context()
            persist_settings()
            return

        for stage_name in stages:
            var = tk.BooleanVar(value=stage_name in selected_stages)
            stage_vars[stage_name] = var

            def _toggle(_name=stage_name):
                update_library_context()
                persist_settings()

            chk = tk.Checkbutton(
                stage_checks_frame,
                text=stage_name,
                variable=var,
                command=_toggle,
                anchor="w",
                justify="left",
                selectcolor=PKM_BG_INNER,
                activebackground=PKM_BG_CARD,
                activeforeground=PKM_YELLOW,
                bg=PKM_BG_CARD,
                fg=PKM_WHITE,
                font=("Segoe UI", 9),
                highlightthickness=0,
                bd=0,
            )
            chk.pack(fill="x", pady=1)

        update_library_context()
        persist_settings()

    def refresh_games(selected_game=None, selected_stages=None):
        games = list_games()
        menu = option_holder["widget"]["menu"]
        menu.delete(0, "end")

        for game_name in games:
            menu.add_command(label=game_name, command=lambda value=game_name: game_var.set(value))

        sync_state["mute_game_change"] = True
        try:
            if selected_game in games:
                game_var.set(selected_game)
            elif games:
                game_var.set(games[0])
            else:
                game_var.set("")
        finally:
            sync_state["mute_game_change"] = False

        rebuild_stage_list(selected_stages=selected_stages)

    def on_game_change(*_args):
        if sync_state["mute_game_change"]:
            return
        rebuild_stage_list()

    def require_current_game():
        current_game = get_current_game()
        if not current_game:
            set_status("Hay tao hoac chon game truoc.")
            return None
        return current_game

    def require_single_stage():
        current_game = require_current_game()
        if not current_game:
            return None, None
        selected_stages = get_selected_stages()
        if len(selected_stages) != 1:
            set_status("Hay tick dung 1 ai de thao tac.")
            return None, None
        return current_game, selected_stages[0]

    def create_game_action():
        name = simpledialog.askstring("Game moi", "Nhap ten game moi:", parent=state.UI.root)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        create_game(name)
        refresh_games(selected_game=name, selected_stages=[])
        set_status(f"Da tao game: {name}")

    def rename_game_action():
        current_game = require_current_game()
        if not current_game:
            return
        new_name = simpledialog.askstring(
            "Sua ten game",
            "Nhap ten moi:",
            initialvalue=current_game,
            parent=state.UI.root,
        )
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name or new_name == current_game:
            return
        rename_game(current_game, new_name)
        refresh_games(selected_game=new_name, selected_stages=[])
        set_status(f"Da doi ten game: {current_game} -> {new_name}")

    def delete_game_action():
        current_game = require_current_game()
        if not current_game:
            return
        if not messagebox.askyesno("Xoa game", f"Xoa game '{current_game}'?", parent=state.UI.root):
            return
        if not messagebox.askyesno(
            "Xac nhan lan 2",
            f"Toan bo ai trong '{current_game}' se bi xoa. Tiep tuc?",
            parent=state.UI.root,
        ):
            return
        delete_game(current_game)
        refresh_games()
        set_status(f"Da xoa game: {current_game}")

    def create_stage_action():
        current_game = require_current_game()
        if not current_game:
            return
        stage_name = simpledialog.askstring("Ai moi", "Nhap ten ai moi:", parent=state.UI.root)
        if not stage_name:
            return
        stage_name = stage_name.strip()
        if not stage_name:
            return
        create_stage(current_game, stage_name)
        refresh_games(selected_game=current_game, selected_stages=[stage_name])
        set_status(f"Da tao ai: {stage_name}")

    def copy_stage_action():
        current_game, stage_name = require_single_stage()
        if not current_game:
            return
        new_name = simpledialog.askstring(
            "Copy ai",
            "Nhap ten ai moi:",
            initialvalue=f"{stage_name}_copy",
            parent=state.UI.root,
        )
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name:
            return
        copy_stage(current_game, stage_name, new_name)
        refresh_games(selected_game=current_game, selected_stages=[new_name])
        set_status(f"Da copy ai: {stage_name} -> {new_name}")

    def delete_stage_action():
        current_game, stage_name = require_single_stage()
        if not current_game:
            return
        if not messagebox.askyesno("Xoa ai", f"Xoa ai '{stage_name}'?", parent=state.UI.root):
            return
        delete_stage(current_game, stage_name)
        refresh_games(selected_game=current_game, selected_stages=[])
        set_status(f"Da xoa ai: {stage_name}")

    def load_stage_into_editor():
        current_game, stage_name = require_single_stage()
        if not current_game:
            return
        json_path = get_stage_json(current_game, stage_name)
        if json_path:
            scenario, templates, _metadata = load_templates_from_file(json_path, prompt_for_missing=True)
            state.process_loops = scenario.get("process_loops", 1)
            state.infinite_loop = scenario.get("infinite_loop", False)
            state.click_delay = scenario.get("click_delay", 1.0)
            state.templates = templates
            set_status(f"Da nap ai vao editor: {stage_name}")
        else:
            state.templates = []
            set_status(f"Da nap ai trong (chua co JSON): {stage_name}")
        state.scenario_metadata = []
        state.scenario_queue = []
        state.current_library_game = current_game
        state.current_library_stage = stage_name
        update_history()

    def save_editor_to_stage():
        current_game, stage_name = require_single_stage()
        if not current_game:
            return
        json_path = save_scenario_to_stage(current_game, stage_name)
        state.current_library_game = current_game
        state.current_library_stage = stage_name
        refresh_games(selected_game=current_game, selected_stages=[stage_name])
        set_status(f"Da luu editor vao: {os.path.basename(json_path)}")

    def run_selected_stages(silent_if_empty=False):
        """Build queue from ticked stages and start. Returns True if started, False otherwise.

        silent_if_empty: when True, don't set a 'no stage ticked' status — used when
        TUNG POKÉBALL falls back to editor mode.
        """
        current_game = get_current_game()
        if not current_game:
            if not silent_if_empty:
                set_status("Hay tao hoac chon game truoc.")
            return False
        selected_stages = get_selected_stages()
        if not selected_stages:
            if not silent_if_empty:
                set_status("Hay tick it nhat 1 ai de chay.")
            return False

        state.scenario_metadata = []
        state.scenario_queue = []
        for stage_name in selected_stages:
            json_path = get_stage_json(current_game, stage_name)
            if not json_path:
                continue
            _scenario, _templates, metadata = load_templates_from_file(json_path, prompt_for_missing=True)
            state.scenario_metadata.append(metadata)
            state.scenario_queue.append(json_path)

        update_library_context()
        persist_settings()
        update_history()

        if not state.scenario_metadata:
            set_status("Khong tim thay ai hop le de chay.")
            return False
        start_clicking()
        return True

    def open_game_folder():
        current_game = get_current_game()
        folder_path = os.path.join(SCENARIOS_ROOT, current_game) if current_game else SCENARIOS_ROOT
        if not os.path.exists(folder_path):
            ensure_scenarios_root()
        os.startfile(folder_path)

    def toggle_all_stages():
        if not stage_vars:
            return
        # If everything is already ticked, untick all; otherwise tick all.
        all_checked = all(var.get() for var in stage_vars.values())
        new_value = not all_checked
        for var in stage_vars.values():
            var.set(new_value)
        update_library_context()
        persist_settings()
        set_status("Da chon tat ca ai." if new_value else "Da bo chon tat ca ai.")

    def import_old_scenario_action():
        current_game = require_current_game()
        if not current_game:
            return
        json_path = filedialog.askopenfilename(
            filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
            title="Chon scenario cu de import",
        )
        if not json_path:
            return
        stage_name = simpledialog.askstring("Import scenario", "Nhap ten ai moi:", parent=state.UI.root)
        if not stage_name:
            return
        stage_name = stage_name.strip()
        if not stage_name:
            return
        import_old_scenario(json_path, current_game, stage_name)
        refresh_games(selected_game=current_game, selected_stages=[stage_name])
        set_status(f"Da import scenario cu vao ai: {stage_name}")

    game_row = tk.Frame(inner, bg=PKM_BG_CARD)
    game_row.pack(fill="x", pady=(0, 4))

    tk.Label(
        game_row,
        text="Game:",
        bg=PKM_BG_CARD,
        fg=PKM_YELLOW,
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left", padx=(0, 6))

    option_holder["widget"] = tk.OptionMenu(game_row, game_var, "")
    option_holder["widget"].config(
        bg=PKM_BLUE_DARK,
        fg=PKM_WHITE,
        activebackground=PKM_BLUE,
        activeforeground=PKM_WHITE,
        highlightthickness=0,
        bd=0,
        font=("Segoe UI", 9),
        width=16,
    )
    option_holder["widget"]["menu"].config(bg=PKM_BG_INNER, fg=PKM_WHITE, font=("Segoe UI", 9))
    option_holder["widget"].pack(side="left", fill="x", expand=True)

    create_btn(game_row, "+", create_game_action, bg=PKM_GREEN, fg=PKM_BG_DARK, hover_bg=PKM_GREEN_LT).pack(side="left", padx=(4, 2))
    create_btn(game_row, "Rename", rename_game_action, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE).pack(side="left", padx=2)
    create_btn(game_row, "Delete", delete_game_action, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT).pack(side="left", padx=(2, 0))

    tk.Frame(inner, bg=PKM_GOLD, height=1).pack(fill="x", pady=4)

    stage_header_row = tk.Frame(inner, bg=PKM_BG_CARD)
    stage_header_row.pack(fill="x", pady=(0, 4))
    tk.Label(
        stage_header_row,
        text="Danh sach ai:",
        bg=PKM_BG_CARD,
        fg=PKM_YELLOW,
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).pack(side="left")
    create_btn(
        stage_header_row,
        "Check all",
        toggle_all_stages,
        bg=PKM_BLUE_DARK,
        fg=PKM_YELLOW,
        hover_bg=PKM_BLUE,
    ).pack(side="right", padx=(4, 0))

    stage_checks_frame.pack(fill="x", pady=(0, 4))

    stage_row_1 = tk.Frame(inner, bg=PKM_BG_CARD)
    stage_row_1.pack(fill="x", pady=1)
    create_btn(stage_row_1, "Ai moi", create_stage_action, bg=PKM_BLUE, fg=PKM_WHITE, hover_bg=PKM_BLUE_LT).pack(side="left", fill="x", expand=True, padx=(0, 2))
    create_btn(stage_row_1, "Copy", copy_stage_action, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE).pack(side="left", fill="x", expand=True, padx=2)
    create_btn(stage_row_1, "Xoa ai", delete_stage_action, bg=PKM_RED, fg=PKM_WHITE, hover_bg=PKM_RED_LIGHT).pack(side="left", fill="x", expand=True, padx=(2, 0))

    stage_row_2 = tk.Frame(inner, bg=PKM_BG_CARD)
    stage_row_2.pack(fill="x", pady=1)
    create_btn(stage_row_2, "Nap vao editor", load_stage_into_editor, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE).pack(side="left", fill="x", expand=True, padx=(0, 2))
    create_btn(stage_row_2, "Luu editor", save_editor_to_stage, bg=PKM_GREEN, fg=PKM_BG_DARK, hover_bg=PKM_GREEN_LT).pack(side="left", fill="x", expand=True, padx=(2, 0))

    stage_row_3 = tk.Frame(inner, bg=PKM_BG_CARD)
    stage_row_3.pack(fill="x", pady=1)
    create_btn(stage_row_3, "Mo folder", open_game_folder, bg=PKM_BLUE_DARK, fg=PKM_WHITE, hover_bg=PKM_BLUE).pack(fill="x", expand=True)

    stage_row_4 = tk.Frame(inner, bg=PKM_BG_CARD)
    stage_row_4.pack(fill="x", pady=1)
    create_btn(stage_row_4, "Import scenario cu", import_old_scenario_action, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, hover_bg=PKM_BLUE).pack(fill="x", expand=True)

    game_var.trace_add("write", on_game_change)

    settings = load_settings()
    refresh_games(
        selected_game=settings.get("last_game") or None,
        selected_stages=settings.get("last_stages") or [],
    )

    state.run_library_selection = run_selected_stages
    return inner
