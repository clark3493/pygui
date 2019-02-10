import tkinter as tk


class Popup(object):
    
    def __init__(self, text):
        self.text = text
        self.bind_keys()
        self.generate_menu()
        
    def bind_keys(self):
        self.text.bind("<Button-3>", self.show_menu_)
        
    def generate_menu(self):
        self.menu = tk.Menu(self.text.master)
        self.menu.add_command(label="Copy", command=self.text.storeobj['Copy'])
        self.menu.add_command(label="Cut", command=self.text.storeobj['Cut'])
        self.menu.add_command(label="Paste", command=self.text.storeobj['Paste'])
        self.menu.add_separator()
        self.menu.add_command(label="Select All", command=self.text.storeobj['SelectAll'])
        
    def show_menu_(self, event=None):
        self.menu.tk_popup(event.x, event.y)
