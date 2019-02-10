import sys

import traceback


ALWAYS_RAISE = (KeyboardInterrupt,)


def print_error(exc_type, exc_value, exc_traceback, *args):
    if any(issubclass(exc_type, c) for c in ALWAYS_RAISE):
        # let the system handle important exceptions
        sys.__excepthook__(*args)
    sys.stderr.write(traceback.format_exc())
