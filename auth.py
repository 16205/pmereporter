from dotenv import load_dotenv
from exchangelib import Account, OAuth2Credentials, Configuration, Identity
from msal import ConfidentialClientApplication
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
import http.server
import os
import requests
import socketserver
import threading
import urllib
import utils
import webbrowser

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

def authenticate_to_ms_graph():
    """
    Authenticates to Microsoft Graph using the OAuth 2.0 client credentials flow.

    This function retrieves the client ID and client secret from the environment
    variables and creates a confidential client application using the MSAL library.
    It then uses the authorization code to obtain an access token and refresh token
    from the Microsoft identity platform. The access token is stored in the
    MS_ACCESS_TOKEN environment variable and the refresh token is stored in the
    MS_REFRESH_TOKEN environment variable.

    Returns:
        str: The access token obtained from the Microsoft identity platform.
    """
    load_dotenv(override=True)
    # Constants
    CLIENT_ID = os.environ['MS_CLIENT_ID']
    CLIENT_SECRET = os.environ['MS_CLIENT_SECRET']
    TENANT_ID = os.environ['MS_TENANT_ID']
    AUTHORITY_URL = f'https://login.microsoftonline.com/{TENANT_ID}'
    SCOPE = ['Mail.Send', 'User.Read']

    # Initialize MSAL ConfidentialClientApplication
    app = ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY_URL, client_credential=CLIENT_SECRET)

    # Function to handle the OAuth callback and extract the authorization code
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            global authorization_code
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            query = urllib.parse.urlparse(self.path).query
            code = urllib.parse.parse_qs(query).get('code')
            if code:
                authorization_code = code[0]
                self.wfile.write(b"Authentication successful. You can now close this window.")
                # Signal the server to shutdown
                threading.Thread(target=httpd.shutdown).start()  # Use a thread to call shutdown
            else:
                self.wfile.write(b"Failed to authenticate.")
                authorization_code = None

    # Start temporary web server on a separate thread
    def run_server():
        global httpd
        with socketserver.TCPServer(("", 8000), Handler) as httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    auth_url = app.get_authorization_request_url(SCOPE)
    webbrowser.open(auth_url)

    # Wait for the server to handle the request
    server_thread.join()

    # Check if we received an authorization code
    if authorization_code:
        result = app.acquire_token_by_authorization_code(authorization_code, scopes=SCOPE)
        if result and 'access_token' in result and 'refresh_token' in result:
            utils.update_token_env(result['access_token'], 'MS_ACCESS_TOKEN')
            utils.update_token_env(result['refresh_token'], 'MS_REFRESH_TOKEN')
            print('Token acquired')
            return result['access_token']
        else:
            print('Failed to acquire token:', result.get('error_description'))
    else:
        print('No authorization code was received.')

def refresh_access_token():
    CLIENT_ID = os.environ['MS_CLIENT_ID']
    CLIENT_SECRET = os.environ['MS_CLIENT_SECRET']
    TENANT_ID = os.environ['MS_TENANT_ID']
    refresh_token = os.environ['MS_REFRESH_TOKEN']
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default offline_access"
    }
    response = requests.post(token_url, headers=headers, data=body)
    response.raise_for_status()
    new_tokens = response.json()
    utils.update_token_env(new_tokens.get('access_token'), 'MS_ACCESS_TOKEN')
    utils.update_token_env(new_tokens.get('refresh_token'), 'MS_REFRESH_TOKEN')
    return new_tokens['access_token']
