from datetime import datetime, timedelta
from . import auth
import base64
import os
import pytz
import requests
import sys
from . import utils

def get_events(dateFrom:datetime, dateTo:datetime=None, departments:list=None, resources:list=None, 
               categories:list=[52,55,60,63,65,66,76,77,81,82]):
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
        categories (list, optional): A list of category IDs to filter events. Defaults to [52,60,63,65,80], which corresponds respectively to
                                                                                [Planned, Planned Nucleair, Niet factureerbaar, Opleiding-Formation, Prime Time].

    Returns:
        dict: A dictionary containing the response from the PlanningPME API, including a list of events that match the criteria.

    Raises:
        Exception: If the API returns a 401 Unauthorized status code, indicating that the bearer token is invalid or expired.
        SystemExit: If the API returns any other status code indicating failure, the program will exit with an error message.
    """
    
    connection_str, headers = utils.init_ppme_api_variables()

    dateFrom, dateTo = dateFrom.isoformat(), dateTo.isoformat()
    
    json = {
        "dateFrom": dateFrom,
        "dateTo": dateTo,
        "resources": resources,
        "categories": categories,
        "results": "Task",
        "tasks": departments,
    }

    # print("Getting mission events...")
    response = requests.post(connection_str + 'do/list', headers=headers, json=json)
    if response.status_code == 200:
        # Return response content only (this is why .json() is used)
        # print(f"Got {len(response.json()['items'])} mission events!")
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
    
    connection_str, headers = utils.init_ppme_api_variables()
    # Variables for process tracking
    total_missions = len(missions)
    processed_count = 0

    # Iterate through missions
    # print("Getting locations for every mission...")
    for mission in (missions):
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

    # print("Got the locations!")
    return missions

def get_sources():
    # TODO: replace with use of Microsoft Graph API
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
    # print("Getting list of sources...")
    ctx = auth.authenticate_to_shpt()

    sp_list = ctx.web.lists.get_by_title("Sources")

    sources_list = sp_list.get_items()
    ctx.load(sources_list)
    try:
        ctx.execute_query()
    except(ValueError):
        sys.exit(f"Failed to retrieve data. Try again after enabling Cato VPN")
    sources = {}

    utc_zone = pytz.timezone('UTC')
    brussels_zone = pytz.timezone('Europe/Brussels')

    for source in sources_list:
        sources[source.properties['Title']] = source.properties
        
        # Convert Calibration Date to UTC+1 (Brussels) to avoid issues with activity computation
        calibration_date_utc = datetime.strptime(sources[source.properties['Title']]['Calibrationdate'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc_zone)
        sources[source.properties['Title']]['Calibrationdate'] = calibration_date_utc.astimezone(brussels_zone).strftime('%Y-%m-%dT%H:%M:%SZ')

    # print('Got all sources!')
    return sources

def get_departments(id:int=None):
    connection_str, headers = utils.init_ppme_api_variables()
    params = {
        "pageSize": 999
    }

    if id==None:
        response = requests.get(connection_str + 'department', params=params, headers=headers)

    else:
        response = requests.get(connection_str + 'department/' + str(id), params=params, headers=headers)    

    return response

def get_categories():
    connection_str, headers = utils.init_ppme_api_variables()
    response = requests.get(connection_str + 'category', headers=headers)

    return response

def get_sent_elements(access_token:str):
    start_date = datetime.today() - timedelta(days=7)
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')  # Format date in ISO 8601

    
    # URL to access the Sent Items folder
    url = f"https://graph.microsoft.com/v1.0/me/mailFolders/sentItems/messages?$select=subject,receivedDateTime,toRecipients&$filter=receivedDateTime ge {start_date_str}&$orderby=receivedDateTime desc&$top=200"

    # Set the header with the authorization token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()
        # Print out the subject, time sent, and recipient of each email in the Sent Items folder
        elements = []
        for message in data.get('value', []):
            subject = message['subject']
            sent_time = message['receivedDateTime']
            recipients = ', '.join([recipient['emailAddress']['address'] for recipient in message['toRecipients']])
            elements.append({'recipients': recipients, 'subject': subject, 'sent_time': sent_time})
        return elements
    else:
        raise ValueError(f"Failed to retrieve data: {response.status_code}")
        # print("Failed to retrieve data:", response.status_code)

def download_sharepoint_file(missions, access_token, min, max, progress_callback=None):
    keys = []
    for mission in missions:
        links = mission.get("attachmentLinks")
        if links != []:
            keys.append(mission.get('key'))
    total_missions = len(keys)

    processed_count = 0
    for mission in missions:
        if mission.get('key') in keys:
            links = mission.get("attachmentLinks")
            if links != []:
                mission['attachmentFileNames'] = []
                for index, link in enumerate(links):
                    # Raise an exception if the link provided starts with "\\Vilv8PPMEP", which is not supported anymore. The planners should use SharePoint to store the files instead.
                    if link.startswith('\\\\Vilv8PPMEP') or link.startswith('\\\\VILV8PPMEP'):
                        raise NameError(f"The provided link at:\n\nPlanningPME > mission n°{mission.get('key')} of {mission.get('start')} with {mission.get('resources')[0].get('lastName')} for {mission.get('customers')[0].get('label') if mission.get('customers') else None} > Extra info > link interventiondoc {index+1}\n\npoints to a legacy storage server file that is not supported anymore. Please use Vincotte NDT SharePoint's dedicated folder instead.")
                    
                    try:
                        drive_item_info = transform_sharepoint_url(link, access_token)
                    except NameError:
                        raise NameError(f"The provided link at:\n\nPlanningPME > mission n°{mission.get('key')} of {mission.get('start')} with {mission.get('resources')[0].get('lastName')} for {mission.get('customers')[0].get('label') if mission.get('customers') else None} > Extra info > link interventiondoc {index+1}\n\nis not a valid url pointing to a Vincotte NDT SharePoint file")
                    headers = {
                        "Authorization": f"Bearer {access_token}"
                    }
                    subdir = datetime.strptime(mission.get('start'), '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d')
                    mission_key = mission.get('key')
                    dir = f"./temp/attachments/{subdir}/{mission_key}/"
                    filename = dir + drive_item_info.get('name')

                    # Raise an exception if the file extension is not pdf, Word or image, to forbid misuse by planners
                    allowed_extensions = ['.pdf', '.doc', '.docx','.docm', '.dot', '.dotx', '.dotm', '.jpeg', '.jpg', '.png', '.heic']
                    if not any(filename.endswith(ext) for ext in allowed_extensions):
                        raise NameError(f"The provided link at:\n\nPlanningPME > mission n°{mission.get('key')} of {mission.get('start')} with {mission.get('resources')[0].get('lastName')} for {mission.get('customers')[0].get('label') if mission.get('customers') else None} > Extra info > link interventiondoc {index+1}\n\npoints to an unauthorized file type. Please use a pdf, Word document, or an image instead.")

                    graph_url = drive_item_info.get('@microsoft.graph.downloadUrl')
                    response = requests.get(graph_url, headers=headers)
                    response.raise_for_status()

                    if not os.path.exists(os.path.dirname(dir)):
                        os.makedirs(os.path.dirname(dir))
                    with open(filename, 'wb') as file:
                        file.write(response.content)
                    mission['attachmentFileNames'].append(drive_item_info.get('name'))
            # Update processed count and emit progress
            processed_count += 1
            progress = processed_count / total_missions
            if progress_callback:
                progress_callback(progress, min, max)
    return missions

def transform_sharepoint_url(sharepoint_url, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    # Encode the SharePoint link
    encoded_link = base64.urlsafe_b64encode(sharepoint_url.encode()).decode().rstrip("=")
    
    # Step 1: Get the drive item ID from the SharePoint link
    drive_item_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_link}/driveItem"

    response = requests.get(drive_item_url, headers=headers)
    if response.status_code != 200:
        if response.status_code == 403:
            raise NameError
        if response.status_code == 401:
            raise ValueError
        raise Exception(f"Error getting drive item: {response.status_code}, {response.text}")
    
    drive_item_info = response.json()
    
    return drive_item_info

def get_user_details(access_token):
    # Define the endpoint for getting user details
    url = "https://graph.microsoft.com/v1.0/me"
    
    # Set the headers including the access token for authorization
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Make the GET request to the Microsoft Graph API
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        user_data = response.json()
        # Extract first name and last name
        first_name = user_data.get('givenName')
        last_name = user_data.get('surname')
        name = first_name + ' ' + last_name
        utils.update_env_var(name, 'MS_USER_NAME')
    else:
        # Handle error
        response.raise_for_status()