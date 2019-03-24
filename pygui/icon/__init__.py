import os


__all__ = ['NEW_FILE_ICON_PATH',
           'OPEN_FILE_ICON_PATH',
           'PYTHON_ICON_PATH',
           'RUN_ICON_PATH',
           'RUN_ONE_ICON_PATH',
           'SAVE_FILE_ICON_PATH',
           'SAVE_FILE_AS_ICON_PATH']

_dirname = os.path.dirname(os.path.abspath(__file__))

NEW_FILE_ICON_PATH     = os.path.join(_dirname, "new_file.png")
OPEN_FILE_ICON_PATH    = os.path.join(_dirname, "open_file.png")
PYTHON_ICON_PATH       = os.path.join(_dirname, "python_icon.png")
RUN_ICON_PATH          = os.path.join(_dirname, "run.png")
RUN_ONE_ICON_PATH      = os.path.join(_dirname, "run_one.png")
SAVE_FILE_ICON_PATH    = os.path.join(_dirname, "save_file.png")
SAVE_FILE_AS_ICON_PATH = os.path.join(_dirname, "save_file_as.png")
