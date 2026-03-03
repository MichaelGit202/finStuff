import pandas as pd



class pandas_csv_reader: 
    
    
    def __init__(self, file_path, chunk_size=100):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.reader = pd.read_csv(self.file_path, chunksize=self.chunk_size)

    def read_chunk(self):
        try:
            data = next(self.reader) # reads next chunk of dataframe, cool 
            # manipulate the data to fit format
        except StopIteration:
            return None
        return data

# This will be my new main loop i guess when i start implementing some of the algos
#for chunk in pd.read_csv('./data/stock_details_5_years.csv', chunksize=100):
#    print(chunk)
#    break