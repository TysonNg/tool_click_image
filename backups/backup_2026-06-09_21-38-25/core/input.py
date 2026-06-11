import time
import math
import random
import win32api
import win32con
import keyboard
from core import state
from utils import safe_print


def human_move(x, y, duration=None):
    start_x, start_y = win32api.GetCursorPos()
    dist = math.hypot(x - start_x, y - start_y)
    if dist < 1:
        return
    if duration is None:
        duration = random.uniform(0.18, 0.38) + dist / 3500.0
    cx1 = start_x + (x - start_x) * random.uniform(0.2, 0.4) + random.randint(-40, 40)
    cy1 = start_y + (y - start_y) * random.uniform(0.2, 0.4) + random.randint(-40, 40)
    cx2 = start_x + (x - start_x) * random.uniform(0.6, 0.8) + random.randint(-40, 40)
    cy2 = start_y + (y - start_y) * random.uniform(0.6, 0.8) + random.randint(-40, 40)
    steps = max(25, int(duration * 120))
    for i in range(1, steps + 1):
        t = i / steps
        t = 0.5 - 0.5 * math.cos(math.pi * t)
        mt = 1 - t
        bx = mt**3 * start_x + 3*mt**2*t*cx1 + 3*mt*t**2*cx2 + t**3 * x
        by = mt**3 * start_y + 3*mt**2*t*cy1 + 3*mt*t**2*cy2 + t**3 * y
        bx += random.uniform(-0.6, 0.6)
        by += random.uniform(-0.6, 0.6)
        win32api.SetCursorPos((int(bx), int(by)))
        time.sleep(duration / steps)


def click(x, y):
    if state.human_click_mode:
        jx = x + random.randint(-3, 3)
        jy = y + random.randint(-3, 3)
        human_move(jx, jy)
        time.sleep(random.uniform(0.04, 0.12))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(random.uniform(0.05, 0.13))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def double_click(x, y, delay=0.1):
    click(x, y)
    if state.human_click_mode:
        time.sleep(delay * random.uniform(0.7, 1.3))
    else:
        time.sleep(delay)
    click(x, y)


def click_and_hold(x, y, hold_time=0.2):
    if state.human_click_mode:
        jx = x + random.randint(-3, 3)
        jy = y + random.randint(-3, 3)
        human_move(jx, jy)
        time.sleep(random.uniform(0.04, 0.12))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(hold_time * random.uniform(0.85, 1.15))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(hold_time)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def press_key(key_name):
    try:
        keyboard.press(key_name)
        keyboard.release(key_name)
        safe_print(f"⌨️ Pressed key: {key_name}")
    except Exception as e:
        safe_print(f"⚠️ Error pressing key {key_name}: {e}")
