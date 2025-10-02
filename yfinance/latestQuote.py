import asyncio
import aiohttp
import json
import os
import requests


#https://query1.finance.yahoo.com/v7/finance/quote?&symbols=TRU,TSLA,TSMC34.SA,USAR,^DJI,^GSPC,^IXIC,^RUT,^SPX,^TNX,^VIX&fields=currency,fromCurrency,toCurrency,exchangeTimezoneName,exchangeTimezoneShortName,gmtOffSetMilliseconds,regularMarketChange,regularMarketChangePercent,regularMarketPrice,regularMarketTime,preMarketChange,preMarketChangePercent,preMarketPrice,preMarketTime,priceHint,postMarketChange,postMarketChangePercent,postMarketPrice,postMarketTime,extendedMarketChange,extendedMarketChangePercent,extendedMarketPrice,extendedMarketTime,overnightMarketChange,overnightMarketChangePercent,overnightMarketPrice,overnightMarketTime&crumb=68UqqEeOU6K&formatted=false&region=US&lang=en-US

#https://query1.finance.yahoo.com/v7/finance/quote?fields=regularMarketChangePercent,regularMarketTime,regularMarketChange,regularMarketPrice,regularMarketVolume&formatted=true&imgHeights=50&imgLabels=logoUrl&imgWidths=50&symbols=^GSPC,ADP,^SPX,NRG,VST,META,GOOG,RDDT,GOOGL,INTC,AMD,PTON,AAPL,F,PFE,WMT,GIS,KHC,CL=F,APO,VZ,NRDS,IONQ,GORV,CPRT,DOCU,CTVA,^DJI,DX-Y.NYB,JPY=X&enablePrivateCompany=true&overnightPrice=true&lang=en-US&region=US&crumb=68UqqEeOU6K

#bad query
#https://query1.finance.yahoo.com/v7/finance/quote?&symbols=TMC,TRU,TSLA,TSMC34.SA,USAR,^DJI,^GSPC,^IXIC,^RUT,^SPX,^TNX,^VIX&fields=currency,fromCurrency,toCurrency,exchangeTimezoneName,exchangeTimezoneShortName,gmtOffSetMilliseconds,regularMarketChange,regularMarketChangePercent,regularMarketPrice,regularMarketTime,preMarketChange,preMarketChangePercent,preMarketPrice,preMarketTime,priceHint,postMarketChange,postMarketChangePercent,postMarketPrice,postMarketTime,extendedMarketChange,extendedMarketChangePercent,extendedMarketPrice,extendedMarketTime,overnightMarketChange,overnightMarketChangePercent,overnightMarketPrice,overnightMarketTime&crumb=68UqqEeOU6K&formatted=false&region=US&lang=en-US
# good query
#https://query1.finance.yahoo.com/v7/finance/spark?symbols=FICO%2CSRPT%2CRGTI%2CUSAR%2CTRU%2CRIVN%2CEFX%2COXY%2CARX%2COPEN%2CPLUG%2CQBTS&range=1d&interval=5m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance
#https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={epocStart}&period2={epocEnd}&interval={interval}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&source=cosaic

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


def save_quote(quote:dict, path:str="latestQuote.json"):
    """Save the latest quote data to a JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(quote, fh, indent=2)
        print(f"Saved latest quote to {path}")
    except Exception as e:
        print(f"Failed to save quote: {e}")



def test_quote():
    """Fetch snapshot quotes for multiple tickers in one request."""
    #symbols = ",".join(tickers)
    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL,TSLA&crumb=68UqqEeOU6K"
    
    cookies = load_cookies()
    print(f"loaded {len(cookies)} cookies")
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    resp = requests.get(url, headers=headers, cookies=cookies)
    data = resp.json()

    print(data)
    return data
    #for r in data["quoteResponse"]["result"]:
     #   print(f"{r['symbol']}: {r['regularMarketPrice']} ({r['regularMarketChangePercent']}%)")



async def fetch_quotes(tickers):
    symbols = ",".join(tickers)
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"
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
    tickers = ["AAPL", "MSFT", "TSLA", "BTC-USD", "ETH-USD"]
    results = await fetch_quotes(tickers)

    for r in results:
        print(f"{r['symbol']}: {r['regularMarketPrice']} (change {r['regularMarketChangePercent']}%)")

if __name__ == "__main__":
    #asyncio.run(__main__())
    data = test_quote()
    save_quote(data)

