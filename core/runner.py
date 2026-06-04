import os
import time
import threading

import pyautogui

from core import state
from core.input import click, click_and_hold, double_click, press_key
from core.state import set_status
from core.vision import capture_screen_gray, find_best_match, get_search_region_screenshot
from utils import safe_print


FINAL_IMAGE_GRACE_SECONDS = 3


def _format_loop_label(loop_index):
    if state.infinite_loop:
        return f"{loop_index}/âˆž"
    return f"{loop_index}/{state.process_loops}"


def _resolve_click_point(tpl, matched_w, matched_h):
    click_mode = tpl.get("click_point_mode", "center")
    base_w = max(1, int(tpl.get("w", matched_w) or matched_w))
    base_h = max(1, int(tpl.get("h", matched_h) or matched_h))

    if click_mode == "custom":
        raw_click_x = int(tpl.get("click_x", base_w // 2))
        raw_click_y = int(tpl.get("click_y", base_h // 2))
        if 0 <= raw_click_x < base_w and 0 <= raw_click_y < base_h:
            scaled_click_x = int(round(raw_click_x * matched_w / base_w))
            scaled_click_y = int(round(raw_click_y * matched_h / base_h))
            return click_mode, scaled_click_x, scaled_click_y

        safe_print(
            f"âš ï¸ Invalid custom click point for {tpl['path']}: "
            f"({raw_click_x}, {raw_click_y}) outside {base_w}x{base_h}. Falling back to center."
        )

    return "center", matched_w // 2, matched_h // 2


def _perform_click_action(tpl, click_x, click_y):
    click_type = tpl.get("click_type", "single")
    if click_type == "double":
        double_click(click_x, click_y)
        safe_print(f"ðŸ–±ï¸ Double-clicked {tpl['path']} at: ({click_x}, {click_y})")
    elif click_type == "hold":
        click_and_hold(click_x, click_y)
        safe_print(f"ðŸ–±ï¸ Click-and-hold {tpl['path']} at: ({click_x}, {click_y})")
    else:
        click(click_x, click_y)
        safe_print(f"ðŸ–±ï¸ Clicked {tpl['path']} at: ({click_x}, {click_y})")


def find_and_click(queue_mode=False):
    safe_print("ðŸŸ¢ [THREAD] find_and_click thread started")
    run_result = "completed"
    try:
        loop_count = 0
        while state.running and (state.infinite_loop or loop_count < state.process_loops):
            safe_print(f"ðŸŸ¢ [THREAD] Loop {_format_loop_label(loop_count + 1)}")
            total_templates = len(state.templates)
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
                    elif is_last_step:
                        max_attempts = FINAL_IMAGE_GRACE_SECONDS * 10
                    else:
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

                        match = find_best_match(
                            screenshot,
                            candidate_images,
                            threshold=threshold,
                            template_names=candidate_names,
                            masks=candidate_masks,
                        )

                        if match.found:
                            safe_print(
                                f"âœ… Best match for {tpl['path']} => {match.template_name} "
                                f"(score: {match.score:.3f}, threshold: {threshold}, scale: {match.scale:.2f}x, method: {match.method})"
                            )
                            safe_print(
                                f"âœ… Match origin: ({match.top_left_x}, {match.top_left_y}), "
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
                                    f"âœ… Final click point: ({click_x}, {click_y}) "
                                    f"[click_mode={click_mode}, match_origin=({match.top_left_x}, {match.top_left_y})]"
                                )
                                _perform_click_action(tpl, click_x, click_y)

                                click_delay_after = tpl.get("click_delay", 0.5)
                                time.sleep(click_delay_after)
                                count += 1
                                if count < tpl["repeat"]:
                                    time.sleep(0.1)
                        else:
                            if wait_until_found or is_last_step:
                                attempt += 1
                                if attempt % 10 == 0:
                                    if wait_until_found:
                                        safe_print(
                                            f"â³ Chá» tÃ¬m {tpl['path']}... ({attempt // 10}s) "
                                            f"[best_score={match.score:.3f}, threshold={threshold}, scale={match.scale:.2f}x, template={match.template_name}]"
                                        )
                                    else:
                                        safe_print(
                                            f"â³ BÆ°á»›c cuá»‘i chÆ°a xuáº¥t hiá»‡n {tpl['path']}... ({attempt // 10}s/{FINAL_IMAGE_GRACE_SECONDS}s) "
                                            f"[best_score={match.score:.3f}, threshold={threshold}, scale={match.scale:.2f}x, template={match.template_name}]"
                                        )
                                time.sleep(0.1)
                            else:
                                attempt = max_attempts

                    if not found and wait_until_found:
                        if wait_timeout == -1:
                            safe_print(f"âš ï¸ Timeout: KhÃ´ng tÃ¬m Ä‘Æ°á»£c {tpl['path']} (chá» vÃ´ cá»±c)")
                        else:
                            safe_print(f"âš ï¸ Timeout: KhÃ´ng tÃ¬m Ä‘Æ°á»£c {tpl['path']} sau {wait_timeout} giÃ¢y")
                    elif not found:
                        safe_print(f"âŒ KhÃ´ng tÃ¬m Ä‘Æ°á»£c {tpl['path']}")
                        if is_last_step:
                            run_result = "failed"
                            return run_result

                elif tpl["type"] == "coord":
                    for i in range(tpl["repeat"]):
                        if not state.running:
                            break
                        click_type = tpl.get("click_type", "single")
                        if click_type == "double":
                            double_click(tpl["x"], tpl["y"])
                            safe_print(f"ðŸ–±ï¸ Double-clicked coordinate {tpl['path']}")
                        elif click_type == "hold":
                            click_and_hold(tpl["x"], tpl["y"])
                            safe_print(f"ðŸ–±ï¸ Click-and-hold coordinate {tpl['path']}")
                        else:
                            click(tpl["x"], tpl["y"])
                            safe_print(f"ðŸ–±ï¸ Clicked coordinate {tpl['path']}")

                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0.1)

                elif tpl["type"] == "key":
                    for i in range(tpl["repeat"]):
                        if not state.running:
                            break
                        key_type = tpl.get("key_type", "press")
                        if key_type == "hold":
                            pyautogui.keyDown(tpl["key"])
                            time.sleep(0.2)
                            pyautogui.keyUp(tpl["key"])
                            safe_print(f"âŒ¨ï¸ Held key: {tpl['key']}")
                        else:
                            press_key(tpl["key"])
                            safe_print(f"âŒ¨ï¸ Pressed key: {tpl['key']}")

                        delay_after = tpl.get("delay_after", 0.5)
                        time.sleep(delay_after)
                        if i < tpl["repeat"] - 1:
                            time.sleep(0.1)

                if state.running:
                    time.sleep(tpl.get("delay", state.click_delay))

            loop_count += 1
            if state.running and (state.infinite_loop or loop_count < state.process_loops):
                safe_print(f"ðŸ”„ Loop {_format_loop_label(loop_count)} completed")

        if not state.running:
            run_result = "stopped"
    except Exception as e:
        run_result = "failed"
        safe_print(f"[AUTOCLICK THREAD ERROR] {e}")
        import traceback

        safe_print(traceback.format_exc())
        if state.UI.status_label:
            state.UI.status_label.config(text=f"âš ï¸ Lá»—i AutoClick: {e}")
    finally:
        state.last_run_result = run_result
        state.running = False
        safe_print(f"ðŸŸ¢ [THREAD] find_and_click thread ended (result={run_result})")
        if not queue_mode and state.UI.status_label:
            if run_result == "stopped":
                set_status("â¹ AutoClick Ä‘Ã£ dá»«ng.")
            elif run_result == "failed":
                set_status("âŒ Ká»‹ch báº£n tháº¥t báº¡i.")
            else:
                set_status("âœ… AutoClick Ä‘Ã£ hoÃ n táº¥t!")
    return run_result


def start_clicking():
    safe_print("ðŸ”µ [DEBUG] start_clicking() called")

    if state.scenario_queue:
        safe_print("ðŸ”µ [DEBUG] Running scenario queue...")
        run_scenario_queue()
        return

    has_templates = len(state.templates) > 0
    safe_print(f"ðŸ”µ [DEBUG] has_templates={has_templates}, templates count={len(state.templates)}")

    if not has_templates:
        msg = "âš ï¸ ChÆ°a thÃªm áº£nh/tá»a Ä‘á»™ nÃ o!"
        state.UI.status_label.config(text=msg)
        safe_print(f"ðŸ”µ [DEBUG] {msg}")
        return

    state.running = True
    state.last_run_result = None
    safe_print("ðŸ”µ [DEBUG] running=True, starting find_and_click thread...")
    set_status("âº AutoClick Ä‘ang cháº¡y...")
    threading.Thread(target=find_and_click, daemon=True).start()


def stop_clicking(event=None):
    state.running = False
    state.queue_stopped = True
    set_status("â¹ AutoClick Ä‘Ã£ dá»«ng (toÃ n bá»™ ká»‹ch báº£n).")


def smart_start(event=None):
    runner = getattr(state, "run_library_selection", None)
    if runner and runner(silent_if_empty=True):
        return
    start_clicking()


def run_scenario_queue():
    from scenario.templates import update_history

    if not state.scenario_metadata:
        state.UI.status_label.config(text="âš ï¸ ChÆ°a táº£i ká»‹ch báº£n nÃ o!")
        return

    state.current_scenario_index = 0
    state.queue_stopped = False
    set_status(f"âº Cháº¡y ká»‹ch báº£n 1/{len(state.scenario_metadata)}...")

    scenario_completed = [False]
    scenario_result = [None]

    def run_next_scenario():
        root = state.UI.root

        if state.queue_stopped:
            set_status(
                f"â¹ ÄÃ£ dá»«ng toÃ n bá»™ ká»‹ch báº£n (Ä‘ang á»Ÿ {state.current_scenario_index + 1}/{len(state.scenario_metadata)})."
            )
            state.running = False
            return

        if state.current_scenario_index >= len(state.scenario_metadata):
            set_status(f"âœ… ÄÃ£ hoÃ n táº¥t táº¥t cáº£ {len(state.scenario_metadata)} ká»‹ch báº£n!")
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
                f"âº Cháº¡y ká»‹ch báº£n {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: {os.path.basename(file_path)}"
            )
            safe_print(f"ðŸ”µ [DEBUG] Starting scenario {state.current_scenario_index + 1}/{len(state.scenario_metadata)}")

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
                        f"ðŸ”µ [DEBUG] Queue stopped by user, halting at scenario {state.current_scenario_index + 1}"
                    )
                    set_status(
                        f"â¹ ÄÃ£ dá»«ng toÃ n bá»™ ká»‹ch báº£n táº¡i {state.current_scenario_index + 1}/{len(state.scenario_metadata)}."
                    )
                    state.running = False
                    return
                if scenario_completed[0]:
                    result = scenario_result[0] or state.last_run_result or "failed"
                    if result == "completed":
                        safe_print(
                            f"ðŸ”µ [DEBUG] Scenario {state.current_scenario_index + 1} completed, moving to next"
                        )
                        state.current_scenario_index += 1
                        root.after(500, run_next_scenario)
                    elif result == "failed":
                        safe_print(
                            f"ðŸ”µ [DEBUG] Scenario {state.current_scenario_index + 1} failed, stopping queue"
                        )
                        set_status(
                            f"âŒ Ká»‹ch báº£n tháº¥t báº¡i táº¡i {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: "
                            f"{os.path.basename(file_path)}"
                        )
                        state.running = False
                    else:
                        safe_print(f"ðŸ”µ [DEBUG] Scenario {state.current_scenario_index + 1} stopped")
                        set_status(
                            f"â¹ ÄÃ£ dá»«ng ká»‹ch báº£n táº¡i {state.current_scenario_index + 1}/{len(state.scenario_metadata)}: "
                            f"{os.path.basename(file_path)}"
                        )
                        state.running = False
                else:
                    root.after(200, check_and_run_next)

            root.after(200, check_and_run_next)

        except Exception as e:
            safe_print(f"âš ï¸ Lá»—i táº£i ká»‹ch báº£n: {e}")
            import traceback

            safe_print(traceback.format_exc())
            state.current_scenario_index += 1
            root.after(500, run_next_scenario)

    run_next_scenario()
