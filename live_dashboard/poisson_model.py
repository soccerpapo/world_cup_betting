import math

def poisson_probability(k, lam):
    """
    Calculates the Poisson probability of exactly 'k' events occurring, 
    given the expected rate of occurrences 'lam' (lambda).
    formula: (e^(-lam) * lam^k) / k!
    """
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def calculate_live_probabilities(home_expected_goals, away_expected_goals, 
                                 current_home_score=0, current_away_score=0, 
                                 elapsed_minutes=0,
                                 home_possession=50, away_possession=50,
                                 home_red_cards=0, away_red_cards=0):
    """
    Calculates the probability of Home Win, Away Win, and Draw from the current game state,
    dynamically adjusting Expected Goals based on live match momentum.
    """
    
    # 1. Calculate time remaining factor
    minutes_remaining = max(0, 90 - elapsed_minutes)
    time_decay = minutes_remaining / 90.0
    
    # 2. Base expected goals for the remaining time
    base_live_home_xg = home_expected_goals * time_decay
    base_live_away_xg = away_expected_goals * time_decay
    
    # 3. Dynamic Momentum Adjustments
    # A. Red Cards: A massive penalty to the penalized team's attack, and a boost to the opponent
    home_red_multiplier = 1.0 - (home_red_cards * 0.4) # Lose 40% attacking power per red card
    away_red_multiplier = 1.0 - (away_red_cards * 0.4)
    
    # B. Possession: If a team is dominating the ball, they are more likely to score
    # We normalize possession around 50%. E.g., 70% possession = 1.4 multiplier.
    home_poss_multiplier = home_possession / 50.0 if home_possession > 0 else 1.0
    away_poss_multiplier = away_possession / 50.0 if away_possession > 0 else 1.0

    # Apply adjustments. 
    # If Home has a red card, Away gets a massive boost to their possession effectiveness.
    live_home_xg = base_live_home_xg * home_poss_multiplier * home_red_multiplier * (1.0 + (away_red_cards * 0.5))
    live_away_xg = base_live_away_xg * away_poss_multiplier * away_red_multiplier * (1.0 + (home_red_cards * 0.5))
    
    # Cap xG at 0 so math doesn't break
    live_home_xg = max(0.01, live_home_xg)
    live_away_xg = max(0.01, live_away_xg)

    # 4. Build the Score Matrix (0 to 5+ goals)
    max_goals = 6
    home_probs = [poisson_probability(i, live_home_xg) for i in range(max_goals)]
    away_probs = [poisson_probability(i, live_away_xg) for i in range(max_goals)]
    
    # Accumulate tail probabilities (5+ goals) into the last bucket to ensure sum is ~1.0
    home_probs[-1] = 1.0 - sum(home_probs[:-1])
    away_probs[-1] = 1.0 - sum(away_probs[:-1])

    # 5. Calculate Match Outcomes
    home_win_prob = 0.0
    away_win_prob = 0.0
    draw_prob = 0.0
    
    # We simulate every possible scoreline for the REST of the match
    for h_goals in range(max_goals):
        for a_goals in range(max_goals):
            scoreline_prob = home_probs[h_goals] * away_probs[a_goals]
            final_home = current_home_score + h_goals
            final_away = current_away_score + a_goals
            
            if final_home > final_away:
                home_win_prob += scoreline_prob
            elif final_away > final_home:
                away_win_prob += scoreline_prob
            else:
                draw_prob += scoreline_prob
                
    return {
        "Home Win": home_win_prob,
        "Away Win": away_win_prob,
        "Draw": draw_prob,
        "Live_Home_xG": live_home_xg,
        "Live_Away_xG": live_away_xg
    }

if __name__ == "__main__":
    # Test Scenario representing the Ghana vs Panama situation
    print("--- 68th MINUTE, 0-0. Ghana dominating possession (70%). ---")
    probs = calculate_live_probabilities(
        home_expected_goals=1.4, away_expected_goals=1.1, 
        current_home_score=0, current_away_score=0, 
        elapsed_minutes=68,
        home_possession=70, away_possession=30
    )
    print(f"Ghana (Home) xG for rest of match: {probs['Live_Home_xG']:.2f}")
    print(f"Panama (Away) xG for rest of match: {probs['Live_Away_xG']:.2f}")
    print(f"Ghana Win: {probs['Home Win']:.1%} | Draw: {probs['Draw']:.1%} | Panama Win: {probs['Away Win']:.1%}")
