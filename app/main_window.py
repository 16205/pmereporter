from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.ui_main_window import Ui_MainWindow
import main

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Connect buttons to functions
        self.pushButton_2.clicked.connect(self.fetch_data)
        self.pushButton.clicked.connect(self.generate_mission_orders)
        self.pushButton_3.clicked.connect(self.send_mission_orders)

    def fetch_data(self):
        # Your function logic here
        print("Fetching data...")
        # Example call to a function from your module
        main.fetch_and_store()

    def generate_mission_orders(self):
        # Your function logic here
        print("Generating mission orders...")
        # Example call to a function from your module
        main.generate()

    def send_mission_orders(self):
        # Your function logic here
        print("Sending mission orders...")
        # Example call to a function from your module
        main.send()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())