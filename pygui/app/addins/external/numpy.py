import os
import sys

import numpy as np

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import widget.ui.object_tree as object_tree

from app.addins import AbstractAddin
from app.addins.views import CreateArrayViewInitator
from widget.tab_view import AbstractTabView
from util.widget import find_widget_child_instance


class NumPyAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app)

        if 'object_tree' in dir(app):
            object_tree.USER_DEFINED_NODES[self.is_ndarray_object] = NumpyTreeNode

            root = app.winfo_toplevel()
            if find_widget_child_instance(root, AbstractTabView) is not None:
                app.object_tree.command_initiators += [CreateArrayViewInitator]

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass

    @staticmethod
    def is_ndarray_object(o):
        return isinstance(o, np.ndarray)


class NumpyTreeNode(object_tree.TreeNode):

    def __init__(self, obj, parent=None, iid=None, name=None):
        super().__init__(obj, parent=parent, iid=iid, name=name)

    @property
    def value(self):
        return "x".join([str(i) for i in self.obj.shape]) + f" {self.obj.dtype} array"
