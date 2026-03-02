import json
import finlib.ohlcv as ohlcv
from enum import Enum
try:
    import pysimdjson as simdjson
    _HAS_SIMDJSON = True
    # prefer simdjson.loads if available, otherwise create a Parser
    _SIMD_LOADS = getattr(simdjson, 'loads', None)
    _SIMD_PARSER = None if _SIMD_LOADS else simdjson.Parser()
except Exception:
    _HAS_SIMDJSON = False
    _SIMD_LOADS = None
    _SIMD_PARSER = None



#general json data structure
#time series data [
    # typical OHLCV data + time stamp
#]

# the part of me that is thinking too fat ahead thinks:
# #TODO support parralell / non-linear data streams, ie a sequential time series data + news data
    # - news data is slower than market data

# im just gona focus on the pure OHLCV data for now

class Action(Enum):
    BUY = 0
    SELL = 1
    BUY_ALL = 2
    SELL_ALL = 3
    ADD_CASH = 4
    REMOVE_CASH = 5


class stock_simulator:


    # init that assumes the data is in one file
    def __init__(self, file_path: str, start_step: int = 0, chunk_size: int = 1000, initial_money: float = 1000.0):
        self.file_path = str(file_path)
        self.current_step = start_step
        self.data = None
        self.chunkSize = int(chunk_size)
        self.cash = initial_money
        self.agregate_added_cash = initial_money

        self.shares = 0.0 # invested money in terms of shares
        self._chunk_pos = 0
        self._fh = None
        self._mode = None  # 'ndjson' or 'array'
        self._eof = False
        self._eoc = True
        self.current_ohlcv = ohlcv.ohlcv()   #The current OHLCV datapoint 

        self.order_history = []  # list of actions taken, e.g. {"step": 10, "action": "buy", "amount": 100.0}
        self.active_orders = []
        

        self.equity_growth = 0.0 # this is the equity growth of this single stock, this is to track growth over time
                           # even if the user pulled it all out then put it back in. 

    def __del__(self):
        try:
            if self._fh:
                self._fh.close()
        except Exception:
            pass

    def _open_if_needed(self):
        if self._fh is not None:
            return
        self._fh = open(self.file_path, 'r', encoding='utf-8')
        # detect format by peeking first non-whitespace char
        while True:
            c = self._fh.read(1)
            if not c:
                break
            if not c.isspace():
                if c == '[':
                    self._mode = 'array'
                elif c == '{':
                    # top-level object; try to find the first array inside it and stream that
                    # scan forward until we hit a '[' that is not inside a string
                    in_string = False
                    escape = False
                    while True:
                        d = self._fh.read(1)
                        if not d:
                            break
                        if in_string:
                            if escape:
                                escape = False
                            elif d == '\\':
                                escape = True
                            elif d == '"':
                                in_string = False
                            continue
                        else:
                            if d == '"':
                                in_string = True
                                continue
                            if d == '[':
                                self._mode = 'array'
                                # file pointer is just after the '[' ready to read first element
                                break
                    # if we didn't find an array, treat as ndjson fallback
                    if self._mode != 'array':
                        self._mode = 'ndjson'
                else:
                    self._mode = 'ndjson'
                break
        # if we decided it's ndjson, rewind to start so reading lines works
        if self._mode == 'ndjson':
            self._fh.seek(0)

    def _parse_json(self, s: str):
        if _HAS_SIMDJSON:
            try:
                if _SIMD_LOADS:
                    return _SIMD_LOADS(s)
                else:
                    # Parser.parse accepts bytes or str depending on binding
                    return _SIMD_PARSER.parse(s)
            except Exception:
                return json.loads(s)
        else:
            return json.loads(s)


    def _read_next_array_item(self):
        fh = self._fh
        buf = []
        in_string = False
        escape = False
        depth = None  # None = not seen container yet, 0 = primitive
        started = False

        while True:
            c = fh.read(1)
            if not c:
                # EOF
                if not buf:
                    self._eof = True
                    return None
                break

            if not started:
                if c.isspace() or c == ',':
                    continue
                if c == ']':
                    self._eof = True
                    return None
                started = True
                buf.append(c)
                if c == '"':
                    in_string = True
                    depth = 0
                elif c == '{' or c == '[':
                    depth = 1
                else:
                    depth = 0
                continue

            buf.append(c)

            if in_string:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_string = False
                continue

            # not in string
            if c == '"':
                in_string = True
            elif c == '{' or c == '[':
                if depth is None:
                    depth = 1
                else:
                    depth += 1
            elif c == '}' or c == ']':
                if depth is None:
                    depth = 0
                elif depth > 0:
                    depth -= 1
                # if we've closed the top-level container and depth is 0, item done
                if depth == 0:
                    # consume any whitespace after the value, and optionally a comma or closing bracket
                    # but we already consumed the closing brace/bracket
                    break
            elif depth == 0 and (c == ',' or c == ']'):
                # primitive ended; remove delimiter from buffer
                buf.pop()
                if c == ']':
                    self._eof = True
                break

        s = ''.join(buf).strip()
        if not s:
            return None
        return self._parse_json(s)

    def load_chunk(self):
        self._open_if_needed()
        if self._eof:
            return []

        items = []
        if self._mode == 'ndjson':
            while len(items) < self.chunkSize:
                line = self._fh.readline()
                if not line:
                    self._eof = True
                    break
                line = line.strip()
                if not line:
                    continue
                items.append(self._parse_json(line))
        else:  # array mode
            while len(items) < self.chunkSize:
                it = self._read_next_array_item()
                if it is None:
                    break
                items.append(it)
            # do not advance `current_step` here; it should reflect how many items
            # have been yielded by `step()` (global position). Reset chunk position.
            self._chunk_pos = 0
            self.data = items
        return items

    def add_cash(self, amount: float):
        if amount <= 0:
            raise ValueError("Added cash amount must be positive")
        self.cash += amount
        self.agregate_added_cash += amount
        action = {"step": self.current_step, "action": Action.ADD_CASH, "amount": amount, "price": self.current_ohlcv.close, "shares": 0}
        self.order_history.append(action)

    def remove_cash(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Removed cash amount must be positive")
        if amount > self.cash:
            raise ValueError("Insufficient cash to remove")
        self.cash -= amount
        self.agregate_added_cash -= amount
        action = {"step": self.current_step, "action": Action.REMOVE_CASH, "amount": amount, "price": self.current_ohlcv.close, "shares": 0}
        self.order_history.append(action)   
        return amount

    #buy and sell all lol
    def buy_all(self):
        self.shares += self.cash/self.current_ohlcv.close  # convert cash to shares at current price
        self.cash = 0

        action = {"step": self.current_step, "action": Action.BUY_ALL, "amount": self.cash, "price": self.current_ohlcv.close, "shares": self.shares}
        self.order_history.append(action)
        self.active_orders.append(action)

    def sell_all(self):
        total_sold = 0 

        for order in self.active_orders:
            total_sold += self.current_ohlcv.close * order["shares"]
        self.active_orders = []
        
        self.shares = 0
        action = {"step": self.current_step, "action": Action.SELL_ALL, "amount": total_sold, "price": self.current_ohlcv.close, "shares": self.shares}
        self.cash += total_sold
        self.order_history.append(action)
   
    

    def buy(self, amount: float):
        cash = self.cash
        if amount > cash:
            raise ValueError("Insufficient cash to buy")
        elif amount <= 0:
            raise ValueError("Buy amount must be positive")
        else:
            self.cash -= amount
            self.shares += amount/self.current_ohlcv.close  # convert cash to shares at current price

            action = {"step": self.current_step, "action": Action.BUY, "amount": amount, "price": self.current_ohlcv.close, "shares": amount/self.current_ohlcv.close}
            self.order_history.append(action)
            self.active_orders.append(action)
           

    def sell_shares(self, amount: float):
        if amount > self.shares:
            raise ValueError("Insufficient shares to sell")
        elif amount <= 0:
            raise ValueError("Sell amount must be positive")
        else:
            self.shares -= amount
            self.cash += amount * self.current_ohlcv.close  # convert shares to cash at current price
            action = {"step": self.current_step, "action": Action.SELL, "amount": amount * self.current_ohlcv.close, "price": self.current_ohlcv.close, "shares": amount}
            self.order_history.append(action)
            

    def sell_equity(self, amount: float):
        if amount > self.shares * self.current_ohlcv.close:
            raise ValueError("Insufficient equity to sell")
        elif amount <= 0:
            raise ValueError("Sell amount must be positive")
        else:
            self.shares -= (amount / self.current_ohlcv.close)
            self.cash += amount 
            action = {"step": self.current_step, "action": Action.SELL, "amount": amount, "price": self.current_ohlcv.close, "shares": amount / self.current_ohlcv.close}
            self.order_history.append(action)
            
    
    #ammount in terms of cash
    def _sell_shares_from_active_orders(self, amount: float):
        total_sold = 0.0
        shares_to_sell = amount / self.current_ohlcv.close

        if shares_to_sell > self.shares:
            raise ValueError("Insufficient shares to sell")

        for order in self.active_orders:
            if shares_to_sell <= 0:
                break
            if order["shares"] <= shares_to_sell:
                total_sold += order["shares"] * self.current_ohlcv.close
                shares_to_sell -= order["shares"]
                self.active_orders.remove(order)
            else:
                total_sold += shares_to_sell * self.current_ohlcv.close
                order["shares"] -= shares_to_sell
                shares_to_sell = 0

        self.shares -= shares_to_sell
        self.cash += total_sold



    #Idk if this is wrong, but total gains is equal to the difference
    # between the sum of the sell prices and the sum of the buy prices, assuming we are always buying and selling the same amount of shares.
    #def get_returns(self) -> float:
    #    if self.buyPrices == []:
    #        return 0.0
    #    total_invested = sum(self.sellPrices - self.buyPrices)

    def get_equity(self) -> float: 
        return self.shares * self.current_ohlcv.close
    
    def get_shares(self) -> float:  
        return self.shares
    
    def get_cash(self) -> float:    
        return self.cash
    
    def get_portfolio_value(self) -> float:
        return {"cash": self.get_cash(), "equity": self.get_equity()}

    def step(self) -> ohlcv.ohlcv : 
        # Return the next item (as a single-element list for compatibility)
        # Load a new chunk when current chunk is exhausted.

        self._calculate_equity_growth()

        if self._eof and (not self.data or self._chunk_pos >= len(self.data)):
            return None

        if not self.data or self._chunk_pos >= len(self.data):
            items = self.load_chunk()
            if not items:
                return None

        # return next record
        self.current_ohlcv = ohlcv.ohlcv(self.data[self._chunk_pos])
        self._chunk_pos += 1
        self.current_step += 1

        # if this chunk is now exhausted, mark end-of-chunk for caller
        if self._chunk_pos >= len(self.data):
            self._eoc = True

        return self.current_ohlcv

    #TODO: calling this every step is slow
    def _calculate_equity_growth(self):
        self.equity_growth = 0.0

        for order in self.active_orders:
            self.equity_growth += (self.current_ohlcv.close - order["price"]) * order["shares"]

    def get_returns(self) -> float:
        return self.get_equity() + self.get_cash() - self.agregate_added_cash
    
    def get_returns_percentage(self) -> float:
        if self.agregate_added_cash == 0:
            return 0.0
        return (self.get_returns() / self.agregate_added_cash) * 100
    
    def get_raw_cash_investment(self) -> float:
        return self.agregate_added_cash
    
