import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.widget import add_menu_command_safe
from app.addins import AbstractAddin, AbstractMenubarAddin


class ConsoleEditorInterface(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app, menubar=menubar)

    def add_bound_methods(self, app):
        app.run_in_session = self.run_in_session.__get__(app)
        app.run_standalone = self.run_standalone.__get__(app)

    def add_menu_options(self, app, menubar=None):
        menubar = self.get_menubar(app, menubar=menubar)
        _ConsoleEditorMenubar.add_menus(menubar)

    @staticmethod
    def bind_keys(app):
        app.tabbed_textpad.bind("<Control-R>", app.run_in_session)
        app.tabbed_textpad.bind("<Control-Shift-R>", app.run_standalone)

    @staticmethod
    def run_in_session(self, event=None):
        pad = self._get_active_pad()
        if pad.storeobj['OpenFilepath'] is not None:
            pad.functions['save_file']()
            self.console.input.push("exec(open(r'%s').read())" % pad.storeobj['OpenFilepath'])
        else:
            temp_file = os.path.join(os.environ['USERPROFILE'], 'PYGUI_TEMP_FILE.py')
            words = pad.get('1.0', tk.END)
            with open(temp_file, 'w') as f:
                f.write(words)
            try:
                self.console.input.push("exec(open(r'%s').read())" % temp_file)
            finally:
                os.remove(temp_file)

    @staticmethod
    def run_standalone(self, event=None):
        self.console.push("import subprocess")
        pad = self._get_active_pad()
        if pad.storeobj['OpenFilepath'] is not None:
            pad.functions['save_file']()
            self._subprocess(pad.storeobj['OpenFilepath'])
        else:
            temp_file = os.path.join(os.environ['USERPROFILE'], 'PYGUI_TEMP_FILE.py')
            words = pad.get('1.0', tk.END)
            with open(temp_file, 'w') as f:
                f.write(words)
            try:
                self._subprocess(temp_file)
            finally:
                os.remove(temp_file)


class _ConsoleEditorMenubar(AbstractMenubarAddin):

    @classmethod
    def add_menus(cls, menubar):
        cls.add_run_menu(menubar)

    @classmethod
    def add_run_menu(cls, menubar):
        if 'runmenu' not in dir(menubar):
            menubar.runmenu = tk.Menu(menubar, tearoff=0)
        menu = cls.initialize_menu(menubar.runmenu)

        add_menu_command_safe(menu, "Run In Session...", menubar.parent.run_in_session)
        add_menu_command_safe(menu, "Run Standalone...", menubar.parent.run_standalone)

        menubar.runmenu = menu
