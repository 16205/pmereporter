from dotenv import load_dotenv
from msal import ConfidentialClientApplication
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from .utils import update_token_env
import http.server
import os
import requests
import socketserver
import threading
import urllib
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
        update_token_env(bearer_token, 'PPME_BEARER_TOKEN')
        # print("Successfully authenticated")
        return
    else:
        raise Exception

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
    Authenticates to Microsoft Graph using the OAuth 2.0 authorization code flow. This function initializes
    an MSAL ConfidentialClientApplication, starts a temporary web server to listen for the OAuth callback,
    and extracts the authorization code from the callback URL. It then exchanges the authorization code for
    an access token and a refresh token, and updates these tokens in the environment variables.

    The function uses environment variables to get the client ID, client secret, and tenant ID required for
    authentication. It defines a scope that includes permissions to send mail and read user profiles.

    Returns:
        str: The access token acquired from Microsoft Graph if authentication is successful, None otherwise.
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
            """
            Handles GET requests sent to the temporary web server. It extracts the authorization code from
            the query parameters of the request URL. If an authorization code is found, it signals the server
            to shutdown and updates the global variable `authorization_code` with the received code.

            Parameters:
                None

            Returns:
                None
            """
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
        """
        Starts a temporary web server on a new thread to listen for the OAuth callback. The server runs
        on localhost and listens on port 8000.

        Parameters:
            None

        Returns:
            None
        """
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
            update_token_env(result['access_token'], 'MS_ACCESS_TOKEN')
            update_token_env(result['refresh_token'], 'MS_REFRESH_TOKEN')
            print('Token acquired')
            return result['access_token']
        else:
            print('Failed to acquire token:', result.get('error_description'))
    else:
        print('No authorization code was received.')

def refresh_access_token():
    """
    This function is used to refresh the access token for Microsoft Graph.

    Args:
        None

    Returns:
        str: The refreshed access token

    Raises:
        requests.exceptions.HTTPError: If the request to refresh the access token fails
    """
    load_dotenv(override=True)

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
    update_token_env(new_tokens.get('access_token'), 'MS_ACCESS_TOKEN')
    update_token_env(new_tokens.get('refresh_token'), 'MS_REFRESH_TOKEN')
    return new_tokens['access_token']
