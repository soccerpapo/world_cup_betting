import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def find_live_winners():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- SCANNING FOR LIVE LIQUID MARKETS ---")
    
    # We'll check the markets endpoint for any open market with 'Soccer' in the title
    path = '/trade-api/v2/markets?status=open&limit=1000'
    headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            markets = data.get('markets', [])
            print(f"Found {len(markets)} total open markets.")
            for m in markets:
                title = m['title'].lower()
                # Search for match winner indicators
                if ('win' in title or 'winner' in title or 'vs' in title) and m.get('yes_ask'):
                    print(f"[{m['ticker']}] {m['title']} | YES Price: ${m['yes_ask']/100.0}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_live_winners()
