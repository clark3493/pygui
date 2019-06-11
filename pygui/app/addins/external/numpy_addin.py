import os
import sys

import numpy as np

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import widget.ui.object_tree as object_tree

from app.addins import AbstractAddin
from data.table.views import ArrayTableView
from widget.tab_view import AbstractTabView
from widget.ui.object_tree import ObjectTree
from util.widget import find_widget_child_instance, find_widget_parent_instance


class NumPyAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app)

        if 'object_tree' in dir(app):
            object_tree.USER_DEFINED_NODES[self.is_ndarray_object] = NumpyTreeNode

            root = app.winfo_toplevel()
            if find_widget_child_instance(root, AbstractTabView) is not None:
                app.object_tree.command_initiators += [CreateArrayViewInitiator]

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

    @property
    def value(self):
        return "x".join([str(i) for i in self.obj.shape]) + f" {self.obj.dtype} array"


class CreateArrayViewInitiator(object):

    @classmethod
    def callbacks(cls):
        return {"View": cls.view}

    @staticmethod
    def view(node):
        def _add_array_table_view(event=None):
            widget = event.widget
            tree = find_widget_parent_instance(widget, ObjectTree)
            if tree is not None:
                node = tree.get_node()
                try:
                    root = widget.winfo_toplevel()
                    tab_view = find_widget_child_instance(root, AbstractTabView)
                    if tab_view is not None:
                        data = ArrayTableView(tab_view, node.obj)
                        name = node.name
                        tab_view.add_tab(widget=data, text=name)
                except ValueError as e:
                    if "Array greater than 2 or greater than 1 dimensions are not currently supported" in str(e):
                        pass
                    else:
                        raise
        return _add_array_table_view

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, np.ndarray)
