class stock_market:
    def __init__(self, ohlcv_data_dir: str):
        self.ohlcv_data_dir = ohlcv_data_dir
        

    def step(self):
        if self._eof:
            return None  # no more data to step through

        self.current_ohlcv = self.ohlcv_list[self.current_index]
        self.current_index += 1

        if self.current_index >= len(self.ohlcv_list):
            self._eof = True

        return self.current_ohlcv