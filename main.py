from datetime import datetime
import ingest
import auth
import process
import json

# auth.authenticate_to_ppme()

dateFrom = datetime(2023, 11, 21)
dateTo = datetime(2023, 11, 21, 23, 59, 59, 999)

response = ingest.get_events(dateFrom, dateTo)

# print(json.dumps(response.json(), indent=4))

with open('example.txt', 'w') as file:
    if response.status_code == 200:
        file.write(json.dumps(response.json(), indent=4))

def generate(date:datetime):
    # Call ingest.get_events()                      (PPME       in  )
    # Call ingest.get_locations()                   (PPME       in  )
    # Call ingest.get_sources()                     (SharePoint in  )
    # Feed results into process.generate_pdfs()     (Internal       )
    # Call ???outbound???.send_mission_orders()     (Outlook    out )
    pass

def check_mat_double_booking():
    # Call ingest.get_events()
    # Call ingest.get_sources()
    # Feed results into process.check_conflicts
    pass
