import base64
from email.message import EmailMessage
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
from auth import get_credentials

def create_email_draft(to: str, subject: str, body: str) -> dict:
    """
    Creates an email draft in Gmail.
    """
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message['To'] = to
    message['Subject'] = subject
    message.set_content("Please enable HTML to view this message.")
    message.add_alternative(body, subtype='html')

    # Encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'message': {
            'raw': encoded_message
        }
    }

    draft = service.users().drafts().create(userId="me", body=create_message).execute()
    return draft
