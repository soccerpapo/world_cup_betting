import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def check_orderbook():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    # We saw these JUN16 tickers earlier
    tickers = [
        'KXWCGAME-26JUN16ARGDZA-ARG', 
        'KXWCGAME-26JUN16ARGDZA-DZA',
        'KXWCGAME-26JUN16ARGDZA-TIE'
    ]
    
    print("--- CHECKING KALSHI ORDERBOOKS ---")
    
    for ticker in tickers:
        path = f'/trade-api/v2/markets/{ticker}/orderbook'
        headers = get_kalshi_auth_headers('GET', path, kalshi_id, kalshi_key)
        url = f'https://external-api.kalshi.com{path}'
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode())
                ob = data.get('orderbook', {})
                yes = ob.get('yes', [])
                no = ob.get('no', [])
                
                print(f"\nTicker: {ticker}")
                if yes:
                    print(f"  YES Bids: {yes[0]}")
                if no:
                    print(f"  NO Bids: {no[0]}")
                if not yes and not no:
                    print("  No liquidity found in orderbook.")
        except Exception as e:
            print(f"Error checking {ticker}: {e}")

if __name__ == "__main__":
    check_orderbook()
