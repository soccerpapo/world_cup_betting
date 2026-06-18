import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

def fetch_live_match_stats(api_key):
    """
    Fetches live, in-play statistics for active soccer matches using API-Football.
    Returns a dictionary of matches with critical data for the Poisson model.
    """
    if not api_key:
        print("Error: API_FOOTBALL_KEY missing from environment.")
        return {}

    print("Fetching live match statistics from API-Football...")
    
    # Endpoint to get currently live fixtures
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    
    headers = {
        'x-apisports-key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            live_matches = {}
            for fixture in data.get("response", []):
                match_id = fixture["fixture"]["id"]
                elapsed_time = fixture["fixture"]["status"].get("elapsed", 0)
                home_team = fixture["teams"]["home"]["name"]
                away_team = fixture["teams"]["away"]["name"]
                
                # Current Score
                score_home = fixture["goals"]["home"] or 0
                score_away = fixture["goals"]["away"] or 0
                
                match_name = f"{home_team} vs {away_team}"
                
                # Initialize default stats
                stats = {
                    "elapsed_time": elapsed_time,
                    "home_score": score_home,
                    "away_score": score_away,
                    "home_red_cards": 0,
                    "away_red_cards": 0,
                    "home_possession": 50,
                    "away_possession": 50,
                    "home_shots_on_target": 0,
                    "away_shots_on_target": 0
                }
                
                # If the API provides detailed statistics array, parse it
                # Note: Some minor leagues might not have full stats
                if "statistics" in fixture and fixture["statistics"]:
                    for team_stats in fixture["statistics"]:
                        is_home = team_stats["team"]["id"] == fixture["teams"]["home"]["id"]
                        prefix = "home_" if is_home else "away_"
                        
                        for stat in team_stats["statistics"]:
                            s_type = stat["type"]
                            s_val = stat["value"]
                            if s_val is None: continue
                            
                            if s_type == "Ball Possession":
                                # Remove '%' and convert to int
                                stats[f"{prefix}possession"] = int(str(s_val).replace('%', ''))
                            elif s_type == "Red Cards":
                                stats[f"{prefix}red_cards"] = int(s_val)
                            elif s_type == "Shots on Goal":
                                stats[f"{prefix}shots_on_target"] = int(s_val)

                live_matches[match_name] = stats
                
            return live_matches

    except urllib.error.HTTPError as e:
        print(f"API-Football HTTP Error: {e.code} - {e.reason}")
        return {}
    except Exception as e:
        print(f"Failed to fetch live match stats: {e}")
        return {}

# Simple test execution
if __name__ == "__main__":
    load_dotenv(override=True)
    key = os.getenv("API_FOOTBALL_KEY")
    if not key:
        print("Please add API_FOOTBALL_KEY to your .env file.")
    else:
        live_data = fetch_live_match_stats(key)
        print(f"Found {len(live_data)} live matches.")
        for match, stats in list(live_data.items())[:3]: # Print first 3
            print(f"\n{match} ({stats['elapsed_time']}')")
            print(f"Score: {stats['home_score']} - {stats['away_score']}")
            print(f"Red Cards: {stats['home_red_cards']} - {stats['away_red_cards']}")
            print(f"Possession: {stats['home_possession']}% - {stats['away_possession']}%")
