import os
import sys

import logging
import tkinter as tk

from code import InteractiveConsole
from uuid import uuid4

SRCDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)

from util import DEFAULT_LOGGING_FORMATTER
from util.context import redirect
from util.handler import print_error


try:
    _ = sys.ps1
except AttributeError:
    # for some reason, calls to sys.ps1 throw exceptions -- fix that here
    sys.ps1 = '>>> '
    sys.ps2 = '... '


logger = logging.getLogger(__name__)
_ch = logging.StreamHandler()
_ch.setFormatter(DEFAULT_LOGGING_FORMATTER)
logger.addHandler(_ch)

LEVELS = {'STDOUT':    11,
          'STDERR':    12,
          'CMD_START': 21,
          'CMD_CONT':  22}

for suffix, lvl in LEVELS.items():
    name = "CONSOLE_%s" % suffix
    logging.addLevelName(lvl, name)


class RedirectedInterpreter(InteractiveConsole):

    def __init__(self,
                 stdout=sys.stdout,
                 stderr=sys.stderr,
                 excepthook=sys.excepthook,
                 locals=None):
        super().__init__(locals=locals)

        self._id = uuid4()

        self.stdout = stdout
        self.stderr = stderr
        self.excepthook = excepthook

        self.locals['__console_stdout__'] = self.stdout
        self.locals['__console_stderr__'] = self.stderr
        self.locals['__console_excepthook__'] = self.excepthook

        self._waiting = False

    @property
    def id(self):
        return self._id

    def pushr(self, string):
        with redirect(stdout=self.stdout,
                      stderr=self.stderr,
                      excepthook=self.excepthook):
            self._waiting = self.push(string)


class Console(tk.Frame, RedirectedInterpreter):

    def __init__(self,
                 parent=None,
                 auto_view=True,
                 command_callback=None,
                 history_filepath=None,
                 locals=None,
                 standalone=False):
        tk.Frame.__init__(self, parent)

        stdout_handler = _MessageHandler(self,
                                         write_hook=self.log,
                                         write_args=[LEVELS['STDOUT']])
        stderr_handler = _MessageHandler(self,
                                         write_hook=self.log,
                                         write_args=[LEVELS['STDERR']])
        RedirectedInterpreter.__init__(self,
                                       stdout=stdout_handler,
                                       stderr=stderr_handler,
                                       excepthook=print_error,
                                       locals=locals)
        self.parent = parent

        self._auto_view = auto_view

        self.input  = _ConsoleInput(self)
        self.output = _ConsoleOutput(self, auto_view=auto_view)

        self.command_callback = command_callback

        self.logger = logging.getLogger(f"CONSOLE_{self.id}")
        self.logger.setLevel(logging.DEBUG)
        self._log_handlers = {}
        self._initialize_logger(filepath=history_filepath)

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

    def log(self, msg, level, *args, **kwargs):
        self.logger.log(level, msg, *args, **kwargs)

    def pushr(self, string, print_input=True):
        if not self._waiting and print_input:
            self.log(string, level=LEVELS['CMD_START'])
        elif print_input:
            self.log(string, level=LEVELS['CMD_CONT'])
        super().pushr(string)
        if self._waiting:
            # TODO: FIX LABEL TEXT
            pass

    def set_history_file(self, filepath, loglevel=logging.INFO):
        log = self.logger

        history_handler = logging.FileHandler(filepath, delay=True)
        history_handler.setLevel(loglevel)  # default setting is only to display input, not stdout or stderr
        history_handler.setFormatter(logging.Formatter("%(message)s\n"))
        history_handler.addFilter(_FilterBlank())
        history_handler.terminator = ""

        # remove the old handler
        if 'history' in self._log_handlers:
            log.handlers = [h for h in log.handlers if h is not self._log_handlers['history']]

        self._log_handlers['history'] = history_handler
        log.addHandler(history_handler)

    def set_history_loglevel(self, level):
        if 'history' in self._log_handlers:
            self._log_handlers['history'].setLevel(level)
        else:
            msg = "Tried setting the history log level for Console %s to %s, but no history file handler was found."
            msg = msg % (self.id, str(level))
            logger.warning(msg)

    def _initialize_logger(self, filepath=None):
        log = self.logger

        console_black_text_output = _MessageHandler(self,
                                                    write_hook=self.output.write)
        console_red_text_output   = _MessageHandler(self,
                                                    write_hook=self.output.write,
                                                    write_kwargs={'foreground': 'red'})

        raw_formatter = logging.Formatter("%(message)s")

        stdout_console_handler = logging.StreamHandler(stream=console_black_text_output)
        stdout_console_handler.setLevel(LEVELS['STDOUT'])
        stdout_console_handler.addFilter(_FilterStdout())
        stdout_console_handler.setFormatter(raw_formatter)
        stdout_console_handler.terminator = ""
        log.addHandler(stdout_console_handler)

        stderr_console_handler = logging.StreamHandler(stream=console_red_text_output)
        stderr_console_handler.setLevel(LEVELS['STDERR'])
        stderr_console_handler.addFilter(_FilterStderr())
        stderr_console_handler.setFormatter(raw_formatter)
        stderr_console_handler.terminator = ""
        log.addHandler(stderr_console_handler)

        cmd_start_console_handler = logging.StreamHandler(stream=console_black_text_output)
        cmd_start_console_handler.setLevel(LEVELS['CMD_START'])
        cmd_start_console_handler.addFilter(_FilterCmdStart())
        cmd_start_console_formatter = logging.Formatter(f"{sys.ps1}%(message)s")
        cmd_start_console_handler.setFormatter(cmd_start_console_formatter)
        log.addHandler(cmd_start_console_handler)

        cmd_cont_console_handler = logging.StreamHandler(stream=console_black_text_output)
        cmd_cont_console_handler.setLevel(LEVELS['CMD_CONT'])
        cmd_cont_console_handler.addFilter(_FilterCmdCont())
        cmd_cont_console_formatter = logging.Formatter(f"{sys.ps2}%(message)s")
        cmd_cont_console_handler.setFormatter(cmd_cont_console_formatter)
        log.addHandler(cmd_cont_console_handler)

        if filepath is not None:
            self.set_history_file(filepath)


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
        return "break" # prevent class default tab behavior from occurring


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


class _MessageHandler(object):

    def __init__(self, parent=None, fileno=0, write_hook=None, write_args=[], write_kwargs={}):
        self.parent = parent
        self.write_hook = write_hook
        self.write_args = write_args
        self.write_kwargs = write_kwargs

    def write(self, string):
        self.write_hook(string, *self.write_args, **self.write_kwargs)


class _FilterCmdStart(logging.Filter):
    def filter(self, record):
        return record.levelno == LEVELS['CMD_START']


class _FilterCmdCont(logging.Filter):
    def filter(self, record):
        return record.levelno == LEVELS['CMD_CONT']


class _FilterStderr(logging.Filter):
    def filter(self, record):
        return record.levelno == LEVELS['STDERR']


class _FilterStdout(logging.Filter):
    def filter(self, record):
        return record.levelno == LEVELS['STDOUT']


class _FilterBlank(logging.Filter):
    # For some reason, stdout sometimes seems to return 2 blank lines as a separate
    # output following the actual output. These lines then screw up the log file. This
    # filter can be used to only display non-white messages.
    def filter(self, record):
        return record.msg.strip() != ""


if __name__ == "__main__":
    root = tk.Tk()
    console = Console(root, standalone=True)
    root.mainloop()
