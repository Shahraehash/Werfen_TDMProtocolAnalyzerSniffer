import sys
#from PySide2.QtCore import Qt, Slot
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QTableView, QGridLayout, QGroupBox)
from PyQt5 import  uic
#from PyQt5.QtWidgets import QTableView as Qtv
import pandas as pd
from PandasModelv2 import PandasModel
#from openpyxl import load_workbook


class Widget(QtWidgets.QMainWindow):
    def __init__(self):        
        super(Widget, self).__init__() # Call the inherited classes __init__ method
        #uic.loadUi('Test1.ui', self) # Load the .ui file
       
        
        ## Items 
        self.items = 0
        
        #Reading Data with Pandas. 
        #self._data = pd.read_excel('dataE.xlsx')
        self._data = pd.read_csv('test.csv')
        ## Writing with openpyxl to edit.
        #self.wb = load_workbook(filename = 'dataE.xlsx')
        #self.ws = self.wb['Sheet1']
        #######UI Build #######
        self.table = self.findChild(QtWidgets.QTableView, 'tableView')
        
        
        
         ###### Left
        # self.table = QTableView(self)       
        
        self.model = PandasModelv2.PandasModel(self._data)
        
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
         
   
       
        

        
        
        ### Do Not Comment Out Below.##########

        ######### Signals and Slots
        self.addNewBtn.clicked.connect(self.add_element)
        # self.quit.clicked.connect(self.quit_application)
        # self.clear.clicked.connect(self.clear_table)
        # self.alarmNote.textChanged[str].connect(self.check_disable)
        # self.assetID.textChanged[str].connect(self.check_disable)
    
        ## Filter area
        self.filter_proxy_model = QtCore.QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterKeyColumn(0) # First column
        self.searchLine.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.table.setModel(self.filter_proxy_model)
        
        ### Select Whole row if click on item.
        #self.selected = self.table.setSelectionBehavior(QTableView.SelectRows)
        
        #### TEST AREA FOR SELECTION ####
        self.table.clicked.connect(self.add_element)
        
        
    '''
    @Slot()
    def add_element(self, index):
        datas = index.data()
        #datas = str(self._data.loc(self.selected))
        self.alarmGen.setText(datas)
       
        #print(self._data.iloc[[0], [0,1,2]])
        
        
    
        
    @Slot()
    def quit_application(self):
        QApplication.quit()


    @Slot()
    def clear_table(self):
        self.table.setRowCount(0)
        self.items = 0   
   '''     
class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Alpha Notation Tool")

        # Menu
        # self.menu = self.menuBar()
        # self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        # self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)
    
    '''
    @Slot()
    def exit_app(self, checked):
        QApplication.quit()        
    ''' 
if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    #window = uic.loadUi("Test1.ui")
    window.resize(906, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())       