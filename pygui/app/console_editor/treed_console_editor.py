import os
import sys

import time
import tkinter as tk

SRCDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)

from icon import *
from widget.editor import TabbedTextpad
from widget.interpreter import Console
from widget.ui import ObjectTree

from simple_console_editor import SimpleConsoleEditor
from simple_console_editor import _ButtonBar, _MenuBar


class TreedConsoleEditor(SimpleConsoleEditor):

    def __init__(self, parent=None, locals={}, configure=True, **kwargs):
        super().__init__(parent, configure=False, **kwargs)
        self.parent = parent
        self.parent.title("PyGUI Console Editor")

        if configure:
            self.paned_window_main = tk.PanedWindow(self, orient=tk.VERTICAL)
            self.paned_window_top = tk.PanedWindow(self.paned_window_main, orient=tk.HORIZONTAL)
            self.tabbed_textpad = TabbedTextpad(self.paned_window_top)
            self.object_tree = ObjectTree(self.paned_window_top, topdict=locals)
            self.console = Console(self.paned_window_main, locals=locals, command_callback=self._on_python)

            #self.button_bar = _ButtonBar(self)
            self.menubar = _MenuBar(self)
            self.parent.config(menu=self.menubar)

            self._configure_ui()
            self._bind_shortcuts()

    def refresh_topdict(self):
        self.object_tree.refresh_topdict()

    def _configure_ui(self):
        self._set_icon()
        self.pack(expand=True, fill=tk.BOTH)

        #self.button_bar.pack(side=tk.TOP, fill=tk.X)
        self.paned_window_main.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        self.paned_window_main.add(self.paned_window_top)
        self.paned_window_main.add(self.console)

        self.paned_window_top.add(self.object_tree, minsize=200)
        self.paned_window_top.add(self.tabbed_textpad)

        self.console.output.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.console.output.configure(bg='gainsboro')
        self.console.input.grid(row=1, column=1, columnspan=1, sticky="nsew")

        label = tk.Label(self.console, text=">>>")
        label.grid(row=1, column=0, sticky="nsew")

        self.console.grid_columnconfigure(0, weight=0)
        self.console.grid_columnconfigure(1, weight=1)
        self.console.grid_rowconfigure(1, weight=0)
        self.console.grid_rowconfigure(0, weight=1)
        self.console.input.focus_force()

    def _on_python(self, event=None):
        self.refresh_topdict()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    tce = TreedConsoleEditor(root)
    root.mainloop()
