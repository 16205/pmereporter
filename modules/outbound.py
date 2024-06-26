from dotenv import load_dotenv
from modules import auth
import base64
import os
import requests

def send_email(subject:str, recipients:list, content:str, file_paths:list=None, from_address:str=None):
    load_dotenv(override=True)
    
    # Constants
    access_token = os.environ.get('MS_ACCESS_TOKEN')
    SENDMAIL_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/sendMail'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create the email message payload
    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": content
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient}} for recipient in recipients
            ],
            "attachments": []
        },
        "saveToSentItems": True,
    }

    # Add the from address if provided
    if from_address:
        email_data["message"]["from"] = {
            "emailAddress": {
                "address": from_address
            }
        }
    
    # Add an attachment if a file path is provided
    if file_paths:
        for file_path in file_paths:
            with open(file_path, "rb") as file:
                # Read the file and encode it in base64
                file_content = base64.b64encode(file.read()).decode()
                
            # Get the file name
            file_name = file_path.split('/')[-1]
            
            # Add the attachment to the message payload
            email_data["message"]["attachments"].append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": file_name,
                "contentType": "application/octet-stream",  # You might want to adjust this based on the file type
                "contentBytes": file_content
            })
    
    # Send the email
    try:
        response = requests.post(SENDMAIL_ENDPOINT, headers=headers, json=email_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            access_token = auth.refresh_access_token()
            headers['Authorization'] = f'Bearer {access_token}'
            response = requests.post(SENDMAIL_ENDPOINT, headers=headers, json=email_data)
            if response.status_code == 403:
                raise Exception(f"The authenticated user is not authorized to use the 'NDTplanning@vincotte.be' email address to send generate mission orders. Please ask ICT to grant access to 'NDTplanning@vincotte.be' for your account, 'avXXXX@vincotte.org'.")
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(f"Failed to send email to {[recipient for recipient in recipients]}. {response.status_code} {response.reason}")