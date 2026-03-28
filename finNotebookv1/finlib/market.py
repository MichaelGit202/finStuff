import finlib.sim as sim


# I think this is a command pattern? Basically this object holds a bunch of tickers and orcestrates a bunch of different sims
# The idea being mabey im running 2 different strategies on 2 differnt stocks or each on a stock, mabey later change the 
# Resolution, so one sim is running at daily and the other hourly, but all orcestrated the same
class Market:
    def __init__(self, initial_cash: float = 10000, symbols = []):
        # probably eventually have a date / time / seconds attribute to keep track of time and sync data
        self.market_step = 0
        self.symbols = symbols
        self.stocks = {}
        self.cash = initial_cash
        self.equity = 0.0

        #for how many rows we want to save to csv/db at a time
        _SAVE_CHUNK_SIZE = 1000
        chunk = []
        self._chunk_format() #TODO haha

        # TODO Fix this
        for symbol in symbols:
            self.stocks[symbol] = sim.stock_simulator(f"./data/stock_details_5_years_{symbol}.json", stream_type="json", chunk_size=100, initial_money=0.0, symbol=symbol)

        # TODO: fix this    
        for stock in self.stocks:
            self.stocks[stock].step() # step once to get the first price for each stock


    #############################################################
    #                  auto run functions                       #
    #############################################################

    def run(self, steps=-1):
        if steps == -1:
            #Run all steps until data runs out
            pass

        for _ in range(steps):
            self.step()


    def stop_signal(self):
        # we're all out of data or something really bad happened
        return False



    #############################################################
    #                  Query Functions                          #
    #############################################################

    def get_current_price(self, symbol):
        if symbol not in self.stocks:
            raise ValueError(f"Symbol {symbol} not found in market.")
        return self.stocks[symbol].current_ohlcv.close
    

    # function for getting a stocks history, means more when I get db setup and better datastream functions
    def query_stock_history(self, symbol):
        pass
    

    #############################################################
    #                  store performance data                   #
    #############################################################
    
    def _chunk_format(self):
        for stock in self.stocks + "full_port":
           self.chunk[stock] = []


    # called every timestep store the current price, equity growth, cash, shares for each stock
    def _track_performance(self):
        entry = {}
        portfolio_value = self.cash

        for stock in self.stocks:
            #some of this data is not neccisary to store
            entry[stock].appemd({"timestep": self.market_step, "OHLCV": self.stocks[stock].current_ohlcv, "equity_growth": self.stocks[stock].equity_growth, "cash": self.stocks[stock].cash, "shares": self.stocks[stock].shares, "portfolio_value": self.stocks[stock].get_portfolio_value()})
            portfolio_value += self.stocks[stock].get_portfolio_value()
            self.chunk.append(entry)
        
        
        if len(self.chunk) >= self._SAVE_CHUNK_SIZE:
            self._save_to_csv()
            self._chunk_format()
    

    def _save_to_csv(self):
        for stock in self.stocks:
            pass

    #############################################################
    #                  Facade methods for sim                   #
    #############################################################

    def step(self):
        # FYI returns each price of each step, can store this for visuals
        for stock in self.stocks:
            self.stock_prices[stock] = {"OHLCV": self.stocks[stock].current_ohlcv, "equity_growth": self.stocks[stock].equity_growth, "cash": self.stocks[stock].cash, "shares": self.stocks[stock].shares}
            
        self.market_step += 1
        return self.stock_prices


    def add_cash(self, symbol, amount):
        if symbol not in self.stocks:
            raise ValueError(f"Symbol {symbol} not found in market.")
        self.stocks[symbol].add_cash(amount)
        self.cash -= amount
    
    def remove_cash(self, symbol, amount):
        if symbol not in self.stocks:
            raise ValueError(f"Symbol {symbol} not found in market.")
        self.stocks[symbol].remove_cash(amount)
        self.cash += amount

    def buy_stock(self, symbol, amount):
        if symbol not in self.stocks:
            raise ValueError(f"Symbol {symbol} not found in market.")
        self.stocks[symbol].buy(amount)

    def sell_shares(self, symbol, amount):
        if symbol not in self.stocks:
            raise ValueError(f"Symbol {symbol} not found in market.")
        self.stocks[symbol].sell_shares(amount)
        

    def sell_equity(self, symbol, amount):
        if symbol not in self.stocks:
            raise ValueError(f"Symbol {symbol} not found in market.")
        self.stocks[symbol].sell_equity(amount)

     
    
    