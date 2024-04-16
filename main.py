from datetime import datetime
import ingest
import auth
import process
import json
import utils

# auth.authenticate_to_ppme()

dateFrom = datetime(2023, 11, 21)
dateTo = datetime(2023, 11, 21, 23, 59, 59, 999)

def fetch_and_store(date:datetime=None):
    """
    Fetches event and source data for a specified date range, then stores this data in JSON files.
    
    This function performs several steps to gather data related to missions and their sources:
    1. It fetches events within a specified date range from a predefined department using the ingest.get_events() function.
    2. It enriches these events with location data by calling ingest.get_locations().
    3. It then writes the enriched mission data to a JSON file for later use.
    4. Similarly, it fetches source data from SharePoint using ingest.get_sources() and writes this data to another JSON file.
    
    Parameters:
    - date (datetime, optional): The specific date for which to fetch and store data. If not provided, uses a default date range defined outside this function.
    
    Returns:
    - None. This function does not return any value but writes data to files.
    """
    # Call ingest.get_events() to fetch events within the specified date range (PPME       in )
    missions = ingest.get_events(dateFrom, dateTo, departments=[30])

    # Call ingest.get_locations() to enrich missions with location data        (PPME       in )
    missions = ingest.get_locations(missions)

    utils.save_to_txt(missions)

    # Write enriched missions data to a JSON file
    with open('temp/missions.json', 'w') as file:
        json.dump(missions, file)

    # Call ingest.get_sources() to fetch source data from SharePoint           (SharePoint in )
    sources = ingest.get_sources()

    # write sources to file
    with open('temp/sources.json', 'w') as file:
        json.dump(sources, file)

def generate(date:datetime=None):
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

    # Feed results into process.generate_pdfs() to generate PDF documents based on the missions and sources data
    process.generate_pdfs(missions, sources)    

def check_mat_double_booking():
    # Call ingest.get_events()
    # Call ingest.get_sources()
    # Feed results into process.check_conflicts
    pass

fetch_and_store()
generate()