

def _observe_func(func, callback=None):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if callback is not None:
            callback()
        return result
    return wrapper


def _observe_method(meth, callback=None):
    def wrapper(obj, *args, **kwargs):
        result = meth(obj, *args, **kwargs)
        if callback is not None:
            callback(obj)
        return result
    return wrapper


class Observer(object):

    def __init__(self, obj, callback, methods=[]):
        self.obj = obj
        self._callback = callback
        self.methods = methods

        self._wrap_methods()

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value
        self._wrap_methods()

    def _wrap_methods(self):
        for method in self.methods:
            setattr(self.obj, method, _observe_method(getattr(self.obj, method), self.callback))


class DictObserver(Observer):

    def __init__(self, dictionary, callback):
        super().__init__(dictionary, callback, methods=['__delattr__',
                                                        '__delitem__',
                                                        '__setattr__',
                                                        '__setitem__',
                                                        'clear',
                                                        'popitem',
                                                        'setdefault',
                                                        'pop',
                                                        'update',
                                                        ])
