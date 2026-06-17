import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def find_missing_games():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- SCANNING KALSHI FOR ANY MATCHUPS ---")
    
    # Check multiple pages if necessary
    cursor = ""
    for page in range(3): # Check up to 600 events
        path = f'/trade-api/v2/events?status=open&limit=200'
        if cursor: path += f"&cursor={cursor}"
        
        headers = get_kalshi_auth_headers('GET', path, kalshi_id, kalshi_key)
        url = f'https://external-api.kalshi.com{path}'
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode())
                events = data.get('events', [])
                cursor = data.get('cursor')
                
                print(f"Scanning Page {page+1} ({len(events)} events)...")
                for e in events:
                    title = e['title']
                    # Look for ANY match-like string
                    if 'vs' in title.lower() or 'game' in title.lower():
                         print(f" >> POTENTIAL MATCH: {title}")
                
                if not cursor: break
        except Exception as e:
            print(f"Error on page {page+1}: {e}")
            break

if __name__ == "__main__":
    find_missing_games()
