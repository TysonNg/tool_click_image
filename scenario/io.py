import json
import os
from tkinter import filedialog, messagebox

from core import state
from core.vision import imread_unicode
from scenario.library import SCENARIOS_ROOT, resolve_image_path
from utils import safe_print


def _serialize_templates(base_dir=None):
    templates = []
    for tpl in state.templates:
        tpl_type = tpl["type"]
        if tpl_type == "image":
            image_path = tpl["path"]
            if base_dir:
                try:
                    image_path = os.path.relpath(image_path, base_dir)
                except ValueError:
                    image_path = tpl["path"]
            templates.append({
                "type": "image",
                "path": image_path,
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", state.click_delay),
                "wait_until_found": tpl.get("wait_until_found", False),
                "wait_timeout": tpl.get("wait_timeout", 0),
                "threshold": tpl.get("threshold", 0.7),
                "click_delay": tpl.get("click_delay", 0.5),
                "click_type": tpl.get("click_type", "single"),
            })
        elif tpl_type == "key":
            templates.append({
                "type": "key",
                "key": tpl["key"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", state.click_delay),
                "key_type": tpl.get("key_type", "press"),
                "delay_after": tpl.get("delay_after", 0.5),
            })
        else:
            templates.append({
                "type": "coord",
                "x": tpl["x"],
                "y": tpl["y"],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", state.click_delay),
                "click_type": tpl.get("click_type", "single"),
                "delay_after": tpl.get("delay_after", 0.5),
            })
    return templates


def _build_scenario_payload(base_dir=None):
    return {
        "process_loops": state.process_loops,
        "infinite_loop": state.infinite_loop,
        "click_delay": state.click_delay,
        "templates": _serialize_templates(base_dir=base_dir),
    }


def _choose_missing_image_folder(example_path, count, scenario_name=None):
    label = f"Kich ban: {scenario_name}\n\n" if scenario_name else ""
    result = messagebox.askyesno(
        "Anh mau khong tim thay",
        f"{label}Khong tim thay {count} anh mau.\n\n"
        f"Ban co muon chi dinh thu muc chua anh mau khong?\n\n"
        f"Vi du: {example_path}",
    )
    if not result:
        return None

    new_base_folder = filedialog.askdirectory(title="Chon thu muc chua anh mau")
    if not new_base_folder:
        raise ValueError("Ban chua chon thu muc anh mau")
    return new_base_folder


def load_templates_from_file(file_path, prompt_for_missing=True):
    with open(file_path, "r", encoding="utf-8") as file_obj:
        scenario = json.load(file_obj)

    base_dir = os.path.dirname(file_path)
    missing_images = []
    for tpl in scenario.get("templates", []):
        if tpl.get("type") != "image":
            continue
        img_path = resolve_image_path(base_dir, tpl.get("path", ""))
        if not os.path.exists(img_path):
            missing_images.append(img_path)

    new_base_folder = None
    if missing_images and prompt_for_missing:
        safe_print(f"⚠️ Khong tim thay {len(missing_images)} anh mau")
        new_base_folder = _choose_missing_image_folder(
            missing_images[0],
            len(missing_images),
            scenario_name=os.path.basename(file_path),
        )
        if new_base_folder is None:
            raise ValueError(
                f"Khong the tai kich ban {os.path.basename(file_path)} vi anh mau khong tim thay"
            )

    templates = []
    for tpl in scenario.get("templates", []):
        tpl_type = tpl.get("type")
        if tpl_type == "image":
            img_path = resolve_image_path(base_dir, tpl.get("path", ""))
            if not os.path.exists(img_path) and new_base_folder:
                img_filename = os.path.basename(img_path)
                candidate_path = os.path.join(new_base_folder, img_filename)
                if not os.path.exists(candidate_path):
                    raise ValueError(
                        f"Khong tim thay anh: {img_filename} trong thu muc {new_base_folder}"
                    )
                img_path = candidate_path
                safe_print(f"✅ Tim thay anh tai: {candidate_path}")

            img = imread_unicode(img_path)
            if img is None:
                raise ValueError(f"Khong doc duoc anh mau: {img_path}")
            w, h = img.shape[::-1]
            templates.append({
                "type": "image",
                "img": img,
                "w": w,
                "h": h,
                "repeat": tpl.get("repeat", 1),
                "delay": tpl.get("delay", scenario.get("click_delay", state.click_delay)),
                "path": img_path,
                "wait_until_found": tpl.get("wait_until_found", False),
                "wait_timeout": tpl.get("wait_timeout", 0),
                "is_detection": tpl.get("is_detection", False),
                "threshold": tpl.get("threshold", 0.7),
                "click_delay": tpl.get("click_delay", 0.5),
                "click_type": tpl.get("click_type", "single"),
            })
        elif tpl_type == "key":
            templates.append({
                "type": "key",
                "key": tpl.get("key", "enter"),
                "repeat": tpl.get("repeat", 1),
                "delay": tpl.get("delay", scenario.get("click_delay", state.click_delay)),
                "key_type": tpl.get("key_type", "press"),
                "delay_after": tpl.get("delay_after", 0.5),
                "path": f"[KEY: {tpl.get('key', 'enter')}]",
            })
        else:
            templates.append({
                "type": "coord",
                "x": tpl.get("x", 0),
                "y": tpl.get("y", 0),
                "repeat": tpl.get("repeat", 1),
                "delay": tpl.get("delay", scenario.get("click_delay", state.click_delay)),
                "click_type": tpl.get("click_type", "single"),
                "delay_after": tpl.get("delay_after", 0.5),
                "path": f"({tpl.get('x', 0)},{tpl.get('y', 0)})",
            })

    metadata = {
        "file_path": file_path,
        "process_loops": scenario.get("process_loops", 1),
        "infinite_loop": scenario.get("infinite_loop", False),
        "click_delay": scenario.get("click_delay", 1.0),
        "templates": templates,
    }
    return scenario, templates, metadata


def save_scenario():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
        title="Luu kich ban AutoClick",
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as file_obj:
            json.dump(_build_scenario_payload(), file_obj, ensure_ascii=False, indent=2)
        state.UI.status_label.config(text=f"Da luu kich ban: {os.path.basename(file_path)}")
    except Exception as exc:
        state.UI.status_label.config(text=f"Luu khong thanh cong: {exc}")


def save_scenario_to_stage(game, stage):
    stage_dir = os.path.join(SCENARIOS_ROOT, game, stage)
    os.makedirs(stage_dir, exist_ok=True)
    json_path = os.path.join(stage_dir, f"{stage}.json")
    with open(json_path, "w", encoding="utf-8") as file_obj:
        json.dump(_build_scenario_payload(base_dir=stage_dir), file_obj, ensure_ascii=False, indent=2)
    return json_path


def load_scenario():
    from scenario.templates import update_history

    file_path = filedialog.askopenfilename(
        filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
        title="Mo kich ban AutoClick",
    )
    if not file_path:
        return

    try:
        scenario, templates, _metadata = load_templates_from_file(file_path, prompt_for_missing=True)
        state.process_loops = scenario.get("process_loops", state.process_loops)
        state.infinite_loop = scenario.get("infinite_loop", False)
        state.click_delay = scenario.get("click_delay", state.click_delay)
        state.templates = templates
        state.current_library_game = None
        state.current_library_stage = None
        update_history()
        state.UI.status_label.config(text=f"Da tai kich ban: {os.path.basename(file_path)}")
    except Exception as exc:
        state.UI.status_label.config(text=f"Tai kich ban that bai: {exc}")


def load_multiple_scenarios():
    from scenario.templates import update_history

    file_paths = filedialog.askopenfilenames(
        filetypes=[("AutoClick Scenario", "*.json"), ("All files", "*.*")],
        title="Chon cac kich ban de chay lien tiep",
    )
    file_paths = list(file_paths) if file_paths else []
    if not file_paths:
        return

    failed_files = []
    safe_print(f"🔵 [DEBUG] Selected {len(file_paths)} scenario files to add")

    for file_path in file_paths:
        try:
            safe_print(f"🔵 [DEBUG] Loading scenario: {file_path}")
            _scenario, _templates, metadata = load_templates_from_file(file_path, prompt_for_missing=True)
            state.scenario_metadata.append(metadata)
            state.scenario_queue.append(file_path)
        except Exception as exc:
            failed_files.append(file_path)
            safe_print(f"⚠️ Loi tai kich ban {file_path}: {exc}")

    if state.scenario_metadata:
        update_history()
        state.UI.status_label.config(
            text=f"Tong {len(state.scenario_metadata)} kich ban. Bam 'TUNG POKEBALL!' de chay."
        )
    elif failed_files:
        failed_list = ", ".join(os.path.basename(path) for path in failed_files)
        state.UI.status_label.config(text=f"Khong tai duoc kich ban nao. File loi: {failed_list}.")
        messagebox.showerror("Loi tai kich ban", f"Khong tai duoc bat ky kich ban nao.\n{failed_list}")


def clear_scenarios():
    from scenario.templates import update_history

    state.scenario_queue = []
    state.scenario_metadata = []
    state.templates = []
    state.current_library_game = None
    state.current_library_stage = None
    update_history()
    state.UI.status_label.config(text="Da xoa tat ca kich ban.")
