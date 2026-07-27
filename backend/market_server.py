from mcp.server.fastmcp import FastMCP
from .market import get_share_price, get_supported_markets
from .market_india import is_indian_stock, get_indian_stock_info, get_indian_market_status

mcp = FastMCP("market_server")


@mcp.tool()
async def lookup_share_price(symbol: str) -> float:
    """This tool provides the current price of the given stock symbol.
    
    Supports both US and Indian markets:
    
    US Stocks (no suffix needed):
    - AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA
    
    Indian Stocks (use .NS for NSE or .BO for BSE):
    - NSE: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS
    - BSE: RELIANCE.BO, TCS.BO, INFY.BO

    Args:
        symbol: the symbol of the stock (e.g., AAPL or RELIANCE.NS)
    """
    return get_share_price(symbol)


@mcp.tool()
async def lookup_indian_stock_info(symbol: str) -> str:
    """Get detailed information about an Indian stock.
    
    Args:
        symbol: Indian stock symbol (e.g., RELIANCE.NS, TCS.NS)
    """
    import json
    info = get_indian_stock_info(symbol)
    return json.dumps(info, indent=2)


@mcp.tool()
async def get_market_status() -> str:
    """Get the current status of all supported markets (US and India)."""
    import json
    
    status = {
        "US_Market": {"status": "check via Massive API"},
        "India_Market": get_indian_market_status(),
        "supported_markets": get_supported_markets(),
    }
    
    return json.dumps(status, indent=2)


if __name__ == "__main__":
    mcp.run(transport='stdio')
