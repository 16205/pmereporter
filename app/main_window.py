from PyQt6 import QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QProgressDialog, QMessageBox, QStyledItemDelegate, QApplication, QStyle, QStyleOptionButton
from datetime import datetime
import json
import os
import shutil
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.ui_main_window import Ui_MainWindow
import main
from modules import utils

# class CenterCheckboxDelegate(QStyledItemDelegate):
#     def paint(self, painter, option, index):
#         if index.column() == 0:  # Assuming the checkboxes are in the first column
#             value = index.data(Qt.ItemDataRole.CheckStateRole)
#             opt = QStyleOptionButton()
#             opt.state = QStyle.StateFlag.State_Enabled
#             if value == Qt.CheckState.Checked:
#                 opt.state |= QStyle.StateFlag.State_On
#             else:
#                 opt.state |= QStyle.StateFlag.State_Off

#             # Checkbox dimensions and positioning
#             opt.rect = option.rect
#             checkbox_size = QApplication.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth)
#             opt.rect.setLeft(option.rect.center().x() - checkbox_size // 2)

#             # Draw the checkbox using the default style
#             QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox, opt, painter, None)
#         else:
#             super().paint(painter, option, index)

#     def editorEvent(self, event, model, option, index):
#         if event.type() == event.Type.MouseButtonRelease and index.column() == 0:
#             # Toggle the checkbox state
#             if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
#                 model.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
#             else:
#                 model.setData(index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
#             return True
#         return super().editorEvent(event, model, option, index)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)  # Updated super call for Python 3
        self.setupUi(self)
        self.showMaximized()  # This line maximizes the window on startup
        self.setupMissionTable() # Initialize the model for Mission tableView
        self.setupDepartmentTable() # Initialize the model for Department tableView
        self.setupSentTable() # Initialize the model for Sent Elements tableView
        self.current_task = None  # Add a variable to track the current task
        self.message = None # The message to display when the task is ongoing
        self.conflict_colors = {}  # Initialize the dictionary to store colors for each source
        self.color_index = 0  # Initialize the index for assigning colors

        # self.cleanUpFolders()
        utils.init_folders()

        # Connect buttons to functions
        self.fetchButton.clicked.connect(self.fetch_data)
        self.genButton.clicked.connect(self.generate_mission_orders)
        self.sendButton.clicked.connect(self.send_mission_orders)
        self.checkSources.clicked.connect(self.check_source_conflicts)
        self.syncButton.clicked.connect(self.sync_sent_elements)
        self.missionTableView.doubleClicked.connect(self.handleMissionDoubleClick)

    def exception_hook(exctype, value, traceback):
        QtWidgets.QMessageBox.critical(None, "Error", str(value))
        sys.__excepthook__(exctype, value, traceback)  # Optionally, re-raise the error to stop the program

    sys.excepthook = exception_hook

    def closeEvent(self, event):
        # Call your cleanup function here
        # self.cleanUpFolders()
        super().closeEvent(event)

    def cleanUpFolders(self):
        # Example: Clearing a temporary folder on close
        temp_folder = './temp/'
        generated_folder = './generated/'
        try:
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
            if os.path.exists(generated_folder):
                shutil.rmtree(generated_folder)
        except Exception as e:
            raise Exception

    def apply_styleSheet(self, table):
        # Add padding for text in cells
        table.setStyleSheet("""
            QTableView::item {
                padding: 3px;  /* Adjust padding as needed */
            }
            QTableView::item:selected {
                background-color: #bcdcf4;  /* Explicitly set the background color for selected items */
                color: black;  /* Ensure the text color is something visible against the background */
            }
        """)

    def setupMissionTable(self):
        # Initialize the model for tableView
        self.missionModel = MissionTableModel(self)
        self.missionTableView.setModel(self.missionModel)

        # Set the table view to only allow checkbox changes
        self.missionTableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable text editing
        self.missionTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # Enable row selection

        # Set column headers
        self.missionHeaders = ['Select All', 'Agents', 'Date & time', 'Client', 'SO n°', 'Intervention n°', 'Departure From', 'Location', 'RT Sources']
        self.missionModel.setHorizontalHeaderLabels(self.missionHeaders)

        self.apply_styleSheet(self.missionTableView)

        self.missionTableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        # # Apply the custom delegate to center checkboxes
        # checkbox_delegate = CenterCheckboxDelegate()
        # self.missionTableView.setItemDelegateForColumn(0, checkbox_delegate)

    def setupSentTable(self):
        # Initialize the model for tableView
        self.sentModel = QStandardItemModel(self)
        self.sentElementsTableView.setModel(self.sentModel)

        self.sentHeaders = ['Recipients', 'Subject', 'Sent Time']
        self.sentModel.setHorizontalHeaderLabels(self.sentHeaders)

        self.apply_styleSheet(self.sentElementsTableView)

        self.sentElementsTableView.verticalHeader().hide()

    def handleMissionDoubleClick(self, index):
        if index.row() != 0:
            # Extract the mission key from the selected row
            mission_key = self.missionModel.item(index.row(), 5).text()  # Assuming column 5 has the mission key
            mission = None
            with open('temp/missions.json', 'r') as file:
                missions = json.load(file)
            for data in missions:  # Assuming you store mission data somewhere accessible
                if data['key'] == mission_key:
                    mission = data
                    break
            
            if mission:
                names = ""
                for resource in mission.get('resources'):
                    names += resource['lastName'] + " " + resource['firstName'] + " - "
                mission_start = datetime.strptime(mission['start'], '%Y-%m-%d %H:%M:%S')

                day_missions = mission_start.strftime('%Y%m%d')  # Format the date
                pdf_path = f"./generated/{day_missions}/{names}{mission['key']}.pdf"
                
                if os.path.exists(pdf_path):
                    # Open the PDF if it exists
                    subprocess.Popen([pdf_path], shell=True)
                else:
                    # Show message box if the PDF does not exist
                    QMessageBox.information(self, "PDF Not Found", "Please first generate the PDF.")

    # ------------------ Functions that interact with the GUI ------------------

    def setupDepartmentTable(self):
        # Initialize the model for tableView
        self.departmentModel = QStandardItemModel(self)
        self.departmentTableView.setModel(self.departmentModel)

        self.departmentHeaders = ['', 'Department']
        self.departmentModel.setHorizontalHeaderLabels(self.departmentHeaders)

        # self.apply_styleSheet(self.departmentTableView)
        self.departmentTableView.verticalHeader().hide()

        # Set the department table to only allow checkbox changes
        self.departmentTableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable text editing
        self.departmentTableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)  # Disable row selection

        def create_checkbox():
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.CheckState.Checked)
            return checkbox_item

        self.departmentModel.appendRow([create_checkbox(), QStandardItem("North")])
        self.departmentModel.appendRow([create_checkbox(), QStandardItem("South")])

        # Resize columns and rows
        self.departmentTableView.resizeColumnsToContents()
        self.departmentTableView.resizeRowsToContents()
 
    def load_data_to_mission_table(self, file_path, conflicts=None):
        # Clear existing data from the model
        self.missionModel.clear()

        self.missionModel.setupInitialData() # Reinitialize the "Select all"

        # Load JSON data from a file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Set column headers
        headers = self.missionHeaders
        self.missionModel.setHorizontalHeaderLabels(headers) 

        # Assuming JSON data is a list of dictionaries
        if data:
            # Populate the rows of the table
            for item in data:
                row = []
                # Create a checkbox item
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.CheckState.Checked)
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
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.missionModel.appendRow(row)

            # Resize columns and rows
            self.missionTableView.resizeColumnsToContents()
            for row in range(self.missionModel.rowCount()):
                self.missionTableView.setRowHeight(row, 60)
        
        # Additional setup for row height, etc.
        self.missionTableView.setRowHeight(0, 10)  # Set a fixed height for the 'Select All' row

        # Highlight rows containing conflicts...
        if conflicts:
            self.highlight_conflict_rows(conflicts)

    def get_selected_items(self, table):
        selected_items = []
        if table == "missions":
            for row in range(1, self.missionModel.rowCount()):
                if self.missionModel.item(row, 0).checkState() == Qt.CheckState.Checked:
                    mission_key = self.missionModel.item(row, 5).text()  # Assuming the mission key is in the sixth column
                    selected_items.append(mission_key)
        elif table == "departments":
            for row in range(self.departmentModel.rowCount()):
                if self.departmentModel.item(row, 0).checkState() == Qt.CheckState.Checked:
                    selected_items.append(self.departmentModel.item(row, 1).text())
        return selected_items
                
    def show_conflict_results(self, result_info):
        if result_info['data']:
            # There are conflicts, show the detailed message and update the table
            self.load_data_to_mission_table("./temp/missions.json", result_info['data'])
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
        for row in range(self.missionModel.rowCount()):
            if row != 0:
                item_key = self.missionModel.item(row, 5).text()  # Assuming key is in the sixth column
                for source, missions in conflicts.items():
                    if item_key in missions:
                        color = QColor(self.conflict_colors[source])
                        for col in range(self.missionModel.columnCount()):
                            item = self.missionModel.item(row, col)
                            item.setBackground(color)

    def load_data_to_sent_table(self, file_path):
        self.sentModel.clear()

        # Load JSON data from a file
        with open(file_path, 'r') as file:
            data = json.load(file)

        headers = self.sentHeaders
        self.sentModel.setHorizontalHeaderLabels(headers)

        # Assuming JSON data is a list of dictionaries
        if data:
            # Populate the rows of the table
            for item in data:
                row = []
                recipients = "\n".join(f"{recipient}" for recipient in item.get('recipients').split(', '))
                # Append other data
                row.extend([
                    QStandardItem(recipients),
                    QStandardItem(item.get('subject')),
                    QStandardItem(item.get('sent_time'))
                ])
                # Set vertical alignment for all items in the row
                for cell in row:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.sentModel.appendRow(row)
                
            # Resize columns and rows
            for row in range(self.sentModel.rowCount()):
                self.sentElementsTableView.setRowHeight(row, 60)
            for column in range(self.sentModel.columnCount()):
                self.sentElementsTableView.setColumnWidth(column, 400)

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
        if self.progress_dialog.exec() == QProgressDialog.DialogCode.Rejected:
            self.thread.terminate()  # Stop the thread if the dialog is canceled

    def update_progress(self, value):
        self.progress_dialog.setValue(value)

    def task_finished(self):
        # Check which task finished and act accordingly
        if self.current_task == 'fetch_and_store':
            self.load_data_to_mission_table("./temp/missions.json")
        elif self.current_task == 'sync_sent_elements':
            self.load_data_to_sent_table("./temp/sentElements.json")
        self.progress_dialog.setValue(100)  # Update progress dialog to show completion
        self.current_task = None  # Reset current task
        self.message = None # Clear message


    # ------------------ Functions linked to buttons ------------------

    def fetch_data(self):
        # Get the date from the dateSelector
        selected_date = self.dateSelector.date().toPyDate()  # Converts QDate to Python date
        departments = self.get_selected_items("departments") # Get departments
        print(departments)

        self.current_task = 'fetch_and_store'  # Set the current task
        self.message = 'Data loading'

        self.start_thread(self.current_task, self.message, selected_date, departments)

    def generate_mission_orders(self):
        selected_keys = self.get_selected_items("missions")
        if not selected_keys:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one mission order to generate.")
            return
        self.current_task = 'generate'  # Set the current task
        self.message = 'Mission orders PDFs gererating'
        self.start_thread(self.current_task, self.message, selected_keys)

    def send_mission_orders(self):
        selected_keys = self.get_selected_items("missions")
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
        self.current_task = 'sync_sent_elements'
        self.message = 'Syncing sent elements'
        self.start_thread(self.current_task, self.message)

class MissionTableModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkState = Qt.CheckState.Checked

    def setupInitialData(self):
        # Initial setup for the 'Select All' checkbox
        select_all_item = QStandardItem()
        select_all_item.setCheckable(True)
        select_all_item.setCheckState(Qt.CheckState.Checked)
        self.insertRow(0, [select_all_item])

    def flags(self, index):
        # Standard flags setup, with non-selectable first row
        if index.row() == 0:
            return super().flags(index) & ~Qt.ItemFlag.ItemIsSelectable
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.row() == 0 and index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
            return self.checkState
        return super().data(index, role)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        # Managing check state and updating all checkboxes based on 'Select All'
        if index.row() == 0 and index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
            self.checkState = value
            self.toggleAllCheckboxes(value)
            self.dataChanged.emit(index, index, [role])  # Important to update the view
            return True
        return super().setData(index, value, role)

    def toggleAllCheckboxes(self, state):
        # Applying check state to all checkboxes in column 0
        for row in range(1, self.rowCount()):  # Skip the first row
            index = self.index(row, 0)
            super().setData(index, state, Qt.ItemDataRole.CheckStateRole)

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
            main.generate(*self.args, progress_callback=self.handle_progress, **self.kwargs)
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
        elif self.task_type =='sync_sent_elements':
            main.get_sent_elements(*self.args, **self.kwargs)
        self.finished.emit()

    def handle_progress(self, progress):
        self.progress_updated.emit(progress)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
