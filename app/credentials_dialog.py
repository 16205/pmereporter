from dotenv import load_dotenv, set_key, dotenv_values
from modules import utils
from PyQt6 import QtWidgets, QtGui
import os

class CredentialsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Credentials')
        self.setFixedWidth(600)

        layout = QtWidgets.QFormLayout(self)

        # Define the path to the .env file
        self.env_path = utils.get_env_path()

        # Initialize environment variables
        self.env_vars = self.load_env_vars()

        # Create line edits for credentials input
        self.setup_inputs()

        # Create label for sections
        ppmeCredentialsLabel = QtWidgets.QLabel('PlanningPME Credentials:')
        msCredentialsLabel = QtWidgets.QLabel('Microsoft Azure Credentials:')
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
        layout.addRow('Client ID:', self.MSClientIdEdit)
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

        self.MSClientIdEdit = QtWidgets.QLineEdit(self.env_vars.get('MS_CLIENT_ID'))
        self.MSClientSecretEdit = QtWidgets.QLineEdit()
        self.MSClientSecretEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        if 'MS_CLIENT_SECRET' in self.env_vars and self.env_vars['MS_CLIENT_SECRET']:
            self.MSClientSecretEdit.setPlaceholderText("[unchanged]")
            self.MSClientSecretEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.MSTenantIdEdit = QtWidgets.QLineEdit(self.env_vars.get('MS_TENANT_ID'))

    def load_env_vars(self):
        load_dotenv(self.env_path)  # Load environment variables from the specified .env file
        return {key: value for key, value in os.environ.items() if key in [
            'PPME_ENDPOINT', 'PPME_APPKEY', 'PPME_AUTH_TOKEN', 'MS_CLIENT_ID', 'MS_CLIENT_SECRET', 'MS_TENANT_ID']}

    def save_credentials(self):
        current_credentials = dotenv_values(self.env_path)  # Load the existing credentials
        changes = False
        
        # Initialize edits dictionary with all current credentials
        edits = dict(current_credentials)

        # Update the dictionary with new values if they have been changed
        new_values = {
            'PPME_ENDPOINT': self.ppmeEndpointEdit.text(),
            'PPME_APPKEY': self.ppmeAppkeyEdit.text(),
            'PPME_AUTH_TOKEN': self.ppmeAuthTokenEdit.text(),
            'MS_CLIENT_ID': self.MSClientIdEdit.text(),
            'MS_CLIENT_SECRET': self.MSClientSecretEdit.text(),
            'MS_TENANT_ID': self.MSTenantIdEdit.text(),
        }

        # Apply new values only if they have been changed from the original
        for key, new_value in new_values.items():
            if new_value and new_value != "[unchanged]":  # Ensure new_value is not placeholder or empty
                if current_credentials.get(key, '') != new_value:
                    edits[key] = new_value
                    set_key(self.env_path, key, new_value)
                    changes = True

        # Close the dialog only if changes were made
        if changes:
            self.accept()