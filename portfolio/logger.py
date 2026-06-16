import csv
import os
from datetime import datetime

LOG_FILE = "bet_log.csv"

def log_opportunity(opp_type, match, bet, bookmaker, odds, edge, recommended_bet_pct, regime):
    """
    Logs a betting opportunity to a CSV file for tracking and analysis.
    """
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header if file is being created
        if not file_exists:
            writer.writerow([
                "Timestamp", 
                "Type", 
                "Match", 
                "Bet", 
                "Bookmaker", 
                "Odds", 
                "Edge", 
                "Recommended_Bet_Pct", 
                "Regime"
            ])
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([
            timestamp,
            opp_type,
            match,
            bet,
            bookmaker,
            odds,
            f"{edge:.4f}",
            f"{recommended_bet_pct:.4f}",
            regime
        ])
    
    print(f"Logged {opp_type} opportunity for {match} to {LOG_FILE}")
