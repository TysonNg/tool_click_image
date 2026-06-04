import json
import os
from tkinter import filedialog, messagebox

import cv2

from core import state
from core.vision import imread_unicode
from scenario.library import SCENARIOS_ROOT, resolve_image_path
from utils import safe_print


def _normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _serialize_template_list(templates_source, base_dir=None):
    templates = []
    for tpl in templates_source:
        tpl_type = tpl["type"]
        if tpl_type == "image":
            image_paths = _normalize_list(tpl.get("paths")) or [tpl["path"]]
            serialized_paths = []
            for image_path in image_paths:
                final_path = image_path
                if base_dir:
                    try:
                        final_path = os.path.relpath(image_path, base_dir)
                    except ValueError:
                        final_path = image_path
                serialized_paths.append(final_path)

            payload = {
                "type": "image",
                "path": serialized_paths[0],
                "repeat": tpl["repeat"],
                "delay": tpl.get("delay", state.click_delay),
                "wait_until_found": tpl.get("wait_until_found", False),
                "wait_timeout": tpl.get("wait_timeout", 0),
                "threshold": tpl.get("threshold", 0.7),
                "click_delay": tpl.get("click_delay", 0.5),
                "click_type": tpl.get("click_type", "single"),
                "search_region_enabled": tpl.get("search_region_enabled", False),
                "search_region": tpl.get("search_region", {"x1": 0, "y1": 0, "x2": 0, "y2": 0}),
                "click_point_mode": tpl.get("click_point_mode", "center"),
                "click_x": tpl.get("click_x"),
                "click_y": tpl.get("click_y"),
            }
            if len(serialized_paths) > 1:
                payload["paths"] = serialized_paths

            mask_paths = _normalize_list(tpl.get("mask_paths"))
            serialized_masks = []
            for mask_path in mask_paths:
                if not mask_path:
                    serialized_masks.append(None)
                    continue
                final_mask_path = mask_path
                if base_dir:
                    try:
                        final_mask_path = os.path.relpath(mask_path, base_dir)
                    except ValueError:
                        final_mask_path = mask_path
                serialized_masks.append(final_mask_path)
            if serialized_masks:
                payload["mask_path"] = serialized_masks[0]
                if len(serialized_masks) > 1:
                    payload["mask_paths"] = serialized_masks

            templates.append(payload)
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


def _serialize_templates(base_dir=None):
    return _serialize_template_list(state.templates, base_dir=base_dir)


def _build_scenario_payload(base_dir=None):
    return {
        "process_loops": state.process_loops,
        "infinite_loop": state.infinite_loop,
        "click_delay": state.click_delay,
        "templates": _serialize_template_list(state.templates, base_dir=base_dir),
    }


def _build_metadata_payload(metadata):
    file_path = metadata["file_path"]
    base_dir = os.path.dirname(file_path)
    process_loops = int(metadata.get("process_loops", 1) or 1)
    if process_loops < 1:
        process_loops = 1
    click_delay = float(metadata.get("click_delay", 1.0) or 1.0)
    return {
        "process_loops": process_loops,
        "infinite_loop": bool(metadata.get("infinite_loop", False)),
        "click_delay": click_delay,
        "templates": _serialize_template_list(metadata.get("templates", []), base_dir=base_dir),
    }


def save_scenario_metadata(metadata):
    file_path = metadata["file_path"]
    payload = _build_metadata_payload(metadata)
    with open(file_path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, ensure_ascii=False, indent=2)
    return file_path


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


def _resolve_existing_path(base_dir, rel_path, new_base_folder=None, kind="anh"):
    final_path = resolve_image_path(base_dir, rel_path)
    if os.path.exists(final_path):
        return final_path
    if not new_base_folder:
        return final_path

    filename = os.path.basename(final_path)
    candidate_path = os.path.join(new_base_folder, filename)
    if not os.path.exists(candidate_path):
        raise ValueError(f"Khong tim thay {kind}: {filename} trong thu muc {new_base_folder}")

    safe_print(f"âœ… Tim thay {kind} tai: {candidate_path}")
    return candidate_path


