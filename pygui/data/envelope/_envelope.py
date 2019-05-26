import os
import sys

import collections
import numpy as np
import pickle

from copy import deepcopy
from scipy.spatial import ConvexHull
from uuid import uuid4

SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from data import Run
from widget.plot import PickableAxes


PointRef = collections.namedtuple('PointRef', ['run', 'run_id', 'index'])


class Envelope(ConvexHull):

    def __init__(self,
                 xname,
                 yname,
                 runs,
                 *args,
                 description="",
                 incremental=True,
                 name=None,
                 keep_all=False,
                 **kwargs):
        self.xname = xname
        self.yname = yname

        self.name = name if name is not None else uuid4()
        self.description = description
        self.keep_all = keep_all

        # store information for data persistence and envelope re-creation
        self._incremental = incremental
        self._initialization_args   = args
        self._initialization_kwargs = kwargs

        if not any(isinstance(runs, o) for o in (list, tuple)):
            runs = [runs]

        if all(x is None for x in runs):
            raise ValueError("Must provide at least one active Run to the Envelope constuctor")

        self._refs = []
        self._runs = []

        inc = True if (len(runs) > 1 or incremental is True) else False

        for run_index, run in enumerate(runs):
            self.runs.append(run)
            if run is not None:
                run0 = run
                break
            else:
                self._store_refs(run)

        points0 = self._stack_points(run0[xname], run0[yname])
        super().__init__(points0, *args, incremental=inc, **kwargs)

        self._store_refs(run0)
        for i, run in enumerate(runs[run_index+1:]):
            self.add_run(run)

        if inc and not incremental:
            self.close()

    @property
    def closed_vertices(self):
        return np.hstack([self.vertices, [self.vertices[0]]])

    @property
    def incremental(self):
        return self._incremental

    @property
    def perimeter(self):
        return self.points[self.closed_vertices, :]

    @property
    def refs(self):
        return self._refs

    @property
    def runs(self):
        return self._runs

    def absorb_envelopes(self, envelopes):
        if not any(isinstance(envelopes, o) for o in (list, tuple)):
            envelopes = [envelopes]
        for env in envelopes:
            self._absorb_envelope(env)

    def add_run(self, run):
        self._store_refs(run)
        self.runs.append(run)
        if run is not None:
            x = run[self.xname]
            y = run[self.yname]
            points = self._stack_points(x, y)
            vertices0 = self.vertices.copy()
            super(Envelope, self).add_points(points)
            if not self.keep_all:
                self._clean_refs(vertices0)

    def close(self):
        super().close()
        self._incremental = False

    def envelope_indices(self, closed=False):
        vertices = self.closed_vertices if closed else self.vertices
        return [self.refs[vertex].index for vertex in vertices]

    def envelope_points(self, closed=False):
        v = self.closed_vertices if closed else self.vertices
        return self.points[v, :]

    def envelope_refs(self, closed=False):
        for index in self.envelope_indices(closed=closed):
            yield self.refs[index]

    def envelope_runs(self, closed=False):
        for index in self.envelope_indices(closed=closed):
            assert self.refs[index].run is not None
            yield self.runs[self.refs[index].run_id]

    def envelope_x(self, closed=False):
        v = self.closed_vertices if closed else self.vertices
        return self.points[v, 0]

    def envelope_y(self, closed=False):
        v = self.closed_vertices if closed else self.vertices
        return self.points[v, 1]

    @classmethod
    def from_envelope_data(cls, filepath, **kwargs):
        with open(filepath, 'rb') as f:
            data = pickle.load(f, **kwargs)
        env = Envelope(data['xname'],
                       data['yname'],
                       data['runs'],
                       *data['initialization_args'],
                       description=data['description'],
                       incremental=data['incremental'],
                       name=data['name'],
                       keep_all=data['keep_all'],
                       **data['initialization_kwargs'])
        return env

    @classmethod
    def from_file(cls,
                  xname,
                  yname,
                  filepath,
                  *args,
                  name=None,
                  description="",
                  run_name=None,
                  run_description="",
                  run_kwargs={},
                  **kwargs):
        run = Run.read_csv(filepath, name=run_name, description=run_description, **run_kwargs)
        return Envelope(xname, yname, run, *args, name=name, description=description, **kwargs)

    def get_envelope_data(self):
        data = {}
        data['xname']       = self.xname
        data['yname']       = self.yname
        data['name']        = self.name
        data['description'] = self.description
        data['keep_all']    = self.keep_all
        data['incremental'] = self.incremental
        data['runs']        = self.runs
        data['initialization_args']   = self._initialization_args
        data['initialization_kwargs'] = self._initialization_kwargs
        return data

    def plot(self, ax, *args, **kwargs):
        if isinstance(ax, PickableAxes):
            parents = list(self.envelope_runs(closed=True))
            indices = list(self.envelope_indices(closed=True))
            ax.plot(self.perimeter[:, 0], self.perimeter[:, 1], parent=parents, indices=indices, *args, **kwargs)
        else:
            ax.plot(self.perimeter[:, 0], self.perimeter[:, 1], *args, **kwargs)

    def save_envelope_data(self, filepath, **kwargs):
        assert filepath.endswith(".pkl")
        data = self.get_envelope_data()
        with open(filepath, 'wb') as f:
            pickle.dump(data, f, **kwargs)

    def _absorb_envelope(self, env):
        for run in env.runs:
            self.add_run(run)

    def _clean_refs(self, indices):
        cleaned_ids = []
        for index in indices:
            if index not in self.vertices:
                old_ref = self.refs[index]
                self.refs[index] = PointRef(run=None, run_id=old_ref.run_id, index=None)
                cleaned_ids.append(old_ref.run_id)
        active_run_ids = list(set([ref.run_id for ref in self.refs if ref.run is not None]))
        for cid in cleaned_ids:
            if cid not in active_run_ids:
                self.runs[cid] = None

    def _get_max_run_id(self):
        try:
            return self.refs[-1].run_id
        except IndexError:
            return -1

    @staticmethod
    def _stack_points(*args):
        arrs = [np.array(x).reshape((len(x), 1)) for x in args]
        return np.hstack(arrs)

    def _store_refs(self, run):
        run_id = self._get_max_run_id() + 1
        len0 = len(self.refs)
        if run is None:
            self.refs.append(PointRef(run=run, run_id=run_id, index=None))
        else:
            for i in range(run.shape[0]):
                itotal = len0 + i
                runref = run if (itotal in self.vertices or self.keep_all) else None
                iref = None if runref is None else run.index[i]
                self.refs.append(PointRef(run=runref, run_id=run_id, index=iref))


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
            envelopes = [envelopes]

        self.full_envelope.absorb_envelopes(envelopes)

    def _initialize_full_envelope(self):
        env0 = deepcopy(self.envelopes[0])
        env0.name = self.name
        env0.description = self.description

        env0.absorb_envelopes(self.envelopes[1:])
        self._full_envelope = env0
