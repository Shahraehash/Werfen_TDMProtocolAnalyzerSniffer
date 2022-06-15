from PyQt5 import QtCore, QtGui, QtWidgets
#import pyqtgraph as pg
import sys

class MainForm(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.playTimer = QtCore.QTimer()
        self.playTimer.setInterval(500)
        self.playTimer.timeout.connect(self.playTick)
        self.toolbar = self.addToolBar("Play")
        self.playScansAction = QtWidgets.QAction(QtGui.QIcon("control_play_blue.png"), "play scans", self)
        self.playScansAction.triggered.connect(self.playScansPressed)
        self.playScansAction.setCheckable(True)
        self.toolbar.addAction(self.playScansAction)


    def playScansPressed(self):
        if self.playScansAction.isChecked():
            self.playTimer.start()
        else:
            self.playTimer.stop()

    def playTick(self):
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    #form.initUI("Scan Log Display")
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()