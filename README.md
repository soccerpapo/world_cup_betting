# World Cup 2026 Betting Engine

A streamlined quantitative betting framework optimized for the short-term, high-variance environment of the 2026 FIFA World Cup.

## Architecture
- **`data/`**: Connects to live odds APIs (replaces historical financial data fetchers).
- **`strategy/`**: Implements statistical arbitrage and line-shopping between sharp and soft bookmakers.
- **`features/`**: Captures tournament-specific regimes (e.g., Knockout stage vs. Group stage match incentives).
- **`portfolio/`**: Implements Fractional Kelly Criterion to protect capital against tournament variance.

## Next Steps
1. Create a remote repository on GitHub.
2. Link it using `git remote add origin <your-repo-url>`.
3. Run `git push -u origin main` (or master).
