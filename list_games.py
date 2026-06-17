import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def list_kalshi_games():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- LISTING KXWCGAME MARKETS ---")
    
    # We'll check KXWCGAME and also Professional Football Game (KXPROFB)
    tickers = ['KXWCGAME', 'KXPROFB', 'KXMATCHPAYERS']
    
    for st in tickers:
        path = f'/trade-api/v2/markets?series_ticker={st}&status=open'
        headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
        url = f'https://external-api.kalshi.com{path}'
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode())
                markets = data.get('markets', [])
                if markets:
                    print(f"\nSeries: {st}")
                    for m in markets:
                        print(f"[{m['ticker']}] {m['title']} | YesAsk: {m.get('yes_ask')}")
        except:
            continue

if __name__ == "__main__":
    list_kalshi_games()
