import os

import tkinter as tk

from .textpad import TextPad
from ..tab_view import AbstractTabView


class TabbedTextpad(AbstractTabView):

    NEW_TAB_BASENAME = "new%d"
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_options()
        self.add_tab()
        
    def add_tab(self, event=None, widget=None, text=None, **kwargs):
        if widget is None:
            return self._add_default_tab(text=None, **kwargs)
        else:
            return super().add_tab(widget=widget)
        
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
            
    def set_options(self):
        self.option_add('*tearOff', False)

    def _add_default_tab(self, text=None, frame_kwargs={}, textpad_kwargs={}, tab_kwargs={}):
        child = tk.Frame(self, **frame_kwargs)
        new_tab = super().add_tab(widget=child, text=text, tab_kwargs=tab_kwargs)

        pad = TextPad(child, **textpad_kwargs)
        pad.pack(expand=True, fill=tk.BOTH)

        self.bind_child_keys(pad)

        return new_tab, child, pad
            
            
class _TextpadTabPopup(tk.Menu):
    
    def __init__(self, parent, tab_index):
        super().__init__(parent)
        self.parent = parent
        self.tab_index = tab_index
        
        self.add_command(label="Save", command=self.save_tab)
        self.add_command(label="Save As", command=self.save_tab_as)
        self.add_separator()
        self.add_command(label="Close", command=self.close_tab)
        
    def close_tab(self, event=None):
        self.parent.close_tab(self.tab_index)
        
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
