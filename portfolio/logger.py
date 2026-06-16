import csv
import os
import json
import urllib.request
import time
from datetime import datetime

LOG_FILE = "bet_log.csv"

def send_discord_alert(opp_type, match, bet, bookmaker, odds, edge, recommended_bet_pct, regime):
    """
    Sends an alert to a Discord webhook if configured.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    # Create a nicely formatted message
    color = 5763719 if opp_type == "+EV" else 15548997 # Green for EV, Red for Arb
    
    embed = {
        "title": f"🚨 New {opp_type} Opportunity: {match}",
        "color": color,
        "fields": [
            {"name": "Bet", "value": bet, "inline": True},
            {"name": "Bookmaker", "value": bookmaker, "inline": True},
            {"name": "Odds", "value": str(odds), "inline": True},
            {"name": "Edge", "value": f"{edge:.2%}", "inline": True},
            {"name": "Rec. Bet Size", "value": f"{recommended_bet_pct:.2%} of Bankroll", "inline": True},
            {"name": "Regime", "value": regime, "inline": False}
        ],
        "footer": {"text": "World Cup Betting Engine"}
    }
    
    data = {"embeds": [embed]}
    
    try:
        req = urllib.request.Request(
            webhook_url, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        urllib.request.urlopen(req)
        # Wait 1 second to respect Discord rate limits
        time.sleep(1)
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

def log_opportunity(opp_type, match, bet, bookmaker, odds, edge, recommended_bet_pct, regime):
    """
    Logs a betting opportunity to a CSV file for tracking and analysis,
    and optionally sends a Discord alert.
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
    
    # Trigger Discord Alert
    send_discord_alert(opp_type, match, bet, bookmaker, odds, edge, recommended_bet_pct, regime)

