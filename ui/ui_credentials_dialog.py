# ui_credentials_dialog.py
from PyQt6 import QtWidgets, QtGui

class Ui_CredentialsDialog(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle('Credentials')
        Dialog.setFixedWidth(600)

        layout = QtWidgets.QFormLayout(Dialog)

        # Set font to bold
        boldFont = QtGui.QFont()
        boldFont.setBold(True)

        # PlanningPME Credentials Section
        self.ppmeCredentialsLabel = QtWidgets.QLabel('PlanningPME Credentials')
        self.ppmeCredentialsLabel.setFont(boldFont)
        self.ppmeAppkeyEdit = QtWidgets.QLineEdit()
        self.ppmeAuthTokenEdit = QtWidgets.QLineEdit()
        self.ppmeAuthTokenEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        layout.addRow(self.ppmeCredentialsLabel, QtWidgets.QLabel(''))  # Section title
        layout.addRow('PPME Appkey', self.ppmeAppkeyEdit)
        layout.addRow('PPME Auth Token', self.ppmeAuthTokenEdit)

        # Microsoft Azure Credentials Section
        self.MSCredentialsLabel = QtWidgets.QLabel('Microsoft Azure Credentials')
        self.MSCredentialsLabel.setFont(boldFont)
        self.MSClientSecretEdit = QtWidgets.QLineEdit()
        self.MSClientSecretEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        layout.addRow(self.MSCredentialsLabel, QtWidgets.QLabel(''))  # Section title
        layout.addRow('Client Secret', self.MSClientSecretEdit)

        # Save button
        self.saveButton = QtWidgets.QPushButton('Save', Dialog)
        layout.addRow(self.saveButton)
