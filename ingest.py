import os
import requests

from dotenv import load_dotenv

load_dotenv(override=True)

connection_str = os.environ['HOST'] + 'api/'

def request(bearer_token):
    response = requests.get(connection_str + 'task', headers=)


