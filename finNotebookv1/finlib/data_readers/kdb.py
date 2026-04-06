###
## jank ass kdb link to pandas for easy integration  
## This is so bad :p
###
import pykx as kx

class kdb_link():
    
    def __init__(self, file_path, chunk_size=100, params=None):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.script_path = params["script_path"] if params and "script_path" in params else (lambda: (_ for _ in ()).throw(ValueError("script_path is required")))()
        self.database_path = params["database_path"] if params and "database_path" in params else (lambda: (_ for _ in ()).throw(ValueError("database_path is required")))()
        self.start_date = params["start_date"] if params and "start_date" in params else (lambda: (_ for _ in ()).throw(ValueError("start_date is required")))()
        self.end_date = params["end_date"] if params and "end_date" in params else (lambda: (_ for _ in ()).throw(ValueError("end_date is required")))()
        self.ticker = params["ticker"] if params and "ticker" in params else (lambda: (_ for _ in ()).throw(ValueError("ticker is required")))()

        # open connection
        try:                        
            self.q = kx.SyncQConnection(host='localhost', port=5000) # hardcoded :p
        except Exception as e:
            print(f"Error connecting to kdb: {e}")
            raise e
        
        self.q(f'\\l {self.script_path}')
        self.q(f'\\l {self.database_path}')

    def read_chunk(self):
        try:
            res = self.q(f'.query[`{self.ticker}; {self.start_date}; {self.end_date}]')
            return res.pd() # convert to pandas dataframe
        except Exception as e:
            print(f"Error reading from kdb: {e}")
            raise e
        

