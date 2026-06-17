import json
import urllib.request
import urllib.error

def fetch_live_odds(api_key, sport="soccer_fifa_world_cup", regions="us,eu,uk", markets="h2h,totals"):
    """
    Fetches live odds from The-Odds-API.
    """
    if not api_key:
        return []

    print(f"Fetching live odds for {sport}...")
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={api_key}&regions={regions}&markets={markets}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            parsed_odds = []
            for event in data:
                home_team = event.get("home_team")
                away_team = event.get("away_team")
                match_name = f"{home_team} vs {away_team}"
                
                for bookmaker in event.get("bookmakers", []):
                    bookmaker_name = bookmaker.get("title")
                    
                    odds_home, odds_away, odds_draw = None, None, None
                    odds_over_2_5, odds_under_2_5 = None, None
                    
                    for market in bookmaker.get("markets", []):
                        if market.get("key") == "h2h":
                            for outcome in market.get("outcomes", []):
                                if outcome.get("name") == home_team:
                                    odds_home = outcome.get("price")
                                elif outcome.get("name") == away_team:
                                    odds_away = outcome.get("price")
                                elif outcome.get("name") == "Draw":
                                    odds_draw = outcome.get("price")
                        elif market.get("key") == "totals":
                            for outcome in market.get("outcomes", []):
                                if outcome.get("point") == 2.5:
                                    if outcome.get("name") == "Over":
                                        odds_over_2_5 = outcome.get("price")
                                    elif outcome.get("name") == "Under":
                                        odds_under_2_5 = outcome.get("price")
                            
                    parsed_odds.append({
                        "match": match_name,
                        "bookmaker": bookmaker_name,
                        "odds_home": odds_home,
                        "odds_away": odds_away,
                        "odds_draw": odds_draw,
                        "odds_over_2_5": odds_over_2_5,
                        "odds_under_2_5": odds_under_2_5
                    })
            return parsed_odds

    except urllib.error.HTTPError as e:
        # Detailed logging for quota errors
        if e.code == 401:
            print("Error: Odds API Quota Reached or Unauthorized.")
        else:
            print(f"Odds API Error: {e.code} - {e.reason}")
        return []
    except Exception as e:
        print(f"Failed to fetch odds: {e}")
        return []
