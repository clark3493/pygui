import os
import sys

from pandas import DataFrame

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.addins import AbstractAddin
from data.table.views import DataFrameView
from widget.tab_view import AbstractTabView
from widget.ui.object_tree import ObjectTree
from util.widget import find_widget_child_instance, find_widget_parent_instance


class DataFrameAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app)

        root = app.winfo_toplevel()
        if find_widget_child_instance(root, AbstractTabView) is not None:
            app.object_tree.command_initiators += [CreateDataFrameViewInitiator]

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass


class CreateDataFrameViewInitiator(object):

    @classmethod
    def callbacks(cls):
        return {"View": cls.view}

    @staticmethod
    def view(node):
        def _add_dataframe_view(event=None):
            widget = event.widget
            tree = find_widget_parent_instance(widget, ObjectTree)
            if tree is not None:
                node = tree.get_node()
                root = widget.winfo_toplevel()
                tab_view = find_widget_child_instance(root, AbstractTabView)
                if tab_view is not None:
                    data = DataFrameView(tab_view, node.obj)
                    name = node.name
                    tab_view.add_tab(widget=data, text=name)
        return _add_dataframe_view

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, DataFrame)
