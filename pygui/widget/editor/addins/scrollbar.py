import tkinter as tk


class Scrollbar(object):
    
    def __init__(self, text):
        self.frame = text.master
        self.text = text
        self.text.configure(wrap='none')
        self.for_x_view()
        self.for_y_view()
        
    def for_x_view(self):
        scroll_x = tk.Scrollbar(self.frame, orient='horizontal', command=self.text.xview)
        scroll_x.config(command=self.text.xview)
        self.text.configure(xscrollcommand=scroll_x.set)
        scroll_x.pack(side='bottom', fill='x', anchor='w')
        
    def for_y_view(self):
        scroll_y = tk.Scrollbar(self.frame)
        scroll_y.config(command=self.text.yview)
        self.text.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side='right', fill='y')
        
        
if __name__ == "__main__":
    root = tk.Tk()
    pad = tk.Text(root, wrap='none')
    sb = Scrollbar(pad)
    pad.pack()
    root.mainloop()
