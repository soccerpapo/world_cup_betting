import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def discover_actual_tickers():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    # From our previous scan of 10,000 series, we found these keywords
    search_keywords = ['soccer', 'fifa', 'world cup', 'uefa']
    
    print("--- DEEP SCANNING FOR TICKERS ---")
    
    # 1. Get Series Tickers for these keywords
    path = '/trade-api/v2/series'
    headers = get_kalshi_auth_headers('GET', path, kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    series_tickers = []
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            for s in data.get('series', []):
                title = s['title'].lower()
                if any(k in title for k in search_keywords):
                    series_tickers.append(s['ticker'])
    except Exception as e:
        print(f"Error fetching series: {e}")
        return

    print(f"Found {len(series_tickers)} potential soccer series. Scanning for open markets...")

    # 2. Search markets in these series
    for st in series_tickers:
        m_path = f'/trade-api/v2/markets?series_ticker={st}&status=open'
        m_headers = get_kalshi_auth_headers('GET', '/trade-api/v2/markets', kalshi_id, kalshi_key)
        m_url = f'https://external-api.kalshi.com{m_path}'
        m_req = urllib.request.Request(m_url, headers=m_headers)
        
        try:
            with urllib.request.urlopen(m_req) as res:
                m_data = json.loads(res.read().decode())
                markets = m_data.get('markets', [])
                if markets:
                    print(f"\nSeries: {st}")
                    for m in markets:
                        print(f"  > [{m['ticker']}] {m['title']} | Ask: {m.get('yes_ask', 'N/A')}")
        except:
            continue

if __name__ == "__main__":
    discover_actual_tickers()
