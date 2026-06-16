import csv
import os
import random

LOG_FILE = "bet_log.csv"

def run_backtest(initial_bankroll=1000.0, num_simulations=100):
    """
    Reads the logged opportunities and runs a Monte Carlo simulation
    to estimate how the bankroll would have performed.
    """
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file '{LOG_FILE}' not found.")
        return

    # Load bets from log
    bets = []
    try:
        with open(LOG_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("Type") == "+EV":
                    try:
                        odds = float(row.get("Odds", 0))
                        edge = float(row.get("Edge", 0))
                        bet_pct = float(row.get("Recommended_Bet_Pct", 0))
                        
                        if odds > 0:
                            win_prob = (edge + 1.0) / odds
                            bets.append({
                                "odds": odds,
                                "win_prob": win_prob,
                                "bet_pct": bet_pct
                            })
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error reading log file: {e}")
        return

    if not bets:
        print("No valid +EV bets found to simulate.")
        return

    print(f"Loaded {len(bets)} +EV bets for simulation.")
    print(f"Running {num_simulations} Monte Carlo simulations with an initial bankroll of ${initial_bankroll:.2f}...")

    final_bankrolls = []
    bankruptcies = 0

    for _ in range(num_simulations):
        bankroll = initial_bankroll
        
        for bet in bets:
            # We can only bet what we have
            if bankroll <= 0:
                break
                
            bet_amount = bankroll * bet["bet_pct"]
            
            # Simulate match outcome
            if random.random() < bet["win_prob"]:
                # Win: return stake + profit
                bankroll += bet_amount * (bet["odds"] - 1.0)
            else:
                # Loss: lose stake
                bankroll -= bet_amount

        if bankroll <= 0.01 * initial_bankroll:  # Consider 99% loss as bankruptcy
            bankruptcies += 1
            
        final_bankrolls.append(bankroll)

    # Calculate statistics
    avg_bankroll = sum(final_bankrolls) / num_simulations
    max_bankroll = max(final_bankrolls)
    min_bankroll = min(final_bankrolls)
    median_bankroll = sorted(final_bankrolls)[num_simulations // 2]
    win_rate = sum(1 for b in final_bankrolls if b > initial_bankroll) / num_simulations

    print("=" * 50)
    print(" " * 12 + "BACKTEST SIMULATION RESULTS" + " " * 12)
    print("=" * 50)
    print(f"Simulations Run:     {num_simulations}")
    print(f"Initial Bankroll:    ${initial_bankroll:.2f}")
    print(f"Average Final:       ${avg_bankroll:.2f}")
    print(f"Median Final:        ${median_bankroll:.2f}")
    print(f"Max Final Bankroll:  ${max_bankroll:.2f}")
    print(f"Min Final Bankroll:  ${min_bankroll:.2f}")
    print(f"Probability of Profit: {win_rate:.2%}")
    print(f"Risk of Ruin:        {bankruptcies / num_simulations:.2%}")
    print("=" * 50)

if __name__ == "__main__":
    run_backtest()
