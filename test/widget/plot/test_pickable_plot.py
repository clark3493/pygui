import os
import sys
import unittest

import matplotlib.pyplot as plt

PROJ_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
SRC_DIR = os.path.join(PROJ_DIR, "pygui")
TEST_DIR = os.path.join(PROJ_DIR, "test")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from data import Run
from widget.plot import PickableAxes


class PickableAxesTestCase(unittest.TestCase):

    TEST_DATA1 = os.path.join(TEST_DIR, "data", "test_data.csv")
    TEST_DATA2 = os.path.join(TEST_DIR, "data", "test_data2.csv")

    def setup1(self):
        run = Run.read_csv(self.TEST_DATA1)
        return run

    def setup2(self):
        run = Run.read_csv(self.TEST_DATA2)
        return run

    #@unittest.skip
    def test_basic_plot_of_xydata(self):
        run = self.setup1()
        run2 = self.setup2()
        ax = plt.subplot(111, projection='pickable')
        ax.options.annotation_data = ['A', 'C', 'D']
        ax.plot(run['TIME'], run['B'], 'r-o', parent=run)
        ax.scatter(run2['TIME'], run2['B'], parent=run2)
        plt.show()


if __name__ == '__main__':
    unittest.main()
