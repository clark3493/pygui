import tkinter as tk


def initialize_preferences(app, *args, **kwargs):
    if 'prefernces' not in dir(app):
        pref = PreferencesWindow(app, *args, **kwargs)
        app.preferences = pref
    else:
        pref = app.preferences
    return pref


class PreferencesWindow(tk.Toplevel):

    def __init__(self, parent, *args, show=False, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.frames = {}

        self.listbox = tk.Listbox(self)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(selectmode=tk.SINGLE)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.container = tk.Frame(self)
        self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.geometry("600x400")
        self.title("Preferences")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        if not show:
            self.withdraw()

    def add_frame(self, name, frame):
        self.frames[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.listbox.insert(len(self.frames.keys()), name)
        frame.tkraise()

    def on_close(self):
        self.withdraw()
        return "break"

    def on_listbox_select(self, event):
        widget = event.widget
        index = int(widget.curselection()[0])
        name = widget.get(index)
        frame = self.frames[name]
        frame.tkraise()


if __name__ == "__main__":
    root = tk.Tk()
    pref = PreferencesWindow(root, show=True)
    b1 = tk.Button(pref.container, text="Button1", command=lambda: print("Button1"))
    b2 = tk.Button(pref.container, text="Button2", command=lambda: print("Button2"))
    pref.add_frame("1", b1)
    pref.add_frame("2", b2)
    root.mainloop()

