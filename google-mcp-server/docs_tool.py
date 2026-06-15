# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
from auth import get_credentials

def append_to_doc(doc_id: str, content: str) -> dict:
    """
    Appends text to the end of a Google Document.
    """
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    # Insert text at the end of the document
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1, # Appending to end is tricky without reading length. Actually, let's insert at index 1 or read document first.
                },
                'text': content + "\n\n"
            }
        }
    ]
    
    # Better logic: read document to find the end index, then append.
    # But for a simple append, we can use the endOfSegmentLocation
    requests = [
        {
            'insertText': {
                'endOfSegmentLocation': {
                    'segmentId': '' # empty string means body
                },
                'text': content + "\n\n"
            }
        }
    ]

    result = service.documents().batchUpdate(
        documentId=doc_id, body={'requests': requests}).execute()
        
    return result
