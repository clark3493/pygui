import tkinter as tk

from tkinter import TclError


class LineNumberCanvas(tk.Canvas):
    
    def __init__(self, *args, text_widget=None, breakpoints=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.text_widget = text_widget
        self.breakpoints = breakpoints
        
    def re_render(self):
        """Re-render the line number canvas."""
        self.delete('all') # to prevent drawing over the previous canvas
        
        temp = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(temp)
            if dline is None:
                break
            x, y = dline[0], dline[1]
            linenum = str(temp).split(".")[0]
            
            id = self.create_text(2, y, anchor="nw", text=linenum)
            
            if int(linenum) in self.breakpoints:
                x1,y1,x2,y2 = self.bbox(id)
                self.create_oval(x1,y1,x2,y2,fill='red')
                self.tag_raise(id)
                
            temp = self.text_widget.index("%s+1line" % temp)
            
    def get_breakpoint_number(self, event):
        if self.find_withtag('current'):
            i = self.find_withtag('current')[0]
            linenum = int(self.itemcget(i, 'text'))
            
            if linenum in self.breakpoints:
                self.breakpoints.remove(linenum)
            else:
                self.breakpoints.append(linenum)
            self.re_render()
            
            
class LineNumbers(object):
    
    def __init__(self, text, binding_keys=('<Down>', '<Up>', '<<Changed>>', '<Configure>')):
        self.text = text
        self.master = text.master
        self.mechanise()
        self._set_()
        self.bind_keys(binding_keys)
        
    def mechanise(self):
        i = 1
        worked = False
        while not worked:
            try:
                self.text.tk.eval('''
                    proc widget_interceptor {widget command args} {

                        set orig_call [uplevel [linsert $args 0 $command]]

                      if {
                            ([lindex $args 0] == "insert") ||
                            ([lindex $args 0] == "delete") ||
                            ([lindex $args 0] == "replace") ||
                            ([lrange $args 0 2] == {mark set insert}) || 
                            ([lrange $args 0 1] == {xview moveto}) ||
                            ([lrange $args 0 1] == {xview scroll}) ||
                            ([lrange $args 0 1] == {yview moveto}) ||
                            ([lrange $args 0 1] == {yview scroll})} {

                            event generate  $widget <<Changed>>
                        }

                        #return original command
                        return $orig_call
                    }
                    ''')
                self.text.tk.eval('''
                    rename {widget} new{n}
                    interp alias {{}} ::{widget} {{}} widget_interceptor {widget} new{n}
                '''.format(n=i, widget=str(self.text)))
                worked = True
            except TclError:
                i += 1
        
    def bind_keys(self, binding_keys=[]):
        for key in binding_keys:
            self.text.bind(key, self.changed)
        self.linenumbers.bind('<Button-1>', self.linenumbers.get_breakpoint_number)
        
    def changed(self, event):
        self.linenumbers.re_render()
        
    def _set_(self):
        self.linenumbers = LineNumberCanvas(self.master, text_widget=self.text, width=30)
        self.linenumbers.pack(side="left", fill="y")
        
        
if __name__ == "__main__":
    root = tk.Tk()
    l = tk.Text(root)
    LineNumbers(l)
    l.pack()
    root.mainloop()
