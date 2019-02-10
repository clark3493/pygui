import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmb


class FileHandler(object):
    
    def __init__(self, text):
        self.text = text
        self.text.storeobj['OpenFilepath'] = None
        self.store_functions()
        self.store_objects()
        self.bind_keys()
        
    def bind_keys(self):
        for key in ['<Control-S>', '<Control-s>']:
            self.text.bind(key, self.save_file)
        for key in ['<Control-Shift-S>', '<Control-Shift-S>']:
            self.text.bind(key, self.save_file_as)
        for key in ['<Control-O>', '<Control-o>']:
            self.text.bind(key, self.open_file)
        self.text.bind('<<Modified>>', self.on_change)
            
    def store_functions(self):
        self.text.functions['open_file'] = self.open_file
        self.text.functions['save_file'] = self.save_file
        self.text.functions['save_file_as'] = self.save_file_as
        
    def store_objects(self):
        self.text.storeobj['modified'] = False
        
    def on_change(self, event=None):
        self.text.storeobj['modified'] = True
    
    def open_file(self, event=None):
        if self.text.storeobj['modified']:
            if not tkmb.askokcancel("Open?", "Opening a file will cause any unsaved changes to be lost. Continue?") and \
                self.text.storeobj['modified']:
                return
        path = tkfiledialog.askopenfilename()
        if path:
            data = open(path, 'rb').read()
            self.text.delete('1.0', tk.END)
            self.text.insert('1.0', data)
            self.text.storeobj['OpenFilepath'] = path
            
    def save_file(self, event=None):
        if not self.text.storeobj['OpenFilepath']:
            path = tkfiledialog.asksaveasfilename()
        else:
            path = self.text.storeobj['OpenFilepath']
        self._save_file(path)
        return path
            
    def save_file_as(self, event=None):
        path = tkfiledialog.asksaveasfilename()
        self._save_file(path)
        return path
            
    def _save_file(self, path):
        if path:
            data = self.text.get('1.0', tk.END)
            with open(path, 'w') as f:
                f.write(data)
            self.text.storeobj['OpenFilepath'] = path
            self.text.storeobj['modified'] = False
            
            
if __name__ == "__main__":
    root = tk.Tk()
    pad = tk.Text(root)
    pad.pack()
    pad.storeobj = {}
    pad.functions = {}
    FileHandler(pad)
    root.mainloop()
