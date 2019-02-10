import os

import tkinter as tk

from tkinter import ttk

from .textpad import TextPad


class TabbedTextpad(ttk.Notebook):

    NEW_TAB_BASENAME = "new%d"
    
    def __init__(self, parent, *args, tabposition='nw', **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        
        self.tab_widgets = {}
        self.set_options()
        self.bind_keys()
        self.add_tab()
        
    @property
    def tab_names(self):
        return [self.tab(name, option="text") for name in self.tabs()]
        
    def add_tab(self, event=None, text=None, frame_kwargs={}, textpad_kwargs={}, tab_kwargs={}):
        child = tk.Frame(self, **frame_kwargs)
        pad = TextPad(child, **textpad_kwargs)
        pad.pack(expand=True, fill=tk.BOTH)
        if text is None:
            i = 1
            text = self.NEW_TAB_BASENAME % i
            while text in self.tab_names:
                i += 1
                text = self.NEW_TAB_BASENAME % i
                
        old_tabs = self.tabs()
        self.add(child, text=text, **tab_kwargs)
        new_tab = [tab for tab in self.tabs() if tab not in old_tabs][0]
        self.tab_widgets[new_tab] = child
        self.bind_child_keys(pad)
        
    def bind_keys(self):
        for key in ['<Control-n>', '<Control-N>']:
            self.bind(key, self.add_tab)
        self.bind('<Button-3>', self.on_right_click)
            
    def bind_child_keys(self, child):
        for key in ['<Control-n>', '<Control-N>']:
            child.bind(key, self.add_tab)
            
    def close_tab(self, index):
        self.forget(index)
        if len(self.tab_names) == 0:
            self.add_tab()
            
    def get_frame(self, index):
        return self.tab_widgets[self.tabs()[index]]
    
    def get_widget(self, index, widget='!textpad'):
        return self.get_frame(index).children[widget]
        
    def on_right_click(self, event=None):
        if event.widget.identify(event.x, event.y) == 'label':
            index = event.widget.index('@%d,%d' % (event.x, event.y))
            popup = TabPopup(self, index)
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
            
            
class TabPopup(tk.Menu):
    
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
