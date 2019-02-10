import sys

from contextlib import contextmanager


@contextmanager
def redirect(stdin=sys.stdin, 
             stdout=sys.stdout,
             stderr=sys.stderr, 
             displayhook=sys.displayhook,
             excepthook=sys.excepthook):
    sys.stdin       = stdin
    sys.stdout      = stdout
    sys.stderr      = stderr
    sys.displayhook = displayhook
    sys.excepthook  = excepthook
    
    try:
        yield
    finally:
        sys.stdin       = sys.__stdin__
        sys.stdout      = sys.__stdout__
        sys.stderr      = sys.__stderr__
        sys.displayhook = sys.__displayhook__
        sys.excepthook  = sys.__excepthook__
