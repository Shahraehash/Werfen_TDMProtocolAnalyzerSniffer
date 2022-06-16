from PyQt5 import QtCore, QtWidgets
import math

class TableViewer(QtWidgets.QTableView):
    
    clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        QtWidgets.QTableView.__init__(self, parent)
        self.dataframe_idx = -1
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dataframe_idx = math.floor(event.pos().y()/30)
            self.clicked.emit()
