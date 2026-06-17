import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def list_kalshi_h2h():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- LISTING KXWCTEAMH2H MARKETS ---")
    
    path = '/trade-api/v2/markets?series_ticker=KXWCTEAMH2H&status=open'
    headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            markets = data.get('markets', [])
            for m in markets:
                print(f"[{m['ticker']}] {m['title']} | YesAsk: {m.get('yes_ask')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_kalshi_h2h()
