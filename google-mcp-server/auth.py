import os.path
import json
import os
# pyrefly: ignore [missing-import]
from google.auth.transport.requests import Request
# pyrefly: ignore [missing-import]
from google.oauth2.credentials import Credentials
# pyrefly: ignore [missing-import]
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose"
]

def get_credentials():
    """Gets valid user credentials from storage or initiates OAuth2 flow."""
    creds = None
    
    # Try loading token from environment variable first
    token_json_str = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_json_str:
        token_info = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    # Fallback to local token.json
    elif os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Try loading credentials from environment variable first
            creds_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            if creds_json_str:
                creds_info = json.loads(creds_json_str)
                flow = InstalledAppFlow.from_client_config(creds_info, SCOPES)
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next local run
        if not os.environ.get("GOOGLE_TOKEN_JSON"):
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            
    return creds
