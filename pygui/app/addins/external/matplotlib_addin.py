import os
import sys

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.addins import AbstractAddin
from widget.ui.object_tree import ObjectTree
from widget.tab_view import AbstractTabView
from util.widget import find_widget_child_instance, find_widget_parent_instance


# TODO: USING MATPLOTLIB TOOLBAR THROWS ATTRIBUTE ERROR EVEN THOUGH IT WORKS FINE. FIX THIS.


class MatplotlibAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app)

        if 'object_tree' in dir(app):
            root = app.winfo_toplevel()
            if find_widget_child_instance(root, AbstractTabView) is not None:
                app.object_tree.command_initiators += [CreateFigureViewInitiator]

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass


class CreateFigureViewInitiator(object):

    label = "View"

    @staticmethod
    def callback(node):
        def _add_figure_view(event=None):
            widget=event.widget
            tree = find_widget_parent_instance(widget, ObjectTree)
            if tree is not None:
                node = tree.get_node()
                root = widget.winfo_toplevel()
                tab_view = find_widget_child_instance(root, AbstractTabView)
                if tab_view is not None:
                    fig = node.obj
                    frame = tk.Frame(tab_view)
                    canvas = FigureCanvasTkAgg(fig, master=frame)
                    #canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                    toolbar = NavigationToolbar2Tk(canvas, frame)
                    toolbar.update()
                    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                    canvas.draw()
                    tab_view.add_tab(widget=frame, text=node.name)
        return _add_figure_view

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, Figure)