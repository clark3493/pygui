from .addins import FileHandler, LineNumbers, Popup
from .addins import Scrollbar, StationeryFunctions
from .addins import PythonSyntaxColor


class TextPadConfig(object):
    
    @classmethod
    def connect(cls, pad):
        StationeryFunctions(pad)
        FileHandler(pad)
        LineNumbers(pad)
        Popup(pad)
        PythonSyntaxColor(pad)
        Scrollbar(pad)
