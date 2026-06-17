import os
import json
import urllib.request
from dotenv import load_dotenv

def debug_apis():
    load_dotenv(override=True)
    odds_key = os.getenv('ODDS_API_KEY')
    kalshi_id = os.getenv('KALSHI_API_KEY_ID')
    kalshi_key = os.getenv('KALSHI_PRIVATE_KEY')

    print(f"--- DEBUGGING DATA SOURCES ---")
    
    # 1. Check The-Odds-API
    print(f"\n[1] Checking The-Odds-API (Key: {odds_key[:5]}...)")
    try:
        # Get active sports first to find the right key
        url = f'https://api.the-odds-api.com/v4/sports/?apiKey={odds_key}'
        with urllib.request.urlopen(url) as res:
            sports = json.loads(res.read().decode())
            active_soccer = [s['key'] for s in sports if 'soccer' in s['key'] and s['active']]
            print(f"Found {len(active_soccer)} active soccer categories.")
            print(f"Available keys: {active_soccer[:10]}")

        # Check the specific World Cup key
        url = f'https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={odds_key}&regions=us&markets=h2h'
        with urllib.request.urlopen(url) as res:
            odds = json.loads(res.read().decode())
            print(f"World Cup Matches Found: {len(odds)}")
            for m in odds[:3]:
                print(f" - {m['home_team']} vs {m['away_team']} (Starts: {m['commence_time']})")
    except Exception as e:
        print(f"Odds API Error: {e}")

    # 2. Check Kalshi
    print(f"\n[2] Checking Kalshi (ID: {kalshi_id[:5]}...)")
    from data.fetch_kalshi import get_kalshi_auth_headers
    try:
        path = '/trade-api/v2/events?category=Sports&status=open'
        headers = get_kalshi_auth_headers('GET', path, kalshi_id, kalshi_key)
        url = f'https://external-api.kalshi.com{path}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            events = data.get('events', [])
            print(f"Total Sports Events on Kalshi: {len(events)}")
            
            # List EVERYTHING on Kalshi to see how they name things
            soccer_hits = []
            for e in events:
                title = e['title']
                if any(word in title.lower() for word in ['soccer', 'football', 'fifa', 'cup', 'vs']):
                    soccer_hits.append(title)
            
            if soccer_hits:
                print(f"Potential Soccer Matches Found: {soccer_hits}")
            else:
                print("No matches containing 'soccer', 'football', or 'vs' found.")
                print(f"First 10 titles found: {[e['title'] for e in events[:10]]}")

    except Exception as e:
        print(f"Kalshi Error: {e}")

if __name__ == "__main__":
    debug_apis()
