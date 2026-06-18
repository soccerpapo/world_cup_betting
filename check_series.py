import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def get_series():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    path = '/trade-api/v2/series'
    headers = get_kalshi_auth_headers('GET', path, kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        print('--- SOCCER SERIES ON KALSHI ---')
        for s in data.get('series', []):
            t = s['title'].lower()
            if 'world cup' in t or 'fifa' in t:
                print(f"[{s['ticker']}] {s['title']}")

if __name__ == '__main__':
    get_series()
