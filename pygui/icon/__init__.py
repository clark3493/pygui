import os


__all__ = ['RUN_ICON_PATH',
           'RUN_ONE_ICON_PATH']

_dirname = os.path.dirname(os.path.abspath(__file__))

RUN_ICON_PATH     = os.path.join(_dirname, "run.png")
RUN_ONE_ICON_PATH = os.path.join(_dirname, "run_one.png")
