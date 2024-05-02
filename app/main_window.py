from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.ui_main_window import Ui_MainWindow
import main

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.showMaximized()  # This line maximizes the window on startup

        # Initialize the model for tableView
        self.model = QStandardItemModel(self)
        self.tableView.setModel(self.model)

        # Connect buttons to functions
        self.pushButton_2.clicked.connect(self.fetch_data)
        self.pushButton.clicked.connect(self.generate_mission_orders)
        self.pushButton_3.clicked.connect(self.send_mission_orders)

    def load_data_to_table(self, file_path):
        # Clear existing data from the model
        self.model.clear()

        # Load JSON data from a file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Assuming JSON data is a list of dictionaries
        if data:
            # Set column headers using keys from the first dictionary, if present
            self.model.setHorizontalHeaderLabels(data[0].keys())

            # Populate the rows of the table
            for item in data:
                row = [QStandardItem(str(value)) for value in item.values()]
                self.model.appendRow(row)

    def fetch_data(self):
        self.thread = Worker('fetch_and_store')  # Initialize the worker thread
        self.thread.progress_updated.connect(self.update_progress)  # Connect progress update signal
        self.thread.finished.connect(self.task_finished)  # Connect the finished signal
        
        # Initialize and display the progress dialog
        self.progress_dialog = QProgressDialog("Fetching data...", "Cancel", 0, 100, self)
        self.progress_dialog.setModal(True)
        self.progress_dialog.setAutoClose(True)
        
        self.thread.start()  # Start the thread
        if self.progress_dialog.exec_() == QProgressDialog.Rejected:
            self.thread.terminate()  # Stop the thread if the dialog is canceled

    def update_progress(self, value):
        self.progress_dialog.setValue(value)

    def task_finished(self):
        # Handle any cleanup or final steps after task completion
        self.progress_dialog.setValue(100)
        self.load_data_to_table("./temp/missions.json")

    def generate_mission_orders(self):
        print("Generating mission orders...")
        main.generate()

    def send_mission_orders(self):
        print("Sending mission orders...")
        main.send()

class Worker(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, task_type, *args, **kwargs):
        super(Worker, self).__init__()
        self.task_type = task_type
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if self.task_type == 'fetch_and_store':
            main.fetch_and_store(progress_callback=self.handle_progress, *self.args, **self.kwargs)
        elif self.task_type == 'generate':
            main.generate(*self.args, **self.kwargs)
        elif self.task_type == 'send':
            main.send(*self.args, **self.kwargs)
        self.finished.emit()

    def handle_progress(self, progress):
        self.progress_updated.emit(progress)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
