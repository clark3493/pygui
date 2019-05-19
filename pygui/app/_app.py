import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(LOCAL_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from icon import *


class AbstractApplication(tk.Frame):

    def __init__(self, parent=None, title="PyGUI", icon_path=PYTHON_ICON_PATH, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.set_title(title)
        self.set_icon(icon_path)

        self.addins = {}

        self.configure_application()

    def configure_application(self):
        raise NotImplementedError("GUI components must be added here.")

    def exit(self):
        root = self.winfo_toplevel()
        root.destroy()

    def set_title(self, title):
        root = self.winfo_toplevel()
        root.title(title)

    def set_icon(self, path):
        img = tk.Image("photo", file=path)
        root = self.winfo_toplevel()
        root.tk.call('wm', 'iconphoto', root._w, img)
