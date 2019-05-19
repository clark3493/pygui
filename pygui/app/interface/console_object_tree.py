import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.widget import add_menu_command_safe
from app.addins import AbstractAddin, AbstractMenubarAddin


class ConsoleObjectTreeInterface(AbstractAddin):

    def __init__(self, app, menubar=None):
        app.console.command_callback = app._on_python
        super().__init__(app)

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass
