import os
import sys

import tkinter as tk
import warnings

from PIL import Image, ImageTk
from _tkinter import TclError

SRCDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)
    
from widget.ui import ToolTip


def add_menu_command_safe(menu, label, command, **kwargs):
    labels = get_menu_labels(menu)
    if label in labels:
        warnings.warn(f"Tried adding {label} option to menubar, but it was already defined.")
    else:
        menu.add_command(label=label, command=command, **kwargs)


def create_button_icon(parent, image_path, height=20, width=None, command=None, tooltip=None):
    width = height if width is None else width
    
    img = Image.open(image_path)
    img = img.resize((width, height), Image.ANTIALIAS)
    icon = ImageTk.PhotoImage(img)
    
    b = tk.Button(parent, command=command)
    b.icon = icon
    b.config(image=icon,
             width=width,
             height=height)

    if tooltip is not None:
        b.tooltip = ToolTip(b, text=tooltip)
    return b


def find_widget_child_instance(widget, class_):
    if isinstance(widget, class_):
        return widget

    try:
        for child in widget.children.values():
            if isinstance(child, class_):
                return child
            else:
                out = find_widget_child_instance(child, class_)
                if out is not None:
                    return out
    except AttributeError:
        return None


def find_widget_parent_instance(widget, class_):
    if isinstance(widget, class_):
        return widget

    try:
        parent = widget.parent
        if isinstance(parent, class_):
            return parent
        else:
            out = find_widget_parent_instance(parent, class_)
            if out is not None:
                return out
    except AttributeError:
        return None


def get_menu_labels(menu):
    last = menu.index("end")
    labels = []
    if last is not None:
        for index in range(last+1):
            try:
                labels.append(menu.entrycget(index, "label"))
            except TclError:
                pass
    return labels
