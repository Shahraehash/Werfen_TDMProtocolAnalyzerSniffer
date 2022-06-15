class MySortFilterProxyModel(QSortFilterProxyModel):

    Q_OBJECT
# public
    MySortFilterProxyModel(QObject parent = None)
    QDate filterMinimumDate() { return minDate; }
    def setFilterMinimumDate(date):
    QDate filterMaximumDate() { return maxDate; }
    def setFilterMaximumDate(date):
protected:
    filterAcceptsRow = bool(int sourceRow, QModelIndex sourceParent)
    lessThan = bool(QModelIndex left, QModelIndex right)
# private
    dateInRange = bool(QDate date)
    minDate = QDate()
    maxDate = QDate()

    def __init__(self, parent):
        QSortFilterProxyModel.__init__(self, parent)