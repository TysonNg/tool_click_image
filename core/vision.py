from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import pyautogui

from core import state


DEFAULT_THRESHOLD = 0.80
DEFAULT_BLUR_KSIZE = (3, 3)
DEFAULT_SCALE_START = 0.70
DEFAULT_SCALE_END = 1.30
DEFAULT_SCALE_STEP = 0.05


@dataclass
class MatchResult:
    found: bool
    score: float
    scale: float
    template_index: int
    template_name: str
    method: str
    top_left_x: int
    top_left_y: int
    center_x: int
    center_y: int
    matched_w: int
    matched_h: int


def screenshot_rgb() -> np.ndarray:
    screenshot = pyautogui.screenshot()
    return np.array(screenshot)


def capture_screen_gray() -> np.ndarray:
    screenshot = screenshot_rgb()
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)


def preprocess_to_gray_blur(
    image: np.ndarray,
    blur_ksize: tuple[int, int] = DEFAULT_BLUR_KSIZE,
    blur_sigma: float = 0.0,
) -> np.ndarray:
    if image.ndim == 2:
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return cv2.GaussianBlur(gray, blur_ksize, blur_sigma)


def scale_values(
    start: float = DEFAULT_SCALE_START,
    end: float = DEFAULT_SCALE_END,
    step: float = DEFAULT_SCALE_STEP,
) -> list[float]:
    values = []
    current = start
    while current <= end + 1e-9:
        values.append(round(current, 4))
        current += step
    return values


def _default_scales() -> list[float]:
    if getattr(state, "precision_mode", True):
        return scale_values(0.85, 1.15, 0.05)
    return scale_values(DEFAULT_SCALE_START, DEFAULT_SCALE_END, DEFAULT_SCALE_STEP)


