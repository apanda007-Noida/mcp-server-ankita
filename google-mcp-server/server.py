# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
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

class TriggerRequest(BaseModel):
    product: str
    week: str

import threading
from pulse.orchestrator import run_pulse

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

@app.post("/api/trigger")
def trigger_pipeline(req: TriggerRequest):
    t = threading.Thread(target=run_pulse, args=(req.product, req.week))
    t.start()
    return {"status": "started", "message": f"Pipeline triggered for {req.product} {req.week}"}

@app.get("/api/config")
def get_config():
    return {
        "google_doc_id": os.environ.get("GOOGLE_DOC_ID", "") 
    }

@app.get("/api/stats")
def get_stats():
    try:
        paths = ["../data/normalized_reviews.json", "data/normalized_reviews.json"]
        reviews = []
        for p in paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    reviews = json.load(f)
                break
                
        if not reviews:
            return {"sentiment": [], "average": 0, "total": 0}
            
        positive = sum(1 for r in reviews if r.get("score", 0) >= 4)
        neutral = sum(1 for r in reviews if r.get("score", 0) == 3)
        negative = sum(1 for r in reviews if r.get("score", 0) <= 2)
        
        avg = sum(r.get("score", 0) for r in reviews) / len(reviews) if len(reviews) > 0 else 0
        
        return {
            "sentiment": [
                {"name": "Positive (4-5★)", "value": positive, "fill": "#4ade80"},
                {"name": "Neutral (3★)", "value": neutral, "fill": "#fb923c"},
                {"name": "Negative (1-2★)", "value": negative, "fill": "#f87171"}
            ],
            "average": round(avg, 1),
            "total": len(reviews)
        }
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_ASSETS_DIR = os.path.join(STATIC_DIR, "assets")

@app.get("/debug")
def debug_info():
    return {
        "cwd": os.getcwd(),
        "files_in_base": os.listdir(BASE_DIR),
        "static_exists": os.path.exists(STATIC_DIR),
        "static_assets_exists": os.path.exists(STATIC_ASSETS_DIR)
    }

if os.path.exists(STATIC_DIR):
    if os.path.exists(STATIC_ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=STATIC_ASSETS_DIR), name="assets")

    @app.get("/")
    def serve_root():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Google MCP Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
