import asyncio
import aiohttp
import json
import os

# Large Cap US Stocks
large_caps = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "PG", "UNH", "HD", "MA", "BAC", "PFE", "KO", "DIS", "NFLX"
]

# Other S&P 500 / Popular Stocks
sp500_names = [
    "INTC", "AMD", "ORCL", "IBM", "CSCO", "T", "VZ", "XOM", "CVX", "WMT",
    "COST", "NKE", "MCD", "SBUX", "BA", "GE", "CAT", "HON", "GS", "MS"
]

# ETFs / Index Funds
etfs = [
    "SPY", "QQQ", "DIA", "IWM", "VTI", "ARKK", "EEM", "GLD", "SLV", "USO"
]

# Cryptos
cryptos = [
    "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "ADA-USD",
    "XRP-USD", "LTC-USD", "AVAX-USD", "MATIC-USD", "DOT-USD"
]

# International / ADRs
international = [
    "BABA", "TSM", "NIO", "SHOP", "RIO", "SONY", "SAP", "TM", "HSBC", "BP"
]


def load_cookies(path: str = None) -> dict:
    """Load cookies from the exported Firefox/Chrome-style JSON file and
    return a simple dict mapping cookie-name -> cookie-value suitable for
    passing to `requests` (or `aiohttp` which accepts a dict of cookies).

    By default this looks for `yahooCookies.json` in the same directory as
    this file.
    """
    if path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "yahooCookies.json")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        print(f"cookie file not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"failed to parse cookie file: {e}")
        return {}

    cookies = {}
    # file is an array of cookie objects with 'name' and 'value' fields
    for c in raw:
        name = c.get("name")
        value = c.get("value")
        if name and value is not None:
            cookies[name] = value

    return cookies


async def fetch_quotes(tickers):
    symbols = ",".join(tickers)
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}&crumb=68UqqEeOU6K"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    cookies = load_cookies()

    async with aiohttp.ClientSession() as session:
        # aiohttp accepts a dict of cookies on the request
        try:
            async with session.get(url, headers=headers, cookies=cookies) as resp:
                data = await resp.json()
                # print a brief summary for debugging
                print(f"fetched quotes for: {symbols} (status={resp.status})")
                return data.get("quoteResponse", {}).get("result", [])
        except Exception as e:
            print(f"aiohttp request failed: {e}")
            return []


async def __main__():
    #tickers = ["AAPL", "MSFT", "TSLA", "BTC-USD", "ETH-USD"]
    tickers = international + large_caps + sp500_names + etfs + cryptos + international
    results = await fetch_quotes(tickers)

    for r in results:
        print(f"{r['symbol']}: {r['regularMarketPrice']} (change {r['regularMarketChangePercent']}%)")


if __name__ == "__main__":
    asyncio.run(__main__())