def resize_template(
    template: np.ndarray,
    scale: float,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray | None]:
    if scale == 1.0:
        return template, mask

    height, width = template.shape[:2]
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC

    resized_template = cv2.resize(template, (new_width, new_height), interpolation=interpolation)
    resized_mask = None
    if mask is not None:
        resized_mask = cv2.resize(mask, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
        _, resized_mask = cv2.threshold(resized_mask, 127, 255, cv2.THRESH_BINARY)
    return resized_template, resized_mask


def match_single(
    search_img: np.ndarray,
    template: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[float, tuple[int, int], str]:
    method = cv2.TM_CCOEFF_NORMED
    if mask is None:
        result = cv2.matchTemplate(search_img, template, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return float(max_val), max_loc, "TM_CCOEFF_NORMED"

    masked_method = cv2.TM_CCORR_NORMED
    result = cv2.matchTemplate(search_img, template, masked_method, mask=mask)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return float(max_val), max_loc, "TM_CCORR_NORMED(masked)"


def _build_match_result(
    score: float,
    scale: float,
    template_index: int,
    template_name: str,
    method: str,
    top_left_x: int,
    top_left_y: int,
    matched_w: int,
    matched_h: int,
    threshold: float,
) -> MatchResult:
    center_x = top_left_x + matched_w // 2
    center_y = top_left_y + matched_h // 2
    return MatchResult(
        found=score >= threshold,
        score=score,
        scale=scale,
        template_index=template_index,
        template_name=template_name,
        method=method,
        top_left_x=top_left_x,
        top_left_y=top_left_y,
        center_x=center_x,
        center_y=center_y,
        matched_w=matched_w,
        matched_h=matched_h,
    )


def find_best_match(
    screen_gray: np.ndarray,
    templates: list[np.ndarray],
    threshold: float = DEFAULT_THRESHOLD,
    scales: list[float] | None = None,
    template_names: list[str] | None = None,
    masks: list[np.ndarray | None] | None = None,
) -> MatchResult:
    if not templates:
        return _build_match_result(
            score=-1.0,
            scale=1.0,
            template_index=-1,
            template_name="",
            method="",
            top_left_x=0,
            top_left_y=0,
            matched_w=0,
            matched_h=0,
            threshold=threshold,
        )

    if scales is None:
        scales = _default_scales()

    processed_screen = preprocess_to_gray_blur(screen_gray)
    screen_h, screen_w = processed_screen.shape[:2]

    if template_names is None:
        template_names = [f"template_{idx}" for idx in range(len(templates))]
    if masks is None:
        masks = [None] * len(templates)

    best_result: MatchResult | None = None

    for template_index, raw_template in enumerate(templates):
        raw_mask = masks[template_index] if template_index < len(masks) else None
        template_name = template_names[template_index] if template_index < len(template_names) else f"template_{template_index}"

        for scale in scales:
            resized_template, resized_mask = resize_template(raw_template, scale, raw_mask)
            matched_h, matched_w = resized_template.shape[:2]
            if matched_w > screen_w or matched_h > screen_h:
                continue
            if matched_w < 4 or matched_h < 4:
                continue

            processed_template = preprocess_to_gray_blur(resized_template)
            score, max_loc, method_name = match_single(processed_screen, processed_template, resized_mask)
            result = _build_match_result(
                score=score,
                scale=scale,
                template_index=template_index,
                template_name=template_name,
                method=method_name,
                top_left_x=max_loc[0],
                top_left_y=max_loc[1],
                matched_w=matched_w,
                matched_h=matched_h,
                threshold=threshold,
            )
            if best_result is None or result.score > best_result.score:
                best_result = result

    if best_result is not None:
        return best_result

    return _build_match_result(
        score=-1.0,
        scale=1.0,
        template_index=-1,
        template_name="",
        method="",
        top_left_x=0,
        top_left_y=0,
        matched_w=0,
        matched_h=0,
        threshold=threshold,
    )


def multi_scale_match(
    screenshot: np.ndarray,
    template: np.ndarray,
    scales: list[float] | None = None,
) -> tuple[np.ndarray, float, int, int]:
    if scales is None:
        scales = _default_scales()

    processed_screen = preprocess_to_gray_blur(screenshot)
    screen_h, screen_w = processed_screen.shape[:2]
    best_res = None
    best_score = -1.0
    best_scale = 1.0
    best_width = template.shape[1]
    best_height = template.shape[0]

    for scale in scales:
        resized_template, _ = resize_template(template, scale)
        matched_h, matched_w = resized_template.shape[:2]
        if matched_w > screen_w or matched_h > screen_h:
            continue
        if matched_w < 4 or matched_h < 4:
            continue

        processed_template = preprocess_to_gray_blur(resized_template)
        try:
            result = cv2.matchTemplate(processed_screen, processed_template, cv2.TM_CCOEFF_NORMED)
        except cv2.error:
            continue
        score = float(np.max(result)) if result.size else -1.0
        if score > best_score:
            best_score = score
            best_res = result
            best_scale = scale
            best_width = matched_w
            best_height = matched_h

    if best_res is None:
        processed_template = preprocess_to_gray_blur(template)
        best_res = cv2.matchTemplate(processed_screen, processed_template, cv2.TM_CCOEFF_NORMED)
    return best_res, best_scale, best_width, best_height


def _sanitize_region(region, screen_width: int, screen_height: int) -> dict[str, int] | None:
    if not region:
        return None
    try:
        x1 = int(region["x1"])
        y1 = int(region["y1"])
        x2 = int(region["x2"])
        y2 = int(region["y2"])
    except (KeyError, TypeError, ValueError):
        return None
    x1 = max(0, min(x1, screen_width - 1))
    y1 = max(0, min(y1, screen_height - 1))
    x2 = max(x1 + 1, min(x2, screen_width))
    y2 = max(y1 + 1, min(y2, screen_height))
    if x2 <= x1 or y2 <= y1:
        return None
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def get_search_region_screenshot(full_screenshot: np.ndarray, template=None, region_override=None):
    screen_height, screen_width = full_screenshot.shape[:2]
    region_source = "full"
    region = None
    if region_override:
        region = region_override
        region_source = "override"
    elif template and template.get("search_region_enabled"):
        region = template.get("search_region")
        region_source = "template"
    elif state.search_region_enabled:
        region = state.search_region
        region_source = "global"

    region = _sanitize_region(region, screen_width, screen_height)
    if region is None:
        return full_screenshot, (0, 0), "full"

    x1 = region["x1"]
    y1 = region["y1"]
    x2 = region["x2"]
    y2 = region["y2"]
    cropped = full_screenshot[y1:y2, x1:x2]
    return cropped, (x1, y1), region_source


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


def imread_unicode(path, flags=cv2.IMREAD_GRAYSCALE):
    with open(path, "rb") as stream:
        bytes_array = bytearray(stream.read())
    numpy_array = np.asarray(bytes_array, dtype=np.uint8)
    return cv2.imdecode(numpy_array, flags)
