from PyQt6 import QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QAction
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QRect
from PyQt6.QtWidgets import QProgressDialog, QMessageBox, QApplication, QStyle, QStyleOptionButton, QHeaderView
from datetime import datetime
from dotenv import load_dotenv
import json
import os
import shutil
import subprocess
import sys
from ui.ui_main_window import Ui_MainWindow
from app import main
from .credentials_dialog import CredentialsDialog
from modules import utils

class CheckBoxHeader(QHeaderView):
    checkStateChanged = pyqtSignal(bool)

    def __init__(self, orientation, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isChecked = True
        self.setSectionsClickable(True)

    def paintSection(self, painter, rect, logicalIndex):
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        if logicalIndex == 0:  # Draw checkbox only in the first column header
            option = QStyleOptionButton()
            checkbox_size = 20  # Adjust size for visibility
            option.rect = QRect(
                rect.x() + (rect.width() - checkbox_size) // 2,
                rect.y() + (rect.height() - checkbox_size) // 2,
                checkbox_size, checkbox_size
            )
            option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
            if self.isChecked:
                option.state |= QStyle.StateFlag.State_On
            else:
                option.state |= QStyle.StateFlag.State_Off

            # print(f"Drawing checkbox at {option.rect}")  # Debug print to verify dimensions
            painter.save()
            painter.fillRect(rect, QColor("white"))  # Explicitly set the background color
            QApplication.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorCheckBox, option, painter)
            painter.restore()

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.position().toPoint())
        if index == 0:
            rect_x = self.sectionViewportPosition(index)
            rect_width = self.sectionSize(index)
            checkbox_size = 20  # Adjust size for visibility
            checkbox_rect = QRect(
                rect_x + (rect_width - checkbox_size) // 2,
                (self.height() - checkbox_size) // 2,
                checkbox_size, checkbox_size
            )
            # print(f"Checkbox rect: {checkbox_rect}")  # Debug print to verify dimensions
            if checkbox_rect.contains(event.position().toPoint()):
                self.isChecked = not self.isChecked
                self.updateSection(index)
                self.checkStateChanged.emit(self.isChecked)
                event.accept()
            else:
                super(CheckBoxHeader, self).mousePressEvent(event)
        else:
            super(CheckBoxHeader, self).mousePressEvent(event)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)  # Updated super call for Python 3
        self.setupUi(self)
        self.showMaximized()  # This line maximizes the window on startup

        self.actionCredentials = QAction("Credentials...", self)
        self.actionCredentials.setShortcut("Ctrl+K")
        self.menuEdit.addAction(self.actionCredentials)
        self.actionCredentials.triggered.connect(self.open_credentials_dialog)

        self.setupMissionTable() # Initialize the model for Mission tableView
        self.setupDepartmentTable() # Initialize the model for Department tableView
        self.current_task = None  # Add a variable to track the current task
        self.message = None # The message to display when the task is ongoing
        self.conflict_colors = {}  # Initialize the dictionary to store colors for each source
        self.color_index = 0  # Initialize the index for assigning colors

        # Connect buttons to functions
        self.fetchButton.clicked.connect(self.fetch_data)
        self.genButton.clicked.connect(self.generate_mission_orders)
        self.sendButton.clicked.connect(self.send_mission_orders)
        self.missionTableView.doubleClicked.connect(self.handleMissionDoubleClick)

        # self.cleanUpFolders()
        utils.init_folders()

    def exception_hook(exctype, value, traceback):
        QtWidgets.QMessageBox.critical(None, "Error", str(value))
        sys.__excepthook__(exctype, value, traceback)  # Optionally, re-raise the error to stop the program

    sys.excepthook = exception_hook

    def open_credentials_dialog(self):
        """Open the credentials dialog for user to fill in the credentials."""
        dialog = CredentialsDialog(self)
        dialog.exec()  # This will block until the dialog is closed

    def closeEvent(self, event):
        self.cleanUpFolders()
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

        # Set custom header view with checkboxes
        self.CheckboxHeader = CheckBoxHeader(Qt.Orientation.Horizontal, self.missionTableView)
        self.CheckboxHeader.checkStateChanged.connect(self.toggleAllCheckboxes)  # Connect to model method
        self.missionTableView.setHorizontalHeader(self.CheckboxHeader)

        # Set column headers
        self.missionHeaders = [None, 'Agents', 'Date & time', 'Client', 'SO n°', 'Intervention n°', 'Departure From', 'Location', 'Vehicle', 'Equipment', 'RT Sources', 'Attachments']
        self.missionModel.setHorizontalHeaderLabels(self.missionHeaders)

        self.apply_styleSheet(self.missionTableView)

        self.missionTableView.horizontalHeader().setVisible(True)
        self.missionTableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def handleMissionDoubleClick(self, index):
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

        # Load JSON data from a file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Set column headers
        headers = self.missionHeaders
        self.missionModel.setHorizontalHeaderLabels(headers) 
        self.missionTableView.setHorizontalHeader(self.CheckboxHeader)

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
                equipment_names = "\n".join(f"{equipment}" for equipment in item.get('equipment')) if item.get('equipment') else ''
                source_names = "\n".join(f"{source}" for source in item.get('sources')) if item.get('sources') else ''
                file_names = "\n".join(f"{filename}" for filename in item.get('attachmentFileNames')) if item.get('attachmentFileNames') else ''
                row.extend([
                    QStandardItem(resource_names),
                    QStandardItem(item.get('start')),
                    QStandardItem(item.get('customers')[0].get('label')),
                    QStandardItem(item.get('SOnumber')),
                    QStandardItem(str(item.get('key'))),
                    QStandardItem(item.get('departurePlace')),
                    QStandardItem(item.get('location')),
                    QStandardItem(item.get('vehicle')),
                    QStandardItem(equipment_names),
                    QStandardItem(source_names),
                    QStandardItem(file_names)
                ])
                # Set vertical alignment for all items in the row
                for cell in row:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.missionModel.appendRow(row)

            # Resize columns and rows
            self.missionTableView.resizeColumnsToContents()
            for row in range(self.missionModel.rowCount()):
                self.missionTableView.setRowHeight(row, 60)

        # Highlight rows containing conflicts...
        if conflicts:
            self.highlight_conflict_rows(conflicts)

    def get_selected_items(self, table):
        selected_items = []
        if table == "missions":
            for row in range(self.missionModel.rowCount()):
                if self.missionModel.item(row, 0).checkState() == Qt.CheckState.Checked:
                    mission_key = self.missionModel.item(row, 5).text()  # Assuming the mission key is in the sixth column
                    selected_items.append(mission_key)
        elif table == "departments":
            for row in range(self.departmentModel.rowCount()):
                if self.departmentModel.item(row, 0).checkState() == Qt.CheckState.Checked:
                    selected_items.append(self.departmentModel.item(row, 1).text())
        return selected_items
    
    def toggleAllCheckboxes(self, checked):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.missionModel.rowCount()):
            self.missionModel.item(row, 0).setCheckState(state)
                
    def show_conflict_results(self, conflicts):
        # There are conflicts, show the detailed message and update the table
        self.load_data_to_mission_table("./temp/missions.json", conflicts)
        sources = "\n".join(f"• {key}" for key in conflicts.keys())
        message = f"The following sources are booked several times:\n\n{sources}\n\nCheck missions overview for more information"
        QtWidgets.QMessageBox.warning(self, "Conflicts found!", message)

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
            item_key = self.missionModel.item(row, 5).text()  # Assuming key is in the sixth column
            for source, missions in conflicts.items():
                if item_key in missions:
                    color = QColor(self.conflict_colors[source])
                    for col in range(self.missionModel.columnCount()):
                        item = self.missionModel.item(row, col)
                        item.setBackground(color)

    # ------------------ Functions related to the worker call ------------------

    def start_thread(self, task_type, message, *args):
        self.thread = Worker(task_type, *args)  # Initialize the worker thread
        self.thread.progress_updated.connect(self.update_progress)  # Connect progress update signal
        self.thread.finished.connect(self.task_finished)  # Connect the finished signal
        self.thread.error_occurred.connect(self.handle_thread_error)  # Connect the error signal
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
        if self.thread.error:
            return  # Skip the rest of the function if an error occurred
        
        # Check which task finished and act accordingly
        if self.current_task == 'fetch_and_store':
            # After fetching, immediately check for conflicts
            conflicts = main.check_sources_conflicts()
            if conflicts:
                self.show_conflict_results(conflicts)
            else:
                self.load_data_to_mission_table("./temp/missions.json")
        self.progress_dialog.setValue(100)  # Update progress dialog to show completion
        self.current_task = None  # Reset current task
        self.message = None # Clear message

    def handle_thread_error(self, error_message):
        QtWidgets.QMessageBox.critical(self, "Error", error_message)
        self.progress_dialog.cancel()

    # ------------------ Functions linked to buttons ------------------

    def fetch_data(self):
        # Check if credentials are available
        if not utils.credentials_are_valid():
            self.open_credentials_dialog()
        if utils.credentials_are_valid():
            self.cleanUpFolders()
            # Get the date from the dateSelector
            selected_date = self.dateSelector.date().toPyDate()  # Converts QDate to Python date
            departments = self.get_selected_items("departments") # Get departments
            if departments == []:
                QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one department.")
                return
            self.current_task = 'fetch_and_store'  # Set the current task
            self.message = 'Data loading'

            self.start_thread(self.current_task, self.message, selected_date, departments)

    def generate_mission_orders(self):
        selected_keys = self.get_selected_items("missions")
        if not selected_keys:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one mission order to generate.")
            return
        self.current_task = 'generate'  # Set the current task
        self.message = 'Mission orders PDFs generating'
        self.start_thread(self.current_task, self.message, selected_keys)

    def send_mission_orders(self):
        selected_keys = self.get_selected_items("missions")
        # Check if any mission orders were selected
        if not selected_keys:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one mission order to send.")
            return
        # Format the date from the date selector
        selected_date = self.dateSelector.date().toPyDate()
        formatted_date = selected_date.strftime('%Y%m%d')
        generated_directory = f'./generated/{formatted_date}/'
        # Check if the directory exists
        if not os.path.exists(generated_directory):
            QtWidgets.QMessageBox.warning(self, "No Data", "Please first generate the mission orders.")
            return
        # Check if PDF files for all selected keys exist
        all_files_exist = True
        for key in selected_keys:
            # Check for any file containing the key in its name
            file_exists = any(key in filename for filename in os.listdir(generated_directory) if filename.endswith('.pdf'))
            if not file_exists:
                all_files_exist = False
                break
        if not all_files_exist:
            QtWidgets.QMessageBox.warning(self, "Incomplete Data", "Some selected missions have not been generated yet. Please generate them first.")
            return
        # Proceed with sending the missions
        self.current_task = 'send'  # Set the current task
        self.message = 'Mission orders sending'
        self.start_thread(self.current_task, self.message, selected_keys)

class MissionTableModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def flags(self, index):
        if index.column() == 0:
            return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        return super().flags(index)

# ------------------ Worker object ------------------

class Worker(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)  # Custom signal to emit error messages

    def __init__(self, task_type, *args, **kwargs):
        super(Worker, self).__init__()
        self.task_type = task_type
        self.args = args
        self.kwargs = kwargs
        self.error = False

    def run(self):
        try:
            if self.task_type == 'fetch_and_store':
                main.fetch_and_store(*self.args, progress_callback=self.handle_progress, **self.kwargs)
            elif self.task_type == 'generate':
                main.generate(*self.args, progress_callback=self.handle_progress, **self.kwargs)
            elif self.task_type == 'send':
                main.send(*self.args, progress_callback=self.handle_progress, **self.kwargs)
        except Exception as e:
            self.error = True
            self.error_occurred.emit(str(e))  # Emit the error message
        self.finished.emit()

    def handle_progress(self, progress):
        self.progress_updated.emit(progress)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
