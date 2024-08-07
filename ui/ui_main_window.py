# Form implementation generated from reading ui file '.\ui\MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.0.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again. Do not edit this file unless you know what you are doing.

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMessageBox
from modules import utils

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1120, 909)
        MainWindow.setWindowTitle("PMEReporter")
        MainWindow.setWindowIcon(QtGui.QIcon(utils.resource_path('media/icon.png')))
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create the menu bar
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        # self.menuBar.setGeometry(QtCore.QRect(0, 0, 500, 5))  # Adjust size accordingly
        self.menuBar.setObjectName("menuBar")

        # Create File menu
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setTitle("File")

        # Create Edit menu
        self.menuEdit = QtWidgets.QMenu(self.menuBar)
        self.menuEdit.setTitle("Edit")

        # Create About menu
        self.menuAbout = QtWidgets.QMenu(self.menuBar)
        self.menuAbout.setTitle("About")

        # Add menus to the menu bar
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuEdit)
        self.menuBar.addMenu(self.menuAbout)

        # Set the menu bar in the main window
        MainWindow.setMenuBar(self.menuBar)

        # Add actions to the File menu
        self.actionExit = QtGui.QAction("Exit", MainWindow)
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.triggered.connect(MainWindow.close)
        self.menuFile.addAction(self.actionExit)

        def showAboutDialog():
            QMessageBox.about(None, "About App", "PMEReporter version 1.2 - ©Vinçotte ASBL - 2024\n\nDeveloped by:\nGabriel Lohest\nglohest@vincotte.be\n+32 497 87 07 60")

        # Add actions to the About menu
        self.actionAbout = QtGui.QAction("About PMEReporter", MainWindow)
        self.actionAbout.triggered.connect(showAboutDialog)
        self.menuAbout.addAction(self.actionAbout)

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
        self.genButton = QtWidgets.QPushButton("Generate Mission Orders")
        self.sendButton = QtWidgets.QPushButton("Send Mission Orders")
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
        # self.dateSelector.setDate(QDate(2023, 11, 21))
        self.dateSelectorHorizontalLayout.addWidget(self.dateSelector, 2)
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
        self.departmentTableView.setFixedHeight(90)
        self.departmentVerticalLayout.addWidget(self.departmentTableView)
        self.rightVerticalLayout.addLayout(self.departmentVerticalLayout)

        self.fetchButton = QtWidgets.QPushButton("Load Missions")
        self.rightVerticalLayout.addWidget(self.fetchButton)
        self.rightVerticalLayout.addWidget(self.genButton)
        self.rightVerticalLayout.addWidget(self.sendButton)

        # Align right V Layout elements to top
        self.rightVerticalLayout.addStretch(1)

        # Add both left and right layouts to the tab 1 layout
        self.tab1layout.addLayout(self.leftVerticalLayout, 4) # 80% of space
        self.tab1layout.addLayout(self.rightVerticalLayout, 1) # 20% of space

        # # ------------------ Second tab ------------------
        # self.tab2 = QtWidgets.QWidget()
        # self.tab2.setObjectName("tab2")
        # self.tabWidget.addTab(self.tab2, "ADR Monthly Transport List")

        # # ------------------ Second tab horizontal layout ------------------
        # self.tab2layout = QtWidgets.QHBoxLayout(self.tab2) # Assign layout to the tab

        
        
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
