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
