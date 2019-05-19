from tkinter import ttk


class AbstractTabView(ttk.Notebook):

    NEW_TAB_BASENAME = "new%d"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

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
        self.bind('<Button-3>', self.on_right_click)

    def close_tab(self, index):
        self.forget(index)
        if len(self.tab_names) == 0:
            self.add_tab()

    def get_container(self, index):
        return self.tab_widgets[self.tabs()[index]]

    def get_widget(self, index, widget=''):
        return self.get_container(index).children[widget]

    def on_right_click(self, event=None):
        pass

    def _add_default_tab(self):
        raise NotImplementedError
