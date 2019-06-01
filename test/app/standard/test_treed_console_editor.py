import os
import sys

import logging
import tkinter as tk

LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
SRC_DIR = os.path.join(os.path.dirname(TEST_DIR), "pygui")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.standard.treed_console_editor import TreedConsoleEditor

history_filepath = os.path.join(LOCAL_DIR, "treed_console_editor.log")
if os.path.exists(history_filepath):
    os.remove(history_filepath)

root = tk.Tk()
root.geometry("800x600")
tce = TreedConsoleEditor(root, history_filepath=history_filepath)
tce.console.set_history_loglevel(logging.DEBUG)
root.mainloop()
