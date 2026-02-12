from openai import OpenAI
import os
import json
from typing import List, Dict, Any, Optional

# Try to import BeautifulSoup for cleaning
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

def clean_content(html_content: str) -> str:
    """
    Cleans HTML content by removing boilerplate tags (nav, header, footer, scripts).
    Returns text content.
    """
    if not BeautifulSoup:
        return html_content # Fallback

    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove distracting elements
    for tag in soup(["script", "style", "nav", "header", "footer", "iframe", "svg", "noscript", "meta"]):
        tag.decompose()
        
    # Get text, or return cleaned HTML if we want structure? 
    # LLMs handle HTML structure well for tables. Let's return cleaned HTML string mainly for structure.
    # But to save tokens, let's try to get a structured text representation or just the body.
    
    body = soup.find("body")
    if body:
        return str(body)[:15000] # Limit to ~15k chars to avoid token limits (approx 3-4k tokens)
    
    return str(soup)[:15000]

def extract_interactive_elements(html_content: str) -> str:
    """
    Extracts interactive elements (a, button, input) with their attributes to help LLM find pagination.
    """
    if not BeautifulSoup or not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "lxml")
    elements = []
    
    # Find all potentially interactive elements
    for tag in soup.find_all(["a", "button", "input"]):
        # Get key attributes
        attrs = []
        if tag.name == "a" and tag.get("href"):
            attrs.append(f'href="{tag.get("href")}"')
        
        for attr in ["id", "class", "aria-label", "title", "name", "value", "type"]:
             val = tag.get(attr)
             if val:
                 if isinstance(val, list): val = " ".join(val)
                 attrs.append(f'{attr}="{val}"')
        
        text = tag.get_text(strip=True)[:50] # Limit text length
        attr_str = " ".join(attrs)
        
        elements.append(f'<{tag.name} {attr_str}>{text}</{tag.name}>')
        
    return "\n".join(elements[:500]) # Limit to first 500 elements or so to save context

def extract_data_with_llm(content_markdown: str, html_content: str, query: str) -> Dict[str, Any]:
    """
    Extracts company data and next page URL/Selector using LLM.
    Uses Markdown for content and HTML snippets for pagination.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: No OpenAI API Key. Returning empty extraction.")
        return {"companies": [], "next_page_url": None, "pagination_selector": None}

    client = OpenAI(api_key=api_key)
    
    # 1. Prepare Content (Markdown for Companies)
    # 2. Prepare Interactive Elements (HTML for Pagination)
    interactive_html = extract_interactive_elements(html_content)
    
    system_prompt = """You are an intelligent web scraper specialized in extracting SUPPLIER/MANUFACTURER company information.
    Your goal is to extract ONLY legitimate business suppliers, manufacturers, or service providers that match the user's query.
    
    Task 1: Extract Companies (Use the Markdown Content)
    Extract fields: name, website, description, email, phone, address.
    
    STRICT FILTERING RULES - DO NOT EXTRACT:
    ❌ Buyer requests or "wanted" posts (e.g., "I want supply of...", "Anyone selling...", "Looking for suppliers...")
    ❌ Error pages (Cloudflare, 404, 403, "Access Denied", "Page Not Found")
    ❌ Navigation or generic pages ("About Us", "Contact Us", "Home", "Login", "Sign Up")
    ❌ Generic page titles or website names without actual company details
    ❌ Forum posts, Q&A requests, or discussion threads
    ❌ Trade show announcements or event listings (UNLESS they list exhibitor companies with contact details)
    ❌ News articles or blog posts (UNLESS they contain a company directory/listing)
    ❌ Social media posts or personal profiles
    ❌ Government websites, policy pages, or regulation documents
    
    ONLY EXTRACT IF:
    ✅ The content clearly describes a business that SUPPLIES/MANUFACTURES/DISTRIBUTES products or services
    ✅ The company has identifiable contact information (website, email, phone, or address)
    ✅ The company name is a proper business name, not a page title or generic phrase
    ✅ The content is from a business directory, B2B platform, or company profile page
    
    VALIDATION:
    - If the "name" field sounds like a request, question, or generic page title → DO NOT INCLUDE IT
    - If there's no contact information (no website, email, phone, or address) → DO NOT INCLUDE IT
    - If it's clearly a buyer looking for suppliers → DO NOT INCLUDE IT
    - If the page is an error or navigation page → Return empty companies array
    
    Task 2: Identify Pagination (Use the HTML Snippets)
    Look for 'Next', '>', 'Load More', or page numbers in the HTML snippets.
    - 'next_page_url': URL from href.
    - 'pagination_selector': precise CSS selector for the button/link (e.g. 'a.next-page', 'button#load-more').
    
    Return JSON:
    {
        "companies": [...],
        "next_page_url": "...",
        "pagination_selector": "..."
    }
    
    IMPORTANT: It's better to return an empty companies array than to include irrelevant or invalid entries.
    """
    
    user_prompt = f"""User Query: {query}
    
    --- MARKDOWN CONTENT (For Companies) ---
    {content_markdown[:15000]}
    
    --- INTERACTIVE HTML SNIPPETS (For Pagination) ---
    {interactive_html[:10000]}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return {"companies": [], "next_page_url": None, "pagination_selector": None}
