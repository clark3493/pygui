import os
import sys

import tkinter as tk

from tkinter import messagebox

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.widget import add_menu_command_safe, find_widget_child_instance
from widget.editor import TabbedTextpad
from ._abstract_addin import AbstractAddin, AbstractMenubarAddin
from .preferences import initialize_preferences


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
        cls.add_preferences_menu(menubar)

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

    @classmethod
    def add_preferences_menu(cls, menubar):
        pref = initialize_preferences(menubar.parent)
        if 'prefmenu' not in dir(menubar):
            menubar.prefmenu = tk.Menu(menubar, tearoff=0)
            menu = cls.initialize_menu(menubar.prefmenu)
            add_menu_command_safe(menu, "Preferences...", command=pref.deiconify)
            menubar.prefmenu = menu
        f = _EditorPreferencesWindow(pref.container)
        f.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        pref.add_frame("Text Editing", f)


class _EditorPreferencesWindow(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = self.get_editor_options()

        self.tab_spacing_label = tk.Label(self, text="Tab spacing")
        self.tab_spacing_var   = tk.StringVar()
        self.tab_spacing_entry = tk.Entry(self,
                                          text=options.text_entry_options.tab_spacing,
                                          textvariable=self.tab_spacing_var)

        self.last_tab_spacing = None

        self.configure_window()
        self.bind_keys()

    def bind_keys(self):
        self.tab_spacing_entry.bind("<FocusIn>", self.on_tab_spacing_gain_focus)
        self.tab_spacing_entry.bind("<FocusOut>", self.on_tab_spacing_lose_focus)
        self.tab_spacing_entry.bind("<Return>", self.on_tab_spacing_lose_focus)

    def configure_window(self):
        self.tab_spacing_label.grid(row=0, column=0)
        self.tab_spacing_entry.grid(row=0, column=1)

    def get_editor(self):
        window = self.winfo_toplevel()
        app = window.parent
        return find_widget_child_instance(app, TabbedTextpad)

    def get_editor_options(self):
        editor = self.get_editor()
        return editor.options

    def on_tab_spacing_gain_focus(self, event=None):
        self.last_tab_spacing = self.tab_spacing_var.get()

    def on_tab_spacing_lose_focus(self, event=None):
        try:
            value = int(self.tab_spacing_var.get())
        except (TypeError, ValueError):
            value = None
            if self.tab_spacing_var.get() == "":
                pass
            else:
                msg  = f"'{self.tab_spacing_entry.get()}' is an invalid value for tab spacing. Entry should be an integer "
                msg += f"representing the number of spaces per tab."
                messagebox.showerror("User entry error!", msg)
                self.tab_spacing_var.set(self.last_tab_spacing if self.last_tab_spacing is not None else "")
                self.last_tab_spacing = None

        if value:
            options = self.get_editor_options()
            options.text_entry_options.tab_spacing = value

