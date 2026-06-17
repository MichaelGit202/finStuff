# Fine
###
## kdb link to pandas for easy integration  
## This is not how it should be done
###
from datetime import datetime, timedelta

import pykx as kx

class kdb_link():
    
    def __init__(self, chunk_size=100, params=None):
        self.chunk_size = chunk_size

        throw_error = lambda msg: (_ for _ in ()).throw(ValueError(msg))

        self.script_path = params["script_path"] if params and "script_path" in params else throw_error("script_path is required")
        self.database_path = params["database_path"] if params and "database_path" in params else throw_error("database_path is required")
        self.start_date = params["start_date"] if params and "start_date" in params else throw_error("start_date is required")
        end = params["end_date"] if params and "end_date" in params else throw_error("end_date is required")
        self.ticker = params["ticker"] if params and "ticker" in params else throw_error("ticker is required")
        self.timeframe = params["timeframe"] if params and "timeframe" in params else throw_error("timeframe is required")

        self.end_date = datetime.strptime(end, "%Y.%m.%d")
        self.reading_cursor = datetime.strptime(self.start_date, "%Y.%m.%d") #TODO, this will have issues when I add in hourly & minutely data

        # open connection
        try:                        
            self.q = kx.SyncQConnection(host='localhost', port=5000) # TODO hardcoded :p
        except Exception as e:
            print(f"Error connecting to kdb: {e}")
            raise e
        
        self.q(f'\\l {self.script_path}')
        self.q(f'\\l {self.database_path}')

    def read_chunk(self):
        print("reading chunk")
        try:
            # calculate date range for this chunk, im not touching q for now
            
            if (self.reading_cursor > self.end_date):
                return None 
            

            if self.timeframe == "1d":
                offset = timedelta(days=self.chunk_size) 
            elif self.timeframe == "1h":
                offset = timedelta(hours=self.chunk_size)
            elif self.timeframe == "1m":    
                offset = timedelta(minutes=self.chunk_size)
            else:
                raise ValueError(f"Unsupported timeframe: {self.timeframe}")

            end_date = self.reading_cursor + offset
            start_q = self.reading_cursor.strftime("%Y-%m-%d %H:%M:%S")
            end_q = end_date.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Querying kdb for data from {start_q} to {end_q}")
            res = self.q(f'.query_fac[`{self.ticker}; "{start_q}"; "{end_q}"]')
            self.reading_cursor = end_date

            return res.pd() # convert to pandas dataframe
        except Exception as e:
            print(f"Error reading from kdb: {e}")
            raise e
        

