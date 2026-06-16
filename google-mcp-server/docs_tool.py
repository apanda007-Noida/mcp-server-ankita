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

    doc = service.documents().get(documentId=doc_id).execute()
    doc_content = doc.get('body').get('content')
    
    end_index = doc_content[-1].get('endIndex', 1) if doc_content else 1
    
    requests = []
    if end_index > 2:
        requests.append({
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,
                    'endIndex': end_index - 1
                }
            }
        })
        
    requests.append({
        'insertText': {
            'location': {
                'index': 1
            },
            'text': content + "\n\n"
        }
    })

    result = service.documents().batchUpdate(
        documentId=doc_id, body={'requests': requests}).execute()
        
    return result
