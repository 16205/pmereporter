from exchangelib import Credentials, Account, Message, FileAttachment
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import os

# Optional: Disable SSL verification
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

email_address = 'your-email@example.com'
password = 'your-password'
recipient_email = 'recipient@example.com'

credentials = Credentials(email_address, password)
account = Account(primary_smtp_address=email_address, credentials=credentials, autodiscover=True)

# Create the email
msg = Message(
    account=account,
    subject='Mission Orders',
    body='Please find the attached mission orders.',
    to_recipients=[recipient_email]
)

# Attach PDF files
pdf_paths = ['path/to/mission1.pdf', 'path/to/mission2.pdf']
for path in pdf_paths:
    with open(path, 'rb') as f:
        content = f.read()
        attachment = FileAttachment(name=os.path.basename(path), content=content)
        msg.attach(attachment)

# Send the email
msg.send_and_save()

print("Email sent!")
