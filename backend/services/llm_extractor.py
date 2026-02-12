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
    
    system_prompt = """You are a data extraction bot. Your job is to find and extract INDIVIDUAL COMPANIES from the webpage content.

IMPORTANT: You are looking for COMPANIES LISTED ON THE PAGE, NOT the website itself.

STEP 1: Read the content carefully
- Look for company names, business names, supplier names, manufacturer names
- These are usually in lists, tables, directories, or profiles
- Each company is a SEPARATE entry

STEP 2: Extract EACH company you find
For each company, extract:
- name: The company/business name
- website: Their website URL (if mentioned)
- email: Their email (if mentioned)  
- phone: Their phone (if mentioned)
- address: Their address/location (if mentioned)
- description: What they do/sell (if mentioned)

STEP 3: What NOT to extract

DO NOT extract if the text is:
- A question or request (e.g., "I need suppliers", "Looking for...", "Anyone selling...")
- An error message (e.g., "Cloudflare", "404", "Access Denied")
- A page section (e.g., "About Us", "Contact Us", "Home")
- The website's own name (we want companies LISTED on the page, not the page itself)

EXAMPLES:

Example 1 - Directory Page:
Content: "1. ABC Cosmetics - Kathmandu - abc@mail.com - Makeup products
          2. XYZ Beauty Ltd - Pokhara - xyz@mail.com - Skincare"

Extract:
[
  {"name": "ABC Cosmetics", "address": "Kathmandu", "email": "abc@mail.com", "description": "Makeup products"},
  {"name": "XYZ Beauty Ltd", "address": "Pokhara", "email": "xyz@mail.com", "description": "Skincare"}
]

Example 2 - Table:
Content: "| Company | City | Contact |
          | Nepal Beauty Co | Kathmandu | contact@nepal.com |
          | Himalaya Cosmetics | Lalitpur | info@himalaya.np |"

Extract:
[
  {"name": "Nepal Beauty Co", "address": "Kathmandu", "email": "contact@nepal.com"},
  {"name": "Himalaya Cosmetics", "address": "Lalitpur", "email": "info@himalaya.np"}
]

Example 3 - Buyer Request (DO NOT EXTRACT):
Content: "I want cosmetics suppliers in Nepal. Anyone can help?"

Extract: []

Example 4 - Error Page (DO NOT EXTRACT):
Content: "Cloudflare - Access Denied"

Extract: []

PAGINATION: Also look for "Next", "Load More", or page 2, 3, etc. buttons to help us get more companies.

Return JSON:
{
  "companies": [...],
  "next_page_url": "URL if you find a next page link",
  "pagination_selector": "CSS selector for next button"
}

REMEMBER: Extract INDIVIDUAL COMPANIES from the content, not the website itself.
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
