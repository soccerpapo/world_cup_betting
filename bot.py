import time
from datetime import datetime
from main import main as run_betting_engine

def run_bot(interval_minutes=5):
    """
    Runs the betting engine continuously on a specified interval.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting World Cup Betting Bot...")
    print(f"The engine will scan for opportunities every {interval_minutes} minutes.")
    print("Press Ctrl+C to stop.")
    print("-" * 50)
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executing scan...")
            run_betting_engine()
            print("-" * 50)
            
            # Sleep for the specified interval
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        print("\nBot stopped manually. Exiting...")

if __name__ == "__main__":
    # You can change the interval here. 5 minutes is a good balance 
    # to avoid hitting API rate limits while staying relatively current.
    run_bot(interval_minutes=5)
