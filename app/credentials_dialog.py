from dotenv import load_dotenv, set_key, dotenv_values
from modules import utils
from ui.ui_credentials_dialog import Ui_CredentialsDialog
from PyQt6 import QtWidgets
from . import main
import os

class CredentialsDialog(QtWidgets.QDialog, Ui_CredentialsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Define the path to the .env file
        self.env_path = utils.get_env_path()

        # Initialize environment variables
        self.env_vars = self.load_env_vars()

        # Create line edits for credentials input
        self.setup_inputs()

        self.saveButton.clicked.connect(self.save_credentials)

    def setup_inputs(self):
        self.ppmeEndpointEdit.setText(self.env_vars.get('PPME_ENDPOINT'))
        self.ppmeAppkeyEdit.setText(self.env_vars.get('PPME_APPKEY'))
        if 'PPME_AUTH_TOKEN' in self.env_vars and self.env_vars['PPME_AUTH_TOKEN']:
            self.ppmeAuthTokenEdit.setPlaceholderText("[unchanged]")
        self.MSClientIdEdit.setText(self.env_vars.get('MS_CLIENT_ID'))
        if 'MS_CLIENT_SECRET' in self.env_vars and self.env_vars['MS_CLIENT_SECRET']:
            self.MSClientSecretEdit.setPlaceholderText("[unchanged]")
        self.MSTenantIdEdit.setText(self.env_vars.get('MS_TENANT_ID'))

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

        # Initialize user access token and full name
        main.init_user()
        
        # Close the dialog only if changes were made
        if changes:
            self.accept()