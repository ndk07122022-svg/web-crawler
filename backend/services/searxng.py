import requests
from typing import List

SEARXNG_URL = "https://searx.up.railway.app/search"

def search_google(query: str, limit: int = 10) -> List[dict]:
    """
    Searches using the hosted SearxNG instance and returns a list of dictionaries with 'url' and 'content'.
    """
    # Mimic a real browser to avoid 403 Forbidden on some instances
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        search_results = []
        seen = set()
        page = 1
        max_pages = 6  # Safety limit
        
        while len(search_results) < limit and page <= max_pages:
            params = {
                "q": query,
                "format": "json",
                "pageno": page
            }
            
            print(f"Querying SearxNG (Page {page}): {SEARXNG_URL}?q={query}&format=json&pageno={page}")
            try:
                response = requests.get(SEARXNG_URL, params=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"SearxNG returned status {response.status_code}")
                    break
                    
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                new_results_count = 0
                for result in results:
                    url = result.get("url")
                    content = result.get("content", "")
                    if url and url not in seen:
                        search_results.append({"url": url, "content": content})
                        seen.add(url)
                        new_results_count += 1
                        
                if new_results_count == 0:
                     print("No new unique results found, stopping pagination.")
                     break
                     
                page += 1
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
                    
        print(f"SearxNG found {len(search_results)} URLs total")
        return search_results[:limit]

    except Exception as e:
        print(f"Error querying SearxNG: {e}")
        return []
