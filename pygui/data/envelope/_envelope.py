import os
import sys

import collections
import numpy as np
import pickle
import warnings

from copy import deepcopy
from scipy.spatial import ConvexHull
from uuid import uuid4

SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from data import Run
from widget.plot import PickableAxes


PointRef = collections.namedtuple('PointRef', ['run_name', 'index'])


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
                 run_info=None,
                 **kwargs):
        if not any(isinstance(runs, o) for o in (list, tuple)):
            runs = [runs]

        if all(x is None for x in runs):
            raise ValueError("Must provide at least one active Run to the Envelope constuctor")

        self.info = _EnvelopeInfo(self, xname, yname, *args, name=name, description=description,
                                  keep_all=keep_all, incremental=incremental, **kwargs)

        self._refs = []
        self._runs = {}
        self._run_info = {}

        inc = True if (len(runs) > 1 or incremental is True) else False

        for run0_index, run in enumerate(runs):
            if run is not None:
                break

        points = self._stack_points(run[self.info.xname], run[self.info.yname])
        super().__init__(points, *args, incremental=inc, **kwargs)
        self._store_run(run)

        for i, run in enumerate(runs):
            if i != run0_index:
                info = None if run_info is None else run_info[i]
                self.add_run(run, info=info)

        if inc and not incremental:
            self.close()

    @property
    def closed_vertices(self):
        return np.hstack([self.vertices, [self.vertices[0]]])

    @property
    def perimeter(self):
        return self.points[self.closed_vertices, :]

    @property
    def refs(self):
        return self._refs

    @property
    def runs(self):
        return self._runs

    @property
    def run_info(self):
        return self._run_info

    def absorb_envelopes(self, envelopes):
        if not any(isinstance(envelopes, o) for o in (list, tuple)):
            envelopes = [envelopes]
        for env in envelopes:
            self._absorb_envelope(env)

    def add_run(self, run, info=None):
        self._store_run(run, info=info)
        if run is not None:
            x = run[self.info.xname]
            y = run[self.info.yname]
            points = self._stack_points(x, y)
            self.add_points(points)
            if not self.info.keep_all:
                self._clean_runs()

    def close(self):
        super().close()
        self.info._incremental = False

    @classmethod
    def from_envelope_data(cls, filepath, **kwargs):
        with open(filepath, 'rb') as f:
            data = pickle.load(f, **kwargs)
        runs = []
        run_info = []
        for key, run in data['runs'].items():
            info = data['run_info'][key]
            if run is not None:
                # DataFrame sub-classed attributes do not get pickled
                #   have to re-initialize the Run object from the pickled DataFrame
                name = info.name
                description = info.description
                filepath = info.filepath
                run = Run(run, name=name, description=description, filepath=filepath)
            runs.append(run)
            run_info.append(info)
        run_info = None if all(x is None for x in run_info) else run_info
        info = data['info']
        env = Envelope(info.xname,
                       info.yname,
                       runs,
                       *info._initialization_args,
                       description=info.description,
                       incremental=info.incremental,
                       name=info.name,
                       keep_all=info.keep_all,
                       run_info=run_info,
                       **info._initialization_kwargs)
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
        data['info'] = self.info.to_persistent_info()
        data['runs'] = self.runs
        data['run_info'] = self.run_info
        return data

    def get_envelope_points(self, closed=False):
        v = self.get_vertices(closed=closed)
        return self.points[v, :]

    def get_envelope_refs(self, closed=False):
        return [self.refs[v] for v in self.get_vertices(closed=closed)]

    def get_envelope_runs(self, closed=False):
        for ref in self.get_envelope_refs(closed=closed):
            yield self.runs[ref.run_name]

    def get_envelope_run_indices(self, closed=False):
        return [self.refs[v].index for v in self.get_vertices(closed=closed)]

    def get_envelope_run_names(self, closed=False):
        return [ref.run_name for ref in self.get_envelope_refs(closed=closed)]

    def get_vertices(self, closed=False):
        return self.closed_vertices if closed else self.vertices

    def plot(self, ax, *args, **kwargs):
        p = self.perimeter
        if isinstance(ax, PickableAxes):
            parents = list(self.get_envelope_runs(closed=True))
            indices = list(self.get_envelope_run_indices(closed=True))
            ax.plot(p[:, 0], p[:, 1], *args, parent=parents, indices=indices, **kwargs)
        else:
            ax.plot(p[:, 0], p[:, 1], *args, **kwargs)

    def save_envelope_data(self, filepath, **kwargs):
        if not filepath.endswith(".pkl"):
            warnings.warn("Pickling envelope data to a filepath without a '.pkl' extension: %s" % filepath)
        data = self.get_envelope_data()
        with open(filepath, 'wb') as f:
            pickle.dump(data, f, **kwargs)

    def _absorb_envelope(self, env):
        for name, run in env.runs.items():
            run_info = env.run_info[name]
            self.add_run(run, info=run_info)

    def _clean_runs(self):
        envelope_run_names = self.get_envelope_run_names()
        for name in self.runs.keys():
            if name not in envelope_run_names:
                self.runs[name] = None

    @staticmethod
    def _stack_points(*args):
        arrs = [np.array(x).reshape((len(x), 1)) for x in args]
        return np.hstack(arrs)

    def _store_refs(self, run):
        assert run is not None
        for index in run.index:
            self.refs.append(PointRef(run_name=run.run_info.name, index=index))

    def _store_run(self, run, info=None):
        if run is None and info is None:
            raise ValueError("Must provide a _RunInfo object if no run is provided")

        if run is not None:
            try:
                self.runs[run.run_info.name] = run
                self.run_info[run.run_info.name] = run.run_info
                self._store_refs(run)
            except AttributeError:
                print(run)
                print(type(run))
                print(dir(run))
                print(run.run_info)
                raise
        else:
            self.runs[info.name] = run
            self.run_info[info.name] = info


class _PersistentEnvelopeInfo(object):

    def __init__(self, xname, yname, *args, name=None, description="", keep_all=False,
                 incremental=True, **kwargs):
        self.xname = xname
        self.yname = yname
        self.name = name if name is not None else uuid4()
        self.description = description
        self.keep_all = keep_all
        self._incremental = incremental
        self._initialization_args = args
        self._initialization_kwargs = kwargs

    @property
    def incremental(self):
        return self._incremental


class _EnvelopeInfo(_PersistentEnvelopeInfo):

    def __init__(self, envelope, *args, **kwargs):
        self.envelope = envelope
        super().__init__(*args, **kwargs)

    def to_persistent_info(self):
        return _PersistentEnvelopeInfo(self.xname,
                                       self.yname,
                                       *self._initialization_args,
                                       name=self.name,
                                       description=self.description,
                                       keep_all=self.keep_all,
                                       incremental=self.incremental,
                                       **self._initialization_kwargs)


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
