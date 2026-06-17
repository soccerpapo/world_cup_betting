import json
import urllib.request
import urllib.error
import os
import time
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def get_kalshi_auth_headers(method, path, api_key_id, private_key_str):
    """
    Generates the required RSA-PSS signature headers for Kalshi API v2.
    """
    clean_key = private_key_str.replace('\\n', '\n').strip('"').strip("'")
    private_key = serialization.load_pem_private_key(
        clean_key.encode('utf-8'),
        password=None
    )
    timestamp = str(int(time.time() * 1000))
    path_no_query = path.split('?')[0]
    message = f"{timestamp}{method}{path_no_query}".encode('utf-8')
    
    signature_bytes = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')
    
    return {
        "KALSHI-ACCESS-KEY": api_key_id,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "KALSHI-ACCESS-SIGNATURE": signature_base64,
        "Content-Type": "application/json"
    }

def fetch_kalshi_prices(api_key_id=None, private_key=None, sport="soccer"):
    """
    Fetches REAL live Match Winner prices from Kalshi API v2 by directly
    querying the Order Book to ensure executable liquidity.
    """
    if not api_key_id or not private_key:
        return []

    print(f"Fetching real Kalshi market prices (Order Book Deep Scan)...")
    base_url = "https://external-api.kalshi.com"
    
    # Target World Cup Game series
    path = "/trade-api/v2/markets?series_ticker=KXWCGAME&status=open&limit=100"
    
    try:
        headers = get_kalshi_auth_headers("GET", "/trade-api/v2/markets", api_key_id, private_key)
        req = urllib.request.Request(f"{base_url}{path}", headers=headers)
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            markets = data.get("markets", [])
            
            parsed_results = []
            for m in markets:
                title = m.get("title", "")
                if " vs " in title:
                    # Parse Match Name
                    match_teams = title.split(" Winner?")[0]
                    teams = match_teams.split(" vs ")
                    home_team = teams[0].strip()
                    away_team = teams[1].strip()
                    
                    ticker = m.get("ticker", "")
                    
                    # FETCH RAW ORDER BOOK FOR THIS SPECIFIC TICKER
                    ob_path = f"/trade-api/v2/markets/{ticker}/orderbook"
                    ob_headers = get_kalshi_auth_headers("GET", ob_path, api_key_id, private_key)
                    ob_req = urllib.request.Request(f"{base_url}{ob_path}", headers=ob_headers)
                    
                    try:
                        with urllib.request.urlopen(ob_req) as ob_res:
                            ob_data = json.loads(ob_res.read().decode('utf-8'))
                            ob = ob_data.get('orderbook', {})
                            
                            # In Kalshi, the "Ask" for YES is determined by the highest "Bid" for NO
                            # The formula is: Yes_Ask = 1.00 - No_Bid (or we can just use the lowest Yes_Ask if Kalshi provides it directly in v2)
                            # However, Kalshi v2 orderbook often returns 'yes' and 'no' arrays of [price, quantity] bids.
                            # So the lowest price someone is willing to sell YES for is: 1.00 - (highest price someone is bidding for NO)
                            
                            no_bids = ob.get('no', [])
                            
                            if not no_bids:
                                continue # No liquidity to trade against
                                
                            # 'no' array is typically sorted. We want the highest bid for NO.
                            # Usually, index [0] is the lowest price in Kalshi's array, so we must find the max.
                            # Alternatively, kalshi provides 'no_dollars' or similar in orderbook_fp.
                            
                            ob_fp = ob_data.get('orderbook_fp', {})
                            no_bids_fp = ob_fp.get('no_dollars', [])
                            
                            if no_bids_fp:
                                # Find the highest 'No' bid
                                highest_no_bid = max([float(bid[0]) for bid in no_bids_fp])
                                
                                # The true cost to buy YES right now is 1 minus the highest NO bid
                                true_yes_ask = round(1.00 - highest_no_bid, 2)
                                
                                # Determine outcome
                                sub_title = m.get("yes_sub_title", "")
                                outcome = "Home Win" # Default fallback
                                if sub_title.lower() == "tie":
                                    outcome = "Draw"
                                elif sub_title.lower() == away_team.lower():
                                    outcome = "Away Win"
                                elif sub_title.lower() == home_team.lower():
                                    outcome = "Home Win"

                                parsed_results.append({
                                    "match": f"{home_team} vs {away_team}",
                                    "ticker": ticker,
                                    "yes_price": true_yes_ask,
                                    "outcome": outcome
                                })
                    except Exception as ob_e:
                        continue # Skip if orderbook fails to load
            
            return parsed_results

    except Exception as e:
        print(f"Kalshi API Error: {e}")
        return []
