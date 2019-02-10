import tkinter as tk

from .textpad_config import TextPadConfig


class TextPad(tk.Text):
    
    def __init__(self, parent=None,
                       autoseparators=True,
                       config=TextPadConfig,
                       maxundo=-1,
                       undo=True,
                       **kwargs):
        super().__init__(parent, autoseparators=autoseparators, maxundo=maxundo, undo=undo, **kwargs)
        
        self.storeobj  = {}
        self.functions = {}
        self.connect_external_module_features(config)
        self.pack(expand=True, fill=tk.BOTH)
        
    def connect_external_module_features(self, config):
        config.connect(self)
        
        
if __name__ == "__main__":
    root = tk.Tk(className=" Test TextPad")
    tp = TextPad(root)
    print(type(tp.master))
    root.mainloop()
