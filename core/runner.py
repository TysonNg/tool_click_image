import os
import time
import threading
import numpy as np
import pyautogui
from core import state
from core.state import set_status
from core.vision import capture_screen_gray, multi_scale_match, get_search_region_screenshot, filter_close_points
from core.input import click, double_click, click_and_hold, press_key
from utils import safe_print


def find_and_click():
    safe_print("🟢 [THREAD] find_and_click thread started")
    try:
        loop_count = 0
        while state.running and loop_count < state.process_loops:
            safe_print(f"🟢 [THREAD] Loop {loop_count + 1}/{state.process_loops}")
            for tpl in state.templates:
                if tpl["type"] == "image":
                    wait_until_found = tpl.get("wait_until_found", False)
                    wait_timeout = tpl.get("wait_timeout", 0)
                    found = False
                    attempt = 0

                    if wait_timeout == -1:
                        max_attempts = float('inf')
                    elif wait_until_found and wait_timeout > 0:
                        max_attempts = wait_timeout * 10
                    else:
                        max_attempts = 1

                    while state.running and attempt < max_attempts and not found:
                        full_screenshot = capture_screen_gray()
                        screenshot, (offset_x, offset_y) = get_search_region_screenshot(full_screenshot)
                        res, used_scale, matched_w, matched_h = multi_scale_match(screenshot, tpl["img"])
                        threshold = tpl.get("threshold", 0.7)
                        loc = np.where(res >= threshold)

                        points = list(zip(*loc[::-1]))
                        filtered_points = filter_close_points(points, min_dist=max(10, matched_w // 2))

                        if filtered_points:
                            safe_print(f"✅ Found {len(filtered_points)} match(es) for {tpl['path']} (threshold: {threshold}, scale: {used_scale:.2f}x)")
                            safe_print(f"✅ Image size (scaled): {matched_w}x{matched_h}, Offset: ({offset_x}, {offset_y})")
                            found = True

                            count = 0
                            for pt in filtered_points:
                                click_x = pt[0] + matched_w // 2 + offset_x
                                click_y = pt[1] + matched_h // 2 + offset_y
                                safe_print(f"✅ Match at: ({pt[0]}, {pt[1]}), Center: ({pt[0] + matched_w // 2}, {pt[1] + matched_h // 2})")
                                safe_print(f"🖱️ Clicking at: ({click_x}, {click_y})")

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
                                    safe_print(f"⏳ Chờ tìm {tpl['path']}... ({attempt // 10 * 1}s) [max_score={max_score:.3f}, threshold={threshold}, scale={used_scale:.2f}x]")
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

                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0.1)

                elif tpl["type"] == "key":
                    for i in range(tpl["repeat"]):
                        key_type = tpl.get("key_type", "press")
                        if key_type == "hold":
                            pyautogui.keyDown(tpl["key"])
                            time.sleep(0.2)
                            pyautogui.keyUp(tpl["key"])
                            safe_print(f"⌨️ Held key: {tpl['key']}")
                        else:
                            press_key(tpl["key"])
                            safe_print(f"⌨️ Pressed key: {tpl['key']}")

                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0.1)

                time.sleep(tpl.get("delay", state.click_delay))
            loop_count += 1
            if loop_count < state.process_loops:
                safe_print(f"🔄 Loop {loop_count}/{state.process_loops} completed")
    except Exception as e:
        safe_print(f"[AUTOCLICK THREAD ERROR] {e}")
        import traceback
        safe_print(traceback.format_exc())
        if state.UI.status_label:
            state.UI.status_label.config(text=f"⚠️ Lỗi AutoClick: {e}")
    finally:
        ended_by_stop = not state.running
        state.running = False
        safe_print(f"🟢 [THREAD] find_and_click thread ended (ended_by_stop={ended_by_stop})")
        if state.UI.status_label:
            if ended_by_stop:
                set_status("⏹ AutoClick đã dừng.")
            else:
                set_status("✅ AutoClick đã hoàn tất!")


