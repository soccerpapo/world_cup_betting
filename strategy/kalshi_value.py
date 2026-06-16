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
    Compares sharp bookmaker probabilities against Kalshi contract prices
    to find +EV discrepancies.
    """
    print("Comparing Kalshi market prices against sharp odds for value...")
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
            
    # 2. Compare against Kalshi market prices
    for k_market in kalshi_data:
        match_name = k_market["match"]
        outcome = k_market["outcome"]
        kalshi_price = k_market["yes_price"] # e.g. 0.60
        
        if match_name in matches_truth:
            true_prob = matches_truth[match_name].get(outcome, 0)
            
            # If the true probability is higher than the Kalshi price, it's +EV
            if true_prob > kalshi_price:
                edge = true_prob - kalshi_price
                value_opportunities.append({
                    "type": "Kalshi +EV",
                    "match": match_name,
                    "bet": outcome,
                    "kalshi_price": kalshi_price,
                    "true_prob": true_prob,
                    "edge": edge,
                    "ticker": k_market["ticker"]
                })
                
    return value_opportunities
