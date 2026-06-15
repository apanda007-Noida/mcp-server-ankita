# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
from typing import List, Dict
# pyrefly: ignore [missing-import]
import numpy as np

# Use a lightweight local model: bge-small
MODEL_NAME = "BAAI/bge-small-en-v1.5"
_model = None

def get_model():
    global _model
    if _model is None:
        # Load the model only when needed to save memory
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def generate_embeddings(reviews: List[Dict]) -> np.ndarray:
    """
    Takes a list of review dicts (containing at least 'content') 
    and returns a numpy array of their embeddings.
    """
    if not reviews:
        return np.array([])
        
    model = get_model()
    texts = [r.get("content", "") for r in reviews]
    
    # Generate embeddings
    # show_progress_bar=False to keep logs clean
    embeddings = model.encode(texts, show_progress_bar=False)
    
    return embeddings