def start_clicking():
    safe_print("🔵 [DEBUG] start_clicking() called")

    if state.scenario_queue:
        safe_print("🔵 [DEBUG] Running scenario queue...")
        run_scenario_queue()
        return

    has_templates = len(state.templates) > 0
    safe_print(f"🔵 [DEBUG] has_templates={has_templates}, templates count={len(state.templates)}")

    if not has_templates:
        msg = "⚠️ Chưa thêm ảnh/tọa độ nào!"
        state.UI.status_label.config(text=msg)
        safe_print(f"🔵 [DEBUG] {msg}")
        return

    state.running = True
    safe_print("🔵 [DEBUG] running=True, starting find_and_click thread...")
    set_status("⏺ AutoClick đang chạy...")
    threading.Thread(target=find_and_click, daemon=True).start()


def stop_clicking(event=None):
    state.running = False
    state.queue_stopped = True
    set_status("⏹ AutoClick đã dừng (toàn bộ kịch bản).")


def smart_start(event=None):
    """Prefer running ticked library stages; fall back to editor/queue if none ticked."""
    runner = getattr(state, "run_library_selection", None)
    if runner and runner(silent_if_empty=True):
        return
    start_clicking()


def run_scenario_queue():
    from scenario.templates import update_history

    if not state.scenario_metadata:
        state.UI.status_label.config(text="⚠️ Chưa tải kịch bản nào!")
        return

    state.current_scenario_index = 0
    state.queue_stopped = False
    set_status(f"⏺ Chạy kịch bản 1/{len(state.scenario_metadata)}...")

    scenario_completed = [False]

    def run_next_scenario():
        root = state.UI.root

        if state.queue_stopped:
            set_status(f"⏹ Đã dừng toàn bộ kịch bản (đang ở {state.current_scenario_index + 1}/{len(state.scenario_metadata)}).")
            state.running = False
            return

        if state.current_scenario_index >= len(state.scenario_metadata):
            set_status(f"✅ Đã hoàn tất tất cả {len(state.scenario_metadata)} kịch bản!")
            state.running = False
            return

        metadata = state.scenario_metadata[state.current_scenario_index]
        file_path = metadata["file_path"]

        try:
            state.process_loops = metadata.get("process_loops", 1)
            state.infinite_loop = metadata.get("infinite_loop", False)
            state.click_delay = metadata.get("click_delay", 1.0)

            state.templates = []
            for tpl in metadata.get("templates", []):
                state.templates.append(tpl.copy())

            update_history()
            set_status(f"⏺ Chạy kịch bản {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: {os.path.basename(file_path)}")
            safe_print(f"🔵 [DEBUG] Starting scenario {state.current_scenario_index + 1}/{len(state.scenario_metadata)}")

            scenario_completed[0] = False
            state.running = True

            def run_scenario_thread():
                try:
                    find_and_click()
                finally:
                    scenario_completed[0] = True

            threading.Thread(target=run_scenario_thread, daemon=True).start()

            def check_and_run_next():
                if state.queue_stopped:
                    safe_print(f"🔵 [DEBUG] Queue stopped by user, halting at scenario {state.current_scenario_index + 1}")
                    set_status(f"⏹ Đã dừng toàn bộ kịch bản tại {state.current_scenario_index + 1}/{len(state.scenario_metadata)}.")
                    state.running = False
                    return
                if scenario_completed[0]:
                    safe_print(f"🔵 [DEBUG] Scenario {state.current_scenario_index + 1} completed, moving to next")
                    state.current_scenario_index += 1
                    root.after(500, run_next_scenario)
                else:
                    root.after(200, check_and_run_next)

            root.after(200, check_and_run_next)

        except Exception as e:
            safe_print(f"⚠️ Lỗi tải kịch bản: {e}")
            import traceback
            safe_print(traceback.format_exc())
            state.current_scenario_index += 1
            root.after(500, run_next_scenario)

    run_next_scenario()
