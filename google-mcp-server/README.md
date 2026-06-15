# Google MCP Server

A FastAPI-based MCP server that provides tools for appending text to Google Docs and drafting emails in Gmail.
It requires manual terminal approval before executing any action.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Download your Google OAuth 2.0 Client credentials:
   - Go to Google Cloud Console
   - Enable Google Docs API and Gmail API
   - Create OAuth 2.0 Client ID (Desktop App)
   - Download the JSON file and save it as `credentials.json` in this directory.

3. Run the server:
   ```bash
   python server.py
   ```
   *The first time you run this, a browser window will open asking you to log into your Google Account to authorize the app. A `token.json` file will be generated.*

## Endpoints

- `POST /append_to_doc`: Appends text to a Google Doc.
  Payload: `{"doc_id": "...", "content": "..."}`
- `POST /create_email_draft`: Creates a Gmail draft.
  Payload: `{"to": "...", "subject": "...", "body": "..."}`
