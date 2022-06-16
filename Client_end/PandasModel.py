from PyQt5 import QtCore, QtGui

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            
            if role == QtCore.Qt.BackgroundRole:
                value = str(self._data.Status.values.tolist()[index.row()])
                #color code according to the status 
                if value == '':
                    return QtGui.QColor('lightgray')
                if value == '--':
                    return QtGui.QColor('silver')
                if value == 'STATUS_Success':
                    return QtGui.QColor('lightgreen')
                if value[:11] == 'STATUS_Error':
                    return QtGui.QColor('red')
                return QtGui.QColor('yellow')
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._data.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                number_of_entries = []
                for i in range(self._data.shape[0]):
                    number_of_entries.append(i)
                return number_of_entries[section]
            except (IndexError, ):
                return QtCore.QVariant()
    
    def sort(self, column, order):
        colname = self._data.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        #sort based on the time from the latest call at the bottom
        self._data.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._data.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()