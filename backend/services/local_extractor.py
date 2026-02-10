import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

def check_relevance_local(markdown_text: str, query: str) -> bool:
    """
    Checks if the page is relevant based on keyword matching in the markdown content.
    """
    if not markdown_text:
        return False
        
    query_terms = query.lower().split()
    text_lower = markdown_text.lower()
    
    # Check if ANY query term is present (loose relevance)
    # Refine this logic as needed (e.g., ALL terms, or specific keywords like 'distributor')
    
    # Heuristic: If looking for "distributors", the page should probably contain that word
    # or "supplier", "wholesale", "manufacturer".
    
    # Negative Keywords (Skip these sites unless they are directories)
    negative_keywords = ["ministry", "government", "department", "policy", "regulations", "act", "software", "visualization", "tableau"]
    
    if any(nk in text_lower for nk in negative_keywords) and not any(dk in text_lower for dk in ["directory", "list", "companies", "members"]):
        return False

    keywords = ["distributor", "supplier", "wholesale", "manufacturer", "dealer", "provider", "company", "companies", "business", "trader"]
    
    # Add query terms to keywords - strict check for country if present
    query_parts = [t for t in query.lower().split() if len(t) > 3]
    keywords.extend(query_parts)
    
    matches = sum(1 for k in keywords if k in text_lower)
    
    # Stricter: If country is in query, it MUST be in text (approximate)
    if "thailand" in query.lower() and "thailand" not in text_lower and "thai" not in text_lower:
         return False
    
    return matches >= 2 # At least 2 keyword matches

def extract_companies_local(html_content: str, source_url: str) -> Dict[str, Any]:
    """
    Extracts company information from HTML using heuristics (Regex/Soup).
    Returns a dictionary representing a single 'aggregated' company result for the page,
    or a list if we could identify distinct blocks (harder without LLM).
    
    For now, we treat the PAGE as the entity (e.g. a directory listing might be hard to parse company-by-company without LLM).
    But we can extract ALL emails/phones found.
    """
    if not html_content:
        return {}
        
    soup = BeautifulSoup(html_content, "lxml")
    text_content = soup.get_text(separator=" ", strip=True)
    
    # 1. Title as Name
    title = soup.title.string.strip() if soup.title else "Unknown"
    
    # 2. Emails
    emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text_content)))
    
    # 3. Phones (Simple heuristic)
    # Matches patterns like +1-555-555-5555 or (555) 555-5555
    phones = list(set(re.findall(r"(\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4})", text_content)))
    phones = [p for p in phones if len(re.sub(r"\D", "", p)) > 8] # Filter short numbers
    
    # 4. Description (Meta)
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        description = meta_desc.get("content", "").strip()
    
    # 5. Website (External links) - Deep Crawl Strategy
    # Find all external links that might be companies
    from urllib.parse import urljoin, urlparse # Import inside function or at top
    
    company_links = []
    
    # exclude patterns for links
    link_blacklist = [
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "youtube.com",
        "google.com", "wikipedia.org", ".gov", "policies", "terms", "contact", "about",
        "login", "signin", "register", "signup", "cart", "checkout", "account", "profile",
        "ad-create", "advertise", "member", "forgot", "reset", "search", "filter", "sort",
        "privacy", "disclaimer", "sitemap", "quote", "checklist", "consultants", "services",
        "associates", "lawyers", "insurance", "designers", "compliance", "labeling"
    ]
    
    source_domain = urlparse(source_url).netloc
    external_links = []
    internal_links = []

    for link in soup.find_all("a", href=True):
        raw_href = link["href"]
        
        # Skip javascript:, mailto:, tel:
        if any(x in raw_href.lower() for x in ["javascript:", "mailto:", "tel:", "#"]):
            continue
            
        # Resolve relative links
        href = urljoin(source_url, raw_href)
        
        # Parse domain
        href_domain = urlparse(href).netloc
        
        # Filter out invalid or blacklisted
        if not href.startswith("http"):
            continue
            
        if any(x in href.lower() for x in link_blacklist):
            continue
            
        # Classify
        if source_domain in href_domain:
             # Internal-ish
             internal_links.append(href)
        else:
             # External
             external_links.append(href)
    
    # Dedup and prioritize
    # 1. External links are best (actual company websites)
    seen = set()
    for l in external_links:
        if l not in seen and l != source_url:
            company_links.append(l)
            seen.add(l)
            
    # 2. If we have very few external links, maybe deep crawl internal profiles?
    # But for CosmeticIndex, internal links were noise. Let's be careful.
    # Only add internal links if they look like "profiles" (heuristic?)
    # For now, append unique internal links after external, limiting total
    for l in internal_links:
        if l not in seen and l != source_url:
            company_links.append(l)
            seen.add(l)
    
    # Structured output simulating the LLM response
    company = {
        "name": title,
        "website": source_url, # Default to the page URL
        "description": description if description else title,
        "email": ", ".join(emails[:3]) if emails else None, # key contacts
        "phone": ", ".join(phones[:3]) if phones else None,
        "address": None # Hard to extract with regex
    }
    
    return {
        "companies": [company], 
        "next_page_url": None,
        "company_links": company_links[:20] # Return top 20 potential company links, prioritized by external
    }
