from features.team_strength import get_elo_probability

def calculate_implied_probability(odds):
    return 1.0 / odds if odds and odds > 0 else 0.0

def remove_vig_3way(odds_1, odds_2, odds_3):
    implied_1 = calculate_implied_probability(odds_1)
    implied_2 = calculate_implied_probability(odds_2)
    implied_3 = calculate_implied_probability(odds_3)
    margin = implied_1 + implied_2 + implied_3
    if margin == 0: return 0, 0, 0
    return implied_1 / margin, implied_2 / margin, implied_3 / margin

def find_kalshi_value(sharp_odds_data, kalshi_data, sharp_book="Pinnacle"):
    """
    Compares sharp bookmaker probabilities AND Elo Ratings against 
    Kalshi contract prices to find high-confidence value.
    """
    print("Cross-checking Kalshi prices against sharp odds and Elo Ratings...")
    value_opportunities = []
    
    # 1. Extract "Truth" probabilities from sharp bookmaker
    matches_truth = {}
    for entry in sharp_odds_data:
        if entry["bookmaker"].lower() == sharp_book.lower():
            fair_home, fair_away, fair_draw = remove_vig_3way(
                entry.get("odds_home"), 
                entry.get("odds_away"), 
                entry.get("odds_draw")
            )
            matches_truth[entry["match"]] = {
                "Home Win": fair_home,
                "Away Win": fair_away,
                "Draw": fair_draw
            }
            
    # 2. Compare against Kalshi market prices with Elo cross-check
    for k_market in kalshi_data:
        match_name = k_market["match"]
        outcome = k_market["outcome"]
        kalshi_price = k_market["yes_price"]
        
        if match_name in matches_truth:
            # A. Get Sharp Bookie Prob
            sharp_prob = matches_truth[match_name].get(outcome, 0)
            
            # B. Get Elo Fundamental Prob
            teams = match_name.split(' vs ')
            home_team = teams[0] if len(teams) == 2 else "Unknown"
            away_team = teams[1] if len(teams) == 2 else "Unknown"
            elo_probs = get_elo_probability(home_team, away_team)
            elo_prob = elo_probs.get(outcome, 0)
            
            # C. Determine Confidence
            # Opportunity exists if Sharp Prob > Kalshi Price
            if sharp_prob > kalshi_price:
                edge = sharp_prob - kalshi_price
                
                # High Confidence if Elo also agrees there is value
                confidence = "LOW"
                if elo_prob > kalshi_price:
                    confidence = "HIGH (Elo Confirmed)"
                
                value_opportunities.append({
                    "type": "Kalshi +EV",
                    "match": match_name,
                    "bet": outcome,
                    "kalshi_price": kalshi_price,
                    "sharp_prob": sharp_prob,
                    "elo_prob": elo_prob,
                    "edge": edge,
                    "confidence": confidence,
                    "ticker": k_market["ticker"]
                })
                
    return value_opportunities
