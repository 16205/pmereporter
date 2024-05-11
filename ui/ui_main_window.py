# Form implementation generated from reading ui file '.\ui\MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1120, 909)
        MainWindow.setWindowTitle("PMEReporter")
        MainWindow.setWindowIcon(QtGui.QIcon('media/icon.png'))
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ------------------ Tab widget ------------------
        self.tabWidget = QtWidgets.QTabWidget(MainWindow)
        self.tabWidget.setObjectName("tabWidget")

        # ------------------ First tab ------------------
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.tabWidget.addTab(self.tab1, "Generate Mission Orders")

        # ------------------ First tab horizontal layout ------------------
        self.tab1layout = QtWidgets.QHBoxLayout(self.tab1) # Assign layout to the tab

        # ------------------ Left side vertical layout ------------------
        self.leftVerticalLayout = QtWidgets.QVBoxLayout()
        self.titleLabel = QtWidgets.QLabel("Mission orders overview")
        self.titleLabel.setFont(QtGui.QFont("Arial", 12))
        self.leftVerticalLayout.addWidget(self.titleLabel)

        # ------------------ Missions tableView ------------------
        self.missionTableView = QtWidgets.QTableView()
        self.missionTableView.setObjectName("Mission orders")
        self.leftVerticalLayout.addWidget(self.missionTableView)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.genButton = QtWidgets.QPushButton("Generate mission orders")
        self.sendButton = QtWidgets.QPushButton("Send mission orders")
        self.horizontalLayout.addWidget(self.genButton)
        self.horizontalLayout.addWidget(self.sendButton)
        self.leftVerticalLayout.addLayout(self.horizontalLayout)

        # ------------------ Right side vertical layout ------------------
        self.rightVerticalLayout = QtWidgets.QVBoxLayout()
        self.titleLabel = QtWidgets.QLabel("Filters")
        self.titleLabel.setFont(QtGui.QFont("Arial", 12))
        self.rightVerticalLayout.addWidget(self.titleLabel)

        # ------------------ Date filter section ------------------
        self.dateSelectorVerticalLayout = QtWidgets.QVBoxLayout()
        self.titleLabel = QtWidgets.QLabel("Date selection")
        self.titleLabel.setFont(QtGui.QFont("Arial", 8))
        self.dateSelectorVerticalLayout.addWidget(self.titleLabel)
        # Date selector
        self.dateSelectorHorizontalLayout = QtWidgets.QHBoxLayout()
        self.dateSelector = QtWidgets.QDateEdit()
        self.dateSelector.setCalendarPopup(True)
        self.dateSelector.setDate(QDate.currentDate().addDays(1))
        self.dateSelectorHorizontalLayout.addWidget(self.dateSelector, 1)
        # Buttons for setting dates
        self.tomorrowButton = QtWidgets.QPushButton("Tomorrow")
        self.nextMondayButton = QtWidgets.QPushButton("Next Monday")
        self.tomorrowButton.clicked.connect(self.setTomorrow)
        self.nextMondayButton.clicked.connect(self.setNextMonday)
        self.dateSelectorHorizontalLayout.addWidget(self.tomorrowButton, 1)
        self.dateSelectorHorizontalLayout.addWidget(self.nextMondayButton, 1)
        # Add dateSelectorLayout to rightVerticalLayout
        self.dateSelectorVerticalLayout.addLayout(self.dateSelectorHorizontalLayout)
        self.rightVerticalLayout.addLayout(self.dateSelectorVerticalLayout)

        # ------------------ Department tableView filter ------------------
        self.departmentVerticalLayout = QtWidgets.QVBoxLayout()
        self.titleLabel = QtWidgets.QLabel("Department selection")
        self.titleLabel.setFont(QtGui.QFont("Arial", 8))
        self.departmentVerticalLayout.addWidget(self.titleLabel)
        # Department tableView selector
        self.departmentTableView = QtWidgets.QTableView()
        self.departmentTableView.setFixedHeight(60)
        self.departmentVerticalLayout.addWidget(self.departmentTableView)
        self.rightVerticalLayout.addLayout(self.departmentVerticalLayout)

        self.fetchButton = QtWidgets.QPushButton("Fetch data")
        self.checkSources = QtWidgets.QPushButton("Check source conflicts")
        self.rightVerticalLayout.addWidget(self.fetchButton)
        self.rightVerticalLayout.addWidget(self.checkSources)

        # Align right V Layout elements to top
        self.rightVerticalLayout.addStretch(1)

        # Add both left and right layouts to the tab 1 layout
        self.tab1layout.addLayout(self.leftVerticalLayout, 3) # 75% of space
        self.tab1layout.addLayout(self.rightVerticalLayout, 1) # 25% of space

        # ------------------ Second tab ------------------
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setObjectName("tab2")
        self.tabWidget.addTab(self.tab2, "Sent mission orders")

        # ------------------ Second tab vertical layout ----------------
        self.tab2layout = QtWidgets.QVBoxLayout(self.tab2) # Assign layout to the tab
        self.titleLabel = QtWidgets.QLabel("Sent elements")
        self.titleLabel.setFont(QtGui.QFont("Arial", 12))

        self.sentElementsTableView = QtWidgets.QTableView()
        self.sentElementsTableView.setObjectName("Sent elements")

        self.tab2layout.addWidget(self.titleLabel)
        self.tab2layout.addWidget(self.sentElementsTableView)

        MainWindow.setCentralWidget(self.tabWidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

    def setTomorrow(self):
        self.dateSelector.setDate(QDate.currentDate().addDays(1))

    def setNextMonday(self):
        today = QDate.currentDate()
        # Calculate the number of days until next Monday
        days_to_monday = (7 - today.dayOfWeek() + 1) % 7
        if days_to_monday == 0:
            days_to_monday = 7  # If today is Monday, set next Monday (7 days ahead)
        self.dateSelector.setDate(today.addDays(days_to_monday))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PMEReporter"))
        self.fetchButton.setText(_translate("MainWindow", "Fetch data"))
        self.genButton.setText(_translate("MainWindow", "Generate mission orders"))
        self.sendButton.setText(_translate("MainWindow", "Send mission orders"))
        self.checkSources.setText(_translate("MainWindow", "Check source conflicts"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())