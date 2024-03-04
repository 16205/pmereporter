import os
import requests
import utils
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from dotenv import load_dotenv
from exchangelib import Account, OAuth2Credentials, Configuration, Identity
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext


load_dotenv(override=True)

connection_str = os.environ['HOST'] + 'token'

def authenticate_to_ppme():
    headers = {
        'X-APPKEY': os.environ['APPKEY']
    }

    response = requests.put(connection_str, headers=headers, 
                            data={'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 
                                'assertion': os.environ['AUTH_TOKEN']})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response data
        data = response.json()
        # Using '.get()' so it returns {} if key 'access_token' does not exist
        bearer_token = data.get('access_token', {})
        utils.update_token_env(bearer_token)
        return
    else:
        print("Failed to retrieve data:", response.status_code)

def authenticate_to_shpt():
    site_url = "https://yourtenant.sharepoint.com/sites/yoursite"
    client_id = "your-client-id"
    client_secret = "your-client-secret"

    client_credential = ClientCredential(client_id, client_secret)
    ctx = ClientContext(site_url).with_credentials(client_credential)

    # Now you can interact with SharePoint resources

    pass

def authenticate_to_mail():
    # OAuth2 credentials and configuration
    client_id = 'your-client-id'
    client_secret = 'your-client-secret'  # Only needed for confidential clients
    tenant_id = 'your-tenant-id'
    account_email = 'user@example.com'

    credentials = OAuth2Credentials(
        client_id=client_id,
        client_secret=client_secret,  # Leave out if using a public client
        tenant_id=tenant_id,
        identity=Identity(primary_smtp_address=account_email)
    )

    config = Configuration(server='outlook.office365.com', credentials=credentials)
    account = Account(primary_smtp_address=account_email, config=config, autodiscover=False, access_type='impersonation')

    # Now you can use the account object to send emails, access mailbox items, etc.

    pass