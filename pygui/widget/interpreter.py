import os
import sys


import tkinter as tk

from code import InteractiveConsole
from uuid import uuid4

SRCDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)
    
from util.context import redirect
from util.handler import print_error


try:
    _ = sys.ps1
except AttributeError:
    # for some reason, calls to sys.ps1 throw exceptions -- fix that here
    sys.ps1 = '>>> '
    sys.ps2 = '... '


class RedirectedInterpreter(InteractiveConsole):
    
    def __init__(self, 
                 stdout=sys.stdout,
                 stderr=sys.stderr,
                 excepthook=sys.excepthook,
                 locals=None):
        super().__init__(locals=locals)
        
        self.stdout     = stdout
        self.stderr     = stderr
        self.excepthook = excepthook
        
        self.locals['__console_stdout__'] = self.stdout
        self.locals['__console_stderr__'] = self.stderr
        self.locals['__console_excepthook__'] = self.excepthook
        
        self._waiting = False
        
    def pushr(self, string):
        with redirect(stdout=self.stdout,
                      stderr=self.stderr,
                      excepthook=self.excepthook):
            self._waiting = self.push(string)
                
    
class Console(tk.Frame, RedirectedInterpreter):
    
    def __init__(self, parent=None,
                       locals=None,
                       history_file=None,
                       auto_view=True,
                       standalone=False,
                       command_callback=None):
        tk.Text.__init__(self, parent)
        RedirectedInterpreter.__init__(self,
                                       stdout=_ConsoleStream(self, fileno=1),
                                       stderr=_ConsoleStream(self, foreground="red", fileno=2),
                                       excepthook=print_error,
                                       locals=locals)
        self.parent = parent
        
        self._auto_view = auto_view
        
        self.input  = _ConsoleInput(self)
        self.output = _ConsoleOutput(self, auto_view=auto_view)

        self.command_callback = command_callback
        
        if standalone:
            self.pack(expand=True, fill=tk.BOTH)
            self.parent.title("PyGUI Console")
            
            self.output.grid(row=0, column=0, columnspan=2,
                             sticky="nsew")
            self.output.configure(bg='gainsboro')
            self.input.grid(row=1, column=1, columnspan=1, sticky="nsew")
            
            label = tk.Label(self, text=">>>")
            label.grid(row=1, column=0, sticky="ne")
            
            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(0, weight=1)
            self.input.focus_force()
        
    @property
    def auto_view(self):
        return self._auto_view
        
    @auto_view.setter
    def auto_view(self, value):
        self.output.auto_view = value
        self._auto_view = value
        
    def pushr(self, string, print_input=True):
        with redirect(stdout=self.stdout,
                      stderr=self.stderr,
                      excepthook=self.excepthook):
            if not self._waiting and print_input:
                sys.stdout.write("%s%s\n" % (sys.ps1, string))
            elif print_input:
                sys.stdout.write("%s\n" % (string))
            self._waiting = self.push(string)
            if self._waiting and print_input:
                sys.stdout.write("%s" % sys.ps2)

        if self.command_callback is not None:
            self.command_callback()
    
    def write(self, string, foreground="black"):
        self.output.write(string, foreground=foreground)
        
        
class _ConsoleInput(tk.Entry):
    
    def __init__(self, parent=None, tab_spacing=4, max_cache=128):
        super().__init__(parent)
        self.parent = parent
        self.tab_spacing = tab_spacing
        self.max_cache = max_cache

        self.bind('<Down>', self.display_next_command)
        self.bind('<Return>', self.enter)
        self.bind('<Tab>', self.tab)
        self.bind('<Up>', self.display_previous_command)

        self._commands = ['']
        self._current_command_index = 1

    def display_next_command(self, event=None):
        cmd = self.get_next_command()
        self.set_displayed_text(cmd)

    def display_previous_command(self, event=None):
        cmd = self.get_previous_command()
        self.set_displayed_text(cmd)

    def enter(self, event=None):
        string = self.get()
        self.delete(0, tk.END)
        if string.strip() == "":
            string = ""
        self.push(string)

    def get_next_command(self):
        if self._current_command_index > 1:
            self._current_command_index -= 1
        return self._commands[-self._current_command_index]

    def get_previous_command(self):
        if self._current_command_index < len(self._commands):
            self._current_command_index += 1
        return self._commands[-self._current_command_index]
        
    def push(self, string):
        self.parent.pushr(string)
        self.store_command(string)
        self._current_command_index = 1

    def set_displayed_text(self, txt):
        self.delete(0, tk.END)
        self.insert(0, txt)

    def store_command(self, cmd):
        if len(self._commands) > self.max_cache:
            self._commands = self._commands[1:]
        self._commands.insert(-1, cmd)
        
    def tab(self, event=None):
        self.insert(tk.INSERT, ' ' * self.tab_spacing)
        self.select_clear()
        return "break"  # prevent class default tab behavior from occurring
                 
                 
class _ConsoleOutput(tk.Text):
    
    def __init__(self, parent=None, auto_view=True):
        super().__init__(parent)
        self.parent = parent
        self.auto_view = auto_view
        
    def disable(self):
        self.configure(state="disabled")
        
    def enable(self):
        self.configure(state="normal")
        
    def write(self, string, foreground="black"):
        self.enable()
        uid = uuid4()
        self.insert(tk.END, string, (uid,))
        self.tag_configure(uid, foreground=foreground)
        self.disable()
        if self.auto_view:
            self.see(tk.END)
                 
                 
class _ConsoleStream(object):
    
    def __init__(self, parent=None, foreground="black", fileno=0):
        self.parent = parent
        self.foreground = foreground
        self._fileno = fileno
        
    def fileno(self):
        return self._fileno
    
    def write(self, string):
        self.parent.write(string, foreground=self.foreground)
        
        
if __name__ == "__main__":
    root = tk.Tk()
    console = Console(root, standalone=True)
    root.mainloop()
    
