import os
from dotenv import load_dotenv

from data.fetch_odds import fetch_live_odds
from strategy.world_cup_arb import find_arbitrage_opportunities
from portfolio.kelly_sizing import calculate_fractional_kelly
from features.tournament_regime import get_match_regime
from portfolio.logger import log_opportunity

# Load environment variables from .env file
load_dotenv()

def main():
    print("Starting World Cup 2026 Betting Engine...\n")
    
    # Get API key from environment, fallback to DEMO_KEY
    api_key = os.getenv("ODDS_API_KEY", "DEMO_KEY")
    
    # 1. Fetch Odds
    odds = fetch_live_odds(api_key=api_key)
    
    # 2. Scan for +EV / Arbs
    opportunities = find_arbitrage_opportunities(odds)
    
    # 3. Analyze and Size Bets Dynamically
    if opportunities:
        print("\nOpportunities found:")
        for opp in opportunities:
            # Parse teams from match string (e.g., "USA vs FRA")
            teams = opp['match'].split(' vs ')
            home_team = teams[0] if len(teams) == 2 else "Unknown"
            away_team = teams[1] if len(teams) == 2 else "Unknown"
            
            # Determine dynamic regime for this specific match
            regime = get_match_regime(home_team, away_team)
            
            if opp['type'] == '+EV':
                win_prob = opp['win_prob']
                odds_offered = opp['odds']
                
                # Dynamic Bankroll Protection: Adjust Kelly fraction based on regime variance
                base_fraction = 0.25 # Standard quarter-Kelly
                if regime == "KNOCKOUT_HIGH_VARIANCE":
                    base_fraction = 0.125 # Halve the bet size for unpredictable knockout games
                elif regime == "GROUP_FINAL_CONDITIONAL":
                    base_fraction = 0.10 # Extremely conservative if a team doesn't need to win
                    
                bet_size = calculate_fractional_kelly(win_prob=win_prob, decimal_odds=odds_offered, fraction=base_fraction)
                
                print(f"- [+EV] {opp['match']} ({opp['bet']} on {opp['bookmaker']} @ {odds_offered})")
                print(f"  Regime: {regime}")
                print(f"  Edge: {opp['edge']:.2%} | Recommended Bet ({base_fraction} Kelly): {bet_size:.2%} of Bankroll")
                
                log_opportunity(
                    opp_type="+EV", match=opp['match'], bet=opp['bet'], 
                    bookmaker=opp['bookmaker'], odds=odds_offered, 
                    edge=opp['edge'], recommended_bet_pct=bet_size, regime=regime
                )
                
            elif opp['type'] == 'Arbitrage':
                print(f"- [ARB] {opp['match']} ({opp['bet']})")
                print(f"  Regime: {regime}")
                print(f"  Best Odds -> {opp['odds']}")
                print(f"  Guaranteed Profit Margin: {opp['edge']:.2%}")
                
                log_opportunity(
                    opp_type="Arbitrage", match=opp['match'], bet=opp['bet'], 
                    bookmaker="Multiple", odds=opp['odds'], 
                    edge=opp['edge'], recommended_bet_pct=0.0, regime=regime
                )
    else:
        print("No profitable opportunities found at this time.")

if __name__ == "__main__":
    main()