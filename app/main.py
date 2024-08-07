from datetime import datetime, time
import calendar
import json
import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules import auth, ingest, process, utils

date = datetime(2024, 7, 30)
# dateTo = datetime(2023, 11, 21, 23, 59, 59, 999)

env_path = utils.get_env_path()

def fetch_and_store(date:datetime = None, departments:list=None, progress_callback=None):
    load_dotenv(env_path)
    if not os.environ.get('MS_USER_NAME'):
        utils.init_user()
    current_progress = 0
    if progress_callback:
        progress_callback(current_progress)  # Start with 0% progress

    dateFrom = date
    dateTo = datetime.combine(dateFrom, time(23, 59, 59, 999))

    depts = []
    if "North" in departments:
        depts.extend([2, 3, 4, 19, 21])
    if "South" in departments:
        depts.extend([5, 6, 7, 8, 9, 10, 11, 20])

    try:
        missions = ingest.get_events(dateFrom, dateTo, depts)
    except Exception:
        auth.authenticate_to_ppme()
        missions = ingest.get_events(dateFrom, dateTo, depts)
    current_progress += 5  # 5% progress after fetching events
    if progress_callback:
        progress_callback(current_progress)
    
    # utils.save_to_json('temp/missions_raw.json', missions) # Debug

    # Adjust the progress callback to fit the specified min-max% range
    def adjusted_progress(inner_progress, min, max):
        # Map inner_progress from 0-100% to min-max% of the overall progress
        mapped_progress = int(min + (float(inner_progress) * (max - min)))
        if progress_callback:
            progress_callback(mapped_progress)

    # Clean missions.json
    missions = process.clean_data(missions)

    # Download mission attachments from SharePoint
    access_token = os.environ.get('MS_ACCESS_TOKEN')
    try:
        missions = ingest.download_sharepoint_file(missions, access_token, 5, 30, adjusted_progress)
    except ValueError:
        try:
            access_token = auth.refresh_access_token()
            missions = ingest.download_sharepoint_file(missions, access_token, 5, 30, adjusted_progress)
        except ValueError:
            access_token = auth.authenticate_to_ms_graph()
            missions = ingest.download_sharepoint_file(missions, access_token, 5, 30, adjusted_progress)

    current_progress = 30  # Increment to 30% after cleaning data and downloading attachments

    missions = ingest.get_locations(missions, 30, 90, adjusted_progress)
    current_progress = 90  # After get_locations, we're at 90%

    utils.save_to_json('temp/missions.json', missions)

    current_progress += 5  # Increment by 5% after writing missions data
    if progress_callback:
        progress_callback(current_progress)

    # Encapsulated ingest.get_sources because sometimes, for some unknown reason, a 503 error happens but goes away when retrying
    try:
        sources = ingest.get_sources()
    except:
        sources = ingest.get_sources()

    utils.save_to_json('temp/sources.json', sources)
    current_progress += 5  # Final 5% to complete the process
    if progress_callback:
        # progress_callback(current_progress)
        progress_callback(100)  # Ensure completion is signaled correctly

def generate(keys:list[str], progress_callback=None):
    """
    Generates PDFs based on the missions and sources data stored in JSON files.
    
    This function reads missions and sources data from their respective JSON files, then
    passes this data to the process.generate_pdfs() function to generate PDF documents.
    These documents are intended to provide a printable format of the missions and sources
    for review or archival purposes.
    
    Parameters:
    - date (datetime, optional): The specific date for which to generate PDFs. Currently not used
      in the function but can be implemented for filtering or specifying the data range in future enhancements.
    
    Returns:
    - None. This function does not return any value but triggers the PDF generation process.
    """
    if progress_callback:
        progress_callback(0)  # Start with 0% progress

    with open('temp/missions.json', 'r') as file1, \
         open('temp/sources.json', 'r') as file2:
        missions = json.load(file1)
        sources = json.load(file2)

    # Feed data into process.generate_pdfs() to generate PDF documents containing the missions details
    process.generate_pdfs(missions, sources, keys)    

    if progress_callback:
        progress_callback(100)  # Ensure completion is signaled correctly

def send(keys:list[str], progress_callback=None):
    load_dotenv(env_path)
    if progress_callback:
        progress_callback(0)  # Start with 0% progress

    with open('temp/missions.json', 'r') as file:
        missions = json.load(file)

    name = os.environ.get('MS_USER_NAME')
    
    process.send_om(missions, keys, name, progress_callback)

    if progress_callback:
        progress_callback(100)  # Ensure completion is signaled correctly

def check_sources_conflicts():
    with open('temp/missions.json', 'r') as file:
        missions = json.load(file)
        result = process.check_sources_double_bookings(missions)
    return result

def generate_ADR_monthly_transports_list(date: datetime=datetime(2024, 7, 1)):
    monthrange = calendar.monthrange(date.year, date.month)

    dateFrom = date.replace(day=1)
    dateTo = date.replace(day=monthrange[1])

    missions = ingest.get_events(dateFrom, dateTo)
    missions = process.clean_data(missions)
    rt_missions = process.filter_rt_missions(missions)
    rt_missions = ingest.get_locations(rt_missions)
    utils.save_to_json('temp/rt_missions.json', rt_missions)
    try:
        sources = ingest.get_sources()
    except:
        sources = ingest.get_sources()
    process.generate_ADR_transport_list(rt_missions, sources)
    return rt_missions

# fetch_and_store(date, ['South'])
# generate(None)
# send(None)
# check_sources_conflicts()
# get_sent_elements() 
# generate_ADR_monthly_transports_list()