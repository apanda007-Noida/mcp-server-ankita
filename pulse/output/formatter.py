from typing import List, Dict

def generate_docs_report(insights: List[Dict], product: str, week: str) -> str:
    """
    Format JSON insights into a clean Markdown report for Google Docs.
    """
    lines = []
    lines.append(f"# {product} \u2014 Weekly Review Pulse")
    lines.append(f"**Period:** {week}")
    lines.append("\n## Top Themes")
    
    # Exclude error/dummy themes or entirely blank descriptions
    valid_insights = [i for i in insights if i.get("theme") and not i.get("theme").startswith("Error")]
    
    # Sort by review count descending
    valid_insights.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    
    for i in valid_insights:
        lines.append(f"- **{i.get('theme')} ({i.get('review_count', 0)} reviews):** {i.get('description')}")
        
    lines.append("\n## Real User Quotes")
    for i in valid_insights:
        quotes = i.get("quotes", [])
        if quotes:
            lines.append(f"**{i.get('theme')}**")
            for q in quotes:
                lines.append(f"> \"{q}\"")
            lines.append("") # blank line
            
    lines.append("## Action Ideas")
    for i in valid_insights:
        actions = i.get("action_ideas", [])
        if actions:
            lines.append(f"**{i.get('theme')}**")
            for a in actions:
                lines.append(f"- [ ] {a}")
            lines.append("") # blank line
            
    return "\n".join(lines)

def generate_email_teaser(insights: List[Dict], product: str, week: str, doc_link: str = "[INSERT DOC LINK HERE]") -> str:
    """
    Format a lightweight teaser for the Gmail output.
    """
    lines = []
    lines.append(f"Subject: {product} App Review Pulse \u2014 {week}\n")
    lines.append(f"Hi Team,")
    lines.append(f"\nThe automated App Review Pulse for {product} is ready for {week}.")
    lines.append(f"\nHere are the top themes customers are talking about this week:\n")
    
    valid_insights = [i for i in insights if i.get("theme") and not i.get("theme").startswith("Error")]
    valid_insights.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    
    # Show top 3 themes
    for i in valid_insights[:3]:
        lines.append(f"- **{i.get('theme')}:** {i.get('description')}")
        
    lines.append(f"\nRead the full report, verbatim quotes, and action ideas in the canonical Google Doc here:")
    lines.append(doc_link)
    
    return "\n".join(lines)
