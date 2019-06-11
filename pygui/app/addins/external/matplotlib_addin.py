import os
import sys

import matplotlib
import tkinter as tk

from matplotlib import backend_tools
from matplotlib.backend_bases import FigureManagerBase
from matplotlib.backend_managers import ToolManager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backends._backend_tk import StatusbarTk, ToolbarTk
from matplotlib.figure import Figure

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.addins import AbstractAddin
from widget.ui.object_tree import ObjectTree
from widget.tab_view import AbstractTabView
from util.widget import find_widget_child_instance, find_widget_parent_instance


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

    @classmethod
    def callbacks(cls):
        return {"View": cls.view}

    @staticmethod
    def view(node):
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
                    canvas.manager = FigureManagerPyGUI(canvas, fig.number, frame)
                    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                    canvas.draw()
                    tab_view.add_tab(widget=frame, text=node.name)
        return _add_figure_view

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, Figure)


class FigureManagerPyGUI(FigureManagerBase):
    """
    A custom figure manager for PyGUI plot viewing.

    This class was generated as a placeholder for figure managers which get called in the guts of matplotlib's
    backend code. Without assigning a manager to to a canvas to be viewed in PyGUI, errors are constantly
    generated while using the tools in the figure toolbar (although the tools still work fine).

    See Also
    --------
    matplotlib.backends._backend_tk.FigureManagerTk:
        The class whose attributes/functionality this class is intended to mimic
    """
    def __init__(self, canvas, num, window):
        super().__init__(canvas, num)
        self.window = window
        self.canvas = canvas
        self.toolmanager = self._get_toolmanager()
        self.toolbar = self._get_toolbar()
        self._num = num

        if self.toolmanager:
            backend_tools.add_tools_to_manager(self.toolmanager)
            if self.toolbar:
                backend_tools.add_tools_to_container(self.toolbar)

        self._shown = False

    def _get_toolbar(self):
        if matplotlib.rcParams['toolbar'] == 'toolbar2':
            toolbar = NavigationToolbar2Tk(self.canvas, self.window)
        elif matplotlib.rcParams['toolbar'] == 'toolmanager':
            toolbar = ToolbarTk(self.toolmanager, self.window)
        else:
            toolbar = None
        return toolbar

    def _get_toolmanager(self):
        if matplotlib.rcParams['toolbar'] == 'toolmanager':
            toolmanager = ToolManager(self.canvas.figure)
        else:
            toolmanager = None
        return toolmanager
