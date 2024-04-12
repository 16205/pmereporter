from datetime import datetime
import ingest
import auth
import process
import json

# auth.authenticate_to_ppme()

dateFrom = datetime(2023, 11, 21)
dateTo = datetime(2023, 11, 21, 23, 59, 59, 999)

def fetch_and_store(date:datetime=None):
    # Call ingest.get_events()                      (PPME       in )
    missions = ingest.get_events(dateFrom, dateTo, departments=[30])

    # Call ingest.get_locations()                   (PPME       in )
    missions = ingest.get_locations(missions)

    # write missions to file
    with open('temp/missions.json', 'w') as file:
        json.dump(missions, file)

    # Call ingest.get_sources()                     (SharePoint in )
    sources = ingest.get_sources()

    # write sources to file
    with open('temp/sources.json', 'w') as file:
        json.dump(sources, file)

    # Feed results into process.generate_pdfs()     (Internal      )
    # process.generate_pdfs(missions, sources)
    # Call outbound.send_mission_orders()           (Outlook    out)

def generate(date:datetime=None):
    with open('temp/missions.json', 'r') as file1, \
         open('temp/sources.json', 'r') as file2:
        missions = json.load(file1)
        sources = json.load(file2)

    # Feed results into process.generate_pdfs()     (Internal      )
    process.generate_pdfs(missions, sources)
    # Call outbound.send_mission_orders()           (Outlook    out)
    

def check_mat_double_booking():
    # Call ingest.get_events()
    # Call ingest.get_sources()
    # Feed results into process.check_conflicts
    pass

# fetch_and_store()
generate()
# print(process.compute_activity(1219, datetime(2024,2,21), 'Ir-192', datetime.today()))