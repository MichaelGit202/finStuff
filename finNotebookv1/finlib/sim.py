import finlib.data_stream as data_stream
import finlib.ohlcv as ohlcv
from enum import Enum
import pandas as pd

#general json data structure
#time series data [
    # typical OHLCV data + time stamp
#]

# the part of me that is thinking too fat ahead thinks:
# #TODO support parralell / non-linear data streams, ie a sequential time series data + news data
    # - news data is slower than market data'
 # TODO implement async data streams for reading to pre-load chunk data for speed

 # TODO refactor all the data stuff, everything should probably just turn into a pandas dataframe
 # TODO calculate visuals

class Action(Enum):
    BUY = 0
    SELL = 1
    BUY_ALL = 2
    SELL_ALL = 3
    ADD_CASH = 4
    REMOVE_CASH = 5


class stock_simulator:


    # init that assumes the data is in one file
    def __init__(self, file_path: str, stream_type, start_step: int = 0, chunk_size: int = 1000, initial_money: float = 1000.0, symbol: str = "no_symbol"):
        
        
        self.current_step = start_step
        self.cash = initial_money
        self.agregate_added_cash = initial_money
        self.shares = 0.0
        self.current_ohlcv = ohlcv.ohlcv()
        self.order_history = []
        self.active_orders = []
        self.equity_growth = 0.0
        self.percent_growth = 0.0


        self.data_stream = data_stream.data_stream(file_path, stream_type, chunk_size)
        self._eof = False
        self._current_chunk = []
        self._chunk_pos = 0
        self.stream_type = stream_type
        self.symbol = symbol

    def __del__(self):
        try:
            del self.data_stream
        except Exception:
            pass
    
    #############################################################
    #                      Utility functions                    #
    #############################################################

    # Getting new data from whatever datasetream we are using
    # TODO refactor
    def _get_next_entry(self):
            # If current chunk is exhausted, load a new chunk

            if isinstance(self._current_chunk, pd.DataFrame):
                chunk_len = self._current_chunk.shape[0]
            else:
                chunk_len = len(self._current_chunk)

            if self._chunk_pos >= chunk_len:
                self._current_chunk = self.data_stream.read_chunk()
                self._chunk_pos = 0
                # Check for empty chunk
                if self._current_chunk is None:
                    self._eof = True
                    return None
                if isinstance(self._current_chunk, pd.DataFrame):
                    if self._current_chunk.empty:
                        self._eof = True
                        return None
                elif hasattr(self._current_chunk, 'empty'):
                    if self._current_chunk.empty:
                        self._eof = True
                        return None
                elif isinstance(self._current_chunk, (list, dict)):
                    if not self._current_chunk:
                        self._eof = True
                        return None

            # Get next entry
            if isinstance(self._current_chunk, pd.DataFrame):
                entry = self._current_chunk.iloc[self._chunk_pos]
            else:
                entry = self._current_chunk[self._chunk_pos]
            self._chunk_pos += 1
            return entry
     
    
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

    #TODO: calling this every step is slow
    def _calculate_equity_growth(self):
        self.equity_growth = 0.0
        self.percent_growth = 0.0
        for order in self.active_orders:
            self.equity_growth += (self.current_ohlcv.close - order["price"]) * order["shares"]

        if self.agregate_added_cash > 0:
            self.percent_growth = (self.equity_growth / self.agregate_added_cash) * 100



    # Jank ass helper function which basically helps me fuck around with the data without having to
    # put the data in a stanard form, instead store that logic in here, This is bad. I should instead be
    # re-shaping the data and putting that in a database in standard form, instead we have this
    def _convert_to_ohlcv(self, data) -> ohlcv.ohlcv:
        # This function should convert the entry to an ohlcv object, depending on the stream type
        if self.stream_type == "pandas_csv":
            entry_dict = data.to_dict()  # Convert Series to dict
            new_dict = {}

            # the magic strings that will be grabbing the data
            new_dict["timestamp"] = entry_dict.get("Date", None)
            new_dict["open"] = entry_dict.get("Open", None) 
            new_dict["high"] = entry_dict.get("High", None)
            new_dict["low"] = entry_dict.get("Low", None)
            new_dict["close"] = entry_dict.get("Close", None)
            new_dict["volume"] = entry_dict.get("Volume", None)

            if None in new_dict.values():
                raise ValueError("Missing OHLCV data in entry: {}".format(entry_dict))
            
            return ohlcv.ohlcv(new_dict)
        elif self.stream_type == "json":
            return ohlcv.ohlcv(data)
        else:
            raise ValueError("Unsupported stream type")



    #############################################################
    #                Cash and Equity management                 #
    #############################################################

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
            
    

    #############################################################
    #                       Get Functions                       #
    #############################################################


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


    def get_returns(self) -> float:
        return self.get_equity() + self.get_cash() - self.agregate_added_cash
    
    def get_returns_percentage(self) -> float:
        if self.agregate_added_cash == 0:
            return 0.0
        return (self.get_returns() / self.agregate_added_cash) * 100
    
    def get_raw_cash_investment(self) -> float:
        return self.agregate_added_cash
    



    #############################################################
    #                       Step Functions                      #
    #############################################################

  
    def step(self) -> ohlcv.ohlcv:
        self._calculate_equity_growth()
        entry = self._get_next_entry()

        # Handle pandas DataFrame and other types
        if entry is None:
            return None
        if isinstance(entry, pd.DataFrame):
            if entry.empty:
                return None
        elif hasattr(entry, 'empty'):    # we return none once the data runs out
            if entry.empty:
                return None
        elif isinstance(entry, (list, dict)):
            if not entry:
                return None
        self.current_ohlcv = self._convert_to_ohlcv(entry)
        self.current_step += 1
        return self.current_ohlcv