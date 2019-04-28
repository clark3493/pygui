import os
import sys

import numpy as np
import pandas as pd
import unittest

SRCDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pygui")
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)

from data import Run, RunSet


class RunDataTestCase(unittest.TestCase):

    TESTDIR = os.path.dirname(os.path.abspath(__file__))
    TEST_DATA_FILEPATH = os.path.join(TESTDIR, "test_data.csv")

    def assertAllClose(self, a, b):
        self.assertTrue(np.allclose(a, b))

    def test_read_csv_returns_dataframe_instance(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        self.assertTrue(isinstance(run, pd.DataFrame))

    def test_read_csv_returns_run(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        self.assertTrue(isinstance(run, Run))

    def test_Run___setitem__single_value(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run['A'] = 3.
        a = run['A'].tolist()
        expected = [3., 3., 3., 3., 3., 3., 3., 3.]
        self.assertAllClose(a, expected)

    def test_Run___setitem__whole_column(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run['A'] = [3., 3., 3., 3., 3., 3., 3., 3.]
        a = run['A'].tolist()
        expected = [3., 3., 3., 3., 3., 3., 3., 3.]
        self.assertAllClose(a, expected)

    def test_RunSet_constructor(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        run2 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run2')
        runset = RunSet([run1, run2])
        self.assertTrue(isinstance(runset, RunSet))

    def test_RunSet___getitem__single_column(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        run2 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run2')
        runset = RunSet([run1, run2])
        data = runset['A']
        data1 = data['run1'].squeeze().tolist()
        data2 = data['run2'].squeeze().tolist()
        expected = [1., 9., 6., 4., 7., 3., 5., 4.]
        self.assertAllClose(data1, expected)
        self.assertAllClose(data2, expected)

    def test_RunSet___setitem__(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        run2 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run2')
        runset = RunSet([run1, run2])
        runset['A'] = 3.
        a1 = runset.runs['run1']['A'].tolist()
        a2 = runset.runs['run2']['A'].tolist()
        expected = [3., 3., 3., 3., 3., 3., 3., 3.]
        self.assertAllClose(expected, a1)
        self.assertAllClose(expected, a2)

    def test_RunSet_add_run(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        runset = RunSet()
        runset.add_run(run1)
        self.assertTrue('run1' in runset.runs)

    def test_RunSet_remove_run(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        runset = RunSet([run1])
        self.assertTrue('run1' in runset.runs)
        runset.remove_run('run1')
        self.assertFalse('run1' in runset.runs)

    def test_RunSet_remove_run_does_not_delete_actual_run(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        runset = RunSet([run1])
        runset.remove_run('run1')
        self.assertEqual(run1['A'][0], 1.)

    def test_RunSet_set_index(self):
        run1 = Run.read_csv(self.TEST_DATA_FILEPATH, name='run1')
        runset = RunSet([run1])
        runset.set_index('TIME')
        indices = run1.index.tolist()
        expected = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        self.assertAllClose(expected, indices)


if __name__ == '__main__':
    unittest.main()
