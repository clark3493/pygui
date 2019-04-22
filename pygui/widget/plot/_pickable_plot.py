import numpy as np

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D
from matplotlib.projections import register_projection


class PickableAxes(Axes):
    name = 'pickable'

    DATA_ARTISTS = (Line2D, PathCollection)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cla()

        self.handlers = {}
        self.options = _PickableAxesOptions(self)

        self.figure.canvas.mpl_connect('pick_event', self.onpick)

    def loglog(self, *args, parent=None, **kwargs):
        picker = self.options.picker if parent is not None else None
        lines = super().loglog(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def onpick(self, event):
        if any(isinstance(event.artist, o) for o in self.DATA_ARTISTS):
            artist = event.artist
            ind = self._get_closest_index(event)
            key = event.mouseevent.key

            handler = self.handlers[artist]

            # TODO: IMPLEMENT ABILITY TO CHECK IF MULTIPLE LINES HAVE BEEN PICKED AND ONLY TAKE ACTION FOR ONE
            if key is None:
                handler.flip_selection_status(ind)
            elif 'control' in key or 'ctrl' in key:
                handler.select(ind)
            else:
                handler.flip_selection_status()

    def plot(self, *args, parent=None, **kwargs):
        picker = self.options.picker if parent is not None else None
        lines = super().plot(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def scatter(self, *args, parent=None, **kwargs):
        picker = self.options.picker if parent is not None else None
        collections = super().scatter(*args, picker=picker, **kwargs)
        self._add_artists(collections, parent)
        return collections

    def semilogx(self, *args, parent=None, **kwargs):
        picker = self.options.picker if parent is not None else None
        lines = super().semilogx(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def semilogy(self, *args, parent=None, **kwargs):
        picker = self.options.picker if parent is not None else None
        lines = super().semilogy(*args, picker=picker, **kwargs)
        self._add_artists(lines, parent)
        return lines

    def _add_artists(self, artists, parent):
        if parent is not None:
            if isinstance(artists, PathCollection):
                artists = [artists]
            for artist in artists:
                self.handlers[artist] = self._create_artist_handler(artist, parent=parent)

    @classmethod
    def _create_artist_handler(cls, artist, *args, **kwargs):
        if isinstance(artist, Line2D):
            return _PickableLine2DHandler(artist, *args, **kwargs)
        elif isinstance(artist, PathCollection):
            return _PickablePathCollectionHandler(artist, *args, **kwargs)
        else:
            return _PickableArtistHandler(artist, *args, **kwargs)

    @staticmethod
    def _get_artist_data(artist):
        if isinstance(artist, Line2D):
            return artist.get_data()
        elif isinstance(artist, PathCollection):
            data = artist.get_offsets()
            rows = data.shape[0]
            return data[:, 0].reshape((rows,)), data[:, 1].reshape((rows,))
        else:
            raise TypeError("Artist type not recognized. Supported types are 'Line2D' and 'PathCollection'")

    def _get_closest_index(self, event):
        indices = event.ind
        datax, datay = self._get_artist_data(event.artist)
        for i, index in enumerate(indices):
            if event.artist.get_linestyle() is not None and index != len(datax)-1:
                # event.ind always seems to return the lower index of the two indices
                # that comprise the selected line segment, even if the mouse click
                # was closer to the higher indexed point
                # this check adds the next index to be checked and see which one
                # is actually closer to the mouse click
                indices = np.append(indices, indices[i]+1)
        datax, datay = [datax[i] for i in indices], [datay[i] for i in indices]
        msx, msy = event.mouseevent.xdata, event.mouseevent.ydata
        dist = np.sqrt((np.array(datax)-msx)**2 + (np.array(datay)-msy)**2)
        return indices[np.argmin(dist)]


class _PickableAxesOptions(object):

    def __init__(self, ax):
        self.ax = ax

        self._draggable_annotations = True
        self._linewidth_delta = 2
        self._markersize_delta = 6
        self._picker = 5
        self._data_to_show = []

    @property
    def data_to_show(self):
        return self._data_to_show

    @data_to_show.setter
    def data_to_show(self, value):
        self._data_to_show = value
        for handler in self.ax.handlers.values():
            handler.data_to_show = value

    @property
    def draggable_annotations(self):
        return self._draggable_annotations

    @draggable_annotations.setter
    def draggable_annotations(self, value):
        self._draggable_annotations = value
        for handler in self.ax.handlers.values():
            handler.draggable_annotations = value

    @property
    def linewidth_delta(self):
        return self._linewidth_delta

    @linewidth_delta.setter
    def linewidth_delta(self, value):
        self._linewidth_delta = value
        for handler in self.ax.handlers.values():
            if 'linewidth_delta' in handler.__dict__:
                handler.linewidth_delta = value

    @property
    def markersize_delta(self):
        return self._markersize_delta

    @markersize_delta.setter
    def markersize_delta(self, value):
        self._markersize_delta = value
        for handler in self.ax.handlers.values():
            if 'markersize_delta' in handler.__dict__:
                handler.markersize_delta = value

    @property
    def picker(self):
        return self._picker

    @picker.setter
    def picker(self, value):
        self._picker = value


class _PickableArtistHandler(object):

    DEFAULT_ANNOTATION_PARAMS = {'xycoords': 'data',
                                 'xytext': (10, 10),
                                 'textcoords': 'offset points',
                                 'fontsize': 8,
                                 'bbox': {'boxstyle': 'round', 'fc': '0.8'},
                                 'arrowprops': {'arrowstyle': '-|>'}}

    def __init__(self,
                 artist,
                 parent=None):
        self.artist = artist
        self.parent = parent
        self.selected = False
        self.data_to_show = artist.axes.options.data_to_show

        self.annotation_params = self.DEFAULT_ANNOTATION_PARAMS
        self.draggable_annotations = artist.axes.options.draggable_annotations
        self.annotations = []

        self._original_attributes = self._get_artist_attributes()
        self.markersize_delta = self.artist.axes.options.markersize_delta
        self.selection_indicators = []

    def add_annotation(self, string, xy):
        annotation = self.artist.axes.annotate(string, xy, **self.annotation_params)
        if self.draggable_annotations:
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
        names = self.data_to_show if names is None else names
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
        names = self.data_to_show if names is None else names
        if index is None:
            return {s: np.array(self.parent[s]) for s in names}
        else:
            return {s: np.array(self.parent[s])[index] for s in names}


class _PickableLine2DHandler(_PickableArtistHandler):

    def __init__(self, artist, *args, **kwargs):
        super().__init__(artist, *args, **kwargs)

        self.linewidth_delta = artist.axes.options.linewidth_delta

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
        a['lw'] = a['lw'] + self.linewidth_delta
        a['ms'] = a['ms'] + self.markersize_delta
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
