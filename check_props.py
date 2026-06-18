import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def check_props():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- SEARCHING KALSHI FOR GHANA VS PANAMA PROPS ---")
    
    path = '/trade-api/v2/markets?status=open&limit=1000'
    headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            markets = data.get('markets', [])
            found = 0
            for m in markets:
                title = m['title'].lower()
                if 'ghana' in title or 'panama' in title:
                    print(f"[{m['ticker']}] {m['title']}")
                    found += 1
            if found == 0:
                print("No active markets found for Ghana or Panama.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_props()
