
import json

class ohlcv_collection:
    def __init__(self, data: list):
        self.timeseries = []

        if type(data) is not list:
            raise TypeError("data must be a list")
        
        if type(data[0]) is dict:
            for item in data:
                self.timeseries.append(ohlcv(item))
         
        elif type(data[0]) is ohlcv:
            self.timeseries = data
        else:
            raise TypeError("data must be a list of dicts or ohlcv objects ", (type(data[0]), " is not recognized"))
    
    def __repr__(self):
        return f"ohlcv_collection(timeseries_length={len(self.timeseries)})"


class ohlcv:
    def __init__(self, data: dict):
        if type(data) is not dict:
            raise TypeError("data must be a dict")
        
        try:
            assert all(key in data for key in ["open", "high", "low", "close", "volume"])
            assert any(key in data for key in ["timestamp", "time"])
        except AssertionError:
            raise KeyError("data dict must contain keys: open, high, low, close, volume")
        
        if ("timestamp" in data) and ("time" in data):
            raise KeyError("data dict cannot contain both 'timestamp' and 'time' keys")
        
        if ("timestamp" in data):
            self.timestamp = data["timestamp"]
        else:
            self.timestamp = data["time"]

        self.open = data.get("open", None)
        self.high = data.get("high", None)
        self.low = data.get("low", None)
        self.close = data.get("close", None)
        self.volume = data.get("volume", None)


    #printable representation of object
    def __repr__(self):
        return f"ohlcv(timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})"


    def get_dict(self):
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }