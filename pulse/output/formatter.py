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
    Format a HTML teaser for the Gmail output matching the specific summary structure.
    """
    valid_insights = [i for i in insights if i.get("theme") and not i.get("theme").startswith("Error")]
    valid_insights.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    
    top_3 = valid_insights[:3] if len(valid_insights) >= 3 else valid_insights
    
    if len(top_3) >= 3:
        theme_names = f"{top_3[0].get('theme')}, {top_3[1].get('theme')}, and {top_3[2].get('theme')}"
    elif len(top_3) == 2:
        theme_names = f"{top_3[0].get('theme')} and {top_3[1].get('theme')}"
    elif len(top_3) == 1:
        theme_names = f"{top_3[0].get('theme')}"
    else:
        theme_names = "various issues"
        
    biggest_pain = top_3[0].get('description', '') if top_3 else ""
    
    # Extract first two action ideas from top theme
    action1 = top_3[0].get('action_ideas', [''])[0].lower() if (top_3 and top_3[0].get('action_ideas')) else "improving user experience"
    action2 = ""
    if top_3 and len(top_3[0].get('action_ideas', [])) > 1:
        action2 = top_3[0].get('action_ideas')[1].lower()
    elif len(top_3) > 1 and top_3[1].get('action_ideas'):
        action2 = top_3[1].get('action_ideas')[0].lower()
    else:
        action2 = "resolving bugs"
        
    lines = []
    lines.append("<p>Hi,</p>")
    lines.append(f"<p>The main signal from this week's {product} review pulse is that users are experiencing significant pain points with {theme_names}.</p>")
    lines.append(f"<p>The biggest user pain point is the consistent issues with {top_3[0].get('theme') if top_3 else ''}, including {biggest_pain}, which are causing frustration and delays.</p>")
    lines.append(f"<p>This week, our recommended focus should be on {action1} and {action2} to reduce failures and waiting time.</p>")
    lines.append(f"<p>Here is the weekly review pulse for {product}:</p>")
    
    lines.append(f"<h3>WEEKLY {product.upper()} PULSE</h3>")
    lines.append(f"<p>[{week}]</p>")
    
    lines.append("<h4>TOP THEMES</h4>")
    lines.append("<ul>")
    for i in top_3:
        lines.append(f"<li><strong>{i.get('theme')} ({i.get('review_count', 0)} reviews):</strong> {i.get('description')}</li>")
    lines.append("</ul>")
    
    lines.append("<h4>QUOTES</h4>")
    lines.append("<ol>")
    for i in top_3:
        for q in i.get('quotes', []):
            lines.append(f"<li>\"{q}\"</li>")
    lines.append("</ol>")
    
    lines.append("<h4>ACTION IDEAS</h4>")
    lines.append("<ol>")
    for i in top_3:
        for a in i.get('action_ideas', []):
            lines.append(f"<li>{a}</li>")
    lines.append("</ol>")
    
    lines.append(f"<br/><p><a href='{doc_link}' style='display:inline-block;padding:10px 16px;background-color:#10b981;color:white;text-decoration:none;border-radius:4px;font-weight:bold;'>Open Full Report in Google Docs</a></p>")
    
    return "\n".join(lines)
