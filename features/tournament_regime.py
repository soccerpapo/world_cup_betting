# Mock database of tournament standings for the 2026 World Cup
# In a production environment, this would be fetched from a live sports data API.
TEAM_STANDINGS = {
    "USA": {"played": 2, "points": 4},
    "FRA": {"played": 2, "points": 6},  # Already advanced, doesn't 'need' points
    "ENG": {"played": 3, "points": 7},  # In Knockouts
    "ARG": {"played": 3, "points": 9},  # In Knockouts
    "MEX": {"played": 1, "points": 3},
    "CAN": {"played": 1, "points": 0},
}

def get_match_regime(home_team, away_team):
    """
    Dynamically classifies the match context based on team standings.
    The World Cup has drastically different incentive structures depending on the stage.
    """
    home_stats = TEAM_STANDINGS.get(home_team, {"played": 0, "points": 0})
    away_stats = TEAM_STANDINGS.get(away_team, {"played": 0, "points": 0})
    
    # Predict the match number for these teams (e.g. if played 2, this is match 3)
    match_number = max(home_stats["played"], away_stats["played"]) + 1
    
    if match_number <= 2:
        return "GROUP_EARLY_AGGRESSIVE" # Teams play normally to win
        
    elif match_number == 3:
        # Simplistic qualification heuristic for the group stage
        # Usually 6 points guarantees advancement (no pressure), 0 means eliminated (no pressure)
        home_needs_points = 0 < home_stats["points"] < 6
        away_needs_points = 0 < away_stats["points"] < 6
        
        if not home_needs_points or not away_needs_points:
            return "GROUP_FINAL_CONDITIONAL" # Risk of heavily rotated squads or playing for a draw
        return "GROUP_FINAL_MUST_WIN"
        
    else:
        return "KNOCKOUT_HIGH_VARIANCE" # Teams play more conservatively; extra time/penalties possible
