from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules import ingest, process
from modules.auth import authenticate_to_ppme

dateFrom = datetime(2023, 11, 21)
dateTo = datetime(2023, 11, 21, 23, 59, 59, 999)

def fetch_and_store(date: datetime = None, progress_callback=None):
    current_progress = 0

    try:
        missions = ingest.get_events(dateFrom, dateTo, departments=[30])
        current_progress += 5  # 5% progress after fetching events
        if progress_callback:
            progress_callback(current_progress)
    except Exception:
        authenticate_to_ppme()
        missions = ingest.get_events(dateFrom, dateTo, departments=[30])
        current_progress += 5  # Repeat increment if re-authentication and fetching events
        if progress_callback:
            progress_callback(current_progress)

    missions = process.clean_data(missions)
    current_progress += 5  # Increment by 5% after cleaning data
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

    with open('temp/missions.json', 'w') as file:
        json.dump(missions, file)
    current_progress += 5  # Increment by 5% after writing missions data
    if progress_callback:
        progress_callback(current_progress)

    sources = ingest.get_sources()
    with open('temp/sources.json', 'w') as file:
        json.dump(sources, file)
    current_progress += 5  # Final 5% to complete the process
    if progress_callback:
        # progress_callback(current_progress)
        progress_callback(100)  # Ensure completion is signaled correctly


def generate(keys:list[str]):
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
    with open('temp/missions.json', 'r') as file1, \
         open('temp/sources.json', 'r') as file2:
        missions = json.load(file1)
        sources = json.load(file2)

    sources_double_boookings = process.check_sources_double_bookings(missions)
    if sources_double_boookings:
        print("\n/!\WARNING/!\: Double bookings detected for the following sources:")
        for source in sources_double_boookings:
            print(f"\nSource \"{source}\" is booked by missions:")
            for mission in sources_double_boookings[source]:
                print(f"{mission}")
        print("\n")

    # Feed data into process.generate_pdfs() to generate PDF documents containing the missions details
    process.generate_pdfs(missions, sources, keys)    

def send():
    with open('temp/missions.json', 'r') as file:
        missions = json.load(file)
    process.send_om(missions, datetime.today())

# fetch_and_store()
# generate()
# send()