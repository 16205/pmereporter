from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QProgressDialog
import json
import os
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.ui_main_window import Ui_MainWindow
import main

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.showMaximized()  # This line maximizes the window on startup
        self.setupTable() # Initialize the model for tableView
        self.current_task = None  # Add a variable to track the current task
        self.message = None # The message to display when the task is ongoing
        self.conflict_colors = {}  # Initialize the dictionary to store colors for each source
        self.color_index = 0  # Initialize the index for assigning colors

        # Connect buttons to functions
        self.fetchButton.clicked.connect(self.fetch_data)
        self.genButton.clicked.connect(self.generate_mission_orders)
        self.sendButton.clicked.connect(self.send_mission_orders)
        self.checkSources.clicked.connect(self.check_source_conflicts)

    def exception_hook(exctype, value, traceback):
        QtWidgets.QMessageBox.critical(None, "Error", str(value))
        sys.__excepthook__(exctype, value, traceback)  # Optionally, re-raise the error to stop the program

    sys.excepthook = exception_hook

    def closeEvent(self, event):
        # Call your cleanup function here
        self.cleanUpFolders()
        super().closeEvent(event)

    def cleanUpFolders(self):
        # Example: Clearing a temporary folder on close
        temp_folder = './temp/'
        generated_folder = './generated/'
        try:
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
                # print("Temporary files deleted.")
            if os.path.exists(generated_folder):
                shutil.rmtree(generated_folder)
                # print("Generated files deleted.")
        except Exception as e:
            raise Exception
            # print(f"Error deleting temporary files: {e}")

    def setupTable(self):
        # Initialize the model for tableView
        self.model = QStandardItemModel(self)
        self.missionTableView.setModel(self.model)

        # Set the table view to only allow checkbox changes
        self.missionTableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Disable text editing
        self.missionTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Enable row selection

        # Set column headers
        self.headers = ['Select', 'Agents', 'Date & time', 'Customer', 'SO n°', 'Intervention n°', 'Departure From', 'Location', 'RT Sources']
        self.model.setHorizontalHeaderLabels(self.headers)

    # ------------------ Functions that interact with the GUI ------------------

    def load_data_to_table(self, file_path, conflicts=None):
        # Clear existing data from the model
        self.model.clear()

        # Load JSON data from a file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Set column headers
            headers = self.headers
            self.model.setHorizontalHeaderLabels(headers) 

        # Assuming JSON data is a list of dictionaries
        if data:
            # Populate the rows of the table
            for item in data:
                row = []
                # Create a checkbox item
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.Checked)
                row.append(checkbox_item)
                # Append other data
                resource_names = "\n".join(f"{resource['lastName']} {resource['firstName']}" for resource in item.get('resources'))
                sources = ""
                for source in item.get('sources'):
                    sources += f"{source}\n"
                row.extend([
                    QStandardItem(resource_names),
                    QStandardItem(item.get('start')),
                    QStandardItem(item.get('customers')[0].get('label')),
                    QStandardItem(item.get('SOnumber')),
                    QStandardItem(str(item.get('key'))),
                    QStandardItem(item.get('departurePlace')),
                    QStandardItem(item.get('location')),
                    QStandardItem(sources)
                ])
                # Set vertical alignment for all items in the row
                for cell in row:
                    cell.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.model.appendRow(row)
                
            # Resize columns and rows
            self.missionTableView.resizeColumnsToContents()
            for row in range(self.model.rowCount()):
                self.missionTableView.setRowHeight(row, 50)

        # Load JSON data from a file and populate the table...
        if conflicts:
            self.highlight_conflict_rows(conflicts)


    def get_selected_items(self):
        selected_items = []
        for row in range(self.model.rowCount()):
            if self.model.item(row, 0).checkState() == Qt.Checked:
                mission_key = self.model.item(row, 5).text()  # Assuming the mission key is in the sixth column
                selected_items.append(mission_key)
        return selected_items

    def show_conflict_results(self, result_info):
        if result_info['data']:
            # There are conflicts, show the detailed message and update the table
            self.load_data_to_table("./temp/missions.json", result_info['data'])
            QtWidgets.QMessageBox.information(self, "Conflict Results", result_info['message'])
        else:
            # No conflicts, just show the message
            QtWidgets.QMessageBox.information(self, "Conflict Results", result_info['message'])

    def assign_colors_to_conflicts(self, conflicts):
        # Assign a unique color for each source
        available_colors = ['lightsalmon', 'lightcoral', 'lightyellow', 'lightpink', 'lightblue', 'lightgrey']
        for key in conflicts.keys():
            if key not in self.conflict_colors:
                self.conflict_colors[key] = available_colors[self.color_index % len(available_colors)]
                self.color_index += 1
    
    def highlight_conflict_rows(self, conflicts):
        # Call this method after data is loaded into the table
        self.assign_colors_to_conflicts(conflicts)
        for row in range(self.model.rowCount()):
            item_key = self.model.item(row, 5).text()  # Assuming key is in the sixth column
            for source, missions in conflicts.items():
                if item_key in missions:
                    for col in range(self.model.columnCount()):
                        self.model.item(row, col).setBackground(QColor(self.conflict_colors[source]))

    # ------------------ Functions related to the worker call ------------------

    def start_thread(self, task_type, message, *args):
        self.thread = Worker(task_type, *args)  # Initialize the worker thread
        self.thread.progress_updated.connect(self.update_progress)  # Connect progress update signal
        self.thread.finished.connect(self.task_finished)  # Connect the finished signal
        
        # Only connect the result_ready signal for the check_sources_conflicts task
        if task_type == 'check_sources_conflicts':
            self.thread.result_ready.connect(self.show_conflict_results)
        
        self.progress_dialog = QProgressDialog(f"Please wait, {message.lower()}...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle(f"{message}")
        self.progress_dialog.setModal(True)
        self.progress_dialog.setAutoClose(True)
        self.thread.start()  # Start the thread
        if self.progress_dialog.exec_() == QProgressDialog.Rejected:
            self.thread.terminate()  # Stop the thread if the dialog is canceled

    def update_progress(self, value):
        self.progress_dialog.setValue(value)

    def task_finished(self):
        # Check which task finished and act accordingly
        if self.current_task == 'fetch_and_store':
            self.load_data_to_table("./temp/missions.json")
        # elif self.current_task == 'generate':
        #     pass
        self.progress_dialog.setValue(100)  # Update progress dialog to show completion
        self.current_task = None  # Reset current task
        self.message = None # Clear message


    # ------------------ Functions linked to buttons ------------------

    def fetch_data(self):
        # Get the date from the dateSelector
        selected_date = self.dateSelector.date().toPyDate()  # Converts QDate to Python date

        self.current_task = 'fetch_and_store'  # Set the current task
        self.message = 'Data loading'

        self.start_thread(self.current_task, self.message, selected_date)

    def generate_mission_orders(self):
        selected_keys = self.get_selected_items()
        if not selected_keys:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one mission order to generate.")
            return
        self.current_task = 'generate'  # Set the current task
        self.message = 'Mission orders PDFs gererating'
        self.start_thread(self.current_task, self.message, selected_keys)

    def send_mission_orders(self):
        selected_keys = self.get_selected_items()
        if not selected_keys:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one mission order to send.")
            return
        self.current_task = 'send'  # Set the current task
        self.message = 'Mission orders sending'
        self.start_thread(self.current_task, self.message, selected_keys)

    def check_source_conflicts(self):
        self.current_task = 'check_sources_conflicts'
        self.message = 'Source conflicts'
        self.start_thread(self.current_task, self.message)

    def sync_sent_elements(self):
        pass

# ------------------ Worker object ------------------

class Worker(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()
    result_ready = pyqtSignal(dict)  # Signal to send back data

    def __init__(self, task_type, *args, **kwargs):
        super(Worker, self).__init__()
        self.task_type = task_type
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if self.task_type == 'fetch_and_store':
            main.fetch_and_store(*self.args, progress_callback=self.handle_progress, **self.kwargs)
        elif self.task_type == 'generate':
            main.generate(*self.args, **self.kwargs)
        elif self.task_type == 'send':
            main.send(*self.args, progress_callback=self.handle_progress, **self.kwargs)
        elif self.task_type == 'check_sources_conflicts':
            result = main.check_sources_conflicts(*self.args, **self.kwargs)
            if result:
                sources = "\n".join(f"• {key}" for key in result.keys())
                message = f"The following sources are booked several times:\n{sources}\nCheck missions overview for more information"
                self.result_ready.emit({'message': message, 'data': result})
            else:
                self.result_ready.emit({'message': "No conflicts detected!", 'data': None})
        self.finished.emit()

    def handle_progress(self, progress):
        self.progress_updated.emit(progress)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
