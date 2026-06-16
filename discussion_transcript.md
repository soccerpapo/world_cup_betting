**User:**
is this infrastructure useful for sports betting, specifically soccer betting?

**Model:**
Yes, this infrastructure is highly applicable to quantitative sports betting, specifically soccer, though it will require replacing some domain-specific components. 

Quantitative finance and algorithmic sports betting share the exact same mathematical foundation: identifying statistical edges, backtesting strategies, sizing positions based on probability, and executing trades (or bets) efficiently.

Here is a breakdown of how your current trading infrastructure maps to soccer betting:

### What translates perfectly (The Core Math & Engine)
* **`models/metalabeling.py`**: This is incredibly valuable for sports betting. You can use a primary model to generate a base prediction (e.g., Home Team Win) and use the meta-labeler to predict the *confidence* of that bet being profitable against the bookmaker's odds.
* **`portfolio/sizing.py`**: Position sizing in trading maps directly to bet sizing (e.g., the Kelly Criterion). This will help you manage your bankroll optimally based on your perceived edge.
* **`backtest/engine.py`**: The logic of stepping through historical data, making predictions, logging hypothetical PnL, and calculating metrics (Sharpe ratio, max drawdown) is exactly what you need to backtest soccer betting strategies.
* **`strategy/stat_arb.py` (Statistical Arbitrage)**: In sports betting, this translates to finding "arbs" (sure bets across different bookmakers) or finding pricing inefficiencies between correlated markets (e.g., Over 2.5 goals vs. Both Teams to Score).

### What needs minor adaptation (Feature Engineering)
* **`features/macro_regime.py`**: Instead of economic regimes (bull/bear markets, inflation), you would adapt this to capture "soccer regimes" like early-season variance, schedule congestion (e.g., playing in the Champions League midweek), or managerial changes.
* **`portfolio/hrp.py` (Hierarchical Risk Parity)**: While usually used for stocks, you could theoretically use HRP to distribute your bankroll across different uncorrelated leagues or betting markets to minimize variance.
* **`models/deep_momentum.py` & `strategy/trend.py`**: Momentum exists in sports (e.g., a team on a winning streak, or a striker in form). However, predicting match outcomes often relies more on Poisson distributions, Elo ratings, and Expected Goals (xG) rather than pure price-series momentum.

### What needs complete replacement (Data & Execution)
* **`execution/alpaca_broker.py`**: Alpaca is strictly for financial markets. You will need to replace this with an API for a betting exchange (like Betfair or Smarkets) or sharp bookmakers (like Pinnacle).
* **`data/fetcher.py`**: Instead of fetching OHLCV financial data (Open, High, Low, Close, Volume), you will need to integrate APIs that provide historical match data, xG, lineups, and historical odds (e.g., from APIs like API-Football, oddsview, or football-data.co.uk).
* **`features/micro_structure.py` & `data/fractional_diff.py`**: These are highly specific to financial market order books and continuous price series. Unless you are doing high-frequency live betting on a betting exchange (analyzing back/lay order books), these won't be very useful.

**Summary:** You have a robust, production-ready quantitative framework here. If you rewrite the **Data Fetcher** to pull soccer stats/odds and rewrite the **Execution Broker** to connect to a betting exchange, the rest of your machine learning, backtesting, and risk-management pipeline is perfectly suited for building a profitable soccer betting syndicate.

---

**User:**
what about for the 2026 soccer world cup?

**Model:**
Using this infrastructure for the 2026 World Cup—which is happening right now—presents a fascinating challenge. While the mathematical foundation holds up, the **nature of the data** in a short, international tournament is radically different from continuous financial markets or long domestic soccer leagues (like the English Premier League). 

Here is how your specific infrastructure maps to the 2026 World Cup, and where you will face immediate bottlenecks:

### The Biggest Challenge: Data Starvation & Variance
Financial markets give you thousands of ticks per second. A domestic soccer league gives you 380 matches a year with the same core squads. The 2026 World Cup (even with the expanded 48-team format) is exactly **104 matches** played over a single month. Furthermore, national teams rarely play together, meaning historical data from qualifiers or the 2022 World Cup is heavily degraded—players age, managers change, and tactical systems evolve.

Because of this, **`models/deep_momentum.py` will likely be useless**. Deep learning requires vast amounts of stationary data. If you try to feed it historical World Cup data, it will almost certainly overfit to past noise.

### How to Pivot Your Modules for the World Cup

**1. Exploit "Dumb Money" with `strategy/stat_arb.py`**
The World Cup is the most heavily bet sporting event in history. Millions of casual bettors flood the market, betting emotionally on their home countries or famous players (like Messi or Mbappé). 
* **The Strategy:** This casual money forces recreational sportsbooks to move their lines away from true probability to balance their liability. 
* **Your Infrastructure:** You can use your `stat_arb.py` logic to scan for discrepancies between "sharp" bookmakers (like Pinnacle or betting exchanges, which represent true probability) and "soft" recreational books. You don't even need to predict the winner; you just use your infrastructure to automatically execute bets when a soft book offers inefficient odds.

**2. Fade the Public with `models/metalabeling.py`**
Meta-labeling is your strongest predictive asset here. Instead of trying to predict the exact score of USA vs. France (which is notoriously difficult), use meta-labeling to predict *when the market is overreacting*.
* **Primary Model:** A very simple Elo rating system or Poisson distribution based on Expected Goals (xG).
* **Meta-Labeler:** A machine learning model that looks at the primary model's prediction, compares it to the bookmaker's odds, factors in public sentiment (e.g., social media volume or line movement), and outputs a simple binary: *Is there positive Expected Value (+EV) in taking the underdog?*

**3. Tournament Regimes via `features/macro_regime.py`**
A World Cup has distinct "regimes" that drastically alter how teams play, much like bull and bear markets:
* **Group Stage (Matches 1 & 2):** Teams play aggressively for wins.
* **Group Stage (Match 3):** Highly conditional. If a team only needs a draw to advance, they will play ultra-defensively. You must explicitly code these incentive structures into your features.
* **Knockout Stage:** Variance increases. Teams play more conservatively because a single mistake means elimination. 
Your `macro_regime.py` should be repurposed to flag which of these states a match falls into, as it drastically changes the probability of outcomes like "Under 2.5 Goals" or "Draws".

**4. Extreme Capital Preservation (`portfolio/sizing.py`)**
Because the sample size is only 104 matches, variance will dominate. You could have a mathematically perfect edge and still lose money if the ball hits the post twice in crucial games. 
* Your `sizing.py` (likely using a Fractional Kelly Criterion) will be the most critical file in your repo. You must size your bets much more conservatively than you would in a 380-game Premier League season to avoid "risk of ruin" (going bankrupt before your edge can play out).

### Summary for June 2026
To deploy this today, abandon complex deep learning predictions. Rewrite your `data/fetcher.py` to pull live odds from multiple bookmakers, use your `stat_arb.py` logic to find mispriced lines driven by casual public betting, and rely heavily on your `sizing.py` to survive the inevitable wild upsets that define the World Cup.