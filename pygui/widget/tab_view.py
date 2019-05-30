import tkinter as tk

from tkinter import ttk


class AbstractTabView(ttk.Notebook):

    __INITIALIZED = False
    NEW_TAB_BASENAME = "new%d"

    def __init__(self, parent, *args, **kwargs):
        if not self.__INITIALIZED:
            self.__initialize_custom_style()
            self.__INITIALIZED = True

        if "style" not in kwargs:
            kwargs["style"] = "AbstractTabView"

        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._active = None

        self.options = _AbstractTabViewOptions(self)
        self.tab_widgets = {}
        self.bind_keys()

    @property
    def tab_names(self):
        return [self.tab(name, option="text") for name in self.tabs()]

    def add_tab(self, event=None, widget=None, text=None, **kwargs):
        if text is None:
            i = 1
            text = self.NEW_TAB_BASENAME % i
            while text in self.tab_names:
                i += 1
                text = self.NEW_TAB_BASENAME % i

        old_tabs = self.tabs()
        kws = kwargs['tab_kwargs'] if 'tab_kwargs' in kwargs else {}
        self.add(widget, text=text, **kws)

        new_tab = [tab for tab in self.tabs() if tab not in old_tabs][0]
        self.tab_widgets[new_tab] = widget
        self.select(new_tab)
        return new_tab

    def bind_keys(self):
        self.bind("<ButtonPress-1>", self.on_left_click_press, True)
        self.bind("<ButtonRelease-1>", self.on_left_click_release)
        self.bind('<Button-3>', self.on_right_click)

    def close_tab(self, index):
        self.forget(index)
        if len(self.tab_names) == 0:
            self.add_tab()

    def get_container(self, index):
        return self.tab_widgets[self.tabs()[index]]

    def get_widget(self, index, widget=''):
        return self.get_container(index).children[widget]

    def on_left_click_press(self, event=None):
        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_left_click_release(self, event=None):
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            self.close_tab(index)

        self.state(["!pressed"])
        self._active = None

    def on_right_click(self, event=None):
        pass

    def _add_default_tab(self):
        raise NotImplementedError

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
            R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=
            '''),
            tk.PhotoImage("img_closeactive", data='''
            R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
            AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
            '''),
            tk.PhotoImage("img_closepressed", data='''
            R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"), border=8, sticky="")
        style.layout("AbstractTabView", [("AbstractTabView.client", {"sticky": "nswe"})])
        style.layout("AbstractTabView.Tab", [
            ("AbstractTabView.tab", {"sticky": "nswe",
                                     "children": [
                                         ("AbstractTabView.padding", {
                                             "side": "top",
                                             "sticky": "nswe",
                                             "children": [
                                                 ("AbstractTabView.focus", {
                                                     "side": "top",
                                                     "sticky": "nswe",
                                                     "children": [
                                                         ("AbstractTabView.label", {"side": "left", "sticky": ""}),
                                                         ("AbstractTabView.close", {"side": "left", "sticky": ""}),
                                                     ]
                                                 })
                                             ]
                                         })
                                     ]})
        ])


class _AbstractTabViewOptions(object):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        # currently just a placeholder
