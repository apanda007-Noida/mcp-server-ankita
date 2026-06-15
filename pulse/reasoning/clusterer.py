import umap
import hdbscan
import numpy as np
from typing import List, Dict

def cluster_embeddings(embeddings: np.ndarray, reviews: List[Dict]) -> List[Dict]:
    """
    Given a numpy array of embeddings and the original review dicts,
    returns the review dicts with a new 'cluster_id' key.
    -1 means noise (unclustered).
    """
    if len(embeddings) == 0:
        return reviews
        
    if len(embeddings) < 15:
        # Too few samples for meaningful UMAP+HDBSCAN, just put them all in one cluster
        for r in reviews:
            r['cluster_id'] = 0
        return reviews
        
    # 1. Dimensionality reduction with UMAP
    # Reduce to 5 dimensions to help HDBSCAN
    n_neighbors = min(15, len(embeddings) - 1)
    reducer = umap.UMAP(
        n_neighbors=n_neighbors, 
        n_components=5, 
        metric='cosine',
        random_state=42
    )
    reduced_embeddings = reducer.fit_transform(embeddings)
    
    # 2. Clustering with HDBSCAN
    # Adjust min_cluster_size based on dataset size, e.g., 5 for small datasets
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    cluster_labels = clusterer.fit_predict(reduced_embeddings)
    
    # Attach labels back to reviews
    for i, label in enumerate(cluster_labels):
        reviews[i]['cluster_id'] = int(label)
        
    return reviews

def group_by_cluster(reviews: List[Dict]) -> Dict[int, List[Dict]]:
    """
    Helper function to group reviews by their cluster_id.
    Returns a dict mapping cluster_id -> List of reviews.
    """
    clusters = {}
    for r in reviews:
        c_id = r.get('cluster_id', -1)
        if c_id not in clusters:
            clusters[c_id] = []
        clusters[c_id].append(r)
    return clusters
