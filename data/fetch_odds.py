def fetch_live_odds(api_key, sport="soccer_fifa_world_cup"):
    """
    Template for fetching live odds from platforms like The-Odds-API.
    In the World Cup, latency and line-movement tracking are critical.
    """
    print(f"Fetching live odds for {sport}...")
    # TODO: Implement REST API call to fetch odds across multiple bookmakers
    return [
        {"match": "USA vs FRA", "bookmaker": "Pinnacle", "odds_home": 4.50, "odds_away": 1.70, "odds_draw": 3.80},
        {"match": "USA vs FRA", "bookmaker": "DraftKings", "odds_home": 4.00, "odds_away": 1.85, "odds_draw": 3.60}
    ]