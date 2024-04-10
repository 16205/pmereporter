import os
import requests
import utils
import sys
from tqdm import tqdm
from datetime import datetime

from dotenv import load_dotenv

load_dotenv(override=True)

connection_str = os.environ['HOST'] + 'api/'

headers = {
        'Authorization': 'Bearer ' + os.environ['BEARER_TOKEN'],
        'X-APPKEY': os.environ['APPKEY'],
        'Content-Type': 'application/json'
    }

def get_events(dateFrom:datetime, dateTo:datetime=None, departments:list=None, resources:list=None, 
               categories:list=[52,60,63,65,78,80]):
    
    dateFrom, dateTo = utils.format_date(dateFrom), utils.format_date(dateTo)
    
    json = {
        "dateFrom": dateFrom,
        "dateTo": dateTo,
        "departments": departments,
        "resources": resources,
        "categories": categories,
        "results": "Task"
    }
    # TODO: calculate datetime 1 day diff
    # TODO: use kwargs
    # if departments != None:
    #     json['departments'] = departments
    # if resources != None:
    #     json['resources'] = resources
    # if categories != None:
    #     json['categories'] = categories

    print("Getting mission events...")
    # TODO: handle error if bad bearer token and other errors
    response = requests.post(connection_str + 'do/list', headers=headers, json=json)

    if response.status_code == 200:
        # Return response content only (this is why .json() is used)
        print(f"Got {len(response.json()['items'])} mission events!")
        return response.json()
    
    elif response.status_code == 401:
        sys.exit(f"Please authenticate to PlanningPME API before requesting for data. {response.status_code} Unauthorized.")
    else:
        sys.exit(f"Failed to retrieve data: {response.status_code}")



def get_departments(id:int=None):
    
    params = {
        "pageSize": 999
    }

    if id==None:
        response = requests.get(connection_str + 'department', params=params, headers=headers)

    else:
        response = requests.get(connection_str + 'department/' + str(id), params=params, headers=headers)    

    return response

def get_categories():
    response = requests.get(connection_str + 'category', headers=headers)

    return response