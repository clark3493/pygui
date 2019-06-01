import os
import sys

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from widget.interpreter import Console
from ._abstract_addin import AbstractAddin


class ConsoleAddin(AbstractAddin):

    def __init__(self, app, parent=None, history_filepath=None, locals={}):
        app.console = Console(parent, history_filepath=history_filepath, locals=locals)

        super().__init__(app)

    def add_bound_methods(self, app):
        app._subprocess = self._subprocess.__get__(app)

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass

    @staticmethod
    def _subprocess(self, filepath):
        cmd = "__outobj__ = subprocess.run('python %s', capture_output=True, text=True)\n" % filepath.replace("\\", "/")
        self.console.pushr(cmd, print_input=False)
        self.console.pushr("if __outobj__.stdout:", print_input=False)
        self.console.pushr("    __console_stdout__.write(__outobj__.stdout)\n", print_input=False)
        self.console.pushr("if __outobj__.stderr:", print_input=False)
        self.console.pushr("    __console_stderr__.write(__outobj__.stderr)\n", print_input=False)
