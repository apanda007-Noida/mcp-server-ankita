from typing import List, Dict

def validate_quotes(summary: Dict, original_reviews: List[Dict]) -> Dict:
    """
    Check if the quotes in the summary are verbatim from the original reviews.
    Removes quotes that are hallucinated.
    """
    valid_quotes = []
    
    # Pre-extract all text for faster lookup
    # Normalize by lowering and stripping whitespace to be slightly forgiving of LLM whitespace changes
    all_texts = [r.get("content", "").lower().strip() for r in original_reviews]
    
    for quote in summary.get("quotes", []):
        norm_quote = quote.lower().strip()
        # Find if quote is a substring of any review
        is_valid = any(norm_quote in text for text in all_texts)
        if is_valid:
            valid_quotes.append(quote)
            
    summary["quotes"] = valid_quotes
    return summary

def validate_all_summaries(summaries: List[Dict], clusters: Dict[int, List[Dict]]) -> List[Dict]:
    """
    Validate quotes for all cluster summaries.
    """
    validated = []
    for summary in summaries:
        c_id = summary.get("cluster_id")
        reviews = clusters.get(c_id, [])
        validated_summary = validate_quotes(summary, reviews)
        validated.append(validated_summary)
        
    return validated
