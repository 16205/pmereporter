# ui_credentials_dialog.py
from PyQt6 import QtWidgets, QtGui

class Ui_CredentialsDialog(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle('Credentials')
        Dialog.setFixedWidth(600)

        layout = QtWidgets.QFormLayout(Dialog)

        # Create labels for sections
        self.ppmeCredentialsLabel = QtWidgets.QLabel('PlanningPME Credentials')
        self.MSCredentialsLabel = QtWidgets.QLabel('Microsoft Azure Credentials')

        # Set font to bold
        boldFont = QtGui.QFont()
        boldFont.setBold(True)
        self.ppmeCredentialsLabel.setFont(boldFont)
        self.MSCredentialsLabel.setFont(boldFont)

        # Add labels and line edits to layout
        self.ppmeEndpointEdit = QtWidgets.QLineEdit()
        self.ppmeAppkeyEdit = QtWidgets.QLineEdit()
        self.ppmeAuthTokenEdit = QtWidgets.QLineEdit()
        self.ppmeAuthTokenEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        layout.addRow(self.ppmeCredentialsLabel, QtWidgets.QLabel(''))  # Section title
        layout.addRow('PPME Endpoint', self.ppmeEndpointEdit)
        layout.addRow('PPME Appkey', self.ppmeAppkeyEdit)
        layout.addRow('PPME Auth Token', self.ppmeAuthTokenEdit)

        self.MSClientIdEdit = QtWidgets.QLineEdit()
        self.MSClientSecretEdit = QtWidgets.QLineEdit()
        self.MSClientSecretEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.MSTenantIdEdit = QtWidgets.QLineEdit()

        layout.addRow(self.MSCredentialsLabel, QtWidgets.QLabel(''))  # Section title
        layout.addRow('Client ID', self.MSClientIdEdit)
        layout.addRow('Client Secret', self.MSClientSecretEdit)
        layout.addRow('Tenant ID', self.MSTenantIdEdit)

        # Save button
        self.saveButton = QtWidgets.QPushButton('Save', Dialog)
        layout.addRow(self.saveButton)