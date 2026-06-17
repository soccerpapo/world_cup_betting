# Elo Ratings for International Teams (Simulated for 2026)
# Standard Elo ratings for top World Cup teams based on historical performance and 2026 form.
# 1500 is the average strength. 2000+ is elite.
ELO_RATINGS = {
    "Argentina": 2150,
    "France": 2120,
    "England": 2080,
    "Spain": 2050,
    "Brazil": 2040,
    "Netherlands": 1980,
    "Portugal": 1970,
    "USA": 1850,
    "Senegal": 1820,
    "Morocco": 1840,
    "Japan": 1810,
    "Australia": 1750,
    "Mexico": 1780,
    "Canada": 1720,
    "South Korea": 1760,
    "Iraq": 1580,
    "Uzbekistan": 1600,
    "Norway": 1800,
    "Austria": 1830,
    "Algeria": 1710,
    "Jordan": 1520,
    "DR Congo": 1590,
    "Croatia": 1920,
    "Ghana": 1680,
    "Panama": 1610,
    "Colombia": 1890,
    "Czech Republic": 1790,
    "South Africa": 1630,
    "Switzerland": 1860,
    "Bosnia & Herzegovina": 1650,
    "Qatar": 1540,
    "Scotland": 1740,
    "Haiti": 1410,
    "Turkey": 1800,
    "Paraguay": 1730,
    "Ecuador": 1820,
    "Curaçao": 1350,
    "Tunisia": 1690,
    "Saudi Arabia": 1620,
    "Belgium": 1940,
    "Uruguay": 1950,
    "Cape Verde": 1570,
    "Egypt": 1740,
    "New Zealand": 1510,
    "Sweden": 1810,
    "Ivory Coast": 1720,
    "Germany": 1930,
}

def get_elo_probability(home_team, away_team):
    """
    Calculates the expected win probability of the home team
    based on the World Football Elo Ratings formula.
    """
    home_elo = ELO_RATINGS.get(home_team, 1500)
    away_elo = ELO_RATINGS.get(away_team, 1500)
    
    # 1. Add Home Advantage (standard is +100 points)
    # Note: In a World Cup (neutral ground), this is usually 0 
    # unless the team is the host (USA, Canada, Mexico).
    home_advantage = 0
    if home_team in ["USA", "Canada", "Mexico"]:
        home_advantage = 100
        
    dr = (home_elo + home_advantage) - away_elo
    
    # 2. Calculate Expected Result (W_e)
    # This represents the win probability for the Home team
    win_prob_home = 1.0 / (10**(-dr / 400.0) + 1.0)
    
    # 3. Derive Draw and Away probabilities
    # Elo formula is binary (Win/Loss), but we can estimate 3-way
    # based on the average draw rate in international soccer (~25-28%).
    draw_prob = 0.26 # Simplified constant for tournament soccer
    
    # Redistribute probabilities to account for the draw
    fair_home = win_prob_home * (1.0 - draw_prob)
    fair_away = (1.0 - win_prob_home) * (1.0 - draw_prob)
    
    return {
        "Home Win": fair_home,
        "Away Win": fair_away,
        "Draw": draw_prob
    }
