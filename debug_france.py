import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def debug():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    path = '/trade-api/v2/markets?series_ticker=KXWCGAME&status=open&limit=200'
    headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            for m in data.get('markets', []):
                if 'france' in m['title'].lower() and 'iraq' in m['title'].lower():
                    print('MARKET MATCH:', m['title'])
                    print(json.dumps({k:v for k,v in m.items() if 'dollars' in k or 'price' in k or 'ticker' in k}, indent=2))
                    
                    # Check Orderbook
                    ticker = m['ticker']
                    ob_path = f'/trade-api/v2/markets/{ticker}/orderbook'
                    ob_headers = get_kalshi_auth_headers('GET', ob_path, kalshi_id, kalshi_key)
                    ob_req = urllib.request.Request(f'https://external-api.kalshi.com{ob_path}', headers=ob_headers)
                    with urllib.request.urlopen(ob_req) as ob_res:
                        ob_data = json.loads(ob_res.read().decode())
                        print('ORDERBOOK:', json.dumps(ob_data.get('orderbook'), indent=2))
    except Exception as e:
        print('Error:', e)

if __name__ == "__main__":
    debug()
