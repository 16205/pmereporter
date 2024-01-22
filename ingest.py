import os
import requests
import utils
from datetime import datetime

from dotenv import load_dotenv

load_dotenv(override=True)

connection_str = os.environ['HOST'] + 'api/'

headers = {
        'Authorization': 'Bearer ' + os.environ['BEARER_TOKEN'],
        'X-APPKEY': os.environ['APPKEY'],
        'Content-Type': 'application/json'
    }

def get_events(dateFrom:datetime=None, dateTo:datetime=None, departments:list=None, resources:list=None):
    dateFrom, dateTo = utils.format_date(dateFrom), utils.format_date(dateTo)
    
    json = {
        "dateFrom": dateFrom,
        "dateTo": dateTo,
    }

    if departments != None:
        json['departments'] = departments
    if resources != None:
        json['resources'] = resources

    # TODO: handle error if bad bearer token and other errors
    response = requests.post(connection_str + 'do/list', headers=headers, json=json)

    if response.status_code == 200:
        return response
    
    else:
        print("Failed to retrieve data:", response.status_code)

def get_departments(id:int=None):
    
    params = {
        "pageSize": 999
    }

    if id==None:
        response = requests.get(connection_str + 'department', params=params, headers=headers)

    else:
        response = requests.get(connection_str + 'department/' + str(id), params=params, headers=headers)    

    return response

