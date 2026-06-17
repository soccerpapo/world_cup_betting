import os
from dotenv import load_dotenv

from data.fetch_odds import fetch_live_odds
from data.fetch_kalshi import fetch_kalshi_prices
from strategy.kalshi_value import find_kalshi_value
from portfolio.kelly_sizing import calculate_fractional_kelly
from features.tournament_regime import get_match_regime
from portfolio.logger import log_opportunity

# Load environment variables from .env file
load_dotenv(override=True)

def main():
    print("Starting World Cup 2026 Kalshi +EV Engine...\n")
    
    # 1. Credentials
    odds_api_key = os.getenv("ODDS_API_KEY")
    kalshi_id = os.getenv("KALSHI_API_KEY_ID")
    kalshi_key = os.getenv("KALSHI_PRIVATE_KEY")
    
    if not odds_api_key or not kalshi_id or not kalshi_key:
        print("Critical Error: Missing API keys in .env file.")
        return

    # 2. Fetch "Truth" Odds (Sharp Bookmakers)
    sharp_odds = fetch_live_odds(api_key=odds_api_key)
    
    if not sharp_odds:
        print("No live odds available (check API quota or sport status).")
        return
    
    # 3. Fetch "Market" Prices (Kalshi)
    kalshi_prices = fetch_kalshi_prices(api_key_id=kalshi_id, private_key=kalshi_key)
    
    if not kalshi_prices:
        print("No live soccer markets found on Kalshi at this time.")
        return
    
    # 4. Scan for +EV discrepancies on Kalshi
    opportunities = find_kalshi_value(sharp_odds, kalshi_prices)
    
    # 5. Analyze and Size Bets
    if opportunities:
        print(f"\nFound {len(opportunities)} +EV opportunities on Kalshi:")
        for opp in opportunities:
            # Parse teams
            teams = opp['match'].split(' vs ')
            home_team = teams[0] if len(teams) == 2 else "Unknown"
            away_team = teams[1] if len(teams) == 2 else "Unknown"
            
            # Dynamic Regime
            regime = get_match_regime(home_team, away_team)
            
            # Reciprocal of the price
            decimal_odds = 1.0 / opp['kalshi_price']
            
            # Standard risk multiplier
            base_fraction = 0.20 
            if regime == "KNOCKOUT_HIGH_VARIANCE": base_fraction = 0.10
            
            bet_size = calculate_fractional_kelly(
                win_prob=opp['sharp_prob'], 
                decimal_odds=decimal_odds, 
                fraction=base_fraction
            )
            
            print(f"- [VALUE] {opp['match']} ({opp['bet']})")
            print(f"  Confidence: {opp['confidence']}")
            print(f"  Kalshi Price: ${opp['kalshi_price']:.2f} | Sharp Prob: {opp['sharp_prob']:.1%} | Elo Prob: {opp['elo_prob']:.1%}")
            print(f"  Edge: {opp['edge']:.2%} | Rec. Position: {bet_size:.2%} of Bankroll")
            
            log_opportunity(
                opp_type="Kalshi +EV", match=opp['match'], bet=opp['bet'], 
                bookmaker="Kalshi", odds=decimal_odds, 
                edge=opp['edge'], recommended_bet_pct=bet_size, 
                regime=regime
            )
    else:
        print("All Kalshi markets are currently efficient (No value found).")

if __name__ == "__main__":
    main()