def load_templates_from_file(file_path, prompt_for_missing=True):
    with open(file_path, "r", encoding="utf-8") as file_obj:
        scenario = json.load(file_obj)

    base_dir = os.path.dirname(file_path)
    missing_images = []
    for tpl in scenario.get("templates", []):
        if tpl.get("type") != "image":
            continue
        image_refs = _normalize_list(tpl.get("paths")) or [tpl.get("path", "")]
        for image_ref in image_refs:
            img_path = resolve_image_path(base_dir, image_ref)
            if not os.path.exists(img_path):
                missing_images.append(img_path)

    new_base_folder = None
    if missing_images and prompt_for_missing:
        safe_print(f"âš ï¸ Khong tim thay {len(missing_images)} anh mau")
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
            image_refs = _normalize_list(tpl.get("paths")) or [tpl.get("path", "")]
            resolved_image_paths = []
            loaded_images = []

            for image_ref in image_refs:
                img_path = _resolve_existing_path(base_dir, image_ref, new_base_folder, kind="anh")
                img = imread_unicode(img_path)
                if img is None:
                    raise ValueError(f"Khong doc duoc anh mau: {img_path}")
                resolved_image_paths.append(img_path)
                loaded_images.append(img)

            mask_refs = _normalize_list(tpl.get("mask_paths"))
            if not mask_refs and tpl.get("mask_path") is not None:
                mask_refs = [tpl.get("mask_path")]

            resolved_mask_paths = []
            loaded_masks = []
            for mask_ref in mask_refs:
                if not mask_ref:
                    resolved_mask_paths.append(None)
                    loaded_masks.append(None)
                    continue

                mask_path = _resolve_existing_path(base_dir, mask_ref, new_base_folder, kind="mask")
                mask = imread_unicode(mask_path, flags=cv2.IMREAD_GRAYSCALE)
                if mask is None:
                    raise ValueError(f"Khong doc duoc mask: {mask_path}")
                _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
                resolved_mask_paths.append(mask_path)
                loaded_masks.append(mask)

            while len(loaded_masks) < len(loaded_images):
                loaded_masks.append(None)
                resolved_mask_paths.append(None)

            primary_image = loaded_images[0]
            width, height = primary_image.shape[::-1]
            templates.append({
                "type": "image",
                "img": primary_image,
                "imgs": loaded_images,
                "mask": loaded_masks[0] if loaded_masks else None,
                "masks": loaded_masks,
                "w": width,
                "h": height,
                "repeat": tpl.get("repeat", 1),
                "delay": tpl.get("delay", scenario.get("click_delay", state.click_delay)),
                "path": resolved_image_paths[0],
                "paths": resolved_image_paths,
                "mask_path": resolved_mask_paths[0] if resolved_mask_paths else None,
                "mask_paths": resolved_mask_paths,
                "wait_until_found": tpl.get("wait_until_found", False),
                "wait_timeout": tpl.get("wait_timeout", 0),
                "is_detection": tpl.get("is_detection", False),
                "threshold": tpl.get("threshold", 0.7),
                "click_delay": tpl.get("click_delay", 0.5),
                "click_type": tpl.get("click_type", "single"),
                "search_region_enabled": tpl.get("search_region_enabled", False),
                "search_region": tpl.get("search_region", {"x1": 0, "y1": 0, "x2": 0, "y2": 0}),
                "click_point_mode": tpl.get("click_point_mode", "center"),
                "click_x": tpl.get("click_x", width // 2),
                "click_y": tpl.get("click_y", height // 2),
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
    safe_print(f"ðŸ”µ [DEBUG] Selected {len(file_paths)} scenario files to add")

    for file_path in file_paths:
        try:
            safe_print(f"ðŸ”µ [DEBUG] Loading scenario: {file_path}")
            _scenario, _templates, metadata = load_templates_from_file(file_path, prompt_for_missing=True)
            state.scenario_metadata.append(metadata)
            state.scenario_queue.append(file_path)
        except Exception as exc:
            failed_files.append(file_path)
            safe_print(f"âš ï¸ Loi tai kich ban {file_path}: {exc}")

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
