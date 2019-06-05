import os

import warnings

from pandas import DataFrame, read_csv
from uuid import uuid4


# TODO: UPDATE RunSet DOCUMENTATION


class Run(DataFrame):
    """
    A subclass of pandas.DataFrame with some additional features.

    Parameters
    ----------
    *args
        Variable length argument list to be passed to the super class constructor.
    name: str or None, optional. Default=None.
        Identifying name for the Run. See Note 1.
    description: str, optional. Default="".
        Additional details about the Run to be used in reports, etc.
    filepath: str or None, optional. Default=None.
        Optional input to track the filepath the Run data originated from.
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
    def __init__(self, *args, name=None, description="", filepath=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_info = _RunInfo(name, description=description, filepath=filepath)

        self.filters = _FunctionCollector(description="All functions take a Run as the first argument, which is not" +
                                                      " stored")
        self._original_run = None

    @property
    def is_filtered(self):
        """
        Boolean indicating if a filtering function has been applied to the original Run state.

        If this flag returns True, then the applied filters can be accessed through the Run's
        _FunctionCollector 'filters' attribute.
        """
        return not self._original_run is None

    def filter_data(self, filt, *args, **kwargs):
        """
        Apply a filter function to the Run.

        The first argument to the filter function should be the Run itself. Any additional positional or keyword
        arguments are passed in the same way they are passed to the filter_data method itself.

        Parameters
        ----------
        filt: function
            The function used to modify the Run in place.
        *args:
            Arbitrary additional arguments to be passed into the filter function (after the Run)
        **kwargs:
            Arbitrary keyword arguments passed into the filter function.

        Notes
        -----
        .. [1] While the name of the method implies filtering data, the "filter" function can be any function which
               takes a DataFrame as its first argument and modifies it in place.
        .. [2] If the Run has not been filtered prior to this filtering operation, a copy of the DataFrame is
               saved so that the Run's original can be restored, if necessary.
        .. [3] The applied filter and arguments are added to the Run's 'filters' _FunctionCollector attribute so
               that information about filters applied to the data can be accessed retroactively.
        """
        if not self.is_filtered:
            self._original_run = self.copy()
        filt(self, *args, **kwargs)
        self.filters.add_func(filt, *args, **kwargs)

    def unfilter(self):
        """
        Restore the Run to its original state (before any filtering operations were applied).

        Any DataFrame columns or indices that were not originally present are removed (along with their associated
        data). The data from the original state replaces the existing Run data. All reference to stored filters and the
        original DataFrame copy are removed.
        """
        if not self.is_filtered:
            return
        self.drop([c for c in self.columns if c not in self._original_run.columns], axis=1, inplace=True)
        self.drop([r for r in self.index if r not in self._original_run.index], axis=0, inplace=True)
        self.update(self._original_run)
        self._original_run = None
        self.filters.clear()

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
        return Run(read_csv(filepath, **kwargs), name=name, description=description, filepath=os.path.abspath(filepath))

    @property
    def _constructor(self):
        return Run


class _RunInfo(object):
    """
    An object to store information about a Run.

    The _RunInfo object displays a formatted summary of the Run's information if it is printed.

    Parameters
    ----------
    name: str or None, optional
        Unique name for the run. A unique ID is generated if None is provided. Default=None.
    description: str, optional
        A description of the Run, for reports, data posterity, etc. Default="".
    filepath: str or None, optional
        The filepath that the Run data is associated with. Default=None.
    """
    def __init__(self, name=None, description="", filepath=None):
        self.name = name if name is not None else uuid4()
        self.description = description
        self.filepath = filepath

    def __str__(self):
        s  = f"RunInfo for Run: {self.name}\n"
        s += f"\tFilepath:\t{self.filepath}\n"
        s += f"\tDescription:\n\t\t{self.description}"
        return s


class _FunctionCollector(object):
    """
    An object for storing a set of functions and associated input arguments.

    All added function objects are stored in chronological order in the _FunctionCollector's 'func_list' attribute.

    Associated *args tuples and **kwargs dicts are stored in the _FunctionCollector's 'args' and 'kwargs' dict
    attributes, respectively, with the function name as the key. The function itself can also be accessed in a similar
    manner through the 'funcs' attribute or directly using the _FunctionCollector's __getitem__ method.

    Parameters
    ----------
    description: str, optional
        An optional string describing the _FunctionCollector

    Examples
    --------

    Create a _FunctionCollector object and add a function for storage with a couple positional arguments

    >>> fc = _FunctionCollector("A really great example!")
    >>> fc.add_func(sum, 3, 5)

    View the stored data

    >>> fc['sum'] is sum
    True
    >>> fc.func_list == [sum]
    True
    >>> fc.args['sum']
    (3, 5)
    >>> fc.kwargs['sum']
    {}
    """
    def __init__(self, description=""):
        self.description = description
        self.func_list = []
        self.funcs = {}
        self.args = {}
        self.kwargs = {}

    def __getitem__(self, item):
        return self.funcs[item]

    def add_func(self, f, *args, **kwargs):
        """Store a function and associated arguments."""
        name = f.__name__
        self.func_list.append(f)
        self.funcs[name]  = f
        self.args[name]   = args
        self.kwargs[name] = kwargs

    def clear(self):
        """Clear all references to the stored functions."""
        self.func_list = []
        self.funcs  = {}
        self.args   = {}
        self.kwargs = {}


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
        if run.run_info.name in self.runs and not self.allow_overwrite:
            raise ValueError("Cannot overwrite an existing Run with the same name: %s\n" % run.name +
                             "Either delete the run or set the RunSet's 'allow_overwrite' attribute to True.")
        if not isinstance(run, Run):
            run = Run(run)

        self.runs[run.run_info.name] = run

    def remove_run(self, name):
        try:
            del(self.runs[name])
        except KeyError:
            warnings.warn("Attempted to delete Run %s from RunSet %s but the run was not found." % (name, self.name))

    def set_index(self, keys, drop=False, append=False, verify_integrity=False):
        for run in self.runs.values():
            run.set_index(keys, drop=drop, inplace=True, append=append, verify_integrity=verify_integrity)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
