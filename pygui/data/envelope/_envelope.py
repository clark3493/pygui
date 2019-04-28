import os
import sys

import collections
import numpy as np

from scipy.spatial import ConvexHull
from copy import deepcopy
from uuid import uuid4

SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from data import Run
from widget.plot import PickableAxes


PointRef = collections.namedtuple('PointRef', ['run', 'index'])

# TODO: ADD ERROR CHECKING/HANDLING FOR ENVELOPES THAT HAVE DIFFERENT XNAMES/YNAMES
# TODO: ADD PLOT HANDLING FOR ENVELOPE SETS


class Envelope(ConvexHull):

    def __init__(self, xname, yname, runs, *args, description="", incremental=True, name=None, keep_all=False, **kwargs):
        self.xname = xname
        self.yname = yname

        self.name = name if name is not None else uuid4()
        self.description = description
        self.keep_all = keep_all

        if not any(isinstance(runs, o) for o in (list, tuple)):
            runs = [runs]

        if len(runs) > 1:
            incremental = True
        run0 = runs[0]
        points0 = self._stack_points(run0[xname], run0[yname])
        super().__init__(points0, *args, incremental=incremental, **kwargs)

        self._refs = []
        self._store_refs(run0)

        for run in runs[1:]:
            self.add_run(run)

    @property
    def closed_vertices(self):
        return np.hstack([self.vertices, [self.vertices[0]]])

    @property
    def perimeter(self):
        return self.points[self.closed_vertices, :]

    @property
    def refs(self):
        return self._refs

    def absorb_envelopes(self, envelopes):
        if not any(isinstance(envelopes, o) for o in (list, tuple)):
            envelopes = [envelopes]
        for env in envelopes:
            self._absorb_envelope(env)

    def add_points(self, x, y, parents, indices):
        assert len(x) == len(y) == len(parents) == len(indices)
        points = self._stack_points(x, y)
        len0 = len(self.refs)
        super(Envelope, self).add_points(points)
        for i, (parent, index) in enumerate(zip(parents, indices)):
            itotal = len0 + i
            runref = parent if (itotal in self.vertices or self.keep_all) else None
            iref = None if runref is None else index
            self.refs.append(PointRef(run=runref, index=iref))

    def add_run(self, run):
        x = run[self.xname]
        y = run[self.yname]
        points = self._stack_points(x, y)
        vertices0 = self.vertices.copy()
        super(Envelope, self).add_points(points)
        self._store_refs(run)
        if not self.keep_all:
            self._clean_refs(vertices0)

    def envelope_indices(self, closed=False):
        vertices = self.closed_vertices if closed else self.vertices
        return [self.refs[vertex].index for vertex in vertices]

    def envelope_refs(self, closed=False):
        for run, index in zip(self.envelope_runs(closed=closed), self.envelope_indices(closed=closed)):
            yield run, index

    def envelope_runs(self, closed=False):
        vertices = self.closed_vertices if closed else self.vertices
        return [self.refs[vertex].run for vertex in vertices]

    def envelope_x(self, closed=False):
        v = self.closed_vertices if closed else self.vertices
        return self.points[v, 0]

    def envelope_y(self, closed=False):
        v = self.closed_vertices if closed else self.vertices
        return self.points[v, 1]

    @classmethod
    def from_file(cls, xname, yname, filepath, *args, name=None, description="", run_name=None, run_description="", run_kwargs={}, **kwargs):
        run = Run.read_csv(filepath, name=run_name, description=run_description, **run_kwargs)
        return Envelope(xname, yname, run, *args, name=name, description=description, **kwargs)

    def get_run_data(self, names, closed=False):
        if isinstance(names, str):
            names = [names]
        return [run[names].iloc[i] for run, i in self.envelope_refs(closed=closed)]

    def plot(self, ax, *args, **kwargs):
        if isinstance(ax, PickableAxes):
            parents = list(self.envelope_runs(closed=True))
            indices = list(self.envelope_indices(closed=True))
            ax.plot(self.perimeter[:, 0], self.perimeter[:, 1], parent=parents, indices=indices, *args, **kwargs)
        else:
            ax.plot(self.perimeter[:, 0], self.perimeter[:, 1], *args, **kwargs)

    def _absorb_envelope(self, env):
        if self.keep_all:
            x = env.points[:, 0]
            y = env.points[:, 1]
            parents = [ref.run for ref in env.refs]
            indices = [ref.index for ref in env.refs]
        else:
            x = env.points[env.vertices, 0]
            y = env.points[env.vertices, 1]
            parents = list(env.envelope_runs(closed=False))
            indices = list(env.envelope_indices(closed=False))
        self.add_points(x, y, parents, indices)

    def _clean_refs(self, indices):
        for index in indices:
            if index not in self.vertices:
                self.refs[index] = PointRef(run=None, index=None)

    @staticmethod
    def _stack_points(*args):
        arrs = [np.array(x).reshape((len(x), 1)) for x in args]
        return np.hstack(arrs)

    def _store_refs(self, run):
        len0 = len(self.refs)
        for i in range(run.shape[0]):
            itotal = len0 + i
            runref = run if (itotal in self.vertices or self.keep_all) else None
            iref = None if runref is None else run.index[i]
            self.refs.append(PointRef(run=runref, index=iref))


class EnvelopeSet(object):

    def __init__(self, envelopes, name=None, description=""):
        self.envelopes = list(envelopes) if any(isinstance(envelopes, o) for o in (list, tuple)) else [envelopes]
        self.name = name if name is not None else uuid4()
        self.description = description

        self._full_envelope = None
        self._initialize_full_envelope()

    @property
    def full_envelope(self):
        return self._full_envelope

    def add_envelopes(self, envelopes):
        if not any(isinstance(envelopes, o) for o in (list, tuple)):
            envelopes = envelopes

        self.full_envelope.absorb_envelopes(envelopes)

    def _initialize_full_envelope(self):
        env0 = deepcopy(self.envelopes[0])
        env0.name = self.name
        env0.description = self.description

        env0.absorb_envelopes(self.envelopes[1:])
        self._full_envelope = env0
