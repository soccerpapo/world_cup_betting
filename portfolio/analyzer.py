import csv
import os
from collections import defaultdict

LOG_FILE = "bet_log.csv"

def analyze_logs():
    """
    Reads the bet_log.csv file and generates a summary report of the 
    opportunities found by the betting engine.
    """
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file '{LOG_FILE}' not found. The bot needs to run and find opportunities first.")
        return

    total_opportunities = 0
    total_ev_edge = 0.0
    total_bankroll_pct = 0.0
    
    opportunities_by_type = defaultdict(int)
    opportunities_by_bookmaker = defaultdict(int)
    opportunities_by_regime = defaultdict(int)

    try:
        with open(LOG_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_opportunities += 1
                
                # Count by Type (+EV vs Arbitrage)
                opp_type = row.get("Type", "Unknown")
                opportunities_by_type[opp_type] += 1
                
                # Count by Regime
                regime = row.get("Regime", "Unknown")
                opportunities_by_regime[regime] += 1
                
                # Aggregate +EV specific stats
                if opp_type == "+EV":
                    try:
                        total_ev_edge += float(row.get("Edge", 0))
                        total_bankroll_pct += float(row.get("Recommended_Bet_Pct", 0))
                    except ValueError:
                        pass
                        
                    bookmaker = row.get("Bookmaker", "Unknown")
                    opportunities_by_bookmaker[bookmaker] += 1

    except Exception as e:
        print(f"Error reading log file: {e}")
        return

    if total_opportunities == 0:
        print("Log file is empty. No opportunities to analyze.")
        return

    # Print Summary Report
    print("=" * 50)
    print(" " * 15 + "BET LOG ANALYSIS" + " " * 15)
    print("=" * 50)
    
    print(f"Total Opportunities Found: {total_opportunities}")
    print(f"  - +EV Bets:    {opportunities_by_type['+EV']}")
    print(f"  - Arbitrages:  {opportunities_by_type['Arbitrage']}")
    
    print("\n--- +EV Value Summary ---")
    ev_count = opportunities_by_type['+EV']
    if ev_count > 0:
        avg_edge = total_ev_edge / ev_count
        print(f"Average Expected Edge:  {avg_edge:.2%}")
        print(f"Total Suggested Capital: {total_bankroll_pct:.2%} of Bankroll")
    else:
        print("No +EV opportunities logged yet.")

    print("\n--- Opportunities by Bookmaker (+EV Only) ---")
    # Sort bookmakers by highest count
    sorted_bookies = sorted(opportunities_by_bookmaker.items(), key=lambda item: item[1], reverse=True)
    for bookie, count in sorted_bookies:
        print(f"  {bookie}: {count}")

    print("\n--- Opportunities by Regime ---")
    for reg, count in opportunities_by_regime.items():
        print(f"  {reg}: {count}")
        
    print("=" * 50)

if __name__ == "__main__":
    analyze_logs()
