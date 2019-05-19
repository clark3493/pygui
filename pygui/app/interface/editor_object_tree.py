import os
import sys

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.addins import AbstractAddin
from app.addins.views import CreateArrayViewInitator


class TabbedEditorObjectTreeInterface(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app)
        app.object_tree.command_initiators += [CreateArrayViewInitator]

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass
