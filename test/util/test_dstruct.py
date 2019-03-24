import os
import sys

import unittest

SRCDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pygui")
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)

from util.dstruct import DictObserver


class DstructUtilTestCase(unittest.TestCase):

    def test_dict_observer(self):
        d = {'a': 1, 'b': 2}
        def callback(obj):
            raise RuntimeError
        observer = DictObserver(d, callback=callback)
        with self.assertRaises(RuntimeError):
            d['c'] = 3


if __name__ == '__main__':
    unittest.main()
