"""Share prices from the Massive market data API, or a simulator when no key is set.

Set MASSIVE_API_KEY to use live data. Without it, prices come from market_simulator
so the whole trading floor still runs out of the box.
"""

import os
from dotenv import load_dotenv
from massive import RESTClient
from .market_simulator import simulated_price

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
    """Return the current price for a symbol, from Massive or the simulator."""
    global massive_unavailable
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


def is_market_open() -> bool:
    """Whether the US market is open; True on simulated data or if Massive is unreachable."""
    if not massive_api_key or massive_unavailable:
        return True
    try:
        client = RESTClient(massive_api_key)
        return client.get_market_status().market == "open"
    except Exception:
        return True
