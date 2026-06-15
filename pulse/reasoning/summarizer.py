import json
import time
import os
from typing import List, Dict
# pyrefly: ignore [missing-import]
from groq import Groq
# pyrefly: ignore [missing-import]
import tiktoken
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

# Groq limits: 30 RPM, 12K TPM
RPM_LIMIT = 30
TPM_LIMIT = 12000

# Sleep to ensure we don't exceed 30 RPM. 60/30 = 2 seconds per request minimum.
# We'll use 3 seconds to be safe.
SLEEP_PER_REQUEST = 3

def get_tokenizer():
    # Use cl100k_base as an approximation for Llama token counting
    return tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    enc = get_tokenizer()
    return len(enc.encode(text))

def truncate_reviews_to_token_limit(reviews: List[Dict], max_tokens: int = 8000) -> List[Dict]:
    """
    Keep taking reviews until we hit the max_tokens limit.
    Assuming reviews are already sorted by relevance (e.g. proximity to centroid).
    """
    sampled = []
    current_tokens = 0
    
    for r in reviews:
        # roughly estimate tokens
        text = r.get("content", "")
        toks = count_tokens(text)
        if current_tokens + toks > max_tokens:
            break
        sampled.append(r)
        current_tokens += toks
        
    return sampled

def summarize_cluster(cluster_id: int, reviews: List[Dict], client: Groq, logger) -> Dict:
    """
    Call Groq API to summarize a single cluster.
    """
    # Exclude noise cluster if we want, but sometimes noise has good insights.
    # For now, we process all clusters passed here.
    
    # 1. Truncate to fit within TPM limits
    sampled_reviews = truncate_reviews_to_token_limit(reviews, max_tokens=8000)
    
    # 2. Build prompt
    reviews_text = ""
    for i, r in enumerate(sampled_reviews):
        reviews_text += f"Review {i+1} [Rating: {r.get('rating')}]: {r.get('content')}\n"
        
    prompt = f"""
    You are an expert product analyst. I am providing you with a cluster of user reviews about the Groww app.
    
    Reviews:
    {reviews_text}
    
    Your task is to analyze these reviews and output a JSON object with the following structure:
    {{
        "theme": "A short 3-5 word name for this cluster's theme",
        "description": "A 1-2 sentence description of what users are saying",
        "quotes": [
            "Exact verbatim quote 1 from the reviews above",
            "Exact verbatim quote 2 from the reviews above"
        ],
        "action_ideas": [
            "Actionable idea 1 to address this feedback",
            "Actionable idea 2 to address this feedback"
        ]
    }}
    
    CRITICAL INSTRUCTION: The quotes MUST be exact verbatim copies of the text in the reviews provided. Do not hallucinate or modify quotes.
    Output ONLY valid JSON.
    """
    
    # Check total prompt tokens
    prompt_tokens = count_tokens(prompt)
    logger.info(f"Cluster {cluster_id} - Sending {len(sampled_reviews)} reviews ({prompt_tokens} tokens) to Groq")
    
    # 3. Call Groq
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        result_str = response.choices[0].message.content
        result_json = json.loads(result_str)
        result_json['cluster_id'] = cluster_id
        result_json['review_count'] = len(reviews)
        
        # 4. Rate limiting delay
        time.sleep(SLEEP_PER_REQUEST)
        
        return result_json
        
    except Exception as e:
        logger.error(f"Error summarizing cluster {cluster_id}: {str(e)}")
        # Rate limiting delay even on failure to avoid hammering API
        time.sleep(SLEEP_PER_REQUEST)
        return {
            "cluster_id": cluster_id,
            "theme": "Error generating theme",
            "description": str(e),
            "quotes": [],
            "action_ideas": [],
            "review_count": len(reviews)
        }

def summarize_all_clusters(clusters: Dict[int, List[Dict]], logger) -> List[Dict]:
    """
    Iterate over all clusters and summarize them using Groq.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment. Returning dummy summaries.")
        # Return dummy data if no key
        results = []
        for c_id, revs in clusters.items():
            results.append({
                "cluster_id": c_id,
                "theme": f"Dummy Theme {c_id}",
                "description": "API key missing. Dummy description.",
                "quotes": [revs[0].get("content", "")] if revs else [],
                "action_ideas": ["Dummy action idea"],
                "review_count": len(revs)
            })
        return results
        
    client = Groq(api_key=api_key)
    results = []
    
    for c_id, revs in clusters.items():
        if c_id == -1 and len(revs) < 5:
            # Skip tiny noise clusters
            continue
            
        summary = summarize_cluster(c_id, revs, client, logger)
        results.append(summary)
        
    return results
