
# Single ticker
#ticker = yf.Ticker("AAPL")
#
## Historical daily prices
#hist = ticker.history(period="1y")
#print(hist)

# Intraday 1-minute data (last 7 days)
#intraday = ticker.history(period="1h", interval="10m")
#print(intraday)
# Options chain
#options = ticker.options          # list of expiration dates
#opt_chain = ticker.option_chain(options[0])  # calls and puts

#print(opt_chain)

#https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?period1=1756155600&period2=1756674000&interval=1m&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&source=cosaic

#Regular request:
##https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={epoc start}&period2={epoc end}&interval={}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&source=cosaic

#intervals: 1m

#news
#https://finance.yahoo.com/xhr/ncp?location=US&queryRef=qsp&serviceKey=ncp_fin&symbols=BTC-USD&lang=en-US&region=US

import requests
import time
import asyncio
import aiohttp
import json

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

class requestObj:
    ticker: str
    url: str
    header: dict


#bad query
#https://query1.finance.yahoo.com/v7/finance/quote?&symbols=TMC,TRU,TSLA,TSMC34.SA,USAR,^DJI,^GSPC,^IXIC,^RUT,^SPX,^TNX,^VIX&fields=currency,fromCurrency,toCurrency,exchangeTimezoneName,exchangeTimezoneShortName,gmtOffSetMilliseconds,regularMarketChange,regularMarketChangePercent,regularMarketPrice,regularMarketTime,preMarketChange,preMarketChangePercent,preMarketPrice,preMarketTime,priceHint,postMarketChange,postMarketChangePercent,postMarketPrice,postMarketTime,extendedMarketChange,extendedMarketChangePercent,extendedMarketPrice,extendedMarketTime,overnightMarketChange,overnightMarketChangePercent,overnightMarketPrice,overnightMarketTime&crumb=68UqqEeOU6K&formatted=false&region=US&lang=en-US
# good query
#https://query1.finance.yahoo.com/v7/finance/spark?symbols=FICO%2CSRPT%2CRGTI%2CUSAR%2CTRU%2CRIVN%2CEFX%2COXY%2CARX%2COPEN%2CPLUG%2CQBTS&range=1d&interval=5m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance

async def fetch(session, req):
    try:
        async with session.get(req.url, headers=req.header) as response:
            response.raise_for_status()
            data = await response.json()
            return {"ticker": req.ticker, "data": data}
    except Exception as e:
        return {"ticker": req.ticker, "error": str(e), "url": req.url}

async def batchFetch(session, reqs):
    tasks = [fetch(session, req) for req in reqs]
    return await asyncio.gather(*tasks)


# Semaphore to limit concurrency
#sem = asyncio.Semaphore(session, maxConcurrent)

#async def safe_fetch(req):
#    async with sem:
#        return await fetch(session, req)
#

async def tickerStream(tickers, timeOffset=260, interval="1m", batchSize=20):
    epocStart = int(time.time()) - timeOffset
    epocEnd = int(time.time())
    requests: requestObj = []
    
    #generate urls
    for ticker in tickers:
        #url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        req = requestObj()
        req.ticker = ticker
        req.url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={epocStart}&period2={epocEnd}&interval={interval}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&source=cosaic"
        
        headers = {
            "User-Agent": "Mozilla/5.0",  # Yahoo sometimes blocks default Python requests
            "Accept": "application/json" #chatgpt reccomendation
        }   

        req.header = headers

        requests.append(req)
        

    #chunking
    reqBatches = batch_list(requests, batchSize)
    for batch in reqBatches:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, req) for req in batch]
            results = await asyncio.gather(*tasks)

        for r in results:
            if "error" in r:
                print(f" error for {r['ticker']} ({r['url']}): {r['error']}")
            else:
                try:
                    closes = r["data"]["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                    print(f"{r['ticker']} closes: {closes[-5:]}")
                except Exception as e:
                    print(f"Parse error for {r['ticker']}: {e}")

    #for each batch of 20, 
    #for batch in reqBatches:
    #    async with aiohttp.ClientSession() as session:
    #        tasks = [fetch(session, req.url, req.header) for req in batch]
#
    #        results = await asyncio.gather(*tasks)
    #        for i, r in enumerate(results):
    #                try:
    #                    closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    #                    print(f"{req.ticker} Result {i+1} closes: {closes[-5:]}")  # last 5 closes
    #                except Exception as e:
    #                    print(f"Error parsing {req.ticker}, result {i+1}: {e}")
    #    #sleep 10 seconds
    #    time.sleep(10)


def batch_list(data, chunk_size):
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


async def __main__():
    #while True: 
       # time.sleep(60)
    await (tickerStream((large_caps + sp500_names + etfs + cryptos + international)))


if __name__ == "__main__":
    asyncio.run(__main__())