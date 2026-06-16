import os
import json
import urllib.request
import urllib.error

MCP_SERVER_URL = "https://google-mcp-server-production-27c2.up.railway.app"

def send_to_google_docs(content: str, logger) -> bool:
    doc_id = os.environ.get("GOOGLE_DOC_ID")
    if not doc_id:
        logger.warning("GOOGLE_DOC_ID not found in environment. Skipping Docs MCP.")
        return False
        
    logger.info(f"Sending report to Google Docs via MCP Server for Doc ID: {doc_id}")
    
    url = f"{MCP_SERVER_URL}/append_to_doc"
    payload = {
        "doc_id": doc_id,
        "content": content
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Docs MCP Response: {result}")
            return True
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to MCP Server at {url}: {e}")
        return False

def send_email_draft(subject: str, body: str, logger) -> bool:
    to_email = os.environ.get("STAKEHOLDER_EMAIL")
    if not to_email:
        logger.warning("STAKEHOLDER_EMAIL not found in environment. Skipping Gmail MCP.")
        return False
        
    logger.info(f"Creating email draft via MCP Server for: {to_email}")
    
    url = f"{MCP_SERVER_URL}/create_email_draft"
    payload = {
        "to": to_email,
        "subject": subject,
        "body": body
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Gmail MCP Response: {result}")
            return True
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to MCP Server at {url}: {e}")
        return False
