import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import AbstractApplication
from app.addins.console import ConsoleAddin
from app.addins.editor import TabbedEditorAddin
from app.addins.misc import ExitAddin, HelpAddin
from app.interface import ConsoleEditorInterface


class SimpleConsoleEditor(AbstractApplication):

    def __init__(self, parent=None, title="PyGUI Console Editor", **kwargs):
        self.paned_window = None

        super().__init__(parent=parent, title=title, **kwargs)

    def configure_application(self):
        self.paned_window = tk.PanedWindow(self, orient=tk.VERTICAL)

        TabbedEditorAddin(self, parent=self.paned_window, menubar=True)
        ConsoleAddin(self, parent=self.paned_window)
        ConsoleEditorInterface(self, menubar=True)
        HelpAddin(self, menubar=True)
        ExitAddin(self, menubar=True)

        self._configure_menubar()
        self._configure_ui()

    def _configure_menubar(self):
        self.winfo_toplevel().configure(menu=self.menubar)
        self.menubar.add_cascade(label="File", menu=self.menubar.filemenu)
        self.menubar.add_cascade(label="Edit", menu=self.menubar.editmenu)
        self.menubar.add_cascade(label="Run", menu=self.menubar.runmenu)
        self.menubar.add_cascade(label="Help", menu=self.menubar.helpmenu)

    def _configure_ui(self):
        self.pack(expand=True, fill=tk.BOTH)

        self.paned_window.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        self.paned_window.add(self.tabbed_textpad)
        self.paned_window.add(self.console)

        self.console.output.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.console.output.configure(bg='gainsboro')
        self.console.input.grid(row=1, column=1, columnspan=1, sticky="nsew")
        self.console.status_label.grid(row=1, column=0, sticky="ne")

        self.console.grid_columnconfigure(0, weight=0)
        self.console.grid_columnconfigure(1, weight=1)
        self.console.grid_rowconfigure(1, weight=0)
        self.console.grid_rowconfigure(0, weight=1)
        self.console.input.focus_force()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    sce = SimpleConsoleEditor(root)
    root.mainloop()
