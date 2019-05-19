import os
import sys

import tkinter as tk

from PIL import Image, ImageTk

SRCDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)
    
from widget.ui import ToolTip


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
                return find_widget_child_instance(child, class_)
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
            return find_widget_parent_instance(parent, class_)
    except AttributeError:
        return None
