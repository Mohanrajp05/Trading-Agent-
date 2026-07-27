"""Indian Stock Market (NSE/BSE) price data using yfinance.

Supports Indian stocks with .NS (NSE) or .BO (BSE) suffix.
Example: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Indian stock suffixes
INDIAN_SUFFIXES = ('.NS', '.BO', '.NSE', '.BSE')

# Popular Indian stocks for reference
INDIAN_STOCKS = {
    # NSE Stocks
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "ITC.NS": "ITC Limited",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "LT.NS": "Larsen & Toubro",
    "AXISBANK.NS": "Axis Bank",
    "BAJFINANCE.NS": "Bajaj Finance",
    "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharmaceutical",
    "TATAMOTORS.NS": "Tata Motors",
    "WIPRO.NS": "Wipro",
    "HCLTECH.NS": "HCL Technologies",
    "ADANIENT.NS": "Adani Enterprises",
    "TATASTEEL.NS": "Tata Steel",
    "NTPC.NS": "NTPC Limited",
    "POWERGRID.NS": "Power Grid Corporation",
    "ONGC.NS": "Oil and Natural Gas Corporation",
    "JSWSTEEL.NS": "JSW Steel",
    "TITAN.NS": "Titan Company",
    "ASIANPAINT.NS": "Asian Paints",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "NESTLEIND.NS": "Nestle India",
    "TECHM.NS": "Tech Mahindra",
    "DIVISLAB.NS": "Divi's Laboratories",
}

# Try to import yfinance
try:
    import yfinance as yf
    YAHOO_AVAILABLE = True
except ImportError:
    YAHOO_AVAILABLE = False
    print("WARNING: yfinance not installed. Run: uv add yfinance")


def is_indian_stock(symbol: str) -> bool:
    """Check if symbol is for Indian market"""
    return any(symbol.upper().endswith(suffix) for suffix in INDIAN_SUFFIXES)


def normalize_indian_symbol(symbol: str) -> str:
    """Normalize Indian stock symbol to Yahoo Finance format"""
    symbol = symbol.upper()
    
    # If already has valid suffix, return as-is
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        return symbol
    
    # If has .NSE or .BSE suffix, convert
    if symbol.endswith('.NSE'):
        return symbol[:-4] + '.NS'
    if symbol.endswith('.BSE'):
        return symbol[:-4] + '.BO'
    
    # Default to NSE (.NS)
    return symbol + '.NS'


def get_indian_share_price(symbol: str) -> float:
    """
    Get price for Indian stocks.
    
    Symbol format:
    - RELIANCE.NS or RELIANCE (for NSE stocks)
    - RELIANCE.BO (for BSE stocks)
    
    Returns price in INR (Indian Rupees)
    """
    if not YAHOO_AVAILABLE:
        raise RuntimeError(
            "yfinance not installed. Run 'uv add yfinance' to enable Indian market support"
        )
    
    # Normalize symbol
    yahoo_symbol = normalize_indian_symbol(symbol)
    
    try:
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period="1d")
        
        if data.empty:
            raise ValueError(f"No data found for {yahoo_symbol}. Check if market is open.")
        
        price = float(data['Close'].iloc[-1])
        
        if price <= 0:
            raise ValueError(f"Invalid price for {yahoo_symbol}")
        
        return price
        
    except Exception as e:
        raise RuntimeError(f"Failed to fetch price for {yahoo_symbol}: {str(e)}")


def get_indian_stock_info(symbol: str) -> dict:
    """Get detailed info about an Indian stock"""
    if not YAHOO_AVAILABLE:
        return {"error": "yfinance not installed"}
    
    yahoo_symbol = normalize_indian_symbol(symbol)
    
    try:
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info
        
        return {
            "symbol": yahoo_symbol,
            "name": info.get("longName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "currency": info.get("currency", "INR"),
            "exchange": info.get("exchange", "NSI"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_indian_market_status() -> dict:
    """Check if Indian market (NSE/BSE) is currently open"""
    from datetime import datetime
    
    now = datetime.now()
    
    # IST is UTC+5:30
    import pytz
    ist = pytz.timezone('Asia/Kolkata')
    ist_time = now.astimezone(ist)
    
    # Market hours: 9:15 AM to 3:30 PM IST, Mon-Fri
    day = ist_time.weekday()  # 0=Monday, 6=Sunday
    hour = ist_time.hour
    minute = ist_time.minute
    
    is_weekday = day < 5
    time_in_minutes = hour * 60 + minute
    market_open_time = 9 * 60 + 15  # 9:15 AM
    market_close_time = 16 * 60  # 4:00 PM
    
    is_open = is_weekday and market_open_time <= time_in_minutes <= market_close_time
    
    return {
        "market": "NSE/BSE",
        "status": "open" if is_open else "closed",
        "time": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "IST",
    }
