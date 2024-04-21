from dotenv import load_dotenv

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

import os
import requests

import utils


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
    
    load_dotenv(override=True)
    connection_str = os.environ['PPME_ENDPOINT'] + 'token'
    headers = {
        'X-APPKEY': os.environ['PPME_APPKEY']
    }

    response = requests.put(connection_str, headers=headers, 
                            data={'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 
                                'assertion': os.environ['PPME_AUTH_TOKEN']})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response data
        data = response.json()
        # Using '.get()' so it returns {} if key 'access_token' does not exist
        bearer_token = data.get('access_token', {})
        utils.update_token_env(bearer_token, 'PPME_BEARER_TOKEN')
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
    load_dotenv(override=True)
    site_url = os.environ['SHP_SITE_URL']
    client_id = os.environ['MS_CLIENT_ID']
    client_secret = os.environ['MS_CLIENT_SECRET']

    client_credential = ClientCredential(client_id, client_secret)
    ctx = ClientContext(site_url).with_credentials(client_credential)

    return ctx
