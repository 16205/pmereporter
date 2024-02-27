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
    pass
