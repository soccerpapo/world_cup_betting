def calculate_implied_probability(odds):
    return 1.0 / odds if odds and odds > 0 else 0.0

def remove_vig_3way(odds_1, odds_2, odds_3):
    implied_1 = calculate_implied_probability(odds_1)
    implied_2 = calculate_implied_probability(odds_2)
    implied_3 = calculate_implied_probability(odds_3)
    margin = implied_1 + implied_2 + implied_3
    if margin == 0: return 0, 0, 0
    return implied_1 / margin, implied_2 / margin, implied_3 / margin

def remove_vig_2way(odds_1, odds_2):
    implied_1 = calculate_implied_probability(odds_1)
    implied_2 = calculate_implied_probability(odds_2)
    margin = implied_1 + implied_2
    if margin == 0: return 0, 0
    return implied_1 / margin, implied_2 / margin

def find_arbitrage_opportunities(odds_data, sharp_book="Pinnacle"):
    print("Scanning for +EV and Arbitrage opportunities across bookmakers...")
    opportunities = []
    
    matches = {}
    for entry in odds_data:
        match = entry["match"]
        if match not in matches: matches[match] = []
        matches[match].append(entry)
        
    for match, bookies in matches.items():
        sharp_entry = next((b for b in bookies if b["bookmaker"].lower() == sharp_book.lower()), None)
        
        if sharp_entry:
            # 1. H2H Moneyline Analysis
            if sharp_entry.get("odds_home") and sharp_entry.get("odds_away") and sharp_entry.get("odds_draw"):
                fair_home, fair_away, fair_draw = remove_vig_3way(
                    sharp_entry["odds_home"], sharp_entry["odds_away"], sharp_entry["odds_draw"]
                )
                
                for b in bookies:
                    if b["bookmaker"].lower() == sharp_book.lower(): continue
                    
                    if b.get("odds_home") and fair_home * b["odds_home"] > 1.0:
                        opportunities.append({"type": "+EV", "match": match, "bet": "Home Win", "bookmaker": b["bookmaker"], "odds": b["odds_home"], "win_prob": fair_home, "edge": (fair_home * b["odds_home"]) - 1.0})
                    if b.get("odds_away") and fair_away * b["odds_away"] > 1.0:
                        opportunities.append({"type": "+EV", "match": match, "bet": "Away Win", "bookmaker": b["bookmaker"], "odds": b["odds_away"], "win_prob": fair_away, "edge": (fair_away * b["odds_away"]) - 1.0})
                    if b.get("odds_draw") and fair_draw * b["odds_draw"] > 1.0:
                        opportunities.append({"type": "+EV", "match": match, "bet": "Draw", "bookmaker": b["bookmaker"], "odds": b["odds_draw"], "win_prob": fair_draw, "edge": (fair_draw * b["odds_draw"]) - 1.0})
            
            # 2. Over/Under 2.5 Analysis
            if sharp_entry.get("odds_over_2_5") and sharp_entry.get("odds_under_2_5"):
                fair_over, fair_under = remove_vig_2way(sharp_entry["odds_over_2_5"], sharp_entry["odds_under_2_5"])
                
                for b in bookies:
                    if b["bookmaker"].lower() == sharp_book.lower(): continue
                    
                    if b.get("odds_over_2_5") and fair_over * b["odds_over_2_5"] > 1.0:
                        opportunities.append({"type": "+EV", "match": match, "bet": "Over 2.5 Goals", "bookmaker": b["bookmaker"], "odds": b["odds_over_2_5"], "win_prob": fair_over, "edge": (fair_over * b["odds_over_2_5"]) - 1.0})
                    if b.get("odds_under_2_5") and fair_under * b["odds_under_2_5"] > 1.0:
                        opportunities.append({"type": "+EV", "match": match, "bet": "Under 2.5 Goals", "bookmaker": b["bookmaker"], "odds": b["odds_under_2_5"], "win_prob": fair_under, "edge": (fair_under * b["odds_under_2_5"]) - 1.0})
                        
        # 3. Pure Arbitrage Check
        best_home = max([b.get("odds_home") or 0 for b in bookies] + [0])
        best_away = max([b.get("odds_away") or 0 for b in bookies] + [0])
        best_draw = max([b.get("odds_draw") or 0 for b in bookies] + [0])
        best_over = max([b.get("odds_over_2_5") or 0 for b in bookies] + [0])
        best_under = max([b.get("odds_under_2_5") or 0 for b in bookies] + [0])
        
        if best_home > 0 and best_away > 0 and best_draw > 0:
            arb_margin = (1.0 / best_home) + (1.0 / best_away) + (1.0 / best_draw)
            if arb_margin < 1.0:
                opportunities.append({"type": "Arbitrage", "match": match, "bet": "H2H Surebet", "bookmaker": "Multiple", "odds": f"H:{best_home}, A:{best_away}, D:{best_draw}", "edge": (1.0 - arb_margin) / arb_margin})
                
        if best_over > 0 and best_under > 0:
            arb_margin = (1.0 / best_over) + (1.0 / best_under)
            if arb_margin < 1.0:
                opportunities.append({"type": "Arbitrage", "match": match, "bet": "O/U 2.5 Surebet", "bookmaker": "Multiple", "odds": f"O:{best_over}, U:{best_under}", "edge": (1.0 - arb_margin) / arb_margin})
                
    return opportunities