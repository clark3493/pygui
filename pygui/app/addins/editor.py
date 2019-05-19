import os
import sys

import tkinter as tk

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.widget import add_menu_command_safe
from widget.editor import TabbedTextpad
from ._abstract_addin import AbstractAddin, AbstractMenubarAddin


class TabbedEditorAddin(AbstractAddin):

    def __init__(self, app, parent=None, menubar=None):
        app.tabbed_textpad = TabbedTextpad(parent)

        super().__init__(app, menubar=menubar)

    def add_bound_methods(self, app):
        app.copy = self.copy.__get__(app)
        app.cut = self.cut.__get__(app)
        app.new = self.new.__get__(app)
        app.open = self.open.__get__(app)
        app.paste = self.paste.__get__(app)
        app.redo = self.redo.__get__(app)
        app.save = self.save.__get__(app)
        app.save_as = self.save_as.__get__(app)
        app.undo = self.undo.__get__(app)
        app._get_active_pad = self._get_active_pad.__get__(app)
        app._get_active_tab_index = self._get_active_tab_index.__get__(app)

    def add_menu_options(self, app, menubar=None):
        menubar = self.get_menubar(app, menubar=menubar)
        _TabbedEditorMenubarAddin.add_menus(menubar)

    @staticmethod
    def bind_keys(app):
        pass

    @staticmethod
    def copy(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Copy']()

    @staticmethod
    def cut(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Cut']()

    @staticmethod
    def new(self, event=None):
        return self.tabbed_textpad.add_tab()

    @staticmethod
    def open(self, event=None):
        pad = self._get_active_pad()
        if pad.storeobj['OpenFilepath'] is None and pad.get('1.0', tk.END).strip() == "":
            tab = self._get_active_tab_index()
            pad = self._get_active_pad()
        else:
            tab, frame, pad = self.new()
        pad.functions['open_file']()
        filename = os.path.split(pad.storeobj['OpenFilepath'])[-1]
        self.tabbed_textpad.tab(tab, text=filename)

    @staticmethod
    def paste(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Paste']()

    @staticmethod
    def redo(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Redo']()

    @staticmethod
    def save(self, event=None):
        index = self._get_active_tab_index()
        self.tabbed_textpad.save_tab(index)

    @staticmethod
    def save_as(self, event=None):
        index = self._get_active_tab_index()
        self.tabbed_textpad.save_tab_as(index)

    @staticmethod
    def undo(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Undo']()

    @staticmethod
    def _get_active_pad(self):
        index = self._get_active_tab_index()
        return self.tabbed_textpad.get_widget(index)

    @staticmethod
    def _get_active_tab_index(self):
        tabname = self.tabbed_textpad.select()
        return self.tabbed_textpad.index(tabname)


class _TabbedEditorMenubarAddin(AbstractMenubarAddin):

    @classmethod
    def add_menus(cls, menubar):
        cls.add_edit_menu(menubar)
        cls.add_file_menu(menubar)

    @classmethod
    def add_edit_menu(cls, menubar):
        if 'editmenu' not in dir(menubar):
            menubar.editmenu = tk.Menu(menubar, tearoff=0)
        menu = cls.initialize_menu(menubar.editmenu)

        add_menu_command_safe(menu, "Undo", menubar.parent.undo)
        add_menu_command_safe(menu, "Redo", menubar.parent.redo)
        menu.add_separator()

        add_menu_command_safe(menu, "Cut", menubar.parent.cut)
        add_menu_command_safe(menu, "Copy", menubar.parent.copy)
        add_menu_command_safe(menu, "Paste", menubar.parent.paste)

        menubar.editmenu = menu

    @classmethod
    def add_file_menu(cls, menubar):
        if 'filemenu' not in dir(menubar):
            menubar.filemenu = tk.Menu(menubar, tearoff=0)
        menu = cls.initialize_menu(menubar.filemenu)

        add_menu_command_safe(menu, "New", command=menubar.parent.new)
        add_menu_command_safe(menu, "Open", command=menubar.parent.open)
        add_menu_command_safe(menu, "Save", command=menubar.parent.save)
        add_menu_command_safe(menu, "Save As", command=menubar.parent.save_as)

        menubar.filemenu = menu
