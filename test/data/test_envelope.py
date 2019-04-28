import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import unittest

SRCDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pygui")
if SRCDIR not in sys.path:
    sys.path.insert(0, SRCDIR)

from data import Run
from data.envelope import Envelope
from data.envelope.mpi import MultiProcessEnvelopeGenerator


class EnvelopeTestCase(unittest.TestCase):

    TESTDIR = os.path.dirname(os.path.abspath(__file__))
    TEST_DATA1 = os.path.join(TESTDIR, "test_data.csv")
    TEST_DATA2 = os.path.join(TESTDIR, "test_data2.csv")

    def assertAllClose(self, a, b):
        self.assertTrue(np.allclose(a, b))

    def setup_run1(self):
        return Run.read_csv(self.TEST_DATA1)

    def setup_run2(self):
        return Run.read_csv(self.TEST_DATA2)

    def test_closed_vertices_envelope1(self):
        run = self.setup_run1()
        env = Envelope('A', 'B', [run])
        expected = [2, 1, 4, 5, 0, 6, 2]
        self.assertAllClose(expected, env.closed_vertices)

    def test_create_envelope(self):
        run1 = self.setup_run1()
        env = Envelope('A', 'B', [run1])
        self.assertEqual(Envelope, type(env))

    def test_create_envelope_multiple_runs(self):
        run1 = self.setup_run1()
        run2 = self.setup_run2()
        env = Envelope('A', 'B', [run1, run2])
        self.assertEqual(Envelope, type(env))

    @unittest.skip
    def test_envelope_indices_1(self):
        run = self.setup_run1()
        env = Envelope('A', 'B', run)
        for index in env.envelope_indices():
            print(index)

    @unittest.skip
    def test_envelope_refs_1(self):
        run = self.setup_run1()
        env = Envelope('A', 'B', run)
        for run, index in env.envelope_refs():
            print(run)
            print(index)

    @unittest.skip
    def test_envelope_runs_1(self):
        run = self.setup_run1()
        env = Envelope('A', 'B', run)
        for parent in env.envelope_runs():
            print(parent)

    @unittest.skip
    def test_get_envelope_parent_data_1C(self):
        run = self.setup_run1()
        env = Envelope('A', 'B', run)
        print(env.get_run_data('C'))

    def test_pass_in_run_instead_of_list(self):
        run = self.setup_run1()
        env = Envelope('A', 'B', run)
        self.assertTrue(type(env) is Envelope)

    @unittest.skip
    def test_plot_envelope_multiple_runs(self):
        run1 = self.setup_run1()
        run2 = self.setup_run2()
        env1 = Envelope('A', 'B', [run1])
        env2 = Envelope('A', 'B', [run1, run2])
        env3 = Envelope('A', 'B', [run2])
        fig, ax = plt.subplots(1, 1)
        env1.plot(ax, label="1")
        env3.plot(ax, label="2")
        env2.plot(ax, label="1+2")
        ax.legend()
        plt.show()

    @unittest.skip
    def test_plot_envelope_pickable_plot(self):
        run1 = self.setup_run1()
        run2 = self.setup_run2()
        env = Envelope('A', 'B', [run1, run2])
        ax = plt.subplot(111, projection='pickable')
        ax.options.annotation_data = ['C', 'D']
        env.plot(ax)
        for vertex in env.vertices:
            ax.text(env.points[vertex, 0], env.points[vertex, 1], str(vertex))
        plt.show()

    @unittest.skip
    def test_plot_absorb_envelope(self):
        run1 = self.setup_run1()
        run2 = self.setup_run2()
        env1 = Envelope('A', 'B', run1)
        env2 = Envelope('A', 'B', run2)
        env1.absorb_envelopes(env2)
        ax = plt.subplot(111, projection='pickable')
        ax.options.annotation_data = ['C', 'D']
        env1.plot(ax)
        plt.show()

    def test_multiprocess_enveloper(self):
        filepaths = [self.TEST_DATA1, self.TEST_DATA2]
        mpeg = MultiProcessEnvelopeGenerator(ncpus=2)
        env = mpeg.compute_envelope('A', 'B', filepaths)
        ax = plt.subplot(111, projection='pickable')
        ax.options.annotation_data = ['C', 'D']
        env.plot(ax)
        for vertex in env.vertices:
            ax.text(env.points[vertex, 0], env.points[vertex, 1], str(vertex))
        plt.show()


if __name__ == '__main__':
    unittest.main()
