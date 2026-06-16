import json
import urllib.request
import urllib.error

def fetch_live_odds(api_key, sport="soccer_fifa_world_cup", regions="us,eu,uk", markets="h2h"):
    """
    Fetches live odds from The-Odds-API.
    In the World Cup, latency and line-movement tracking are critical.
    
    :param api_key: Your API key for The-Odds-API
    :param sport: The sport key (e.g., 'soccer_fifa_world_cup')
    :param regions: Bookmaker regions (us, uk, eu, au)
    :param markets: Betting markets (h2h = Head to Head / Match Winner)
    """
    print(f"Fetching live odds for {sport}...")
    
    if api_key == "DEMO_KEY" or not api_key:
        print("Warning: Using DEMO_KEY. Returning mock data.")
        return [
            {"match": "USA vs FRA", "bookmaker": "Pinnacle", "odds_home": 4.50, "odds_away": 1.70, "odds_draw": 3.80},
            {"match": "USA vs FRA", "bookmaker": "DraftKings", "odds_home": 4.00, "odds_away": 1.85, "odds_draw": 3.60}
        ]

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
                    
                    for market in bookmaker.get("markets", []):
                        if market.get("key") == "h2h":
                            odds_home = None
                            odds_away = None
                            odds_draw = None
                            
                            for outcome in market.get("outcomes", []):
                                if outcome.get("name") == home_team:
                                    odds_home = outcome.get("price")
                                elif outcome.get("name") == away_team:
                                    odds_away = outcome.get("price")
                                elif outcome.get("name") == "Draw":
                                    odds_draw = outcome.get("price")
                            
                            parsed_odds.append({
                                "match": match_name,
                                "bookmaker": bookmaker_name,
                                "odds_home": odds_home,
                                "odds_away": odds_away,
                                "odds_draw": odds_draw
                            })
            return parsed_odds

    except urllib.error.URLError as e:
        print(f"Failed to fetch odds: {e.reason}")
        return []
