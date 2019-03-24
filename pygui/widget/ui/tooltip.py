import tkinter as tk

import threading
import time
            
            
class HoverTimer(object):
    
    def __init__(self, widget, delay=1, **kwargs):
        self.widget = widget
        self.delay = delay
        
        self.start_time = None
        self.hover_time = -1.
        self.active = False
        
        self.widget.bind('<Enter>', self.clock_main)
        self.widget.bind('<Leave>', self.kill_clock)
        
    def clock(self):
        self.active = True
        self.start_time = time.time()
        while self.active:
            self.hover_time = time.time() - self.start_time
            time.sleep(0.05)
            
    def clock_main(self, event=None):
        threading.Thread(target=self.clock).start()
        
    def kill_clock(self, event=None):
        self.active = False
        self.start_time = None
        self.hover_time = -1.
            
    
class ToolTip(HoverTimer):
    
    def __init__(self, widget, text=None, **kwargs):
        super().__init__(widget, **kwargs)
        
        self.widget = widget
        self.text = text
        
        self.tipwindow = None
        
        self.widget.bind('<Enter>', self.showtip_main)
        self.widget.bind('<Leave>', self.hidetip)
        
    def showtip(self):
        """Display text in tooltip window."""
        while self.active:
            if self.hover_time > self.delay:
                if self.tipwindow or not self.text:
                    return
                x, y, cx, cy = self.widget.bbox("insert")
                x = x + self.widget.winfo_rootx() + 28
                y = y + cy + self.widget.winfo_rooty() + 28
                self.tipwindow = tw = tk.Toplevel(self.widget)
                tw.wm_overrideredirect(1)
                tw.wm_geometry("+%d+%d" % (x, y))
                
                label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                                 background="#ffffe0", relief=tk.SOLID,
                                 borderwidth=1, font=("tahoma", "8", "normal"))
                label.pack(ipadx=1)
        
    def showtip_main(self, event=None):
        self.clock_main()
        threading.Thread(target=self.showtip).start()
        return "break"
        
    def hidetip(self, event=None):
        self.kill_clock()
        tw = self.tipwindow
        self.tipwindow = None
        self.active = False
        if tw:
            tw.destroy()
        return "break"
