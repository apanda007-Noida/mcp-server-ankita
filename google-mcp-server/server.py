# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
import uvicorn
import sys
import os
import json

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

@app.get("/api/insights")
def get_insights():
    try:
        paths = ["../data/insights.json", "data/insights.json"]
        for p in paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

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

if os.path.exists("static"):
    if os.path.exists("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/")
    def serve_root():
        return FileResponse("static/index.html")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        return FileResponse("static/index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Google MCP Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
