import warnings

from pandas import DataFrame, read_csv
from uuid import uuid4


class Run(DataFrame):
    """
    A subclass of pandas.DataFrame with some additional features.

    Parameters
    ----------
    name: str or None, optional. Default=None.
        Identifying name for the Run. See Note 1.
    description: str, optional. Default="".
        Additional details about the Run to be used in reports, etc.
    *args
        Variable length argument list to be passed to the super class constructor.
    **kwargs
        Arbitrary keyword arguments to be passed to the super class constructor.

    Notes
    -----
    .. [1] In some instances, the Run name is used as a lookup key. Therefor, the name given to
           the Run should be unique. If a name is not provided, a unique ID is generated.

    See Also
    --------
    .. [1] pandas.DataFrame
    """
    def __init__(self, *args, name=None, description="", **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name if name is not None else uuid4()
        self.description = description

    @property
    def _constructor(self):
        return Run

    @classmethod
    def read_csv(cls, filepath, name=None, description="", **kwargs):
        """
        Create a Run object by reading in a CSV per the pandas read_csv function.

        Parameters
        ----------
        filepath: str
            The filepath of the CSV to be read in.
        name: str or None, optional. Default=None.
            Identifying name for the Run.
        description: str, optional. Default="".
            Additional details about the Run to be used in reports, etc.
        **kwargs
            Arbitrary keyword arguments to be passed into the read_csv function.

        Returns
        -------
        run: Run
            The Run containing the data from the CSV.
        """
        name = filepath if name is None else name
        return Run(read_csv(filepath, **kwargs), name=name, description=description)


class RunSet(object):

    def __init__(self, runs=[], name=None, description="", allow_overwrite=False):
        self.runs = {}

        self.name = name if name is not None else uuid4()
        self.description = description
        self.allow_overwrite = allow_overwrite

        for run in runs:
            self.add_run(run)

    def __getitem__(self, key):
        return {name: run[key] for name, run in self.runs.items()}

    def __setitem__(self, key, value):
        for run in self.runs.values():
            run[key] = value

    @property
    def run_names(self):
        return tuple(self.runs.keys())

    def add_run(self, run):
        if run.name in self.runs and not self.allow_overwrite:
            raise ValueError("Cannot overwrite an existing Run with the same name: %s\n" % run.name +
                             "Either delete the run or set the RunSet's 'allow_overwrite' attribute to True.")
        if not isinstance(run, Run):
            run = Run(run)

        self.runs[run.name] = run

    def remove_run(self, name):
        try:
            del(self.runs[name])
        except KeyError:
            warnings.warn("Attempted to delete Run %s from RunSet %s but the run was not found." % (name, self.name))

    def set_index(self, keys, drop=False, append=False, verify_integrity=False):
        for run in self.runs.values():
            run.set_index(keys, drop=drop, inplace=True, append=append, verify_integrity=verify_integrity)
