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


# TODO: ADD EXAMPLES TO DOCUMENTATION


PointRef = collections.namedtuple('PointRef', ['run_name', 'index'])
"""
A simple object for holding information about each point within an envelope.

Parameters
----------
run_name: str
    The name of the run the associated point belongs to.
index: int
    The corresponding index within the parent Run for the associated point.
"""


class Envelope(ConvexHull):
    """
    An object for calculating and performing various operations on convex hulls of x,y data.

    Envelope is an extension of the scipy.spatial.ConvexHull class with functionality built in for plotting,
    accessing associated data from the data source, etc.

    Parameters
    ----------
    xname: str
        The name of the column within the provided Runs which should make up the 'x' data.
    yname: str
        The name of the column within the provided Runs which should make up the 'y' data.
    runs: pygui.data.run.Run or list(pygui.data.run.Run)
        The Runs which contain the data the Envelope should be built on.
    *args:
        Arbitrary positional arguments which are provided to the ConvexHull constructor after the points array.
    description: str, optional
        An optional description to store with the envelope for reports, documentation, etc. Default="".
    name: str or None, optional.
        The name of the Envelope. See Notes 1 and 2. Default=None.
    keep_all: bool, optional.
        Flag to keep all points from every single provided Run. See Note 3. Default=False.
    run_info: list(pygui.run._RunInfo) or None, optional.
        A list of RunInfo objects corresponding to each provided Run. See Note 4. Default=None.
    **kwargs:
        Arbitrary keyword arguments passed into the ConvexHull constructor.

    Notes
    -----
    .. [1] If a name is not provided to the Envelope constructor, a random unique string ID is generated with uuid.uuid4
    .. [2] If a name is provided by the user, it should be unique, as the names are used as dictionary keys for internal
           Envelope bookkeeping. Similar for Run names.
    .. [3] If the Envelope 'keep_all' flag is False, then only Runs which contain data that lie on the outer hull are
           stored. References within the envelope to Runs which contain no outer hull data are replaced by None,
           allowing the Run to be garbage collected if there are no external references.
    .. [4] In general, the user should not need to use the run_info optional keyword argument to the Envelope
           constructor. This is used when information about Runs which contain no data on the envelope hull should be
           tracked for posterity (ex: to retroactively determine what files were used in the Envelope generation). If an
           envelope with keep_all=False is saved to disk and then an Envelope is generated from that saved data, the
           Runs which were originally provided to the Envelope are not available. This hook provides a way to keep track
           of what all the Envelope has already evaluated. This is handled internally in the Envelope.from_envelope_data
           class method.
    .. [5] The scipy.spatial.ConvexHull class is built on an external library and therefore is not able to be pickled.
           Therefore, data persistence is handled by saving off the data which makes up the ConvexHull and allowing the
           Envelope to re-construct itself from this data. See the Envelope methods 'from_envelope_data' and
           'save_envelope_data'.

    See Also
    --------
    .. [1] scipy.spatial.ConvexHull
    """
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
        # make sure the 'runs' argument is iterable
        if not any(isinstance(runs, o) for o in (list, tuple)):
            runs = [runs]

        # make sure at least one active run was provided
        if all(x is None for x in runs):
            raise TypeError("Must provide at least one active Run to the Envelope constructor. All Runs in the 'runs'" +
                            " argument were None.")

        # run_info provided, ensure there is a corresponding object for each provided Run
        if run_info is not None:
            if not any(isinstance(run_info, o) for o in (list, tuple)):
                run_info = [run_info]
            if len(run_info) != len(runs):
                raise ValueError("If run_info is provided, it must be in a list the same length as the provided Runs.")

        self.info = _EnvelopeInfo(self, xname, yname, *args, name=name, description=description,
                                  keep_all=keep_all, incremental=incremental, **kwargs)
        """_EnvelopeInfo: An object for storing and handling information about the envelope."""

        # initialize private variables
        self._refs = []
        self._runs = {}
        self._run_info = {}

        # determine if incremental addition of point data to the ConvexHull will be needed
        inc = True if (len(runs) > 1 or incremental is True) else False

        # get the first run in the provided list of Runs which is not None. The provided Runs were already checked to
        # to ensure that at least one object was not None so the loop will terminate with a non-None Run and the
        # run0_index variable will persist for later access
        for run0_index, run in enumerate(runs):
            if run is not None:
                break

        # initialize the Convexhull with data from the first Run and store Run internally
        points = self._stack_points(run[self.info.xname], run[self.info.yname])
        super().__init__(points, *args, incremental=inc, **kwargs)
        self._store_run(run)

        # store all the other Runs and add their points to the hull, if available
        for i, run in enumerate(runs):
            if i != run0_index:
                info = None if run_info is None else run_info[i]
                self.add_run(run, info=info)

        # turn off incremental functionality if not requested by the user
        if inc and not incremental:
            self.close()

    @property
    def closed_vertices(self):
        """numpy.ndarray: convex hull vertex indices with duplicate first and last points, shape=(n_hull_points+1,)"""
        return np.hstack([self.vertices, [self.vertices[0]]])

    @property
    def perimeter(self):
        """numpy.ndarray: x,y data points on the hull with duplicate first and last points, shape=(n_hull_points+1,2)"""
        return self.points[self.closed_vertices, :]

    @property
    def refs(self):
        """
        list(PointRef): list of reference objects corresponding to each point in the entire envelope.

        Each PointRef corresponds to the point at the same index position within the ConvexHull's list of points and
        allows access to, e.g., the name of the Run which the point came from.
        """
        return self._refs

    @property
    def runs(self):
        """
        list(Run or None): list of all Runs which have been provided to the envelope.

        Some of the elements of the list may be None if the Run has no points on the convex hull of the envelope and all
        Runs are not being kept.
        """
        return self._runs

    @property
    def run_info(self):
        """
        list(_RunInfo): a _RunInfo object corresponding to each Run that has been provided to the envelope.

        There is a _RunInfo object corresponding to every element in the Envelope's 'runs' list, even if the element is
        None.
        """
        return self._run_info

    def absorb_envelopes(self, envelopes):
        """
        Absorb points and Runs stored in another envelope and recompute the overall convex hull.

        The calling Envelope object is modified **in place**; a new Envelope object is **not** returned.

        Parameters
        ----------
        envelopes: Envelope or list(Envelope)
            The envelopes to be absorbed.
        """
        if not any(isinstance(envelopes, o) for o in (list, tuple)):
            envelopes = [envelopes]
        for env in envelopes:
            self._absorb_envelope(env)

    def add_run(self, run, info=None):
        """
        Store a new Run and recompute the convex hull after inclusion of the Run's data points.

        If the provided 'run' argument is None, then a _RunInfo object *must* be provided in the info keyword argument.

        The calling Envelope object is modified **in place**; a new Envelope object is **not** returned.

        Parameters
        ----------
        run: pygui.data.run.Run or None
            The Run to be stored.
        info: None or _RunInfo, optional
            Optional _RunInfo to be associated with the run if it is None.
        """
        self._store_run(run, info=info)
        if run is not None:
            x = run[self.info.xname]
            y = run[self.info.yname]
            points = self._stack_points(x, y)
            self.add_points(points)
            if not self.info.keep_all:
                self._clean_runs()

    def close(self):
        """
        Halt incremental functionality and update internal attributes.

        See Also
        --------
        .. [1] scipy.spatial.ConvexHull.close
        """
        super().close()
        self.info._incremental = False

    @classmethod
    def from_envelope_data(cls, filepath, **kwargs):
        """
        Generate an Envelope from pickled envelope data.

        This class method provides a way to re-generate an Envelope from persistent envelope data because the ConvexHull
        class cannot be pickled directly.

        Parameters
        ----------
        filepath: str
            The filepath to the ppickle file containing envelope data
        **kwargs
            Arbitrary keyword arguments provided to the pickle.load function.

        Returns
        -------
        Envelope
            The Envelope generated from the pickled data.

        See Also
        --------
        .. [1] pickle
        .. [2] Envelope.save_envelope_data
        """
        # load the data
        with open(filepath, 'rb') as f:
            data = pickle.load(f, **kwargs)

        # gather up all Run and _RunInfo data
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

        # rebuild the envelope
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
    def from_csv(cls,
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
        """
        Generate an Envelope from a csv file containing x,y data.

        A Run is generated from the CSV file which is then used to generate the Envelope.

        Parameters
        ----------
        xname: str
            The name of the column within the CSV which should make up the 'x' data.
        yname: str
            The name of the column within the CSV which should make up the 'y' data.
        filepath: str
            The filepath to the CSV
        *args
            Arbitrary positional arguments provided to the Envelope constructor.
        name: str or None, optional
            The name of the Envelope. Default=None.
        description: str, optional
            An optional description to store with the envelope for reports, documentation, etc. Default="".
        run_name: str or None, optional
            Identifying name for the Run. Default=None.
        run_description: str, optional
            Additional details about the Run to be used in reports, etc.
        run_kwargs: dict of str: object
            Dictionary of keyword arguments provided to the Run constructor.
        **kwargs
            Arbitrary keyword arguments provided to the Envelope constructor.

        Returns
        -------
        Envelope
        """
        run = Run.read_csv(filepath, name=run_name, description=run_description, **run_kwargs)
        return Envelope(xname, yname, run, *args, name=name, description=description, **kwargs)

    def get_envelope_data(self):
        """
        Get data which defines the envelope.

        Generally, this method is used to extract data for pickling. The data is stored in a dictionary with the
        following key, value pairs:
            info: _PersistentEnvelopeInfo
                An object contianing information about the envelope which can be pickled. This is just a copy of
                an _EnvelopeInfo object with reference to the Envelope itself removed.
            runs: list(Run or None)
                The list of all Runs stored in the Envelope. Some may be None if the Run contains no points on the
                ConvexHull and the Envelope's 'keep_all' attribute is False.
            run_info:
                The list of all _RunInfo objects corresponding to each element in the 'runs' list

        Returns
        -------
        dict of str: object
        """
        data = {}
        data['info'] = self.info.to_persistent_info()
        data['runs'] = self.runs
        data['run_info'] = self.run_info
        return data

    def get_envelope_points(self, closed=False):
        """
        Get the x,y data corresponding to the vertices of the envelope.

        Parameters
        ----------
        closed: bool, optional
            Return points for the closed envelope. Default=False.

        Returns
        -------
        numpy.ndarray
            Array of x,y data, shape=(n, 2)
        """
        v = self.get_vertices(closed=closed)
        return self.points[v, :]

    def get_envelope_refs(self, closed=False):
        """
        Get the PointRefs corresponding to the vertices of the envelope.

        Parameters
        ----------
        closed: bool, optional
            Return references for the closed envelope. Default=False.

        Returns
        -------
        list(PointRef)
        """
        return [self.refs[v] for v in self.get_vertices(closed=closed)]

    def get_envelope_runs(self, closed=False):
        """
        Get the Runs corresponding to the vertices of the envelope.

        The returned list is the same length as the number of points on the convex hull, regardless of whether or not
        a particular Run contributes more than one point to the hull.

        Parameters
        ----------
        closed: bool, optional
            Return Runs for the closed envelope. Default=False.

        Returns
        -------
        list(Run)
        """
        for ref in self.get_envelope_refs(closed=closed):
            yield self.runs[ref.run_name]

    def get_envelope_run_indices(self, closed=False):
        """
        Get the indices from the parent Run for each vertex of the envelope.

        The indices are in pandas terms, so that the data point can be accessed with run[<column_name>][index].

        Parameters
        ----------
        closed: bool, optional
            Return indices for the closed envelope. Default=False.

        Returns
        -------
        list(object)
        """
        return [self.refs[v].index for v in self.get_vertices(closed=closed)]

    def get_envelope_run_names(self, closed=False):
        """
        Get the name of parent Run for each vertex of the envelope.

        Parameters
        ----------
        closed: bool, optional
            Return the names for the closed envelope. Default=False.

        Returns
        -------
        list(str)
        """
        return [ref.run_name for ref in self.get_envelope_refs(closed=closed)]

    def get_vertices(self, closed=False):
        """
        Get the vertex indices of the envelope.

        Parameters
        ----------
        closed: bool, optional
            Return the vertices for the closed envelope.

        Returns
        -------
        list(int)
        """
        return self.closed_vertices if closed else self.vertices

    def plot(self, ax, *args, **kwargs):
        """
        Plot the envelope on the provided axes.

        If a PickableAxes is provided, the parents and indices of each point on the envelope are provided to the plot
        method.

        Parameters
        ----------
        ax: matplotlib.axes._subplots.AxesSubplot or pygui.widget.plot._pickable_plot.PickableAxes
            The axes on which to plot the envelope.
        *args
            Arbitrary positional arguments provided to the ax.plot method after the x and y data.
        **kwargs
            Arbitrary keyword arguments provided to the ax.plot method.

        Returns
        -------
        list(matplotlib.lines.Line2D)

        See Also
        --------
        .. [1] matplotlib.axes.Axes.plot
        """
        p = self.perimeter
        if isinstance(ax, PickableAxes):
            parents = list(self.get_envelope_runs(closed=True))
            indices = list(self.get_envelope_run_indices(closed=True))
            return ax.plot(p[:, 0], p[:, 1], *args, parent=parents, indices=indices, **kwargs)
        else:
            return ax.plot(p[:, 0], p[:, 1], *args, **kwargs)

    def save_envelope_data(self, filepath, **kwargs):
        """
        Save data which makes up an Envelope object so that it can be regenerated later.

        Parameters
        ----------
        filepath: str
            The filepath that the pickled data object should be saved to.
        **kwargs
            Arbitrary keyword arguments provided to the pickle.dump function.
        """
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
                # run does not contain any points on the convex hull
                # remove reference to the Run within the Envelope so that it can be garbage collected
                #   if there are no external references
                self.runs[name] = None

    @staticmethod
    def _stack_points(*args):
        """Create column vectors from arbitrary number of provided 1D vectors and stack them horizontally."""
        arrs = [np.array(x).reshape((len(x), 1)) for x in args]
        return np.hstack(arrs)

    def _store_refs(self, run):
        assert run is not None      # cannot store reference to a Run which has no points in memory
        for index in run.index:
            self.refs.append(PointRef(run_name=run.run_info.name, index=index))

    def _store_run(self, run, info=None):
        if run is None and info is None:
            raise ValueError("Must provide a _RunInfo object if no run is provided")

        if run is not None:
            self.runs[run.run_info.name] = run
            self.run_info[run.run_info.name] = run.run_info
            self._store_refs(run)
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

    def __str__(self):
        s  = f"EnvelopeInfo for Envelope: {self.name}\n"
        s += f"\txname:\t\t\t{self.xname}\n"
        s += f"\tyname:\t\t\t{self.yname}\n"
        s += f"\tdescription:\t{self.description}\n"
        s += f"\tkeep_all:\t\t{self.keep_all}\n"
        s += f"\tincremental:\t{self.incremental}\n"
        return s

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
