from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class UniformButton(QPushButton):
    def __init__(self, title="", name="", font=None, id=None):
        QWidget.__init__(self)
        self.setFont(font)
        self.setText(title)
        self.setObjectName(name)

        self.ID = id