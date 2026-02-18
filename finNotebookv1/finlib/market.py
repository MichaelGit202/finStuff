### Object to hold all tickers apart of a dataset


class stock_market:
    def __init__(self, ohlcv_list: list, initial_cash: float = 10000):
        self.ohlcv_list = ohlcv_list
        self.current_index = 0
        self._eof = False
        self.current_ohlcv = None
        


    def step(self):
        if self._eof:
            return None  # no more data to step through

        self.current_ohlcv = self.ohlcv_list[self.current_index]
        self.current_index += 1

        if self.current_index >= len(self.ohlcv_list):
            self._eof = True

        return self.current_ohlcv