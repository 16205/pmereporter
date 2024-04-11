import auth
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

def get_locations(missions):
    # Iterate through missions
    print("Getting locations for every mission...")
    for mission in tqdm(missions["items"]):
        # Get mission id (=key)
        id = mission["key"]

        # Query for mission details
        response = requests.get(connection_str + f"do/{id}", headers=headers)

        if response.status_code == 200:
            # --------------This part below should be part of a process function, since it is not ingest related
            # Extract location info in "place" dictionary, out of mission details
            place = response.json()["place"]

            # Handle case when information is not filled out correctly by planners, that is, zip and city in street field:
            # Set var adress as being only the "address" field (=street) out of "place" dictionary
            address = place["address"]

            # Handle case when information is filled out correctly by planners, that is, zip and city in their respective fields
            if place["zip"] is not None and place["city"] is not None:
                address += f"<br/>{place['zip']} {place['city']}"

            # Append locations to mission
            mission["location"] = address

        elif response.status_code == 401:
            sys.exit(f"Please authenticate to PlanningPME API before requesting for data. {response.status_code} Unauthorized.")
        else:
            sys.exit(f"Failed to retrieve data: {response.status_code}")

    print("Got the locations!")
    return missions

def get_sources():
    print("Getting list of sources...")
    ctx = auth.authenticate_to_shpt()

    sp_list = ctx.web.lists.get_by_title("Sources")

    sources_list = sp_list.get_items()
    ctx.load(sources_list)
    ctx.execute_query()

    sources = {}

    for source in sources_list:
        sources[source.properties['Title']] = source.properties

    print('Got all sources!')
    return sources

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