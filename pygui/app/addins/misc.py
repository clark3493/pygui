import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.widget import add_menu_command_safe
from ._abstract_addin import AbstractAddin, AbstractMenubarAddin


class ExitAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app, menubar=menubar)

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        menubar = self.get_menubar(app, menubar=menubar)
        _ExitMenubarAddin.add_menus(menubar)

    @staticmethod
    def bind_keys(app):
        pass


class _ExitMenubarAddin(AbstractMenubarAddin):

    @classmethod
    def add_menus(cls, menubar):
        cls.add_exit_menu_option(menubar)

    @classmethod
    def add_exit_menu_option(cls, menubar):
        if 'filemenu' not in dir(menubar):
            menubar.filemenu = tk.Menu(menubar, tearoff=0)
        menu = cls.initialize_menu(menubar.filemenu)

        add_menu_command_safe(menu, "Exit", menubar.parent.exit)

        menubar.filemenu = menu


class HelpAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app, menubar=menubar)

    def add_bound_methods(self, app):
        app.about = self.about.__get__(app)

    def add_menu_options(self, app, menubar=None):
        menubar = self.get_menubar(app, menubar)
        _HelpMenubarAddin.add_menus(menubar)

    @staticmethod
    def bind_keys(app):
        pass

    @staticmethod
    def about(self, event=None):
        tk.messagebox.showinfo("About PyGUI", "Eventually, an informative message should go here...")


class _HelpMenubarAddin(AbstractMenubarAddin):

    @classmethod
    def add_menus(cls, menubar):
        cls.add_help_menu(menubar)

    @classmethod
    def add_help_menu(cls, menubar):
        if 'helpmenu' not in dir(menubar):
            menubar.helpmenu = tk.Menu(menubar, tearoff=0)
        menu = cls.initialize_menu(menubar.helpmenu)

        add_menu_command_safe(menu, "About...", menubar.parent.about)

        menubar.helpmenu = menu
