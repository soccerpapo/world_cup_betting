def get_match_regime(match_number, team_a_needs_points=True, team_b_needs_points=True):
    """
    Classifies the match context. The World Cup has drastically different 
    incentive structures depending on the stage of the tournament.
    """
    if match_number <= 2:
        return "GROUP_EARLY_AGGRESSIVE" # Teams play normally to win
    elif match_number == 3:
        if not team_a_needs_points or not team_b_needs_points:
            return "GROUP_FINAL_CONDITIONAL" # Risk of heavily rotated squads or playing for a draw
        return "GROUP_FINAL_MUST_WIN"
    else:
        return "KNOCKOUT_HIGH_VARIANCE" # Teams play more conservatively; extra time/penalties possible