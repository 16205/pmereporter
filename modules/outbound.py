import base64
import requests

def send_email(access_token:str, subject:str, recipients:list, content:str, file_path:str=None):
    # Constants
    SENDMAIL_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/sendMail'

    if access_token is None or access_token == "":
        raise ValueError("Access token is not provided.")
    
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
    
    # Add an attachment if a file path is provided
    if file_path:
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
    response = requests.post(SENDMAIL_ENDPOINT, headers=headers, json=email_data)
    if response.status_code == 202:
        # print(f"Email sent to {recipient}.")
        return
    else:
        raise ValueError(f"Failed to send email to {[recipient for recipient in recipients]}. {response.status_code} {response.reason}")