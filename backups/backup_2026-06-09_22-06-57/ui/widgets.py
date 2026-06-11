import tkinter as tk
from ui.theme import *


def get_responsive_font(root, base_size, style="normal"):
    try:
        scale_factor = max(0.8, min(1.2, root.winfo_width() / 1000.0))
        size = max(7, int(base_size * scale_factor))
        if style == "bold":
            return ("Segoe UI", size, "bold")
        else:
            return ("Segoe UI", size)
    except:
        if style == "bold":
            return ("Segoe UI", base_size, "bold")
        else:
            return ("Segoe UI", base_size)


def create_btn(parent, text, command, bg=PKM_RED, fg=PKM_WHITE,
               hover_bg=None, font=("Segoe UI", 9, "bold"), **kwargs):
    _hover = hover_bg or bg
    btn = tk.Button(
        parent, text=text, command=command, font=font,
        bg=bg, fg=fg, activebackground=_hover, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2", padx=6, pady=3,
        highlightthickness=2, highlightbackground=PKM_BORDER,
        highlightcolor=PKM_YELLOW, **kwargs
    )

    def on_enter(e):
        if btn["state"] != "disabled":
            btn.config(bg=_hover)

    def on_leave(e):
        if btn["state"] != "disabled":
            btn.config(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    btn._original_padx = 6
    btn._original_pady = 3
    btn._original_font = font
    btn._base_font_size = font[1] if len(font) > 1 else 9
    btn._bg = bg
    btn._hover_bg = _hover

    return btn


def create_card(parent, title, title_color=PKM_YELLOW):
    from core.state import UI
    border = tk.Frame(parent, bg=title_color, bd=0)
    border.pack(fill="both", expand=True, pady=(0, 6), padx=0)

    title_bar = tk.Frame(border, bg=PKM_BG_CARD, pady=4, padx=6)
    title_bar.pack(fill="x", side="top")

    dot_canvas = tk.Canvas(title_bar, width=14, height=14,
                           bg=PKM_BG_CARD, highlightthickness=0)
    dot_canvas.pack(side="left", padx=(0, 6))
    dot_canvas.create_oval(1, 1, 13, 13, fill=title_color, outline=PKM_WHITE, width=2)
    dot_canvas.create_line(1, 7, 13, 7, fill=PKM_WHITE, width=2)

    title_font_size = 10
    try:
        if UI.root and UI.root.winfo_width() < 900:
            title_font_size = 8
        elif UI.root and UI.root.winfo_width() < 1200:
            title_font_size = 9
    except:
        pass

    title_label = tk.Label(title_bar, text=title, font=("Segoe UI", title_font_size, "bold"),
                           bg=PKM_BG_CARD, fg=title_color)
    title_label.pack(side="left")
    title_label._base_size = 10
    title_label._title_color = title_color

    tk.Frame(border, bg=title_color, height=2).pack(fill="x")

    inner = tk.Frame(border, bg=PKM_BG_CARD, padx=0, pady=0)
    inner.pack(fill="both", expand=True)
    inner._original_padx = 0
    inner._original_pady = 0

    return inner
