import tkinter as tk


class StationeryFunctions(object):
    
    def __init__(self, text, select_background="skyblue"):
        self.text = text
        self.text.storeobj["select_background"] = select_background
        self.set_options()
        self.bind_keys()
        self.bound_function_config()
        self.store_functions()
        
    def bind_keys(self):
        for key in ["<Control-a>", "<Control-A>"]:
            self.text.master.bind(key, self.select_all)
        for key in ["<Button-1>", "<Return>"]:
            self.text.master.bind(key, self.deselect_all)
        for key in ["<Control-y>"]:
            self.text.master.bind(key, self.redo)
        for key in ["<Control-z>"]:
            self.text.master.bind(key, self.undo)
            
    def bound_function_config(self):
        self.text.tag_configure("sel", background=self.text.storeobj["select_background"])
            
    def copy(self, event=None):
        self.text.event_generate("<<Copy>>")
        
    def cut(self, event=None):
        self.text.event_generate("<<Cut>>")
        
    def deselect_all(self, event=None):
        self.text.tag_remove("sel", "1.0", "end")
    
    def paste(self, event=None):
        self.text.event_generate("<<Paste>>")
        
    def redo(self, event=None):
        self.text.event_generate("<<Redo>>")
        
    def select_all(self, event=None):
        self.text.tag_add("sel", "1.0", "end")
            
    def set_options(self):
        self.text.unod = True
        self.text.autoseparators = True
        self.text.maxundo = -1
        
    def store_functions(self):
        self.text.storeobj['Copy']        = self.copy
        self.text.storeobj['Cut']         = self.cut
        self.text.storeobj['Paste']       = self.paste
        self.text.storeobj['Undo']        = self.undo
        self.text.storeobj['Redo']        = self.redo
        self.text.storeobj['SelectAll']   = self.select_all
        self.text.storeobj['DeselectAll'] = self.deselect_all
        
    def undo(self, event=None):
        self.text.event_generate("<<Undo>>")
