import os
import requests
import utils

from dotenv import load_dotenv

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
