import json
import os
import shutil
import time
import gc


SCENARIOS_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scenarios")
)
SETTINGS_PATH = os.path.join(SCENARIOS_ROOT, "settings.json")


def ensure_scenarios_root():
    os.makedirs(SCENARIOS_ROOT, exist_ok=True)
    return SCENARIOS_ROOT


def _game_dir(game):
    return os.path.join(ensure_scenarios_root(), game)


def _stage_dir(game, stage):
    return os.path.join(_game_dir(game), stage)


def _unique_name(parent_dir, name):
    base, ext = os.path.splitext(name)
    candidate = name
    index = 2
    while os.path.exists(os.path.join(parent_dir, candidate)):
        candidate = f"{base}_{index}{ext}"
        index += 1
    return candidate


def list_games():
    root = ensure_scenarios_root()
    games = [
        name for name in os.listdir(root)
        if os.path.isdir(os.path.join(root, name))
    ]
    games.sort(key=str.lower)
    return games


def list_stages(game):
    game_dir = _game_dir(game)
    if not os.path.isdir(game_dir):
        return []
    stages = [
        name for name in os.listdir(game_dir)
        if os.path.isdir(os.path.join(game_dir, name))
    ]
    stages.sort(key=str.lower)
    return stages


def get_stage_json(game, stage):
    stage_dir = _stage_dir(game, stage)
    if not os.path.isdir(stage_dir):
        return None
    json_files = [
        os.path.join(stage_dir, name)
        for name in os.listdir(stage_dir)
        if name.lower().endswith(".json")
    ]
    json_files.sort(key=lambda path: os.path.basename(path).lower())
    return json_files[0] if json_files else None


def resolve_image_path(json_dir, path):
    if not path:
        return path
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(json_dir, path))


def create_game(name):
    os.makedirs(_game_dir(name), exist_ok=True)


def rename_game(old_name, new_name):
    """Rename game directory with retry logic for permission errors"""
    old_path = _game_dir(old_name)
    new_path = _game_dir(new_name)
    
    # Retry logic for Windows permission issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release any file handles
            gc.collect()
            time.sleep(0.1)
            
            # Try direct rename
            os.rename(old_path, new_path)
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                # Wait before retry
                time.sleep(0.5)
                continue
            else:
                # Final attempt: try copy + delete
                try:
                    # Create temp dir first
                    temp_path = new_path + "_temp"
                    if os.path.exists(temp_path):
                        shutil.rmtree(temp_path)
                    
                    # Copy directory
                    shutil.copytree(old_path, temp_path)
                    
                    # Delete original
                    shutil.rmtree(old_path)
                    
                    # Rename temp to final
                    os.rename(temp_path, new_path)
                    return
                except Exception as copy_err:
                    raise PermissionError(
                        f"Không thể đổi tên thư mục '{old_name}' sang '{new_name}'. "
                        f"Có thể thư mục đang được sử dụng. "
                        f"Hãy đóng AutoClick hoặc game window và thử lại. "
                        f"Lỗi: {e}"
                    ) from e
        except Exception as e:
            raise e


def delete_game(name):
    """Delete game directory with retry logic for permission errors"""
    game_path = _game_dir(name)
    
    # Retry logic for Windows permission issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release any file handles
            gc.collect()
            time.sleep(0.1)
            
            # Try direct delete
            shutil.rmtree(game_path)
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                # Wait before retry
                time.sleep(0.5)
                continue
            else:
                raise PermissionError(
                    f"Không thể xóa game '{name}'. Có thể thư mục đang được sử dụng. "
                    f"Hãy đóng AutoClick hoặc game window và thử lại. "
                    f"Lỗi: {e}"
                ) from e
        except Exception as e:
            raise e


def create_stage(game, stage_name):
    os.makedirs(_stage_dir(game, stage_name), exist_ok=True)


def delete_stage(game, stage_name):
    """Delete stage directory with retry logic for permission errors"""
    stage_path = _stage_dir(game, stage_name)
    
    # Retry logic for Windows permission issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release any file handles
            gc.collect()
            time.sleep(0.1)
            
            # Try direct delete
            shutil.rmtree(stage_path)
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                # Wait before retry
                time.sleep(0.5)
                continue
            else:
                raise PermissionError(
                    f"Không thể xóa stage '{stage_name}'. Có thể thư mục đang được sử dụng. "
                    f"Hãy đóng AutoClick hoặc game window và thử lại. "
                    f"Lỗi: {e}"
                ) from e
        except Exception as e:
            raise e


def copy_stage(game, stage_name, new_name):
    """Copy stage directory with retry logic for permission errors"""
    src_path = _stage_dir(game, stage_name)
    dst_path = _stage_dir(game, new_name)
    
    # Retry logic for Windows permission issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release any file handles
            gc.collect()
            time.sleep(0.1)
            
            # Try direct copy
            shutil.copytree(src_path, dst_path)
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                # Wait before retry
                time.sleep(0.5)
                continue
            else:
                raise PermissionError(
                    f"Không thể copy stage '{stage_name}'. Có thể thư mục đang được sử dụng. "
                    f"Hãy đóng AutoClick hoặc game window và thử lại. "
                    f"Lỗi: {e}"
                ) from e
        except Exception as e:
            raise e


def copy_image_to_stage(game, stage, src_path):
    stage_dir = _stage_dir(game, stage)
    os.makedirs(stage_dir, exist_ok=True)
    file_name = _unique_name(stage_dir, os.path.basename(src_path))
    dst_path = os.path.join(stage_dir, file_name)
    shutil.copy2(src_path, dst_path)
    return file_name


def save_settings(last_game, last_stages):
    ensure_scenarios_root()
    data = {
        "last_game": last_game or "",
        "last_stages": sorted(last_stages or [], key=str.lower),
    }
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file_obj:
        json.dump(data, file_obj, ensure_ascii=False, indent=2)


def load_settings():
    ensure_scenarios_root()
    if not os.path.exists(SETTINGS_PATH):
        return {"last_game": "", "last_stages": []}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except Exception:
        return {"last_game": "", "last_stages": []}
    return {
        "last_game": data.get("last_game", "") or "",
        "last_stages": list(data.get("last_stages", []) or []),
    }


def import_old_scenario(json_path, game, stage_name):
    with open(json_path, "r", encoding="utf-8") as file_obj:
        scenario = json.load(file_obj)

    create_game(game)
    create_stage(game, stage_name)
    stage_dir = _stage_dir(game, stage_name)

    copied_names = {}
    for template in scenario.get("templates", []):
        if template.get("type") != "image":
            continue
        original_path = resolve_image_path(os.path.dirname(json_path), template.get("path", ""))
        if not os.path.isfile(original_path):
            raise FileNotFoundError(f"Khong tim thay anh: {original_path}")
        if original_path not in copied_names:
            copied_names[original_path] = copy_image_to_stage(game, stage_name, original_path)
        template["path"] = copied_names[original_path]

    new_json_path = os.path.join(stage_dir, f"{stage_name}.json")
    with open(new_json_path, "w", encoding="utf-8") as file_obj:
        json.dump(scenario, file_obj, ensure_ascii=False, indent=2)
    return new_json_path
