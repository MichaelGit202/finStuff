
#Single Ticker Scraper Script
import requests
import time
import asyncio
import aiohttp
import json
import sys


interval = sys.argv[0]


class requestObj:
    ticker: str
    url: str
    header: dict



def readTickers(): 
    with open("tickers.txt") as file:
         return [t.strip() for t in file.read().split(',')]
        


# function to fetch an already built request with the request object
async def fetch(session, req: requestObj):
    try:
        async with session.get(req.url, headers=req.header) as response:
            response.raise_for_status()
            data = await response.json()
            return {"ticker": req.ticker, "data": data}
    except Exception as e:
        return {"ticker": req.ticker, "error": str(e), "url": req.url}






# likely going to have to re-write this to implement better batching
async def tickerStream(tickers, timeOffset=260, interval="1m", batchSize=20):
    epocStart = int(time.time()) - timeOffset
    epocEnd = int(time.time())
    requests: requestObj = []
    
    #generate urls
    for ticker in tickers:
        req = requestObj()
        req.ticker = ticker
        req.url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={epocStart}&period2={epocEnd}&interval={interval}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&source=cosaic"
        
        headers = {
            "User-Agent": "Mozilla/5.0",  # Yahoo sometimes blocks default Python requests
            "Accept": "application/json" #chatgpt recomendation
        }   

        req.header = headers
        requests.append(req)
        
    quotes = []
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
                    #closes = r["data"]["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                    #print(f"{r['ticker']} closes: {closes[-5:]}")
                    print(r)
                    quotes.append(r)
                except Exception as e:
                    print(f"Parse error for {r['ticker']}: {e}")

    return quotes

   # https://query2.finance.yahoo.com/v8/finance/chart/FIG?period1=1753968600&period2=1757354400&interval=1wk&includePrePost=true&events=div|split|earn&lang=en-US&region=US&source=cosaic



def batch_list(data, chunk_size):
    return[data[i:i +  chunk_size] for i in range(0, len(data), chunk_size)]


def generate_HiLoPeriod_report(quotes):
    for q in quotes: 
        closes = q["data"]["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        highest = max(closes)
        initial_price = closes[0]
        final_price = closes[len(closes) - 1]
        quot_times =  q["data"]["chart"]["result"][0]["indicators"]["timestamp"]
        quote_time_start = quot_times[0]
        quote_time_start = quot_times[len(quot_times) - 1]
        




async def __main__():
    #tickers = readTickers()
    tickers = ['aapl']
    quotes = await (tickerStream(tickers=tickers)) 





if __name__ == "__main__":
    asyncio.run(__main__())