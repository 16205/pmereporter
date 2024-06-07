import os
import keyring
from modules import utils
from dotenv import load_dotenv, set_key
from PyQt6 import QtWidgets
from ui.ui_credentials_dialog import Ui_CredentialsDialog

class CredentialsDialog(QtWidgets.QDialog, Ui_CredentialsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Define the path to the .env file
        self.env_path = utils.get_env_path()

        # Load environment variables
        load_dotenv(self.env_path)

        # Create line edits for credentials input
        self.setup_inputs()

        self.saveButton.clicked.connect(self.save_credentials)

    def setup_inputs(self):

        # Load sensitive data from keyring
        self.ppmeAppkeyEdit.setText(keyring.get_password('pmereporter', 'PPME_APPKEY') if keyring.get_password('pmereporter', 'PPME_APPKEY') else "")
        self.ppmeAuthTokenEdit.setPlaceholderText("[unchanged]" if keyring.get_password('pmereporter', 'PPME_AUTH_TOKEN') else "")
        self.MSClientSecretEdit.setPlaceholderText("[unchanged]" if keyring.get_password('pmereporter', 'MS_CLIENT_SECRET') else "")

    def save_credentials(self):

        # Save sensitive data to keyring if changed
        if self.ppmeAppkeyEdit.text():
            keyring.set_password('pmereporter', 'PPME_APPKEY', self.ppmeAppkeyEdit.text())
            changes = True
        if self.ppmeAuthTokenEdit.text() and self.ppmeAuthTokenEdit.text() != "[unchanged]":
            keyring.set_password('pmereporter', 'PPME_AUTH_TOKEN', self.ppmeAuthTokenEdit.text())
            changes = True
        if self.MSClientSecretEdit.text() and self.MSClientSecretEdit.text() != "[unchanged]":
            keyring.set_password('pmereporter', 'MS_CLIENT_SECRET', self.MSClientSecretEdit.text())
            changes = True

        if changes:
            self.accept()  # Close the dialog only if changes were made

        if utils.credentials_are_valid():
            utils.init_user()