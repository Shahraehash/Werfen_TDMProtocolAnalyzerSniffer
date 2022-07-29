from PyQt5 import QtCore, QtWidgets

class TableViewer(QtWidgets.QTableView):
    
    clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        QtWidgets.QTableView.__init__(self, parent)
        self.dataframe_idx = -1
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
 
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            self.dataframe_idx = index.row()
            self.clicked.emit()
