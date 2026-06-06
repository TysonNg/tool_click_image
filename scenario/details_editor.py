import os
import tkinter as tk
from tkinter import messagebox

from core import state
from scenario.io import save_scenario_metadata
from scenario.templates import _create_scrollable_form, create_image_template_via_user_flow, edit_existing_image_template, update_history
from ui.theme import PKM_BG_CARD, PKM_BG_DARK, PKM_BG_INNER, PKM_BLUE, PKM_BLUE_DARK, PKM_GOLD, PKM_GREEN, PKM_RED, PKM_WHITE, PKM_YELLOW
from ui.dialogs import _safe_destroy, _force_destroy


def edit_scenario_details():
    if not state.scenario_metadata:
        state.UI.status_label.config(text="Khong co kich ban nao de sua.")
        return

    selected = state.UI.history_list.curselection()
    if not selected:
        state.UI.status_label.config(text="Hay chon mot item de xac dinh kich ban.")
        return

    index = selected[0]
    scenario_idx = 0
    current_line = 0
    for s_idx, metadata in enumerate(state.scenario_metadata):
        current_line += 3
        current_line += max(1, len(metadata["templates"]))
        current_line += 1
        if current_line > index:
            scenario_idx = s_idx
            break

    if scenario_idx >= len(state.scenario_metadata):
        state.UI.status_label.config(text="Khong the xac dinh kich ban.")
        return

    metadata = state.scenario_metadata[scenario_idx]
    scenario_name = os.path.basename(metadata["file_path"])

    dialog = tk.Toplevel(state.UI.root)
    dialog.title(f"Edit Kich Ban: {scenario_name}")
    dialog.geometry("720x620")
    dialog.resizable(True, True)

    main_frame = tk.Frame(dialog, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    header_frame = tk.Frame(main_frame, bg=PKM_BG_INNER)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
    tk.Label(
        header_frame,
        text=f"Edit Kich Ban: {scenario_name}",
        font=("Segoe UI", 12, "bold"),
        bg=PKM_BG_INNER,
        fg=PKM_YELLOW,
    ).pack(pady=15)

    button_frame = tk.Frame(main_frame, bg=PKM_BG_CARD)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 15))

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

    tk.Label(
        content_frame,
        text="Danh sach item trong kich ban:",
        font=("Segoe UI", 11, "bold"),
        bg="white",
        fg="black",
    ).pack(anchor="w", pady=(0, 10))

    list_frame = tk.Frame(content_frame, bg="white")
    list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    scrollbar = tk.Scrollbar(list_frame, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    template_list = tk.Listbox(
        list_frame,
        font=("Segoe UI", 9),
        bg=PKM_BG_INNER,
        fg=PKM_WHITE,
        selectbackground=PKM_GOLD,
        selectforeground=PKM_BG_DARK,
        yscrollcommand=scrollbar.set,
        height=12,
    )
    template_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=template_list.yview)

    def persist_metadata():
        save_scenario_metadata(metadata)
        update_history()

    def refresh_template_list():
        template_list.delete(0, tk.END)
        for idx, tpl in enumerate(metadata["templates"]):
            if tpl["type"] == "image":
                click_mode = tpl.get("click_point_mode", "center")
                region_flag = " region" if tpl.get("search_region_enabled", False) else ""
                text = (
                    f"{idx + 1}. [IMG] {os.path.basename(tpl['path'])} "
                    f"(threshold: {tpl.get('threshold', 0.7)}, click: {click_mode}{region_flag})"
                )
            elif tpl["type"] == "key":
                text = f"{idx + 1}. [KEY] {tpl['path']}"
            else:
                text = f"{idx + 1}. [XY] {tpl['path']}"
            template_list.insert(tk.END, text)

    def apply_wait_choice(tpl, wait_choice):
        if wait_choice == "vo cuc":
            tpl["wait_until_found"] = True
            tpl["wait_timeout"] = -1
        elif wait_choice == "co (30s)":
            tpl["wait_until_found"] = True
            tpl["wait_timeout"] = 30
        elif wait_choice == "khong":
            tpl["wait_until_found"] = False
            tpl["wait_timeout"] = 0

    def open_image_editor(tpl, on_done):
        if edit_existing_image_template(tpl):
            on_done()
            messagebox.showinfo("Thanh cong", "Da cap nhat anh.")

    def edit_selected_template():
        sel = template_list.curselection()
        if not sel:
            messagebox.showwarning("Canh bao", "Hay chon mot item de sua.")
            return
        tpl = metadata["templates"][sel[0]]
        if tpl["type"] != "image":
            messagebox.showinfo("Thong bao", "Bulk/chinh tay hien chi ap dung cho item anh.")
            return

        def on_done():
            persist_metadata()
            refresh_template_list()

        open_image_editor(tpl, on_done)

    def bulk_edit_all_images():
        image_templates = [tpl for tpl in metadata["templates"] if tpl["type"] == "image"]
        if not image_templates:
            messagebox.showinfo("Thong bao", "Khong co item anh de sua hang loat.")
            return

        bulk_dialog = tk.Toplevel(dialog)
        bulk_dialog.title(f"Sua tat ca anh: {scenario_name}")
        bulk_dialog.geometry("560x640")
        bulk_dialog.minsize(520, 520)
        bulk_dialog.resizable(True, True)

        bulk_main = tk.Frame(bulk_dialog, bg="white")
        bulk_main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        bulk_header = tk.Frame(bulk_main, bg=PKM_BG_INNER)
        bulk_header.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        tk.Label(
            bulk_header,
            text=f"Sua tat ca {len(image_templates)} anh",
            font=("Segoe UI", 12, "bold"),
            bg=PKM_BG_INNER,
            fg=PKM_YELLOW,
        ).pack(pady=15)

        bulk_button_frame = tk.Frame(bulk_main, bg="white")
        bulk_button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

        bulk_content_container, bulk_content = _create_scrollable_form(bulk_main)
        bulk_content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            bulk_content,
            text="De trong = giu nguyen. Chi ap dung cho cac item anh.",
            font=("Segoe UI", 10),
            bg="white",
            fg="gray25",
        ).pack(anchor="w", pady=(0, 12))

        fields = {
            "repeat": tk.StringVar(value=""),
            "delay": tk.StringVar(value=""),
            "click_type": tk.StringVar(value="giu nguyen"),
            "click_delay": tk.StringVar(value=""),
            "threshold": tk.StringVar(value=""),
            "wait_until_found": tk.StringVar(value="giu nguyen"),
        }

        def add_bulk_entry(label, key):
            tk.Label(bulk_content, text=label, font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(8, 3))
            tk.Entry(bulk_content, textvariable=fields[key], font=("Segoe UI", 11), width=40).pack(anchor="w", pady=(0, 12), fill=tk.X)

        add_bulk_entry("So lan click:", "repeat")
        add_bulk_entry("Delay truoc (giay):", "delay")

        tk.Label(bulk_content, text="Loai click:", font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(8, 3))
        click_type_combo = tk.OptionMenu(bulk_content, fields["click_type"], "giu nguyen", "single", "double", "hold")
        click_type_combo.config(font=("Segoe UI", 11), bg="white", fg="black", width=37)
        click_type_combo.pack(anchor="w", pady=(0, 12), fill=tk.X)

        add_bulk_entry("Delay sau click (giay):", "click_delay")
        add_bulk_entry("Threshold (0.0-1.0):", "threshold")

        tk.Label(bulk_content, text="Cho tim duoc?:", font=("Segoe UI", 11, "bold"), bg="white", fg="black").pack(anchor="w", pady=(8, 3))
        wait_combo = tk.OptionMenu(bulk_content, fields["wait_until_found"], "giu nguyen", "khong", "co (30s)", "vo cuc")
        wait_combo.config(font=("Segoe UI", 11), bg="white", fg="black", width=37)
        wait_combo.pack(anchor="w", pady=(0, 20), fill=tk.X)

        def apply_bulk_edit(event=None):
            try:
                repeat_text = fields["repeat"].get().strip()
                delay_text = fields["delay"].get().strip()
                click_type = fields["click_type"].get()
                click_delay_text = fields["click_delay"].get().strip()
                threshold_text = fields["threshold"].get().strip()
                wait_choice = fields["wait_until_found"].get()

                for tpl in image_templates:
                    if repeat_text:
                        tpl["repeat"] = int(repeat_text)
                    if delay_text:
                        tpl["delay"] = float(delay_text)
                    if click_type != "giu nguyen":
                        tpl["click_type"] = click_type
                    if click_delay_text:
                        tpl["click_delay"] = float(click_delay_text)
                    if threshold_text:
                        tpl["threshold"] = float(threshold_text)
                    if wait_choice != "giu nguyen":
                        apply_wait_choice(tpl, wait_choice)

                persist_metadata()
                refresh_template_list()
                _safe_destroy(bulk_dialog)
                messagebox.showinfo("Thanh cong", f"Da cap nhat {len(image_templates)} anh.")
            except Exception as e:
                messagebox.showerror("Loi", f"Loi: {e}")

        tk.Button(bulk_button_frame, text="Ap dung tat ca", command=apply_bulk_edit, bg=PKM_GREEN, fg="white", font=("Segoe UI", 11, "bold"), padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)
        tk.Button(bulk_button_frame, text="Huy", command=lambda: _safe_destroy(bulk_dialog), bg=PKM_RED, fg="white", font=("Segoe UI", 11, "bold"), padx=30, pady=10, width=18).pack(side=tk.LEFT, padx=5, expand=True)
        bulk_dialog.bind("<Return>", apply_bulk_edit)
        bulk_dialog.bind("<Escape>", lambda e: _safe_destroy(bulk_dialog))
        bulk_dialog.protocol("WM_DELETE_WINDOW", lambda: _safe_destroy(bulk_dialog))
        bulk_dialog.transient(dialog)
        bulk_dialog.grab_set()

    def delete_selected_template():
        sel = template_list.curselection()
        if not sel:
            messagebox.showwarning("Canh bao", "Hay chon mot item de xoa.")
            return
        if messagebox.askyesno("Xac nhan xoa", "Ban co chac muon xoa item nay?"):
            metadata["templates"].pop(sel[0])
            persist_metadata()
            refresh_template_list()
            messagebox.showinfo("Thanh cong", "Da xoa item.")

    def add_new_template():
        template = create_image_template_via_user_flow(metadata=metadata)
        if template is None:
            return
        metadata["templates"].append(template)
        persist_metadata()
        refresh_template_list()
        messagebox.showinfo("Thanh cong", f"Da them anh: {os.path.basename(template['path'])}.")

    def move_template_up():
        sel = template_list.curselection()
        if not sel or sel[0] == 0:
            messagebox.showwarning("Canh bao", "Khong the di chuyen len.")
            return
        idx = sel[0]
        metadata["templates"][idx - 1], metadata["templates"][idx] = metadata["templates"][idx], metadata["templates"][idx - 1]
        persist_metadata()
        refresh_template_list()
        template_list.selection_set(idx - 1)

    def move_template_down():
        sel = template_list.curselection()
        if not sel or sel[0] == template_list.size() - 1:
            messagebox.showwarning("Canh bao", "Khong the di chuyen xuong.")
            return
        idx = sel[0]
        metadata["templates"][idx], metadata["templates"][idx + 1] = metadata["templates"][idx + 1], metadata["templates"][idx]
        persist_metadata()
        refresh_template_list()
        template_list.selection_set(idx + 1)

    refresh_template_list()

    button_row1 = tk.Frame(button_frame, bg=PKM_BG_CARD)
    button_row1.pack(fill="x", pady=5)
    tk.Button(button_row1, text="Edit Anh", command=edit_selected_template, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.LEFT, fill="x", expand=True, padx=3)
    tk.Button(button_row1, text="Len", command=move_template_up, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.LEFT, fill="x", expand=True, padx=3)
    tk.Button(button_row1, text="Xuong", command=move_template_down, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.LEFT, fill="x", expand=True, padx=3)
    tk.Button(button_row1, text="Xoa", command=delete_selected_template, bg=PKM_RED, fg=PKM_WHITE, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.LEFT, fill="x", expand=True, padx=3)

    button_row2 = tk.Frame(button_frame, bg=PKM_BG_CARD)
    button_row2.pack(fill="x", pady=5)
    tk.Button(button_row2, text="Them Anh", command=add_new_template, bg=PKM_GREEN, fg=PKM_BG_DARK, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.LEFT, fill="x", expand=True, padx=3)
    tk.Button(button_row2, text="Sua Tat Ca", command=bulk_edit_all_images, bg=PKM_BLUE_DARK, fg=PKM_YELLOW, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.LEFT, fill="x", expand=True, padx=3)
    tk.Button(button_row2, text="Dong", command=lambda: [_safe_destroy(dialog), update_history()], bg=PKM_BLUE, fg=PKM_WHITE, font=("Segoe UI", 10, "bold"), padx=15, pady=8).pack(side=tk.RIGHT, fill="x", expand=True, padx=3)

