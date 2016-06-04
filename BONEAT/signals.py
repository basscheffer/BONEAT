from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Signals(QObject):

    saveconfig = pyqtSignal()
    loadconfig = pyqtSignal()
    basename = pyqtSignal(str)