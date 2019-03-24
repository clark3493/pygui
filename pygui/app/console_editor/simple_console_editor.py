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
    
    def __init__(self, parent=None, locals={}, configure=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent.title("PyGUI Console Editor")

        if configure:
            #self.button_bar = _ButtonBar(self)
            self.menubar = _MenuBar(self)
            self.parent.config(menu=self.menubar)

            self.paned_window = tk.PanedWindow(self, orient=tk.VERTICAL)
            self.tabbed_textpad = TabbedTextpad(self.paned_window)
            self.console = Console(self.paned_window, locals=locals)

            self._configure_ui()
            self._bind_shortcuts()
        
    def about(self, event=None):
        tk.messagebox.showinfo("About PyGUI", "Eventually, an informative message should go here...")
    
    def copy(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Copy']()
        
    def cut(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Cut']()
    
    def exit(self, event=None):
        self.parent.destroy()
        
    def new(self, event=None):
        return self.tabbed_textpad.add_tab()
        
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
        
    def paste(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Paste']()
        
    def redo(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Redo']()
        
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
        
    def save(self, event=None):
        index = self._get_active_tab_index()
        self.tabbed_textpad.save_tab(index)
        
    def save_as(self, event=None):
        index = self._get_active_tab_index()
        self.tabbed_textpad.save_tab_as(index)
        
    def undo(self, event=None):
        pad = self._get_active_pad()
        pad.functions['Undo']()
        
    def _bind_shortcuts(self):
        self.tabbed_textpad.bind("<Control-R>", self.run_in_session)
        self.tabbed_textpad.bind("<Control-Shift-R>", self.run_standalone)

    def _configure_ui(self):
        self._set_icon()
        self.pack(expand=True, fill=tk.BOTH)
        
        #self.button_bar.pack(side=tk.TOP, fill=tk.X)
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
        
    def _get_active_pad(self):
        index = self._get_active_tab_index()
        return self.tabbed_textpad.get_widget(index)
        
    def _get_active_tab_index(self):
        tabname = self.tabbed_textpad.select()
        return self.tabbed_textpad.index(tabname)

    def _set_icon(self):
        img = tk.Image("photo", file=PYTHON_ICON_PATH)
        if self.parent is not None:
            obj = self.parent
        else:
            obj = self
        obj.tk.call('wm', 'iconphoto', obj._w, img)
        
    def _subprocess(self, filepath):
        cmd = "__outobj__ = subprocess.run('python %s', capture_output=True, text=True)\n" % filepath.replace("\\", "/")
        self.console.pushr(cmd, print_input=False)
        self.console.pushr("if __outobj__.stdout:", print_input=False)
        self.console.pushr("    __console_stdout__.write(__outobj__.stdout)\n", print_input=False)
        self.console.pushr("if __outobj__.stderr:", print_input=False)
        self.console.pushr("    __console_stderr__.write(__outobj__.stderr)\n", print_input=False)
        
        
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
        
        self._new_file_button       = None
        self._open_file_button      = None
        self._run_in_session_button = None
        self._run_standalone_button = None
        self._save_file_button      = None
        self._save_file_as_button   = None
        
        self.arrange_buttons()
        
    @property
    def buttons(self):
        return [self.new_file_button,
                self.open_file_button,
                self.run_in_session_button,
                self.run_standalone_button,
                self.save_file_button,
                self.save_file_as_button]
        
    @property
    def new_file_button(self):
        if self._new_file_button is None:
            self._new_file_button = create_button_icon(self,
                                                       image_path=NEW_FILE_ICON_PATH,
                                                       height=self.size,
                                                       command=self.parent.new,
                                                       tooltip="New file")
        return self._new_file_button
        
    @property
    def open_file_button(self):
        if self._open_file_button is None:
            self._open_file_button = create_button_icon(self,
                                                        image_path=OPEN_FILE_ICON_PATH,
                                                        height=self.size,
                                                        command=self.parent.open,
                                                        tooltip="Open file")
        return self._open_file_button
    
    @property
    def run_in_session_button(self):
        if self._run_in_session_button is None:
            self._run_in_session_button = create_button_icon(self,
                                                             image_path=RUN_ICON_PATH,
                                                             height=self.size,
                                                             command=self.parent.run_in_session,
                                                             tooltip="Run active editor in session\nVariables previously defined in console are accessible")
        return self._run_in_session_button
        
    @property
    def run_standalone_button(self):
        if self._run_standalone_button is None:
            self._run_standalone_button = create_button_icon(self,
                                                             image_path=RUN_ONE_ICON_PATH,
                                                             height=self.size,
                                                             command=self.parent.run_standalone,
                                                             tooltip="Run active editor stand-alone\nExecution will be isolated from variables defined in console")
        return self._run_standalone_button
        
    @property
    def save_file_button(self):
        if self._save_file_button is None:
            self._save_file_button = create_button_icon(self,
                                                        image_path=SAVE_FILE_ICON_PATH,
                                                        height=self.size,
                                                        command=self.parent.save,
                                                        tooltip="Save file")
        return self._save_file_button
        
    @property
    def save_file_as_button(self):
        if self._save_file_as_button is None:
            self._save_file_as_button = create_button_icon(self,
                                                           image_path=SAVE_FILE_AS_ICON_PATH,
                                                           height=self.size,
                                                           command=self.parent.save_as,
                                                           tooltip="Save file as")
        return self._save_file_as_button
        
    @property
    def size(self):
        return self._size
        
    def arrange_buttons(self):
        self.new_file_button.pack(side=tk.LEFT)
        self.open_file_button.pack(side=tk.LEFT)
        self.save_file_button.pack(side=tk.LEFT)
        self.save_file_as_button.pack(side=tk.LEFT)
        self.run_in_session_button.pack(side=tk.LEFT)
        self.run_standalone_button.pack(side=tk.LEFT)
        
        
if __name__ == "__main__":
    root = tk.Tk()
    img = tk.Image("photo", file=PYTHON_ICON_PATH)
    root.tk.call('wm', 'iconphoto', root._w, img)
    root.geometry("800x600")
    sce = SimpleConsoleEditor(root)
    root.mainloop()
