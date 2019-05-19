import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.widget import get_menu_labels


class AbstractAddin(object):

    def __init__(self, app, menubar=None):
        self.add_bound_methods(app)
        if menubar is not None:
            self.add_menu_options(app, menubar=menubar)
        self.bind_keys(app)

    def add_bound_methods(self, app):
        raise NotImplementedError

    def add_menu_options(self, app, menubar=None):
        raise NotImplementedError

    @staticmethod
    def bind_keys(app):
        raise NotImplementedError

    @staticmethod
    def get_menubar(app, menubar=None):
        if isinstance(menubar, tk.Menu):
            return menubar
        elif 'menubar' in dir(app):
            return app.menubar
        else:
            menubar = tk.Menu(app, tearoff=0)
            menubar.parent = app
            app.menubar = menubar
            return menubar


class AbstractMenubarAddin(object):

    @classmethod
    def add_menus(cls, menubar):
        raise NotImplementedError

    @staticmethod
    def initialize_menu(menu):
        labels = get_menu_labels(menu)
        if len(labels) > 0:
            menu.add_separator()
        return menu
