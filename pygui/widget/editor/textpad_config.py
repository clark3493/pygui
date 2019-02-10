from .addins import FileHandler, LineNumbers, Popup
from .addins import Scrollbar, StationeryFunctions


class TextPadConfig(object):
    
    @classmethod
    def connect(cls, pad):
        StationeryFunctions(pad)
        FileHandler(pad)
        LineNumbers(pad)
        Popup(pad)
        Scrollbar(pad)
