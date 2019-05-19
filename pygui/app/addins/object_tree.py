import os
import sys

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from widget.ui import ObjectTree
from ._abstract_addin import AbstractAddin


class ObjectTreeAddin(AbstractAddin):

    def __init__(self, app, parent=None, topdict={}):
        app.object_tree = ObjectTree(parent, topdict=topdict)

        super().__init__(app)

    def add_bound_methods(self, app):
        app.refresh_topdict = self.refresh_topdict.__get__(app)
        app._on_python = self._on_python.__get__(app)

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass

    @staticmethod
    def refresh_topdict(self):
        self.object_tree.refresh_topdict()

    @staticmethod
    def _on_python(self, event=None):
        self.refresh_topdict()
