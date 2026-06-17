import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def find_specific_game():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- SEARCHING FOR IRAN / NEW ZEALAND ON KALSHI ---")
    
    path = '/trade-api/v2/markets?status=open&limit=1000'
    headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            markets = data.get('markets', [])
            for m in markets:
                title = m['title'].lower()
                if 'iran' in title or 'zealand' in title or 'egypt' in title:
                    print(f"[{m['ticker']}] {m['title']} | YesAsk: {m.get('yes_ask')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_specific_game()
