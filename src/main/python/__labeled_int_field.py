from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
  
import sys
  
# A simple widget consisting of a QLabel and a QLineEdit that 
# uses a QIntValidator to ensure that only integer inputs are
# accepted. This class could be implemented in a separate 
# script called, say, labelled_int_field.py
class LabelledIntField(QWidget):
    def __init__(self, title, font, initial_value=None):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)

        #self.label = QLabel()
        #self.label.setText(title)
        #self.label.setFixedWidth(100)
        #self.label.setFont(QFont("Arial",weight=QFont.Bold))
        #layout.addWidget(self.label)
        
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setAttribute(Qt.WA_MacShowFocusRect, 0) # this gets rid of outline on focus
        self.lineEdit.setFixedWidth(70)
        self.lineEdit.setFont(font)
        #self.lineEdit.setFixedHeight(24)
        #print(maxnum)
        self.lineEdit.setValidator(QIntValidator())
        if initial_value != None:
            self.lineEdit.setText(str(initial_value))
        layout.addWidget(self.lineEdit)
        #layout.addStretch()
        
    #def setLabelWidth(self, width):
        #self.label.setFixedWidth(width)
        
    def setInputWidth(self, width):
        self.lineEdit.setFixedWidth(width)
        
    def getValue(self):
        return int(self.lineEdit.text())