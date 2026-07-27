"""Share prices from multiple markets: US (Massive API) and India (yfinance).

Set MASSIVE_API_KEY to use live US data. Without it, prices come from market_simulator
so the whole trading floor still runs out of the box.

Indian stocks (.NS/.BO suffix) use yfinance for live data.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import pytz
from massive import RESTClient
from .market_simulator import simulated_price
from .market_india import (
    is_indian_stock,
    get_indian_share_price,
    get_indian_market_status,
    INDIAN_SUFFIXES,
)

load_dotenv(override=True)

massive_api_key = os.getenv("MASSIVE_API_KEY")
# Once the live provider has failed, keep using the simulator for this process.
# Repeating the same network request for every holding only creates noisy logs
# and slows down account rendering.
massive_unavailable = False


def _last_trade(client: RESTClient, symbol: str) -> float:
    return float(client.get_last_trade(symbol).price)


def _snapshot(client: RESTClient, symbol: str) -> float:
    snapshot = client.get_snapshot_ticker("stocks", symbol)
    return float(snapshot.min.close or snapshot.prev_day.close)


def _previous_close(client: RESTClient, symbol: str) -> float:
    return float(client.get_previous_close_agg(symbol)[0].close)


# Best price first, prior close last. Lower tier plans reject the earlier calls,
# so we remember the first tier that works and start there next time.
price_methods = [_last_trade, _snapshot, _previous_close]
plan_tier = 0


def get_share_price(symbol: str) -> float:
    """
    Return the current price for a symbol.
    
    Supports:
    - US stocks: AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA
    - Indian stocks (NSE): RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS
    - Indian stocks (BSE): RELIANCE.BO, TCS.BO, INFY.BO
    """
    global massive_unavailable
    
    # Check for Indian stocks first
    if is_indian_stock(symbol):
        try:
            return get_indian_share_price(symbol)
        except Exception as e:
            print(f"Indian market error for {symbol}: {e}")
            return 0.0
    
    # US market logic
    if massive_api_key and not massive_unavailable:
        try:
            return get_share_price_massive(symbol)
        except Exception as e:
            massive_unavailable = True
            print(f"Massive API unavailable ({e}); using a simulated price")
    return simulated_price(symbol)


def get_share_price_massive(symbol: str) -> float:
    """Best price the plan allows, remembering the working tier to avoid repeat failures."""
    global plan_tier
    client = RESTClient(massive_api_key)
    for tier in range(plan_tier, len(price_methods)):
        try:
            price = price_methods[tier](client, symbol)
            plan_tier = tier
            return price
        except Exception:
            continue
    raise RuntimeError(f"No Massive price available for {symbol}")


def _is_us_market_open() -> bool:
    """US market hours: 9:30 AM - 4:00 PM ET, Monday-Friday."""
    try:
        et = pytz.timezone("US/Eastern")
        now = datetime.now(pytz.utc).astimezone(et)
        if now.weekday() >= 5:
            return False
        minutes = now.hour * 60 + now.minute
        return 9 * 60 + 30 <= minutes <= 16 * 60
    except Exception:
        return False


def is_market_open() -> bool:
    """Whether any supported market is open."""
    try:
        status = get_indian_market_status()
        if status["status"] == "open":
            return True
    except Exception:
        pass

    if massive_api_key and not massive_unavailable:
        try:
            client = RESTClient(massive_api_key)
            return client.get_market_status().market == "open"
        except Exception:
            pass

    return _is_us_market_open()


def get_supported_markets() -> dict:
    """Return information about supported markets"""
    return {
        "US": {
            "exchanges": ["NYSE", "NASDAQ", "AMEX"],
            "suffix": "",
            "currency": "USD",
            "data_source": "Massive API" if massive_api_key else "Simulator",
        },
        "India": {
            "exchanges": ["NSE", "BSE"],
            "suffix": ".NS / .BO",
            "currency": "INR",
            "data_source": "Yahoo Finance",
        },
    }
