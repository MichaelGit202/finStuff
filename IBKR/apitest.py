import asyncio
import math
import os
from ib_async import IB, Stock
from ib_async.ib import StartupFetch


def get_wsl_default_gateway_ip() -> str | None:
    """Return default gateway IP from WSL routing table (usually Windows host)."""
    try:
        with open('/proc/net/route', 'r', encoding='utf-8') as f:
            next(f, None)  # skip header
            for line in f:
                fields = line.strip().split()
                if len(fields) < 3:
                    continue
                destination_hex = fields[1]
                gateway_hex = fields[2]
                if destination_hex != '00000000':
                    continue
                raw = bytes.fromhex(gateway_hex)
                return '.'.join(str(b) for b in raw[::-1])
    except OSError:
        return None
    return None


def get_wsl_resolver_ip() -> str | None:
    """Return resolver nameserver IP from WSL, sometimes usable as host."""
    try:
        with open('/etc/resolv.conf', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2 and parts[0] == 'nameserver':
                    return parts[1]
    except OSError:
        return None
    return None

async def main():
    ib = IB()
    
    # Using clientId=99 to completely bypass any connections jammed by Jupyter
    client_id = int(os.getenv('IB_CLIENT_ID', '107'))
    preferred_port = int(os.getenv('IB_PORT', '4001'))
    market_data_type = int(os.getenv('IB_MKT_DATA_TYPE', '1'))
    preferred_host = os.getenv('IB_HOST', '127.0.0.1')
    host_candidates = [preferred_host]
    wsl_gateway = get_wsl_default_gateway_ip()
    if wsl_gateway and wsl_gateway not in host_candidates:
        host_candidates.append(wsl_gateway)

    wsl_resolver = get_wsl_resolver_ip()
    if wsl_resolver and wsl_resolver not in host_candidates:
        host_candidates.append(wsl_resolver)

    candidate_ports = [preferred_port, 4002, 4001, 7497, 7496]
    seen = set()
    candidate_ports = [p for p in candidate_ports if not (p in seen or seen.add(p))]
    
    try:
        print(f"Trying IB API hosts {host_candidates} with Client ID: {client_id}")

        connected_host = None
        connected_port = None
        for host in host_candidates:
            for port in candidate_ports:
                try:
                    print(f"- Attempting {host}:{port} ...")
                    await ib.connectAsync(
                        host,
                        port,
                        clientId=client_id,
                        timeout=6,
                        readonly=True,
                        fetchFields=StartupFetch(0),
                    )
                    if ib.isConnected():
                        connected_host = host
                        connected_port = port
                        break
                except Exception as e:
                    print(f"  Failed on {host}:{port}: {e}")
            if connected_port is not None:
                break

        if connected_port is None:
            raise ConnectionError(
                "Unable to connect to IB API on hosts/ports "
                f"{host_candidates} x {candidate_ports}. Check Gateway/TWS is running, API is enabled, "
                "and trusted localhost connection is allowed."
            )

        print(f"Connected successfully on {connected_host}:{connected_port}!")
        
        # 1=live, 2=frozen, 3=delayed, 4=delayed-frozen
        ib.reqMarketDataType(market_data_type)
        
        # Set up Apple contract on SMART routing
        contract = Stock('AAPL', 'SMART', 'USD')
        print("Qualifying contract details...")
        await ib.qualifyContractsAsync(contract)
        
        # Request the streaming ticker handle
        ticker = ib.reqMktData(contract)
        print("\nStreaming pipeline open. Press Ctrl+C to terminate connection.\n")
        switched_to_delayed = False
        empty_ticks = 0

        def valid(v):
            return v is not None and not (isinstance(v, float) and math.isnan(v))

        def first_valid(*values):
            for v in values:
                if valid(v):
                    return v
            return math.nan
        
        # Continuous loop to monitor the streaming object updates
        while True:
            # CRUCIAL: You must use asyncio.sleep() so the background engine 
            # can breathe and capture incoming network packets from the socket.
            await asyncio.sleep(1)

            last = ticker.last
            market = ticker.marketPrice()
            close = ticker.close
            delayed_bid = getattr(ticker, 'delayedBid', math.nan)
            delayed_ask = getattr(ticker, 'delayedAsk', math.nan)
            delayed_last = getattr(ticker, 'delayedLast', math.nan)
            delayed_close = getattr(ticker, 'delayedClose', math.nan)

            if not valid(last) and not valid(market) and not valid(close):
                empty_ticks += 1
            else:
                empty_ticks = 0

            # Auto-fallback when real-time entitlement is missing.
            if not switched_to_delayed and market_data_type == 1 and empty_ticks >= 5:
                print("No real-time prices received. Switching to delayed market data (type=3).")
                ib.reqMarketDataType(3)
                ib.cancelMktData(contract)
                ticker = ib.reqMktData(contract)
                switched_to_delayed = True
                empty_ticks = 0

            bid_out = first_valid(ticker.bid, delayed_bid)
            ask_out = first_valid(ticker.ask, delayed_ask)
            display_price = first_valid(last, market, close, delayed_last, delayed_close)
            print(
                f"AAPL (SMART) -> Bid: {bid_out} | Ask: {ask_out} | "
                f"Last: {ticker.last} | DelayedLast: {delayed_last} | Px: {display_price}"
            )
            
    except asyncio.CancelledError:
        print("\nStream cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Disconnecting socket safely...")
        ib.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")