from PyQt6 import QtWidgets, QtGui
import os

class CredentialsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Credentials')
        self.setFixedWidth(600)

        layout = QtWidgets.QFormLayout(self)

        # Initialize environment variables
        self.env_vars = self.load_env_vars()

        # Create line edits for credentials input
        self.setup_inputs()

        # Create label for sections
        ppmeCredentialsLabel = QtWidgets.QLabel('PlanningPME Credentials')
        msCredentialsLabel = QtWidgets.QLabel('Microsoft Azure Credentials')
        # Set font to bold
        boldFont = QtGui.QFont()
        boldFont.setBold(True)
        ppmeCredentialsLabel.setFont(boldFont)
        msCredentialsLabel.setFont(boldFont)
        
        # Add line edits to layout
        layout.addRow(ppmeCredentialsLabel, QtWidgets.QLabel(''))  # Section title
        layout.addRow('PPME Endpoint', self.ppmeEndpointEdit)
        layout.addRow('PPME Appkey', self.ppmeAppkeyEdit)
        layout.addRow('PPME Auth Token', self.ppmeAuthTokenEdit)

        layout.addRow(msCredentialsLabel, QtWidgets.QLabel(''))  # Section title
        layout.addRow('Client ID:', self.MSClientEdit)
        layout.addRow('Client Secret:', self.MSClientSecretEdit)
        layout.addRow('Tenant ID:', self.MSTenantIdEdit)

        # Save button
        self.saveButton = QtWidgets.QPushButton('Save', self)
        self.saveButton.clicked.connect(self.save_credentials)
        layout.addRow(self.saveButton)

    def setup_inputs(self):
        self.ppmeEndpointEdit = QtWidgets.QLineEdit(self.env_vars.get('PPME_ENDPOINT'))
        self.ppmeAppkeyEdit = QtWidgets.QLineEdit(self.env_vars.get('PPME_APPKEY'))
        self.ppmeAuthTokenEdit = QtWidgets.QLineEdit()
        self.ppmeAuthTokenEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        if 'PPME_AUTH_TOKEN' in self.env_vars and self.env_vars['PPME_AUTH_TOKEN']:
            self.ppmeAuthTokenEdit.setPlaceholderText("[unchanged]")
            self.ppmeAuthTokenEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.PasswordEchoOnEdit)

        self.MSClientEdit = QtWidgets.QLineEdit(self.env_vars.get('MS_CLIENT_ID'))
        self.MSClientSecretEdit = QtWidgets.QLineEdit()
        self.MSClientSecretEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        if 'MS_CLIENT_SECRET' in self.env_vars and self.env_vars['MS_CLIENT_SECRET']:
            self.MSClientSecretEdit.setPlaceholderText("[unchanged]")
            self.MSClientSecretEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.MSTenantIdEdit = QtWidgets.QLineEdit(self.env_vars.get('MS_TENANT_ID'))

    def load_env_vars(self):
        if os.path.exists('.env'):
            with open('.env', 'r') as file:
                env_vars = file.readlines()
            return {line.split('=')[0].strip(): line.split('=')[1].strip() for line in env_vars if '=' in line}
        return {}

    def save_credentials(self):
        changes = False
        with open('.env', 'w') as f:
            for key, edit in [('PPME_ENDPOINT', self.ppmeEndpointEdit), ('PPME_APPKEY', self.ppmeAppkeyEdit), 
                              ('CLIENT_ID', self.MSClientEdit), ('TENANT_ID', self.MSTenantIdEdit)]:
                if self.env_vars.get(key, '') != edit.text() and self.env_vars.get(key, ''):
                    f.write(f'{key}={edit.text()}\n')
                    changes = True

            # Handle secrets specially to not overwrite with placeholders
            for key, edit in [('PPME_AUTH_TOKEN', self.ppmeAuthTokenEdit), ('CLIENT_SECRET', self.MSClientSecretEdit)]:
                if edit.text() and edit.text() != "[unchanged]" and edit.text():
                    f.write(f'{key}={edit.text()}\n')
                    changes = True

        if changes:
            self.accept()  # Close the dialog only if changes were made

