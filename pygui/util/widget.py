import tkinter as tk

from PIL import Image, ImageTk


def create_button_icon(parent, image_path, height=20, width=None, command=None):
    width = height if width is None else width
    
    img = Image.open(image_path)
    img = img.resize((width, height), Image.ANTIALIAS)
    icon = ImageTk.PhotoImage(img)
    
    b = tk.Button(parent)
    b.icon = icon
    b.config(image=icon,
             width=width,
             height=height,
             command=command)
    return b
