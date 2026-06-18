import os
import time
import math
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from datetime import datetime

from live_data import fetch_live_match_stats
from poisson_model import calculate_live_probabilities

# Import our actual team strength model and odds fetcher
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from features.team_strength import get_elo_probability
from data.fetch_odds import fetch_live_odds
from strategy.kalshi_value import remove_vig_3way

def prob_to_xg(win_prob):
    """
    Roughly converts a team's pre-match win probability into an Expected Goals (xG) 
    metric for the Poisson model. A 50% win prob roughly translates to 1.5 xG.
    """
    # Base xG of 0.5 + scaling based on win probability
    return 0.5 + (win_prob * 2.0)

def fetch_sharp_baselines(api_key):
    """
    Fetches the latest sharp odds and converts them into true probabilities to use as baselines.
    """
    if not api_key: return {}
    
    # We fetch odds across common soccer leagues to ensure coverage
    leagues = ["soccer_fifa_world_cup", "soccer_epl", "soccer_usa_mls", "soccer_conmebol_copa_america"]
    sharp_baselines = {}
    
    for league in leagues:
        odds_data = fetch_live_odds(api_key, sport=league)
        for entry in odds_data:
            if entry["bookmaker"].lower() == "pinnacle": # Use sharpest book
                try:
                    f_home, f_away, f_draw = remove_vig_3way(
                        entry.get("odds_home"), 
                        entry.get("odds_away"), 
                        entry.get("odds_draw")
                    )
                    # Normalize names to match API-Football format roughly
                    home = entry["match"].split(" vs ")[0]
                    away = entry["match"].split(" vs ")[1]
                    sharp_baselines[f"{home} vs {away}"] = {
                        "Home Win": f_home,
                        "Away Win": f_away,
                        "Draw": f_draw
                    }
                except Exception:
                    pass
    return sharp_baselines

def generate_dashboard(live_matches, sharp_baselines):
    """
    Creates a rich, formatted table displaying live match data and calculated probabilities.
    """
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Minute", style="dim", width=8)
    table.add_column("Matchup", min_width=20)
    table.add_column("Score", justify="center", style="bold white")
    table.add_column("Base Prob Source", style="dim", justify="center")
    table.add_column("Model Prediction (Home - Draw - Away)", justify="center", style="bold green")

    if not live_matches:
        table.add_row("N/A", "No live soccer matches currently found.", "-", "-", "-")
        return table

    for match, stats in live_matches.items():
        elapsed = stats['elapsed_time']
        h_score = stats['home_score']
        a_score = stats['away_score']
        
        # 1. Parse Teams
        teams = match.split(' vs ')
        home_team = teams[0] if len(teams) == 2 else "Unknown"
        away_team = teams[1] if len(teams) == 2 else "Unknown"

        # 2. Get TRUE pre-match probabilities (Prefer Sharp Market over Elo)
        source = "Elo"
        base_probs = get_elo_probability(home_team, away_team)
        
        if match in sharp_baselines:
            base_probs = sharp_baselines[match]
            source = "Market"
        else:
            for sharp_match, s_probs in sharp_baselines.items():
                if home_team in sharp_match and away_team in sharp_match:
                    base_probs = s_probs
                    source = "Market"
                    break
        
        # 3. Convert those true probabilities into Expected Goals for the Poisson model
        home_xg = prob_to_xg(base_probs["Home Win"])
        away_xg = prob_to_xg(base_probs["Away Win"])
        
        # 4. Calculate real-time probabilities using actual data AND live stats
        probs = calculate_live_probabilities(
            home_xg, away_xg, 
            current_home_score=h_score, 
            current_away_score=a_score, 
            elapsed_minutes=elapsed,
            home_possession=stats.get('home_possession', 50),
            away_possession=stats.get('away_possession', 50),
            home_red_cards=stats.get('home_red_cards', 0),
            away_red_cards=stats.get('away_red_cards', 0)
        )
        
        prob_string = f"{probs['Home Win']:.1%}  -  {probs['Draw']:.1%}  -  {probs['Away Win']:.1%}"
        
        # Color code the minute (red if past 80 mins)
        min_str = f"[red]{elapsed}'[/red]" if elapsed > 80 else f"[green]{elapsed}'[/green]"
        
        table.add_row(
            min_str,
            f"[bold]{match}[/bold]",
            f"{h_score} - {a_score}",
            source,
            prob_string
        )

    return table

def run_dashboard():
    load_dotenv(override=True)
    api_key = os.getenv("API_FOOTBALL_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    
    if not api_key:
        print("CRITICAL: API_FOOTBALL_KEY not found in .env file.")
        return

    # Cache the sharp market probabilities at startup
    sharp_baselines = {}
    if odds_key:
        print("Fetching opening market consensus from The-Odds-API (This uses 1-4 credits)...")
        sharp_baselines = fetch_sharp_baselines(odds_key)

    console = Console()
    
    with Live(console=console, screen=True, refresh_per_second=1) as live:
        try:
            while True:
                live_matches = fetch_live_match_stats(api_key)
                
                # Show all live matches
                display_matches = live_matches
                
                table = generate_dashboard(display_matches, sharp_baselines)
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                panel = Panel(
                    table, 
                    title=f"⚽ QUANTITATIVE LIVE SOCCER DASHBOARD (Last Updated: {timestamp}) ⚽", 
                    subtitle="Press Ctrl+C to exit",
                    border_style="blue"
                )
                
                live.update(panel)
                time.sleep(300)
                
        except KeyboardInterrupt:
            pass 

if __name__ == "__main__":
    run_dashboard()
