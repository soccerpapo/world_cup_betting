def calculate_3way_arb(odds1, odds2, odds3, total_stake=100.0):
    """
    Calculates the distribution for a 3-way arbitrage (Home, Away, Draw).
    """
    individual_implied_probs = [1.0/odds1, 1.0/odds2, 1.0/odds3]
    total_implied_prob = sum(individual_implied_probs)
    
    if total_implied_prob >= 1.0:
        return None, "Not a profitable arbitrage opportunity."

    profit_pct = (1.0 / total_implied_prob) - 1.0
    
    stakes = [
        (total_stake * individual_implied_probs[0]) / total_implied_prob,
        (total_stake * individual_implied_probs[1]) / total_implied_prob,
        (total_stake * individual_implied_probs[2]) / total_implied_prob
    ]
    
    returns = [stakes[0] * odds1, stakes[1] * odds2, stakes[2] * odds3]
    
    return {
        "stakes": stakes,
        "profit_pct": profit_pct,
        "guaranteed_profit": total_stake * profit_pct,
        "returns": returns
    }, None

def calculate_2way_arb(odds1, odds2, total_stake=100.0):
    """
    Calculates the distribution for a 2-way arbitrage (Over/Under).
    """
    individual_implied_probs = [1.0/odds1, 1.0/odds2]
    total_implied_prob = sum(individual_implied_probs)
    
    if total_implied_prob >= 1.0:
        return None, "Not a profitable arbitrage opportunity."

    profit_pct = (1.0 / total_implied_prob) - 1.0
    
    stakes = [
        (total_stake * individual_implied_probs[0]) / total_implied_prob,
        (total_stake * individual_implied_probs[1]) / total_implied_prob
    ]
    
    returns = [stakes[0] * odds1, stakes[1] * odds2]
    
    return {
        "stakes": stakes,
        "profit_pct": profit_pct,
        "guaranteed_profit": total_stake * profit_pct,
        "returns": returns
    }, None

def main():
    print("=== World Cup Arbitrage Calculator ===")
    mode = input("Enter '2' for 2-way (O/U) or '3' for 3-way (H2H): ")
    total = float(input("Total amount you want to stake (e.g., 100): "))
    
    if mode == '3':
        o1 = float(input("Odds 1 (Home): "))
        o2 = float(input("Odds 2 (Away): "))
        o3 = float(input("Odds 3 (Draw): "))
        res, err = calculate_3way_arb(o1, o2, o3, total)
        if err:
            print(f"Error: {err}")
        else:
            print(f"\n--- ARB RESULTS (Profit: {res['profit_pct']:.2%}) ---")
            print(f"Bet 1: ${res['stakes'][0]:.2f}")
            print(f"Bet 2: ${res['stakes'][1]:.2f}")
            print(f"Bet 3: ${res['stakes'][2]:.2f}")
            print(f"Guaranteed Profit: ${res['guaranteed_profit']:.2f}")
    elif mode == '2':
        o1 = float(input("Odds 1: "))
        o2 = float(input("Odds 2: "))
        res, err = calculate_2way_arb(o1, o2, total)
        if err:
            print(f"Error: {err}")
        else:
            print(f"\n--- ARB RESULTS (Profit: {res['profit_pct']:.2%}) ---")
            print(f"Bet 1: ${res['stakes'][0]:.2f}")
            print(f"Bet 2: ${res['stakes'][1]:.2f}")
            print(f"Guaranteed Profit: ${res['guaranteed_profit']:.2f}")

if __name__ == "__main__":
    main()
