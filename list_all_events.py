import os
import json
import urllib.request
from data.fetch_kalshi import get_kalshi_auth_headers
from dotenv import load_dotenv

def find_all_events():
    load_dotenv(override=True)
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print("--- SCANNING ALL OPEN EVENTS ON KALSHI ---")
    
    path = '/trade-api/v2/events?status=open&limit=200'
    headers = get_kalshi_auth_headers('GET', path, kalshi_id, kalshi_key)
    url = f'https://external-api.kalshi.com{path}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            events = data.get('events', [])
            for e in events:
                print(f"[{e['event_ticker']}] {e['title']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_all_events()
