from PyQt5.QtCore import QSortFilterProxyModel, QRegExp, Qt

class CustomProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filters = dict()
        self.list_kept_indices = []


    @property
    def filters(self):
        return self._filters

    def setFilter(self, expression, column):
        #set the values in the dictionary
        if expression:
            self._filters[column] = expression
        elif column in self._filters:
            del self._filters[column]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        for column, expression in self.filters.items():
            txt_idx = self.sourceModel().index(source_row, column, source_parent)
            text = txt_idx.data()
            regex = QRegExp(expression, Qt.CaseInsensitive, QRegExp.RegExp)
            if regex.indexIn(text) == -1:
                return False
            else:
                self.list_kept_indices += [txt_idx.row()]
        return True
