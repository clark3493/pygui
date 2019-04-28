import os

import multiprocessing as mp

from . import Envelope

# TODO: IMPLEMENT ABILITY TO HANDLE DIFFERENT XNAME/YNAME PER FILEPATH


class MultiProcessEnvelopeGenerator(object):

    def __init__(self, ncpus=None):
        self.ncpus = ncpus if ncpus is not None else mp.cpu_count()

    def compute_envelope(self, xname, yname, filepaths):
        pool = mp.Pool(processes=self.ncpus)
        env0 = Envelope.from_file(xname, yname, filepaths[0])
        inputs = [(xname, yname, filepath) for filepath in filepaths[1:]]
        data = pool.starmap(self.get_envelope_data, inputs)
        for x, y, parents, indices in data:
            env0.add_points(x, y, parents, indices)
        return env0

    @staticmethod
    def get_envelope_data(xname, yname, filepath):
        env = Envelope.from_file(xname, yname, filepath)
        return (env.envelope_x(closed=False),
                env.envelope_y(closed=False),
                env.envelope_runs(closed=False),
                env.envelope_indices(closed=False))

