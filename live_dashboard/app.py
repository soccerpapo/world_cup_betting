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
    This is called continuously to track live smart money movement.
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

def generate_dashboard(live_matches, live_sharp_odds):
    """
    Creates a rich, formatted table displaying live match data, Poisson probabilities, 
    and live Sharp Market consensus.
    """
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Min", style="dim", width=4)
    table.add_column("Matchup", min_width=20)
    table.add_column("Score", justify="center", style="bold white")
    table.add_column("Stats (Poss/Shots)", style="dim")
    table.add_column("Poisson Math (H-D-A)", justify="center", style="bold green")
    table.add_column("Live Sharp (H-D-A)", justify="center", style="bold cyan")
    table.add_column("Smart Money Filter", justify="center", style="bold")

    if not live_matches:
        table.add_row("N/A", "No live soccer matches currently found.", "-", "-", "-", "-", "-")
        return table

    for match, stats in live_matches.items():
        elapsed = stats['elapsed_time']
        h_score = stats['home_score']
        a_score = stats['away_score']
        
        # 1. Parse Teams
        teams = match.split(' vs ')
        home_team = teams[0] if len(teams) == 2 else "Unknown"
        away_team = teams[1] if len(teams) == 2 else "Unknown"

        # 2. Get TRUE pre-match probabilities for baseline
        base_probs = get_elo_probability(home_team, away_team) # Fallback
        
        sharp_live_prob = None
        if match in live_sharp_odds:
            base_probs = live_sharp_odds[match]
            sharp_live_prob = live_sharp_odds[match]
        else:
            for sharp_match, s_probs in live_sharp_odds.items():
                if home_team in sharp_match and away_team in sharp_match:
                    base_probs = s_probs
                    sharp_live_prob = s_probs
                    break
        
        # 3. Poisson Model Live Calculation
        home_xg = prob_to_xg(base_probs["Home Win"])
        away_xg = prob_to_xg(base_probs["Away Win"])
        
        probs = calculate_live_probabilities(
            home_xg, away_xg, 
            current_home_score=h_score, 
            current_away_score=a_score, 
            elapsed_minutes=elapsed,
            home_possession=stats.get('home_possession', 50),
            away_possession=stats.get('away_possession', 50),
            home_red_cards=stats.get('home_red_cards', 0),
            away_red_cards=stats.get('away_red_cards', 0),
            home_shots_on_target=stats.get('home_shots_on_target', 0),
            away_shots_on_target=stats.get('away_shots_on_target', 0),
            home_dangerous_attacks=stats.get('home_dangerous_attacks', 0),
            away_dangerous_attacks=stats.get('away_dangerous_attacks', 0),
            home_corners=stats.get('home_corners', 0),
            away_corners=stats.get('away_corners', 0)
        )
        
        prob_string = f"{probs['Home Win']:.1%} - {probs['Draw']:.1%} - {probs['Away Win']:.1%}"
        stats_string = f"{stats.get('home_possession', 50)}%/{stats.get('away_possession', 50)}% | {stats.get('home_shots_on_target', 0)}S-{stats.get('away_shots_on_target', 0)}S"
        
        # 4. Cross-Reference with Live Sharp Market
        sharp_string = "N/A (Using Elo)"
        filter_status = "[bold yellow]No Sharp Data[/bold yellow]"
        
        if sharp_live_prob:
            sharp_string = f"{sharp_live_prob['Home Win']:.1%} - {sharp_live_prob['Draw']:.1%} - {sharp_live_prob['Away Win']:.1%}"
            
            # The Ultimate Filter: Does Math agree with Smart Money?
            math_fav = max(probs, key=probs.get)
            sharp_fav = max(sharp_live_prob, key=sharp_live_prob.get)
            
            if math_fav == sharp_fav:
                divergence = abs(probs[math_fav] - sharp_live_prob[math_fav])
                if divergence > 0.15: # 15% disagreement
                    filter_status = "[bold red]DANGER (LURE)[/bold red]"
                else:
                    filter_status = "[bold green]SAFE TO TRADE[/bold green]"
            else:
                filter_status = "[bold red]DANGER (LURE)[/bold red]"

        min_str = f"[red]{elapsed}'[/red]" if elapsed > 80 else f"[green]{elapsed}'[/green]"
        
        table.add_row(
            min_str,
            f"[bold]{match}[/bold]",
            f"{h_score} - {a_score}",
            stats_string,
            prob_string,
            sharp_string,
            filter_status
        )

    return table

def run_dashboard():
    load_dotenv(override=True)
    api_key = os.getenv("API_FOOTBALL_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    
    if not api_key:
        print("CRITICAL: API_FOOTBALL_KEY not found in .env file.")
        return

    console = Console()
    
    with Live(console=console, screen=True, refresh_per_second=1) as live:
        try:
            while True:
                # 1. Fetch real-time data
                live_matches = fetch_live_match_stats(api_key)
                
                # 2. Fetch LIVE Sharp Odds to catch smart money movement
                live_sharp_odds = {}
                if odds_key:
                    live_sharp_odds = fetch_sharp_baselines(odds_key)

                # Filter to only show games we actually care about (to save space)
                target_teams = ["Ghana", "Panama", "France", "Iraq", "USA", "Germany", "Argentina"]
                filtered_matches = {k: v for k, v in live_matches.items() if any(t in k for t in target_teams)}
                display_matches = filtered_matches if filtered_matches else live_matches
                
                # 3. Generate the visual table
                table = generate_dashboard(display_matches, live_sharp_odds)
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                panel = Panel(
                    table, 
                    title=f"⚽ QUANTITATIVE LIVE SOCCER DASHBOARD (Last Updated: {timestamp}) ⚽", 
                    subtitle="Press Ctrl+C to exit",
                    border_style="blue"
                )
                
                live.update(panel)
                
                # Wait 300 seconds (5 minutes) before next API pull to conserve credits
                time.sleep(300)
                
        except KeyboardInterrupt:
            pass 

if __name__ == "__main__":
    run_dashboard()
