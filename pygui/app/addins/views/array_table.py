import os
import sys

import numpy as np

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from data.table.views import ArrayTableView
from util.widget import find_widget_child_instance, find_widget_parent_instance
from widget.tab_view import AbstractTabView
from widget.ui.object_tree import ObjectTree


class CreateArrayViewInitator(object):

    label = "View"

    @staticmethod
    def callback(node):
        def _add_array_table_view(event=None):
            widget = event.widget
            tree = find_widget_parent_instance(widget, ObjectTree)
            if tree is not None:
                node = tree.get_node()
                try:
                    root = widget.winfo_toplevel()
                    tab_view = find_widget_child_instance(root, AbstractTabView)
                    if tab_view is not None:
                        data = ArrayTableView(tab_view, node.obj, index_style='array')
                        name = node.name
                        tab_view.add_tab(widget=data, text=name)
                except ValueError:
                    pass
        return _add_array_table_view

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, np.ndarray)
