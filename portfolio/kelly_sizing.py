def calculate_fractional_kelly(win_prob, decimal_odds, fraction=0.25):
    """
    Calculates the Fractional Kelly Criterion bet size.
    Because a World Cup only has 104 matches, variance is enormous.
    A standard Kelly could ruin a bankroll quickly; using a fraction (e.g., 1/4th) is safer.
    
    :param win_prob: Your model's perceived probability of winning (0.0 to 1.0)
    :param decimal_odds: The bookmaker's decimal odds (e.g., 2.0 for even money)
    :param fraction: The fraction of the Kelly size to actually bet (default 0.25)
    """
    q = 1.0 - win_prob
    b = decimal_odds - 1.0
    
    if b <= 0:
        return 0.0
        
    kelly_fraction = (b * win_prob - q) / b
    
    # If the edge is negative, bet size is 0
    if kelly_fraction <= 0:
        return 0.0
        
    # Apply fractional multiplier to protect bankroll
    safe_fraction = kelly_fraction * fraction
    return safe_fraction