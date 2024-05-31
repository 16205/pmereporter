from datetime import datetime, time
import json
import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules import auth, ingest, process, utils

date = datetime(2024, 5, 29)
# dateTo = datetime(2023, 11, 21, 23, 59, 59, 999)

def fetch_and_store(date:datetime = None, departments:list=None, progress_callback=None):
    current_progress = 0
    if progress_callback:
        progress_callback(current_progress)  # Start with 0% progress

    dateFrom = date
    dateTo = datetime.combine(dateFrom, time(23, 59, 59, 999))

    depts = []
    if "North" in departments:
        depts.extend([2, 3, 4, 19])
    if "South" in departments:
        depts.extend([5, 6, 7, 8, 9, 10, 11])

    try:
        missions = ingest.get_events(dateFrom, dateTo, depts)
    except Exception:
        auth.authenticate_to_ppme()
        missions = ingest.get_events(dateFrom, dateTo, depts)
    
    current_progress += 5  # 5% progress after fetching events
    if progress_callback:
        progress_callback(current_progress)
    
    # utils.save_to_json('temp/missions_raw.json', missions) # Debug

    missions = process.clean_data(missions)

    for mission in missions:
        links = mission.get("attachmentLinks")
        if links != []:
            load_dotenv(override=True)
            access_token = os.environ.get('MS_ACCESS_TOKEN')
            for index, link in enumerate(links):
                try:
                    ingest.download_sharepoint_file(access_token, link, f"{mission.get("key")}_{index}")
                except ValueError:
                    try:
                        access_token = auth.refresh_access_token()
                        ingest.download_sharepoint_file(access_token, link, f"{mission.get("key")}_{index}")
                    except ValueError:
                        access_token = auth.authenticate_to_ms_graph()['access_token']
                        ingest.download_sharepoint_file(access_token, link, f"{mission.get("key")}_{index}")

    current_progress += 5  # Increment by 5% after cleaning data and downloading attachments
    if progress_callback:
        progress_callback(current_progress)

    # Adjust the progress callback to fit the specified min-max% range
    def adjusted_progress(inner_progress, min, max):
        # Map inner_progress from 0-100% to min-max% of the overall progress
        mapped_progress = int(min + (float(inner_progress) * (max-min)))
        if progress_callback:
            progress_callback(mapped_progress)

    missions = ingest.get_locations(missions, 10, 90, adjusted_progress)
    current_progress = 90  # After get_locations, we're at 90%

    utils.save_to_json('temp/missions.json', missions)

    current_progress += 5  # Increment by 5% after writing missions data
    if progress_callback:
        progress_callback(current_progress)

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
    if progress_callback:
        progress_callback(0)  # Start with 0% progress

    with open('temp/missions.json', 'r') as file:
        missions = json.load(file)
    process.send_om(missions, keys, progress_callback)

    if progress_callback:
        progress_callback(100)  # Ensure completion is signaled correctly

def check_sources_conflicts():
    with open('temp/missions.json', 'r') as file:
        missions = json.load(file)
        result = process.check_sources_double_bookings(missions)
    return result

def get_sent_elements():
    try:
        load_dotenv(override=True)
        access_token = os.environ.get('MS_ACCESS_TOKEN')
        utils.save_to_json('temp/sentElements.json', ingest.get_sent_elements(access_token))
    except ValueError:
        try:
            access_token = auth.refresh_access_token()
            utils.save_to_json('temp/sentElements.json', ingest.get_sent_elements(access_token))
        except ValueError:
            access_token = auth.authenticate_to_ms_graph()['access_token']
            utils.save_to_json('temp/sentElements.json', ingest.get_sent_elements(access_token))
            
# fetch_and_store(date, ['North', 'South'])
# generate(None)
# send(None)
# check_sources_conflicts()
# get_sent_elements()