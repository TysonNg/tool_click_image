import tkinter as tk
from core import state


def on_window_configure(event=None):
    try:
        root = state.UI.root
        root.minsize(700, 500)

        current_width = root.winfo_width()
        current_height = root.winfo_height()

        if current_width > 1 and current_height > 1:
            state.UI.status_label.config(wraplength=max(300, current_width - 100))

            scale_factor = current_width / 1000.0
            scale_factor = max(0.7, min(1.3, scale_factor))

            try:
                _scale_all_elements(root, scale_factor)
            except:
                pass
    except:
        pass


def _scale_all_elements(widget, scale_factor):
    try:
        if isinstance(widget, tk.Button) and hasattr(widget, '_original_padx'):
            new_padx = max(3, int(widget._original_padx * scale_factor))
            new_pady = max(2, int(widget._original_pady * scale_factor))
            widget.config(padx=new_padx, pady=new_pady)
            if hasattr(widget, '_base_font_size'):
                new_size = max(7, int(widget._base_font_size * scale_factor))
                widget.config(font=("Segoe UI", new_size, "bold"))

        elif isinstance(widget, tk.Label):
            try:
                current_font = widget.cget("font")
                if current_font and isinstance(current_font, tuple) and len(current_font) > 1:
                    base_size = int(current_font[1])
                    new_size = max(7, int(base_size * scale_factor))
                    widget.config(font=(current_font[0], new_size) + current_font[2:])
            except:
                pass

        elif isinstance(widget, tk.Frame):
            try:
                padx = widget.cget("padx")
                pady = widget.cget("pady")
                if padx and pady:
                    new_padx = max(4, int(int(padx) * scale_factor))
                    new_pady = max(4, int(int(pady) * scale_factor))
                    widget.config(padx=new_padx, pady=new_pady)
            except:
                pass

        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                _scale_all_elements(child, scale_factor)
    except:
        pass
