import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def find_h2h_markets():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    # We know these teams are playing from the Odds API
    targets = ['argentina', 'algeria', 'austria', 'jordan']
    
    print("--- SCANNING FOR MATCH WINNER MARKETS ---")
    
    # 1. Search Markets endpoint (latest 200)
    path = '/trade-api/v2/markets?status=open&limit=200'
    headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            for m in data.get('markets', []):
                title = m['title'].lower()
                if any(t in title for t in targets):
                    print(f"FOUND: [{m['ticker']}] {m['title']} | Ask: {m.get('yes_ask')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_h2h_markets()
