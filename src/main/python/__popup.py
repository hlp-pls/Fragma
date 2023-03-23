from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from __labeled_float_field import LabelledFloatField
from __labeled_int_field import LabelledIntField

class CustomDialog(QDialog):
    def __init__(self, parent=None, flags=None, title="", message="", font=None, type="", initial_value=None):
        super().__init__(parent, flags=flags)

        self.name = title
        self.type = type
        if type == "FLOAT_INPUT" or type == "INT_INPUT":
            QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        #elif type == "PROGRESS":
            #QBtn = QDialogButtonBox.Cancel
        elif type == "MESSAGE":
            QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if type == "FLOAT_INPUT":
            self.field = LabelledFloatField(title="", font=font, initial_value=initial_value)
        elif type == "INT_INPUT":
            self.field = LabelledIntField(title="", font=font, initial_value=initial_value)
        
        if type == "FLOAT_INPUT" or type == "INT_INPUT":
            self.field.lineEdit.setFixedWidth(80)

        

        self.layout = QVBoxLayout()
        self.inner_layout = QVBoxLayout()
        self.frame = QFrame(self)
        
        #self.__lyt.setContentsMargins(0,0,0,0)
        self.frame.setLayout(self.inner_layout)
        #self.setCentralWidget(self.frame)
        message = QLabel(message)
        self.inner_layout.addWidget(message)
        if type == "FLOAT_INPUT" or type == "INT_INPUT":
            self.inner_layout.setSpacing(20)
            self.inner_layout.addWidget(self.field.lineEdit)
        #elif type == "PROGRESS_BAR":
            #self.progress = QProgressBar(self)
            #self.inner_layout.addWidget(self.progress)
        self.inner_layout.setSpacing(20)
        self.inner_layout.addWidget(self.buttonBox)
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)
    
    def accept(self) -> None:
        print("check duration value")
        return super().accept()
    
    def getValue(self):
        return self.field.getValue()
    
    # def setProgress(self, val):
    #     if type == "PROGRESS_BAR":
    #         self.progress.setValue(val)


class CustomProgressDialog(QProgressDialog):
    def __init__(self, parent=None, flags=None, title="", message="", font=None, type="", initial_value=None):
        super().__init__(parent, flags=flags)

        self.name = title
        self.type = type
        
        QBtn = QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.inner_layout = QVBoxLayout()
        self.frame = QFrame(self)

        #self.__lyt.setContentsMargins(0,0,0,0)
        self.frame.setLayout(self.inner_layout)
        #self.setCentralWidget(self.frame)
        message = QLabel(message)
        self.inner_layout.addWidget(message)
        
        self.progress = QProgressBar(self)
        self.inner_layout.addWidget(self.progress)
        self.inner_layout.setSpacing(20)
        self.inner_layout.addWidget(self.buttonBox)
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

    # def accept(self) -> None:
    #     print("check duration value")
    #     return super().accept()
    
    # def getValue(self):
    #     return self.field.getValue()

    def reject(self) -> None:
        return super().reject()
    
    def setProgress(self, val):
        self.progress.setValue(val)