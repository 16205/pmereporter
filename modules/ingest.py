from datetime import datetime
from dotenv import load_dotenv
from modules import auth
from tqdm import tqdm
import os
import requests
import sys

def init_ppme_api_variables():
    """
    Load environment variables from.env file and initialize variables for PlanningPME API connection.

    Returns:
        connection_str (str): URL for PlanningPME API endpoint
        headers (dict): Dictionary of headers for PlanningPME API requests
    """
    load_dotenv(override=True)

    connection_str = os.environ['PPME_ENDPOINT'] + 'api/'

    headers = {
        'Authorization': 'Bearer ' + os.environ['PPME_BEARER_TOKEN'],
        'X-APPKEY': os.environ['PPME_APPKEY'],
        'Content-Type': 'application/json'
    }

    return connection_str, headers

def get_events(dateFrom:datetime, dateTo:datetime=None, departments:list=None, resources:list=None, 
               categories:list=[52,60,63,65,78,80]):
    """
    Fetches events from the PlanningPME API within a specified date range and optional filters.

    This function sends a POST request to the PlanningPME API to retrieve events that match the given criteria.
    The events can be filtered by departments, resources, and categories. If no dateTo is provided, it defaults
    to the same as dateFrom. The categories have a default set of values if not specified.

    Parameters:
        dateFrom (datetime): The start date for the event search.
        dateTo (datetime, optional): The end date for the event search. Defaults to None, which will be interpreted as dateFrom.
        departments (list, optional): A list of department IDs to filter events. Defaults to None.
        resources (list, optional): A list of resource IDs to filter events. Defaults to None.
        categories (list, optional): A list of category IDs to filter events. Defaults to [52,60,63,65,78,80].

    Returns:
        dict: A dictionary containing the response from the PlanningPME API, including a list of events that match the criteria.

    Raises:
        Exception: If the API returns a 401 Unauthorized status code, indicating that the bearer token is invalid or expired.
        SystemExit: If the API returns any other status code indicating failure, the program will exit with an error message.
    """
    
    connection_str, headers = init_ppme_api_variables()

    dateFrom, dateTo = dateFrom.isoformat(), dateTo.isoformat()
    
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

    print("Getting mission events...")
    # TODO: handle error if bad bearer token and other errors
    response = requests.post(connection_str + 'do/list', headers=headers, json=json)

    if response.status_code == 200:
        # Return response content only (this is why .json() is used)
        print(f"Got {len(response.json()['items'])} mission events!")
        return response.json()
    
    elif response.status_code == 401:
        raise Exception(f"Please (re)authenticate to PlanningPME API before requesting for data. {response.status_code} Unauthorized.")
    else:
        sys.exit(f"Failed to retrieve data: {response.status_code}")

def get_locations(missions:list, min:int, max:int, progress_callback=None):
    """
    Retrieves and appends location information for each mission in the provided list.

    This function iterates through a list of missions, querying an API for each mission's details to extract
    and append location information. It supports updating a progress callback function to notify about the
    progress of location retrieval.

    Parameters:
        missions (list): A list of dictionaries, each representing a mission with at least a "key" for the mission ID.
        min (int): The minimum value of the progress range, used in the progress callback.
        max (int): The maximum value of the progress range, used in the progress callback.
        progress_callback (function, optional): A callback function that accepts three arguments: the current progress,
                                                 the minimum, and the maximum values of the progress range. This function
                                                 is called after each mission's location information is retrieved.

    Returns:
        list: The input list of missions, with location information appended to each mission dictionary.

    Raises:
        SystemExit: If the API returns a 401 Unauthorized status code, indicating that the bearer token is invalid or expired,
                    or if the API returns any other status code indicating failure.
    """
    
    connection_str, headers = init_ppme_api_variables()
    # Variables for process tracking
    total_missions = len(missions)
    processed_count = 0

    # Iterate through missions
    print("Getting locations for every mission...")
    for mission in tqdm(missions):
        # Get mission id (=key)
        id = mission["key"]

        # Query for mission details
        response = requests.get(connection_str + f"do/{id}", headers=headers)

        if response.status_code == 200:
            # Extract location info in "place" dictionary, out of mission details
            place = response.json()["place"]

            # Handle case when information is not filled out correctly by planners, that is,
            # when entire address (with zip and city) is filled in the "address" field
            address = place.get("address")

            # Handle case when information is filled out correctly by planners
            zip_code = place.get('zip', '')
            city = place.get('city', '')
            if zip_code or city:
                address += "\r\n"
                address += f"{(zip_code + ' ') if zip_code else ''}"
                address += f"{city if city else ''}"

                # Append locations to mission
            if address:
                mission["location"] = address

        elif response.status_code == 401:
            sys.exit(f"Please (re)authenticate to PlanningPME API before requesting for data. {response.status_code} Unauthorized.")
        else:
            sys.exit(f"Failed to retrieve data: {response.status_code}")

        # Update processed count and emit progress
        processed_count += 1
        progress = processed_count / total_missions
        if progress_callback:
            progress_callback(progress, min, max)

    print("Got the locations!")
    return missions

def get_sources():
    """
    Retrieves a list of sources from a SharePoint list named "Sources".

    This function authenticates to SharePoint using a custom authentication method, then fetches and returns
    all items from the "Sources" list. Each source item's properties are stored in a dictionary with the source's
    title as the key. If the function encounters a ValueError during the execution of the query, it assumes
    a connectivity issue possibly due to VPN not being enabled and exits the program with an error message.

    Returns:
        dict: A dictionary where each key is the title of a source, and the value is a dictionary of the source's properties.

    Raises:
        SystemExit: If there's a ValueError during the SharePoint query execution, indicating a potential connectivity issue.
    """
    print("Getting list of sources...")
    ctx = auth.authenticate_to_shpt()

    sp_list = ctx.web.lists.get_by_title("Sources")

    sources_list = sp_list.get_items()
    ctx.load(sources_list)
    try:
        ctx.execute_query()
    except(ValueError):
        sys.exit(f"Failed to retrieve data. Try again after enabling Cato VPN")
    sources = {}

    for source in sources_list:
        sources[source.properties['Title']] = source.properties

    print('Got all sources!')
    return sources

def get_departments(id:int=None):
    connection_str, headers = init_ppme_api_variables()
    params = {
        "pageSize": 999
    }

    if id==None:
        response = requests.get(connection_str + 'department', params=params, headers=headers)

    else:
        response = requests.get(connection_str + 'department/' + str(id), params=params, headers=headers)    

    return response

def get_categories():
    connection_str, headers = init_ppme_api_variables()
    response = requests.get(connection_str + 'category', headers=headers)

    return response