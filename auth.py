import os
import requests

from dotenv import load_dotenv

load_dotenv(override=True)

def authenticate():
    headers = {
        'X-APPKEY': os.environ['APPKEY']
    }

    response = requests.put(os.environ['HOST'] + 'token', headers=headers, 
                            data={'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 
                                'assertion': os.environ['AUTH_TOKEN']})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response data
        data = response.json()
        # Using '.get()' so it returns {} if key 'access_token' does not exist
        bearer_token = data.get('access_token', {})
        print(bearer_token)
        return bearer_token
    else:
        print("Failed to retrieve data:", response.status_code)
