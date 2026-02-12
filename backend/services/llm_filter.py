from typing import List, Dict
import os
import json

# Try to import openai, but handle if it's not present (though we should probably add it to requirements)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def filter_search_results(results: List[Dict[str, str]], query: str) -> List[str]:
    """
    Filters search results based on the query using an LLM.
    Returns a list of URLs that are relevant.
    """
    if not results:
        return []

    # If OpenAI is not available or no key, return all results (fail open)
    # This is a placeholder. ideally we should have a free LLM or user provided key.
    # The user mentioned "Crawl4AI with its AI capabilities", but that's for extraction.
    # For now, let's use a dummy filter if no key, or try to use a free provider if possible.
    # Actually, let's simply return all results if we can't filter, but print a warning.
    
    # Check for API Key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not OpenAI or not api_key:
        print("Warning: OpenAI client not available or API key missing. Skipping LLM filtering.")
        return [r.get("url") for r in results if r.get("url")]

    client = OpenAI(api_key=api_key)
    
    # Prepare the prompt
    candidates = ""
    for i, r in enumerate(results):
        content = r.get('content', '') or r.get('snippet', '') or r.get('description', '')
        snippet_preview = content[:300] if content else 'No snippet available'
        candidates += f"{i}. URL: {r.get('url', 'No URL')}\n   Title: {r.get('title', 'No title')}\n   Snippet: {snippet_preview}\n\n"
    
    print(f"\n=== LLM Filter Input ===")
    print(f"Query: {query}")
    print(f"Number of candidates: {len(results)}")
    print(f"\nCandidates:\n{candidates}")
    print(f"========================\n")

    system_prompt = f"""You are a URL filter. Your job is to pick URLs that will help find companies matching the user's search intent.

User is searching for: "{query}"

YOUR TASK: Select URLs that are likely to have COMPANY LISTINGS or COMPANY INFORMATION matching the user's query.

GOOD URLs (SELECT these):
✅ Business directories (e.g., "Nepal Business Directory", "Cosmetics Suppliers List")
✅ B2B platforms (e.g., "TradeIndia", "Alibaba", industry marketplaces)
✅ Company listing pages with multiple businesses
✅ Industry association member lists
✅ Trade directory pages
✅ Company profile pages of suppliers/manufacturers

BAD URLs (SKIP these):
❌ Blog posts or news articles
❌ Wikipedia pages
❌ Social media profiles (LinkedIn, Facebook)
❌ Job sites (Indeed, LinkedIn Jobs)
❌ E-commerce product pages (Amazon, eBay)
❌ Forums or Q&A sites (Quora, Reddit)
❌ Login/signup pages
❌ Error pages

SIMPLE RULE: Will this URL help find companies that match "{query}"?
- If YES → Include it
- If NO → Skip it

Return a JSON array of the indices of relevant URLs.
Example: [0, 2, 4]
If nothing is relevant: []"""

    user_prompt = f"User Query: '{query}'\n\nSearch Results:\n{candidates}\n\nWhich URLs will help find companies matching this query? Return JSON array of indices."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Better understanding of business/directory pages
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        
        content = response.choices[0].message.content.strip()
        print(f"\n=== LLM Filter Response ===")
        print(f"Raw response: {content}")
        print(f"============================\n")
        
        # Parse output
        try:
            indices = json.loads(content)
            if isinstance(indices, list):
                valid_urls = []
                for idx in indices:
                    if isinstance(idx, int) and 0 <= idx < len(results):
                        url = results[idx].get("url")
                        if url:
                            valid_urls.append(url)
                            print(f"  ✓ Selected [{idx}]: {url}")
                print(f"\n✅ LLM Filtered {len(results)} -> {len(valid_urls)} URLs")
                return valid_urls
            else:
                print(f"❌ LLM response is not a list: {indices}")
                return [r.get("url") for r in results if r.get("url")] # Fail open
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {content}")
            print(f"   Error: {e}")
            return [r.get("url") for r in results if r.get("url")] # Fail open

    except Exception as e:
        print(f"Error calling LLM: {e}")
        return [r.get("url") for r in results if r.get("url")] # Fail open

    return [r.get("url") for r in results if r.get("url")]
