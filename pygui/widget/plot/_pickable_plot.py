import numpy as np

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D
from matplotlib.projections import register_projection


class PickableAxes(Axes):
    """
    A subclass of matplotlib.axes._axes.Axes which support selection and action on data series.

    The axes currently support plotting methods the same as in a basic Axes except that
    a parent Run (i.e. DataFrame) can be supplied with the data. Corresponding data
    from the parent can be displayed for a particular point by clicking on it within
    the active Figure.

    The columns from the parent run which are shown when a daa point is selected are defined
    in the PickableAxes object's options.annotation_data attribute.

    Parameters
    ----------
    *args
        Positional arguments passed to the Axes constructor
    **kwargs
        Arbitrary keyword arguments passed to the Axes constructor

    Notes
    -----
    .. [1] To select multiple points within the same data series, hold Ctrl while clicking

    References
    ----------
    .. [1] matplotlib Custom Projections documentation:
           https://matplotlib.org/gallery/misc/custom_projection.html

    See Also
    --------
    .. [1] PickableAxesOptions
    .. [2] matplotlib.axes._axes.Axes
    """

    name = 'pickable'
    """
    The matplotlib projection name. The user will use this name to activate
    the PickableAxes functionality i.e. subplot(111, projection='pickable').
    """

    DATA_ARTISTS = (Line2D, PathCollection)
    """
    Supported artists (i.e. plot features) for pickable functionality.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cla()

        self.handlers = {}
        self.options = PickableAxesOptions(self)

        self.figure.canvas.mpl_connect('pick_event', self.onpick)

    def loglog(self, *args, parent=None, **kwargs):
        """
        Make a pickable plot with log scaling on both the x and y axes.

        Parameters
        ----------
        *args:
            Positional arguments passed to the Axes.loglog method
        parent: pygui.data.run.Run or DataFrame, optional. Default=None.
            The parent DataFrame that the x,y data came from.
        **kwargs:
            Arbitrary keyword arguments passed to the Axes.loglog method.

        Returns
        -------
        lines: list(Line2D)
            A list of Line2D object(s) representing the plotted data.

        Notes
        -----
        .. [1] A parent must be supplied in order for the data series to be pickable.
        """
        picker = self.options.picker if parent is not None else None
        lines = super().loglog(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def onpick(self, event):
        """
        Callback function for a pick event.

        Parameters
        ----------
        event: matplotlib.backend_bases.Event
            The pick event obejct.
        """

        # only act when supported objects are picked
        if any(isinstance(event.artist, o) for o in self.DATA_ARTISTS):
            artist = event.artist                   # the picked plot feature
            ind = self._get_closest_index(event)    # the index of the data series closest to the click
            key = event.mouseevent.key              # any keys that were pressed at the time of the click

            # get the artist handler obejct
            handler = self.handlers[artist]

            # TODO: IMPLEMENT ABILITY TO CHECK IF MULTIPLE LINES HAVE BEEN PICKED AND ONLY TAKE ACTION FOR ONE
            if key is None:
                # no keyboard keys held, simply select/deselect the artist
                handler.flip_selection_status(ind)
            elif 'control' in key or 'ctrl' in key:
                # allow multiple selections
                handler.select(ind)
            else:
                # simply select/deselect te artist
                handler.flip_selection_status()

    def plot(self, *args, parent=None, **kwargs):
        """
        Make a pickable plot.

        Parameters
        ----------
        *args:
            Positional arguments passed to the Axes.loglog method
        parent: pygui.data.run.Run or DataFrame, optional. Default=None.
            The parent DataFrame that the x,y data came from.
        **kwargs:
            Arbitrary keyword arguments passed to the Axes.loglog method.

        Returns
        -------
        lines: list(Line2D)
            A list of Line2D object(s) representing the plotted data.

        Notes
        -----
        .. [1] A parent must be supplied in order for the data series to be pickable.
        """
        picker = self.options.picker if parent is not None else None
        lines = super().plot(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def scatter(self, *args, parent=None, **kwargs):
        """
        Make a pickable scatter plot.

        Parameters
        ----------
        *args:
            Positional arguments passed to the Axes.loglog method
        parent: pygui.data.run.Run or DataFrame, optional. Default=None.
            The parent DataFrame that the x,y data came from.
        **kwargs:
            Arbitrary keyword arguments passed to the Axes.loglog method.

        Returns
        -------
        paths: PathCollection
            Collection representing the plotted data.

        Notes
        -----
        .. [1] A parent must be supplied in order for the data series to be pickable.
        """
        picker = self.options.picker if parent is not None else None
        collections = super().scatter(*args, picker=picker, **kwargs)
        self._add_artists(collections, parent)
        return collections

    def semilogx(self, *args, parent=None, **kwargs):
        """
        Make a pickable plot with log scaling on the x axis.

        Parameters
        ----------
        *args:
            Positional arguments passed to the Axes.loglog method
        parent: pygui.data.run.Run or DataFrame, optional. Default=None.
            The parent DataFrame that the x,y data came from.
        **kwargs:
            Arbitrary keyword arguments passed to the Axes.loglog method.

        Returns
        -------
        lines: list(Line2D)
            A list of Line2D object(s) representing the plotted data.

        Notes
        -----
        .. [1] A parent must be supplied in order for the data series to be pickable.
        """
        picker = self.options.picker if parent is not None else None
        lines = super().semilogx(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def semilogy(self, *args, parent=None, **kwargs):
        """
        Make a pickable plot with log scaling on the y axis.

        Parameters
        ----------
        *args:
            Positional arguments passed to the Axes.loglog method
        parent: pygui.data.run.Run or DataFrame, optional. Default=None.
            The parent DataFrame that the x,y data came from.
        **kwargs:
            Arbitrary keyword arguments passed to the Axes.loglog method.

        Returns
        -------
        lines: list(Line2D)
            A list of Line2D object(s) representing the plotted data.

        Notes
        -----
        .. [1] A parent must be supplied in order for the data series to be pickable.
        """
        picker = self.options.picker if parent is not None else None
        lines = super().semilogy(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def _add_artists(self, artists, parent):
        """
        Create a handler object for each artist and store them.

        Parameters
        ----------
        artists: list(matplotlib.artist.Artist)
            List of matplotlib artists (e.g. Line2D, PathCollection)
        parent: pygui.data.run.Run or DataFrame or None
            The parent DataFrame or None
        """
        if parent is not None:
            if isinstance(artists, PathCollection):
                artists = [artists]
            for artist in artists:
                self.handlers[artist] = self._create_artist_handler(artist, parent=parent)

    @classmethod
    def _create_artist_handler(cls, artist, *args, **kwargs):
        """
        Determine the type of the artist and create an appropriate handler object.

        Parameters
        ----------
        artist: matplotlib.artist.Artist
            The artist for which the handler is to be made.
        *args
            Positional arguments passed to the handler constructor.
        **kwargs
            Arbitrary keywords arguments passed to the handler constructor.

        Returns
        -------
        handler: _PickableArtistHandler or a subclass thereof
        """
        if isinstance(artist, Line2D):
            return _PickableLine2DHandler(artist, *args, **kwargs)
        elif isinstance(artist, PathCollection):
            return _PickablePathCollectionHandler(artist, *args, **kwargs)
        else:
            return _PickableArtistHandler(artist, *args, **kwargs)

    @staticmethod
    def _get_artist_data(artist):
        """
        Get the x,y data which the artist represents.

        Parameters
        ----------
        artist: matplotlib.artist.Artist
            the artist containing the data.

        Returns
        -------
        data: numpy.array (ndim=1), numpy.array (ndim=1)
        """
        if isinstance(artist, Line2D):
            return artist.get_data()
        elif isinstance(artist, PathCollection):
            data = artist.get_offsets()
            rows = data.shape[0]
            return data[:, 0].reshape((rows,)), data[:, 1].reshape((rows,))
        else:
            raise TypeError("Artist type not recognized. Supported types are 'Line2D' and 'PathCollection'")

    def _get_closest_index(self, event):
        """
        Get the data index closest to the pick event's mouse location.

        The event.ind attribute always seems to return the lower of the two indices
        that comprise a selected line segment, even if the mouse click was closer to
        the higher indexed point.

        This method checks both the returned index and the next higher index to determine
        which one is closer.

        Parameters
        ----------
        event: matplotlib.backend_bases.Event
            The pick event.

        Returns
        -------
        ind: int
            The index of the data closest to the click.
        """

        # get the lower index (or indices) that is returned by default
        indices = event.ind

        # get the full data series for the artist
        datax, datay = self._get_artist_data(event.artist)

        # check each returned index
        for i, index in enumerate(indices):
            # verify that the artist has a line and that the last item in the data series was not selected
            if event.artist.get_linestyle() is not None and index != len(datax)-1:
                # if so, append the next higher index
                indices = np.append(indices, indices[i]+1)

        # get the data corresponding to the lower and higher indices
        datax, datay = [datax[i] for i in indices], [datay[i] for i in indices]

        # get the mouse click location
        msx, msy = event.mouseevent.xdata, event.mouseevent.ydata

        # calculate the distance from the mouse click to the data
        dist = np.sqrt((np.array(datax)-msx)**2 + (np.array(datay)-msy)**2)

        # return the index corresponding to the smaller distance
        return indices[np.argmin(dist)]


class PickableAxesOptions(object):
    """
    An object to store options for PickableAxes for which the user has control.

    The attributes of a PickableAxesOptions object can be modified to adjust the
    settings for a particular axes. Alternatively, the class attributes can be modified
    to adjust the settings for all subsequently created PickableAxes, as the object
    attributes are set to the value of the class attributes upon initialization.

    Parameters
    ----------
    ax: matplotlib.axes._axes.Axes
        The axes for which the options correspond.
    """

    ANNOTATION_DATA = []
    """
    The column names from a parent object that will be displayed when a data point is selected.
    
    dtype: list(str)
    """

    ANNOTATION_PARAMS = {'xycoords': 'data',
                         'xytext': (10, 10),
                         'textcoords': 'offset points',
                         'fontsize': 8,
                         'bbox': {'boxstyle': 'round', 'fc': '0.8'},
                         'arrowprops': {'arrowstyle': '-|>'}}
    """
    Keywords arguments passed to the annotation box constructor when displaying data.
    
    dtype: dict{str: misc}
    """

    DRAGGABLE_ANNOTATIONS = True
    """
    Flag to allow the user to drag annotation boxes within a figure.
    
    dtype: bool
    """

    LINEWIDTH_DELTA = 2
    """
    Linewidth increment to indicate that a line has been selected.
    
    dtype: int
    """

    MARKERSIZE_DELTA = 6
    """
    Markersize delta to indicate that a data point has been selected.
    
    Note: not currently supported for scatter plots.
    
    dtype: int
    """

    PICKER = 5.
    """
    Picker setting for pickable artists. See https://matplotlib.org/users/event_handling.html.
    
    dtype: None, bool, float or function
    """

    def __init__(self, ax):
        self.ax = ax

        self.annotation_data       = self.ANNOTATION_DATA
        self.annotation_params     = self.ANNOTATION_PARAMS
        self.draggable_annotations = self.DRAGGABLE_ANNOTATIONS
        self.linewidth_delta       = self.LINEWIDTH_DELTA
        self.markersize_delta      = self.MARKERSIZE_DELTA
        self.picker                = self.PICKER


class _PickableArtistHandler(object):

    def __init__(self,
                 artist,
                 parent=None):
        self.artist = artist
        self.parent = parent
        self.selected = False
        self.options = artist.axes.options

        self.annotations = []

        self._original_attributes = self._get_artist_attributes()
        self.selection_indicators = []

    def add_annotation(self, string, xy):
        annotation = self.artist.axes.annotate(string, xy, **self.options.annotation_params)
        if self.options.draggable_annotations:
            annotation.draggable()
        self.annotations.append(annotation)
        self.draw_idle()

    def add_selection_indicator(self, ind):
        x, y = self._get_data_coordinates(ind)
        attributes = self._selection_attributes
        # TODO: CLEAN THIS UP
        # TODO: FIGURE OUT HOW TO ADD INDICATOR FOR SCATTER PLOTS
        if 'linestyle' in attributes:
            del(attributes['linestyle'])
        if 'ls' in attributes:
            del(attributes['ls'])
        si = self.artist.axes.plot(x, y, linestyle=None, **attributes)
        self.selection_indicators += si
        self.draw_idle()

    def deselect(self, ind=None):
        raise NotImplementedError("This method must be overwritten by a subclass implemented for a specific type of" +
                                  "artist")

    def draw_idle(self):
        self.artist.figure.canvas.draw_idle()

    def flip_selection_status(self, ind=None):
        if self.selected:
            self.deselect(ind)
        else:
            self.select(ind)

    def remove_annotations(self):
        for annotation in self.annotations:
            annotation.remove()
        self.annotations = []
        self.draw_idle()

    def remove_selection_indicators(self):
        for si in self.selection_indicators:
            si.remove()
        self.selection_indicators = []
        self.draw_idle()

    def show_data(self, index, names=None):
        names = self.options.annotation_data if names is None else names
        data = self._get_parent_data(index=index, names=names)
        string = self._data_string(data)
        x, y = self._get_data_coordinates(index)
        self.add_annotation(string, (x, y))
        self.draw_idle()

    def select(self, ind=None):
        raise NotImplementedError("This method must be overwritten by a subclass implemented for a specific type of" +
                                  " artist")

    @property
    def _selection_attributes(self):
        raise NotImplementedError("This property must be overwritten by a subclass implemented for a specific type of" +
                                  " artist")

    @staticmethod
    def _data_string(data):
        s = ''
        nkeys = len(data.keys())
        for i, (name, value) in enumerate(data.items()):
            s += '%s: %s' % (name, str(value))
            if i != nkeys - 1:
                s += '\n'
        return s

    def _get_artist_attributes(self):
        return {}

    def _get_data_coordinates(self, ind):
        raise NotImplementedError("This method must be overwritten by a subclass implemented for a specific type of" +
                                  "artist")

    def _get_parent_data(self, index=None, names=None):
        names = self.options.annotation_data if names is None else names
        if index is None:
            return {s: np.array(self.parent[s]) for s in names}
        else:
            return {s: np.array(self.parent[s])[index] for s in names}


class _PickableLine2DHandler(_PickableArtistHandler):

    def add_line_selection_indicator(self):
        attributes = self._selection_attributes
        self.artist.set_linewidth(attributes['lw'])
        self.draw_idle()

    def deselect(self, ind=None):
        self.remove_line_selection_indicator()
        self.remove_selection_indicators()
        self.remove_annotations()
        self.selected = False

    def remove_line_selection_indicator(self):
        lw = self._original_attributes['lw']
        self.artist.set_linewidth(lw)
        self.draw_idle()

    def select(self, ind=None):
        self.add_line_selection_indicator()
        if ind is not None:
            self.add_selection_indicator(ind)
            self.show_data(index=ind)
        self.selected = True

    @property
    def _selection_attributes(self):
        a = self._original_attributes.copy()
        a['lw'] = a['lw'] + self.options.linewidth_delta
        a['ms'] = a['ms'] + self.options.markersize_delta
        return a

    def _get_data_coordinates(self, ind):
        xdata, ydata = self.artist.get_data()
        if isinstance(ind, np.integer):
            return xdata[ind], ydata[ind]
        else:
            return np.array([xdata[i] for i in ind]), np.array([ydata[i] for i in ind])

    def _get_artist_attributes(self):
        return {'color': self.artist.get_color(),
                'ls': self.artist.get_ls(),
                'lw': self.artist.get_lw(),
                'marker': self.artist.get_marker(),
                'mec': self.artist.get_mec(),
                'mew': self.artist.get_mew(),
                'mfcalt': self.artist.get_mfcalt(),
                'ms': self.artist.get_ms()}


class _PickablePathCollectionHandler(_PickableArtistHandler):

    def deselect(self, ind=None):
        self.remove_selection_indicators()
        self.remove_annotations()
        self.selected = False

    def select(self, ind=None):
        if ind is not None:
            self.add_selection_indicator(ind)
            self.show_data(index=ind)
        self.selected = True

    @property
    def _selection_attributes(self):
        return {}

    def _get_artist_attributes(self):
        return {'edgecolor': self.artist.get_edgecolor(),
                'facecolor': self.artist.get_facecolor(),
                'fill': self.artist.get_fill(),
                'sizes': self.artist.get_sizes()}

    def _get_data_coordinates(self, ind):
        data = self.artist.get_offsets()
        if isinstance(ind, np.integer):
            return data[ind, 0], data[ind, 1]
        else:
            return np.array([data[i, 0] for i in ind]), np.array([data[i, 1] for i in ind])


register_projection(PickableAxes)
