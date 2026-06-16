from data.fetch_odds import fetch_live_odds
from strategy.world_cup_arb import find_arbitrage_opportunities
from portfolio.kelly_sizing import calculate_fractional_kelly
from features.tournament_regime import get_match_regime

def main():
    print("Starting World Cup 2026 Betting Engine...\n")
    
    # 1. Determine Match Regime
    regime = get_match_regime(match_number=3) 
    print(f"Current Match Context: {regime}")
    
    # 2. Fetch Odds
    odds = fetch_live_odds(api_key="DEMO_KEY")
    
    # 3. Scan for +EV / Arbs
    opportunities = find_arbitrage_opportunities(odds)
    
    # 4. Size Bets Conservatively
    if opportunities:
        print("\nOpportunities found:")
        for opp in opportunities:
            if opp['type'] == '+EV':
                win_prob = opp['win_prob']
                odds_offered = opp['odds']
                bet_size = calculate_fractional_kelly(win_prob=win_prob, decimal_odds=odds_offered, fraction=0.25)
                
                print(f"- [+EV] {opp['match']} ({opp['bet']} on {opp['bookmaker']} @ {odds_offered})")
                print(f"  Edge: {opp['edge']:.2%} | Recommended Bet (1/4 Kelly): {bet_size:.2%} of Bankroll")
                
            elif opp['type'] == 'Arbitrage':
                print(f"- [ARB] {opp['match']} ({opp['bet']})")
                print(f"  Best Odds -> {opp['odds']}")
                print(f"  Guaranteed Profit Margin: {opp['edge']:.2%}")
    else:
        print("No profitable opportunities found at this time.")

if __name__ == "__main__":
    main()