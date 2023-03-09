from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from __labeled_float_field import LabelledFloatField

class CustomDialog(QDialog):
    def __init__(self, parent=None, flags=None, title="", message="", font=None, type=""):
        super().__init__(parent, flags=flags)

        self.name = title
        if type == "FLOAT_INPUT":
            QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        elif type == "MESSAGE":
            QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.float_field = LabelledFloatField(title="", font=font, initial_value=1.0)
        self.float_field.lineEdit.setFixedWidth(80)

        self.layout = QVBoxLayout()
        self.inner_layout = QVBoxLayout()
        self.frame = QFrame(self)
        
        #self.__lyt.setContentsMargins(0,0,0,0)
        self.frame.setLayout(self.inner_layout)
        #self.setCentralWidget(self.frame)
        message = QLabel(message)
        self.inner_layout.addWidget(message)
        if type == "FLOAT_INPUT":
            self.inner_layout.setSpacing(20)
            self.inner_layout.addWidget(self.float_field.lineEdit)
        self.inner_layout.setSpacing(20)
        self.inner_layout.addWidget(self.buttonBox)
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)
    
    def accept(self) -> None:
        print("check duration value")
        return super().accept()
    
    def getValue(self):
        return self.float_field.getValue()