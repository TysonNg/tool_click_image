import os
import time
import threading

import pyautogui

from core import state
from core.input import click, click_and_hold, double_click, press_key
from core.state import set_status
from core.vision import capture_screen_gray, find_best_match_hybrid, get_search_region_screenshot
from utils import safe_print


FINAL_IMAGE_GRACE_SECONDS = 3


def _format_loop_label(loop_index):
    if state.infinite_loop:
        return f"{loop_index}/∞"
    return f"{loop_index}/{state.process_loops}"


def _resolve_click_point(tpl, matched_w, matched_h):
    """
    Enhanced: Calculate click point with proper scale correction.
    
    Logic:
    - base_w/h: original template size when captured
    - matched_w/h: matched template size (may be scaled)
    - click_x/y: relative click position in original template
    - scaled_click: click position in matched (scaled) template
    """
    click_mode = tpl.get("click_point_mode", "center")
    base_w = max(1, int(tpl.get("w", matched_w) or matched_w))
    base_h = max(1, int(tpl.get("h", matched_h) or matched_h))
    
    # Calculate scale factor (matched / base)
    scale_w = matched_w / base_w
    scale_h = matched_h / base_h

    if click_mode == "custom":
        # Click point from config (relative to original template)
        raw_click_x = int(tpl.get("click_x", base_w // 2))
        raw_click_y = int(tpl.get("click_y", base_h // 2))
        
        # Validate bounds
        if 0 <= raw_click_x < base_w and 0 <= raw_click_y < base_h:
            # Scale click point according to matched/base ratio
            scaled_click_x = int(round(raw_click_x * scale_w))
            scaled_click_y = int(round(raw_click_y * scale_h))
            
            # Debug logging
            safe_print(
                f"🔵 [CLICK_CALC] Custom click point:"
                f"\n  - Base size: {base_w}x{base_h}"
                f"\n  - Matched size: {matched_w}x{matched_h}"
                f"\n  - Scale factor: {scale_w:.3f}x{scale_h:.3f}"
                f"\n  - Raw click (base): ({raw_click_x}, {raw_click_y})"
                f"\n  - Scaled click (matched): ({scaled_click_x}, {scaled_click_y})"
            )
            
            return click_mode, scaled_click_x, scaled_click_y

        safe_print(
            f"⚠️ Invalid custom click point for {tpl['path']}: "
            f"({raw_click_x}, {raw_click_y}) outside {base_w}x{base_h}. Falling back to center."
        )

    # Fallback: center of matched image
    center_x = matched_w // 2
    center_y = matched_h // 2
    
    safe_print(
        f"🔵 [CLICK_CALC] Center click point:"
        f"\n  - Matched size: {matched_w}x{matched_h}"
        f"\n  - Center: ({center_x}, {center_y})"
    )
    
    return "center", center_x, center_y


def _perform_click_action(tpl, click_x, click_y):
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


def find_and_click(queue_mode=False):
    safe_print("🟢 [THREAD] find_and_click thread started")
    run_result = "completed"
    try:
        loop_count = 0
        last_step_failed = False  # Track if last step failed to retry next loop
        while state.running and (state.infinite_loop or loop_count < state.process_loops):
            safe_print(f"🟢 [THREAD] Loop {_format_loop_label(loop_count + 1)}")
            total_templates = len(state.templates)
            last_step_failed = False  # Reset for this loop iteration
            
            for tpl_index, tpl in enumerate(state.templates):
                if not state.running:
                    break

                if tpl["type"] == "image":
                    is_last_step = tpl_index == total_templates - 1
                    wait_until_found = tpl.get("wait_until_found", False)
                    wait_timeout = tpl.get("wait_timeout", 0)
                    found = False
                    attempt = 0

                    if wait_timeout == -1:
                        max_attempts = float("inf")
                    elif wait_until_found and wait_timeout > 0:
                        max_attempts = wait_timeout * 10
                    else:
                        # For all other cases (including last step without wait), just 1 attempt
                        max_attempts = 1

                    while state.running and attempt < max_attempts and not found:
                        full_screenshot = capture_screen_gray()
                        screenshot, (offset_x, offset_y), region_source = get_search_region_screenshot(
                            full_screenshot,
                            template=tpl,
                        )
                        threshold = tpl.get("threshold", 0.7)
                        candidate_images = tpl.get("imgs") or [tpl["img"]]
                        candidate_masks = tpl.get("masks") or [tpl.get("mask")]
                        candidate_names = tpl.get("paths") or [tpl["path"]]

                        match = find_best_match_hybrid(
                            screenshot,
                            candidate_images,
                            threshold=threshold,
                            template_names=candidate_names,
                            masks=candidate_masks,
                        )

                        if match.found:
                            safe_print(
                                f"✅ Best match for {tpl['path']} => {match.template_name} "
                                f"(score: {match.score:.3f}, threshold: {threshold}, scale: {match.scale:.2f}x, method: {match.method})"
                            )
                            safe_print(
                                f"✅ Match origin: ({match.top_left_x}, {match.top_left_y}), "
                                f"Matched size: {match.matched_w}x{match.matched_h}, "
                                f"Region offset: ({offset_x}, {offset_y}), Region source: {region_source}"
                            )
                            found = True

                            count = 0
                            while state.running and count < tpl["repeat"]:
                                click_mode, scaled_click_x, scaled_click_y = _resolve_click_point(
                                    tpl,
                                    match.matched_w,
                                    match.matched_h,
                                )
                                click_x = match.top_left_x + scaled_click_x + offset_x
                                click_y = match.top_left_y + scaled_click_y + offset_y
                                safe_print(
                                    f"✅ Final click point: ({click_x}, {click_y}) "
                                    f"[click_mode={click_mode}, match_origin=({match.top_left_x}, {match.top_left_y}), "
                                    f"scaled_offset=({scaled_click_x}, {scaled_click_y}), region_offset=({offset_x}, {offset_y})]"
                                )
                                _perform_click_action(tpl, click_x, click_y)

                                click_delay_after = tpl.get("click_delay", 0.5)
                                time.sleep(click_delay_after)
                                count += 1
                                if count < tpl["repeat"]:
                                    time.sleep(0)  # No gap between repeats
                        else:
                            if wait_until_found or is_last_step:
                                attempt += 1
                                if attempt % 10 == 0:
                                    if wait_until_found:
                                        safe_print(
                                            f"⏳ Chờ tìm {tpl['path']}... ({attempt // 10}s) "
                                            f"[best_score={match.score:.3f}, threshold={threshold}, scale={match.scale:.2f}x, template={match.template_name}]"
                                        )
                                    else:
                                        safe_print(
                                            f"⏳ Bước cuối chưa xuất hiện {tpl['path']}... ({attempt // 10}s/{FINAL_IMAGE_GRACE_SECONDS}s) "
                                            f"[best_score={match.score:.3f}, threshold={threshold}, scale={match.scale:.2f}x, template={match.template_name}]"
                                        )
                                time.sleep(0)  # No gap in retry loop
                            else:
                                attempt = max_attempts

                    if not found and wait_until_found:
                        if wait_timeout == -1:
                            safe_print(f"⚠️ Timeout: Không tìm được {tpl['path']} (chờ vô cực)")
                        else:
                            safe_print(f"⚠️ Timeout: Không tìm được {tpl['path']} sau {wait_timeout} giây")
                    elif not found:
                        # If wait_until_found is False and it's not the last step, skip gracefully
                        if not wait_until_found and not is_last_step:
                            safe_print(f"⏭️ Bỏ qua (không chờ): {tpl['path']}")
                        else:
                            safe_print(f"❌ Không tìm được {tpl['path']}")
                            if is_last_step:
                                # Last step not found: mark for potential retry in next loop
                                last_step_failed = True
                                break  # Break from template loop to check if more loops available

                elif tpl["type"] == "coord":
                    for i in range(tpl["repeat"]):
                        if not state.running:
                            break
                        
                        # Calculate absolute coordinates if relative
                        click_x = tpl["x"]
                        click_y = tpl["y"]
                        
                        if tpl.get("is_relative", False):
                            # Get window info and convert relative to absolute
                            try:
                                from core.relative_capture import RelativeCoordinateCapture
                                game_hwnd = tpl.get("game_hwnd")
                                window_title = tpl.get("window_title")
                                if not game_hwnd and window_title:
                                    game_hwnd = RelativeCoordinateCapture.find_window_by_title(window_title)
                                if game_hwnd:
                                    # Temporarily set game_hwnd to get offset
                                    old_hwnd = state.game_hwnd
                                    state.game_hwnd = game_hwnd
                                    win_info = RelativeCoordinateCapture.get_game_window_info()
                                    state.game_hwnd = old_hwnd
                                    
                                    if win_info:
                                        click_x = win_info['client_left'] + tpl["x"]
                                        click_y = win_info['client_top'] + tpl["y"]
                                        safe_print(f"📍 Relative→Absolute: ({tpl['x']}, {tpl['y']}) + ({win_info['client_left']}, {win_info['client_top']}) = ({click_x}, {click_y})")
                            except Exception as e:
                                safe_print(f"⚠️ Lỗi tính tọa độ relative: {e}")
                                # Fallback to direct coordinates
                                pass
                        
                        click_type = tpl.get("click_type", "single")
                        if click_type == "double":
                            double_click(click_x, click_y)
                            safe_print(f"🖱️ Double-clicked coordinate {tpl['path']}")
                        elif click_type == "hold":
                            click_and_hold(click_x, click_y)
                            safe_print(f"🖱️ Click-and-hold coordinate {tpl['path']}")
                        else:
                            click(click_x, click_y)
                            safe_print(f"🖱️ Clicked coordinate {tpl['path']}")

                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0)  # No gap between repeats

                elif tpl["type"] == "key":
                    for i in range(tpl["repeat"]):
                        if not state.running:
                            break
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
                            time.sleep(0)  # No gap between repeats

                if state.running:
                    time.sleep(tpl.get("delay", state.click_delay))

            loop_count += 1
            if state.running and (state.infinite_loop or loop_count < state.process_loops):
                safe_print(f"🔄 Loop {_format_loop_label(loop_count)} completed")
            elif last_step_failed:
                # No more loops left and last step failed
                safe_print(f"❌ Hết vòng lặp, lần cuối cùng bước cuối không tìm được hình. Scenario thất bại.")
                run_result = "failed"
                break  # Exit main loop

        if not state.running:
            run_result = "stopped"
    except Exception as e:
        run_result = "failed"
        safe_print(f"[AUTOCLICK THREAD ERROR] {e}")
        import traceback

        safe_print(traceback.format_exc())
        if state.UI.status_label:
            state.UI.status_label.config(text=f"⚠️ Lỗi AutoClick: {e}")
    finally:
        state.last_run_result = run_result
        state.running = False
        safe_print(f"🟢 [THREAD] find_and_click thread ended (result={run_result})")
        if not queue_mode and state.UI.status_label:
            if run_result == "stopped":
                set_status("⏹ AutoClick đã dừng.")
            elif run_result == "failed":
                set_status("❌ Kịch bản thất bại.")
            else:
                set_status("✅ AutoClick đã hoàn tất!")
    return run_result


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
    state.last_run_result = None
    safe_print("🔵 [DEBUG] running=True, starting find_and_click thread...")
    set_status("▶ AutoClick đang chạy...")
    threading.Thread(target=find_and_click, daemon=True).start()


def stop_clicking(event=None):
    state.running = False
    state.queue_stopped = True
    set_status("⏹ AutoClick đã dừng (toàn bộ kịch bản).")


def smart_start(event=None):
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
    set_status(f"▶ Chạy kịch bản 1/{len(state.scenario_metadata)}...")

    scenario_completed = [False]
    scenario_result = [None]

    def run_next_scenario():
        root = state.UI.root

        if state.queue_stopped:
            set_status(
                f"⏹ Đã dừng toàn bộ kịch bản (đang ở {state.current_scenario_index + 1}/{len(state.scenario_metadata)})."
            )
            state.running = False
            return

        if state.current_scenario_index >= len(state.scenario_metadata):
            set_status(f"✅ Đã hoàn tất tất cả {len(state.scenario_metadata)} kịch bản!")
            state.running = False
            return

        metadata = state.scenario_metadata[state.current_scenario_index]
        file_path = metadata["file_path"]

        try:
            state.process_loops = max(1, int(metadata.get("process_loops", 1) or 1))
            state.infinite_loop = metadata.get("infinite_loop", False)
            state.click_delay = metadata.get("click_delay", 1.0)

            state.templates = []
            for tpl in metadata.get("templates", []):
                state.templates.append(tpl.copy())

            update_history()
            set_status(
                f"▶ Chạy kịch bản {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: {os.path.basename(file_path)}"
            )
            safe_print(f"🔵 [DEBUG] Starting scenario {state.current_scenario_index + 1}/{len(state.scenario_metadata)}")

            scenario_completed[0] = False
            scenario_result[0] = None
            state.running = True
            state.last_run_result = None

            def run_scenario_thread():
                try:
                    scenario_result[0] = find_and_click(queue_mode=True)
                finally:
                    scenario_completed[0] = True

            threading.Thread(target=run_scenario_thread, daemon=True).start()

            def check_and_run_next():
                if state.queue_stopped:
                    safe_print(
                        f"🔵 [DEBUG] Queue stopped by user, halting at scenario {state.current_scenario_index + 1}"
                    )
                    set_status(
                        f"⏹ Đã dừng toàn bộ kịch bản tại {state.current_scenario_index + 1}/{len(state.scenario_metadata)}."
                    )
                    state.running = False
                    return
                if scenario_completed[0]:
                    result = scenario_result[0] or state.last_run_result or "failed"
                    if result == "completed":
                        safe_print(
                            f"🔵 [DEBUG] Scenario {state.current_scenario_index + 1} completed, moving to next"
                        )
                        state.current_scenario_index += 1
                        root.after(500, run_next_scenario)
                    elif result == "failed":
                        safe_print(
                            f"🔵 [DEBUG] Scenario {state.current_scenario_index + 1} failed, stopping queue"
                        )
                        set_status(
                            f"❌ Kịch bản thất bại tại {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: "
                            f"{os.path.basename(file_path)}"
                        )
                        state.running = False
                    else:
                        safe_print(f"🔵 [DEBUG] Scenario {state.current_scenario_index + 1} stopped")
                        set_status(
                            f"⏹ Đã dừng kịch bản tại {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: "
                            f"{os.path.basename(file_path)}"
                        )
                        state.running = False
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
