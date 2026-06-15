# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
import uvicorn
import sys
import os

# Import our tools
from docs_tool import append_to_doc
from gmail_tool import create_email_draft

app = FastAPI(title="Google Workspace MCP Server")

class DocRequest(BaseModel):
    doc_id: str
    content: str

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

def require_approval(action_name: str, payload: dict) -> bool:
    """
    Blocks the current thread to ask for terminal approval.
    """
    if os.environ.get("REQUIRE_APPROVAL", "true").lower() == "false":
        print(f"AUTO-APPROVING ACTION: {action_name}")
        return True
    print("\n" + "="*50)
    print(f"ACTION REQUESTED: {action_name}")
    print("PAYLOAD:")
    for k, v in payload.items():
        print(f"  {k}: {v}")
    print("="*50)
    
    # Force flush to ensure it prints before input
    sys.stdout.flush()
    
    while True:
        response = input("Approve? (y/n): ").strip().lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False

@app.post("/append_to_doc")
def api_append_to_doc(req: DocRequest):
    # Ask for approval in terminal
    approved = require_approval("APPEND_TO_DOC", req.dict())
    
    if not approved:
        raise HTTPException(status_code=403, detail="Action rejected by user at terminal.")
        
    try:
        result = append_to_doc(req.doc_id, req.content)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_email_draft")
def api_create_email_draft(req: EmailRequest):
    # Ask for approval in terminal
    approved = require_approval("CREATE_EMAIL_DRAFT", req.dict())
    
    if not approved:
        raise HTTPException(status_code=403, detail="Action rejected by user at terminal.")
        
    try:
        result = create_email_draft(req.to, req.subject, req.body)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Google MCP Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
