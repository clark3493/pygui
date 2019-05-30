import os

import tkinter as tk
import tkinter.font as tkfont

from .textpad import TextPad
from ..tab_view import AbstractTabView, _AbstractTabViewOptions


class TabbedTextpad(AbstractTabView):

    NEW_TAB_BASENAME = "new%d"
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.options = _TabbedTextpadOptions(self)
        self.set_options()
        self.add_tab()
        
    def add_tab(self, event=None, widget=None, text=None, **kwargs):
        if widget is None:
            name = self._add_default_tab(text=None, **kwargs)
        else:
            name = super().add_tab(widget=widget, text=text)
        self._handle_new_tab(name)
        return name
        
    def bind_keys(self):
        super().bind_keys()
        for key in ['<Control-n>', '<Control-N>']:
            self.bind(key, self.add_tab)
            
    def bind_child_keys(self, child):
        for key in ['<Control-n>', '<Control-N>']:
            child.bind(key, self.add_tab)

    def get_widget(self, index, widget='!textpad'):
        return super().get_widget(index, widget=widget)
        
    def on_right_click(self, event=None):
        if event.widget.identify(event.x, event.y) == 'label':
            index = event.widget.index('@%d,%d' % (event.x, event.y))
            frame = self.get_container(index)

            if '!textpad' in frame.children:
                popup = _TextpadTabPopup(self, index)
                popup.tk_popup(event.x_root, event.y_root)
            
    def save_tab(self, index):
        pad = self.get_widget(index)
        path = pad.functions['save_file']()
        self.tab(self.tabs()[index], text=os.path.split(path)[-1])
        
    def save_tab_as(self, index):
        pad = self.get_widget(index)
        path = pad.functions['save_file_as']()
        self.tab(self.tabs()[index], text=os.path.split(path)[-1])

    def set_editor_tab_spacing(self, value):
        for name, widget in self.tab_widgets.items():
            if '!textpad' in widget.children:
                pad = widget.children['!textpad']
                pad.set_tab_spacing(value)
            
    def set_options(self):
        self.option_add('*tearOff', False)

    def _add_default_tab(self, text=None, frame_kwargs={}, textpad_kwargs={}, tab_kwargs={}):
        child = tk.Frame(self, **frame_kwargs)
        new_tab = super().add_tab(widget=child, text=text, tab_kwargs=tab_kwargs)

        pad = TextPad(child, **textpad_kwargs)
        pad.pack(expand=True, fill=tk.BOTH)

        self.bind_child_keys(pad)

        return new_tab

    def _handle_new_tab(self, name):
        widget = self.tab_widgets[name]

        if '!textpad' in widget.children:
            pad = widget.children['!textpad']
            pad.set_tab_spacing(self.options.text_entry_options.tab_spacing)


class _TabbedTextpadOptions(_AbstractTabViewOptions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.text_entry_options = _TextEntryOptions(self)


class _TextEntryOptions(object):

    def __init__(self, parent):
        self.parent = parent
        self._tab_spacing = 4

    @property
    def tab_spacing(self):
        return self._tab_spacing

    @tab_spacing.setter
    def tab_spacing(self, value):
        self._tab_spacing = value
        self.parent.parent.set_editor_tab_spacing(value)
            
            
class _TextpadTabPopup(tk.Menu):
    
    def __init__(self, parent, tab_index):
        super().__init__(parent)
        self.parent = parent
        self.tab_index = tab_index
        
        self.add_command(label="Save", command=self.save_tab)
        self.add_command(label="Save As", command=self.save_tab_as)
        
    def save_tab(self, event=None):
        self.parent.save_tab(self.tab_index)
        
    def save_tab_as(self, event=None):
        self.parent.save_tab_as(self.tab_index)
        

if __name__ == "__main__":
    root = tk.Tk()
    nb = TabbedTextpad(root)
    nb.pack(expand=1, fill='both')
    nb.add_tab()
    root.mainloop()
