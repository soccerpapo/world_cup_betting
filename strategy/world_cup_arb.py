def calculate_implied_probability(odds):
    return 1.0 / odds if odds and odds > 0 else 0.0

def remove_vig(odds_home, odds_away, odds_draw):
    """
    Removes the bookmaker margin (vig) from a 3-way moneyline 
    to estimate the 'true' fair probabilities of each outcome.
    """
    implied_home = calculate_implied_probability(odds_home)
    implied_away = calculate_implied_probability(odds_away)
    implied_draw = calculate_implied_probability(odds_draw)
    
    margin = implied_home + implied_away + implied_draw
    if margin == 0:
        return 0, 0, 0
        
    fair_home = implied_home / margin
    fair_away = implied_away / margin
    fair_draw = implied_draw / margin
    
    return fair_home, fair_away, fair_draw

def find_arbitrage_opportunities(odds_data, sharp_book="Pinnacle"):
    """
    Scans for discrepancies between sharp books (true probability) and 
    soft books (recreational money) to find +EV bets or pure arbs.
    """
    print("Scanning for +EV and Arbitrage opportunities across bookmakers...")
    opportunities = []
    
    # Group odds by match
    matches = {}
    for entry in odds_data:
        match = entry["match"]
        if match not in matches:
            matches[match] = []
        matches[match].append(entry)
        
    for match, bookies in matches.items():
        # 1. Identify +EV Bets (using the sharp book to define 'true' odds)
        sharp_entry = next((b for b in bookies if b["bookmaker"].lower() == sharp_book.lower()), None)
        
        if sharp_entry and sharp_entry.get("odds_home") and sharp_entry.get("odds_away") and sharp_entry.get("odds_draw"):
            fair_home, fair_away, fair_draw = remove_vig(
                sharp_entry["odds_home"], 
                sharp_entry["odds_away"], 
                sharp_entry["odds_draw"]
            )
            
            for b in bookies:
                if b["bookmaker"].lower() == sharp_book.lower():
                    continue
                    
                # Check Home Win
                if b.get("odds_home") and fair_home * b["odds_home"] > 1.0:
                    edge = (fair_home * b["odds_home"]) - 1.0
                    opportunities.append({
                        "type": "+EV",
                        "match": match,
                        "bet": "Home Win",
                        "bookmaker": b["bookmaker"],
                        "odds": b["odds_home"],
                        "win_prob": fair_home,
                        "edge": edge
                    })
                
                # Check Away Win
                if b.get("odds_away") and fair_away * b["odds_away"] > 1.0:
                    edge = (fair_away * b["odds_away"]) - 1.0
                    opportunities.append({
                        "type": "+EV",
                        "match": match,
                        "bet": "Away Win",
                        "bookmaker": b["bookmaker"],
                        "odds": b["odds_away"],
                        "win_prob": fair_away,
                        "edge": edge
                    })
                    
                # Check Draw
                if b.get("odds_draw") and fair_draw * b["odds_draw"] > 1.0:
                    edge = (fair_draw * b["odds_draw"]) - 1.0
                    opportunities.append({
                        "type": "+EV",
                        "match": match,
                        "bet": "Draw",
                        "bookmaker": b["bookmaker"],
                        "odds": b["odds_draw"],
                        "win_prob": fair_draw,
                        "edge": edge
                    })
        
        # 2. Pure Arbitrage Check
        best_home = max([b.get("odds_home") or 0 for b in bookies] + [0])
        best_away = max([b.get("odds_away") or 0 for b in bookies] + [0])
        best_draw = max([b.get("odds_draw") or 0 for b in bookies] + [0])
        
        if best_home > 0 and best_away > 0 and best_draw > 0:
            arb_margin = (1.0 / best_home) + (1.0 / best_away) + (1.0 / best_draw)
            if arb_margin < 1.0:
                profit_pct = (1.0 - arb_margin) / arb_margin
                opportunities.append({
                    "type": "Arbitrage",
                    "match": match,
                    "bet": "All Outcomes (Surebet)",
                    "bookmaker": "Multiple",
                    "odds": f"H:{best_home}, A:{best_away}, D:{best_draw}",
                    "edge": profit_pct
                })
                
    return opportunities