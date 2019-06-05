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

    @staticmethod
    def simple_filter(run, column, inc):
        """Add increment 'inc' to run[column]"""
        run.loc[:, column] = run.loc[:, column] + inc

    def test_filter_no_errors(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(self.simple_filter, 'A', 3)

    def test_filter_set_is_filtered_attribute(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(self.simple_filter, 'A', 3)
        self.assertTrue(run.is_filtered)

    def test_filter_get_stored_filter(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(self.simple_filter, 'A', 3)
        f = run.filters.funcs['simple_filter']
        self.assertTrue(f is self.simple_filter)

    def test_filter_getitem_stored_filter(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(self.simple_filter, 'A', 3)
        f = run.filters['simple_filter']
        self.assertTrue(f is self.simple_filter)

    def test_filter_get_stored_args(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(self.simple_filter, 'A', 3)
        args = run.filters.args['simple_filter']
        self.assertEqual(args, ('A', 3))

    def test_filter_modifies_run_in_place(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        orig_values = run['A'].tolist()
        run.filter_data(self.simple_filter, 'A', 3)
        new_values = run['A'].tolist()
        self.assertTrue(all(x-3. == y for x, y in zip(new_values, orig_values)))

    def test_filter_clear_filter_collector(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        orig_values = run['A'].tolist()
        run.filter_data(self.simple_filter, 'A', 3)
        self.assertNotAlmostEqual(orig_values[0], run['A'][0])  # make sure run changed
        run.filters.clear()
        self.assertTrue(run.filters.funcs == {})
        self.assertTrue(run.filters.args == {})
        self.assertTrue(run.filters.kwargs == {})

    def test_filter_unfilter(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        orig_values = run['A'].tolist()
        run.filter_data(self.simple_filter, 'A', 3)
        self.assertNotAlmostEqual(orig_values[0], run['A'][0])
        run.unfilter()
        new_values = run['A'].tolist()
        self.assertTrue(x == y for x, y in zip(orig_values, new_values))

    def test_filter_unfilter_removes_added_data(self):
        def add_column(df, column, inc, new_column='Z'):
            df.loc[:, column] = df.loc[:, column] + inc
            df[new_column] = 99
            df.loc[100] = [1., 2., 3., 4., 5., 6., 7.]
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(add_column, 'A', 3)
        self.assertTrue(len(run['Z']) == len(run['B']))
        self.assertTrue(100 in run.index)
        run.unfilter()
        self.assertTrue('Z' not in run.columns)
        self.assertTrue(100 not in run.index)

    def test_filter_unfilter_removes_copy_reference(self):
        run = Run.read_csv(self.TEST_DATA_FILEPATH)
        run.filter_data(self.simple_filter, 'A', 3)
        self.assertIsNotNone(run._original_run)
        run.unfilter()
        self.assertIsNone(run._original_run)

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
