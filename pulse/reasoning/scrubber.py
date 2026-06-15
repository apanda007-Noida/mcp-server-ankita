import re
from typing import List, Dict

# Basic regex patterns for PII
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
# Masking string
MASK = "[REDACTED]"

def scrub_pii_from_text(text: str) -> str:
    """
    Remove basic PII (emails, phone numbers) from a given text string.
    """
    if not text:
        return text
        
    text = EMAIL_REGEX.sub(MASK, text)
    text = PHONE_REGEX.sub(MASK, text)
    
    return text

def scrub_reviews(reviews: List[Dict]) -> List[Dict]:
    """
    Given a list of normalized reviews [{"rating": x, "content": "..."}, ...],
    scrub PII from the 'content' fields.
    """
    scrubbed = []
    for r in reviews:
        scrubbed.append({
            "rating": r.get("rating"),
            "content": scrub_pii_from_text(r.get("content", ""))
        })
    return scrubbed
