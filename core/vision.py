import cv2
import numpy as np
import pyautogui
from core import state


def capture_screen_gray():
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)


def multi_scale_match(screenshot, template, scales=None):
    if scales is None:
        scales = [1.0, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15, 0.8, 1.2, 0.75, 1.25, 1.35, 1.5]
    best_res = None
    best_score = -1.0
    best_scale = 1.0
    best_tpl = template
    sh, sw = screenshot.shape[:2]
    for s in scales:
        if s == 1.0:
            tpl = template
        else:
            nw = max(4, int(template.shape[1] * s))
            nh = max(4, int(template.shape[0] * s))
            if nw >= sw or nh >= sh:
                continue
            tpl = cv2.resize(template, (nw, nh),
                             interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
        try:
            res = cv2.matchTemplate(screenshot, tpl, cv2.TM_CCOEFF_NORMED)
        except cv2.error:
            continue
        score = float(np.max(res)) if res.size else -1.0
        if score > best_score:
            best_score = score
            best_res = res
            best_scale = s
            best_tpl = tpl
    if best_res is None:
        best_res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        best_tpl = template
    return best_res, best_scale, best_tpl.shape[1], best_tpl.shape[0]


def get_search_region_screenshot(full_screenshot):
    if not state.search_region_enabled:
        return full_screenshot, (0, 0)
    x1 = state.search_region["x1"]
    y1 = state.search_region["y1"]
    x2 = state.search_region["x2"]
    y2 = state.search_region["y2"]
    cropped = full_screenshot[y1:y2, x1:x2]
    return cropped, (x1, y1)


def filter_close_points(points, min_dist=20):
    filtered = []
    for pt in points:
        if not filtered:
            filtered.append(pt)
        else:
            too_close = False
            for f_pt in filtered:
                if abs(pt[0] - f_pt[0]) < min_dist and abs(pt[1] - f_pt[1]) < min_dist:
                    too_close = True
                    break
            if not too_close:
                filtered.append(pt)
    return filtered


def imread_unicode(path):
    with open(path, "rb") as stream:
        bytes_array = bytearray(stream.read())
    numpy_array = np.asarray(bytes_array, dtype=np.uint8)
    img = cv2.imdecode(numpy_array, cv2.IMREAD_GRAYSCALE)
    return img
