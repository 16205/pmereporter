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
    """
    Authenticates to the PPME api service using the APPKEY and AUTH_TOKEN environment variables.
    Upon successful authentication, updates the environment variable for the bearer token
    using the utility function `update_token_env`.

    The function sends a PUT request to the PPME service with the necessary authentication
    details and handles the response. If the authentication is successful, it updates the
    bearer token in the environment. If the authentication fails, it logs the failure.

    Returns:
        None. The function directly updates the environment variable for the bearer token
        upon successful authentication or logs an error message upon failure.
    """
    
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
        print("Successfully authenticated")
        return
    else:
        # TODO: Investigate whether to replace print with sys.exit()
        print("Failed to authenticate:", response.status_code)

def authenticate_to_shpt():
    """
    Authenticates to a SharePoint site using the client credentials flow.

    This function retrieves the SharePoint site URL, client ID, and client secret from
    environment variables. It then creates a client credential object and uses it to
    authenticate to the SharePoint site. The authenticated client context is returned,
    allowing for further operations on the SharePoint site.

    Returns:
        ClientContext: An authenticated SharePoint client context object.
    """
    site_url = os.environ['SHP_SITE_URL']
    client_id = os.environ['SHP_CLIENT_ID']
    client_secret = os.environ['SHP_CLIENT_SECRET']

    client_credential = ClientCredential(client_id, client_secret)
    ctx = ClientContext(site_url).with_credentials(client_credential)

    return ctx

def authenticate_to_mail():
    """
    Authenticates to an Exchange mailbox using OAuth2 credentials.

    This function sets up OAuth2 credentials with the necessary client ID, client secret,
    tenant ID, and the primary SMTP address of the mailbox. It then creates a configuration
    object for connecting to the Exchange server and initializes an Account object with
    impersonation access type to interact with the mailbox.

    The environment variables 'SHP_CLIENT_ID', 'SHP_CLIENT_SECRET', 'TENANT_ID', and
    'ACCOUNT_EMAIL' are used to retrieve the necessary authentication details.

    Returns:
        account: An authenticated exchangelib Account object for the specified mailbox.
    """
    # Retrieve authentication details from environment variables
    client_id = os.environ['SHP_CLIENT_ID']
    client_secret = os.environ['SHP_CLIENT_SECRET']
    tenant_id = os.environ['TENANT_ID']
    account_email = os.environ['ACCOUNT_EMAIL']

    # Setup OAuth2 credentials with the retrieved details
    credentials = OAuth2Credentials(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        identity=Identity(primary_smtp_address=account_email)
    )

    # Create a configuration object for the Exchange server
    config = Configuration(server='outlook.office365.com', credentials=credentials)
    # Initialize and return an Account object for interacting with the mailbox
    account = Account(primary_smtp_address=account_email, config=config, autodiscover=False, access_type='impersonation')

    return account