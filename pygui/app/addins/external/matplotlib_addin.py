import os
import sys

import matplotlib
import tkinter as tk

from tkinter import filedialog
from matplotlib import backend_tools
from matplotlib.axes import Axes
from matplotlib.backend_bases import FigureManagerBase
from matplotlib.backend_managers import ToolManager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backends._backend_tk import ToolbarTk
from matplotlib.figure import Figure

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(LOCAL_DIR)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.addins import AbstractAddin
from app.addins._utils import get_event_node
from widget.tab_view import AbstractTabView
from util.widget import find_widget_child_instance


class MatplotlibAddin(AbstractAddin):

    def __init__(self, app, menubar=None):
        super().__init__(app)

        if 'object_tree' in dir(app):
            root = app.winfo_toplevel()
            if find_widget_child_instance(root, AbstractTabView) is not None:
                app.object_tree.command_initiators += [FigureCommandInitiator, AxesCommandInitiator]

    def add_bound_methods(self, app):
        pass

    def add_menu_options(self, app, menubar=None):
        pass

    @staticmethod
    def bind_keys(app):
        pass


class FigureCommandInitiator(object):

    @classmethod
    def callbacks(cls):
        return {"View": cls.view,
                "Save": cls.save}

    @staticmethod
    def view(node):
        def _add_figure_view(event=None):
            widget = event.widget
            nd = get_event_node(event)
            if nd is not None:
                root = widget.winfo_toplevel()
                tab_view = find_widget_child_instance(root, AbstractTabView)
                if tab_view is not None:
                    fig = nd.obj
                    frame = tk.Frame(tab_view)
                    canvas = FigureCanvasTkAgg(fig, master=frame)
                    canvas.manager = FigureManagerPyGUI(canvas, fig.number, frame)
                    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                    canvas.draw()
                    tab_view.add_tab(widget=frame, text=nd.name)
        return _add_figure_view

    @staticmethod
    def save(node):
        def _save(event=None):
            nd = get_event_node(event)
            if nd is not None:
                fig = nd.obj
                filetypes = tuple(((v + f' (.{k})', f'.{k}') for k, v in fig.canvas.get_supported_filetypes().items()))
                filename = filedialog.asksaveasfilename(initialdir="/", title="Select file", filetypes=filetypes,
                                                        defaultextension="")
                if filename:
                    fig.savefig(filename)
        return _save

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, Figure)


class AxesCommandInitiator(object):

    # TODO: CONVERT AXES MANIPULATIONS INTO A SINGLE FUNCTION WHICH OPENS A SINGLE GUI WITH OPTIONS FOR EVERYTHING

    @classmethod
    def callbacks(cls):
        return {"Set Title": cls.set_title,
                "Set XLabel": cls.set_xlabel,
                "Set YLabel": cls.set_ylabel,
                "Toggle Grid": cls.toggle_grid}

    @staticmethod
    def set_title(node):
        def _set_title(event=None):
            node = get_event_node(event)
            if node is not None:
                if isinstance(node.obj, Axes):
                    ax = node.obj
                    ax.set_title("TESTING")
                    ax.figure.canvas.draw_idle()
        return _set_title

    @staticmethod
    def set_xlabel(node):
        def _set_xlabel(event=None):
            node = get_event_node(event)
            if node is not None:
                if isinstance(node.obj, Axes):
                    ax = node.obj
                    ax.set_xlabel("TESTING")
                    ax.figure.canvas.draw_idle()
        return _set_xlabel

    @staticmethod
    def set_ylabel(node):
        def _set_ylabel(event=None):
            node = get_event_node(event)
            if node is not None:
                if isinstance(node.obj, Axes):
                    ax = node.obj
                    ax.set_ylabel("TESTING")
                    ax.figure.canvas.draw_idle()
        return _set_ylabel

    @staticmethod
    def toggle_grid(node):
        def _toggle_grid(event=None):
            node = get_event_node(event)
            if node is not None:
                if isinstance(node.obj, Axes):
                    ax = node.obj
                    ax.grid()
                    ax.figure.canvas.draw_idle()
        return _toggle_grid

    @staticmethod
    def filter(node, event=None):
        return isinstance(node.obj, Axes)


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
