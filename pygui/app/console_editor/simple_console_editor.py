import os
import sys

import tkinter as tk


SRCDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)

from icon import *
from util.widget import create_button_icon
from widget.editor import TabbedTextpad
from widget.interpreter import Console


class SimpleConsoleEditor(tk.Frame):
    
    def __init__(self, parent=None, locals=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent.title("PyGUI Console Editor")
        
        self.menubar = _MenuBar(self)
        self.parent.config(menu=self.menubar)
        
        self.button_bar = _ButtonBar(self)
        self.paned_window = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.tabbed_textpad = TabbedTextpad(self.paned_window)
        self.console = Console(self.paned_window, locals=locals)
        
        self._configure_ui()
        
    def about(self, event=None):
        pass
    
    def copy(self, event=None):
        pass
        
    def cut(self, event=None):
        pass
    
    def exit(self, event=None):
        pass
        
    def new(self, event=None):
        pass
        
    def open(self, event=None):
        pass
        
    def paste(self, event=None):
        pass
        
    def redo(self, event=None):
        pass
        
    def run_in_session(self, event=None):
        tabname = self.tabbed_textpad.select()
        index = self.tabbed_textpad.index(tabname)
        pad = self.tabbed_textpad.get_widget(index)
        if pad.storeobj['OpenFilepath'] is not None:
            pad.save_file()
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
        
    def run_standalone(self, event=None):
        pass
        
    def save(self, event=None):
        pass
        
    def save_as(self, event=None):
        pass
        
    def undo(self, event=None):
        pass
        
    def _configure_ui(self):
        self.pack(expand=True, fill=tk.BOTH)
        
        self.button_bar.pack(side=tk.TOP)
        self.paned_window.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        
        self.paned_window.add(self.tabbed_textpad)
        
        self.paned_window.add(self.console)
        
        self.console.output.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.console.output.configure(bg='gainsboro')
        self.console.input.grid(row=1, column=1, columnspan=1, sticky="nsew")
        
        label = tk.Label(self.console, text=">>>")
        label.grid(row=1, column=0, sticky="ne")
        
        self.console.grid_columnconfigure(0, weight=0)
        self.console.grid_columnconfigure(1, weight=1)
        self.console.grid_rowconfigure(1, weight=0)
        self.console.grid_rowconfigure(0, weight=1)
        self.console.input.focus_force()
        
        
class _MenuBar(tk.Menu):
    
    def __init__(self, parent=None, tearoff=0):
        super().__init__(parent, tearoff=tearoff)
        self.parent = parent
        
        self._editmenu = None
        self._filemenu = None
        self._helpmenu = None
        self._runmenu  = None
        
        self.add_cascade(label="File", menu=self.filemenu)
        self.add_cascade(label="Edit", menu=self.editmenu)
        self.add_cascade(label="Run",  menu=self.runmenu)
        self.add_cascade(label="Help", menu=self.helpmenu)
        
    @property
    def editmenu(self):
        if self._editmenu is None:
            menu = tk.Menu(self, tearoff=0)
            
            menu.add_command(label="Undo", command=self.parent.undo)
            menu.add_command(label="Redo", command=self.parent.redo)
            menu.add_separator()
            
            menu.add_command(label="Cut", command=self.parent.cut)
            menu.add_command(label="Copy", command=self.parent.copy)
            menu.add_command(label="Paste", command=self.parent.paste)
            
            self._editmenu = menu
        return self._editmenu
    
    @property
    def filemenu(self):
        if self._filemenu is None:
            menu = tk.Menu(self, tearoff=0)
            
            menu.add_command(label="New", command=self.parent.new)
            menu.add_command(label="Open", command=self.parent.open)
            menu.add_command(label="Save", command=self.parent.save)
            menu.add_command(label="Save As", command=self.parent.save_as)
            menu.add_separator()
            
            menu.add_command(label="Exit", command=self.parent.exit)
            
            self._filemenu = menu
        return self._filemenu
        
    @property
    def helpmenu(self):
        if self._helpmenu is None:
            menu = tk.Menu(self, tearoff=0)
            
            menu.add_command(label="About...", command=self.parent.about)
            
            self._helpmenu = menu
        return self._helpmenu
        
    @property
    def runmenu(self):
        if self._runmenu is None:
            menu = tk.Menu(self, tearoff=0)
            
            menu.add_command(label="Run In Session...", command=self.parent.run_in_session)
            menu.add_command(label="Run Standalone...", command=self.parent.run_standalone)
            
            self._runmenu = menu
        return self._runmenu
        
        
class _ButtonBar(tk.Frame):
    
    def __init__(self, parent, size=30):
        super().__init__(parent)
        self.parent = parent
        
        self._size = size
        
        self.icon_dir = os.path.join(SRCDIR, "icon")
        
        self._run_in_session_button = None
        self._run_standalone_button = None
        
        self.arrange_buttons()
        
    @property
    def buttons(self):
        return [self.run_in_session_button,
                self.run_standalone_button]
        
    @property
    def run_in_session_button(self):
        if self._run_in_session_button is None:
            self._run_in_session_button = create_button_icon(self,
                                                             image_path=RUN_ICON_PATH,
                                                             height=self.size,
                                                             command=self.parent.run_in_session)
        return self._run_in_session_button
        
    @property
    def run_standalone_button(self):
        if self._run_standalone_button is None:
            b = tk.Button(self)
            self.run_standalone_icon = tk.PhotoImage(file=RUN_ONE_ICON_PATH, width=self.size, height=self.size)
            b.config(image=self.run_standalone_icon, width=self.size, height=self.size, command=self.parent.run_standalone)
            self._run_standalone_button = b
            self._run_standalone_button = create_button_icon(self,
                                                             image_path=RUN_ONE_ICON_PATH,
                                                             height=self.size,
                                                             command=self.parent.run_standalone)
        return self._run_standalone_button
        
    @property
    def size(self):
        return self._size
        
    def arrange_buttons(self):
        self.run_in_session_button.pack(side=tk.LEFT)
        self.run_standalone_button.pack(side=tk.LEFT)
        
        
if __name__ == "__main__":
    root = tk.Tk()
    sce = SimpleConsoleEditor(root)
    root.mainloop()
