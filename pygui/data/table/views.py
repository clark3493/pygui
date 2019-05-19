import numpy as np

from ._table import Table


class ArrayTableView(Table):

    def __init__(self, parent, array, **kwargs):
        array = self._prep_array(array)
        assert len(array.shape) == 2

        nrows, ncols = array.shape
        super().__init__(parent, nrows=nrows, ncols=ncols, data=array, **kwargs)

    @staticmethod
    def _prep_array(array):
        array = np.array(array)
        if len(array.shape) > 2:
            raise ValueError("Array greater than 2 or greater than 1 dimensions are not currently supported")

        if len(array.shape) == 1:
            array = array.reshape((1, array.shape[0]))

        return array
