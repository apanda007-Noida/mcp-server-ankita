from typing import List, Dict

def generate_docs_report(insights: List[Dict], product: str, week: str) -> str:
    """
    Format JSON insights into a clean plain text report for Google Docs
    (since the current MCP tool uses raw insertText).
    """
    lines = []
    lines.append(f"{product.upper()} \u2014 WEEKLY REVIEW PULSE")
    lines.append(f"Period: {week}")
    
    # Exclude error/dummy themes or entirely blank descriptions
    valid_insights = [i for i in insights if i.get("theme") and not i.get("theme").startswith("Error")]
    
    # Sort by review count descending
    valid_insights.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    
    lines.append("\n" + "="*40)
    lines.append("TOP THEMES")
    lines.append("="*40 + "\n")
    
    for i in valid_insights:
        lines.append(f"\u2022 {i.get('theme')} ({i.get('review_count', 0)} reviews):\n  {i.get('description')}\n")
        
    lines.append("\n" + "="*40)
    lines.append("REAL USER QUOTES")
    lines.append("="*40 + "\n")
    
    for i in valid_insights:
        quotes = i.get("quotes", [])
        if quotes:
            lines.append(f"--- {i.get('theme').upper()} ---")
            for q in quotes:
                lines.append(f"\" {q} \"")
            lines.append("") # blank line
            
    lines.append("\n" + "="*40)
    lines.append("ACTION IDEAS")
    lines.append("="*40 + "\n")
    
    for i in valid_insights:
        actions = i.get("action_ideas", [])
        if actions:
            lines.append(f"--- {i.get('theme').upper()} ---")
            for a in actions:
                lines.append(f"[ ] {a}")
            lines.append("") # blank line
            
    return "\n".join(lines)

def generate_email_teaser(insights: List[Dict], product: str, week: str, doc_link: str = "[INSERT DOC LINK HERE]") -> str:
    """
    Format a lightweight HTML teaser for the Gmail output.
    """
    lines = []
    lines.append(f"<h2>{product} App Review Pulse — {week}</h2>")
    lines.append(f"<p>Hi Team,</p>")
    lines.append(f"<p>The automated App Review Pulse for {product} is ready for {week}.</p>")
    lines.append(f"<p>Here are the top themes customers are talking about this week:</p>")
    lines.append(f"<ul>")
    
    valid_insights = [i for i in insights if i.get("theme") and not i.get("theme").startswith("Error")]
    valid_insights.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    
    # Show top 3 themes
    for i in valid_insights[:3]:
        lines.append(f"<li><strong>{i.get('theme').upper()}:</strong><br/>{i.get('description')}</li>")
        
    lines.append("</ul>")
    lines.append(f"<br/><p>Read the full report, verbatim quotes, and action ideas in the canonical Google Doc here:</p>")
    lines.append(f"<p><a href='{doc_link}' style='display:inline-block;padding:10px 16px;background-color:#10b981;color:white;text-decoration:none;border-radius:4px;font-weight:bold;'>Open Full Report</a></p>")
    
    return "\n".join(lines)
