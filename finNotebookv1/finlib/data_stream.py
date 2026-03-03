import finlib.data_readers.json_reader as json_reader
from finlib.data_readers.pandas_csv import pandas_csv_reader
from enum import Enum

class data_streams(Enum):
    JSON = "json"
    PANDAS_CSV = "pandas_csv"



#Facade class for streaming in data 
class data_stream:

    # TODO Abstract the args to just a dict to be abstracted in get_reader
    def __init__(self, file_path, stream_type, chunk_size=100):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.stream_type = stream_type
        self.reader = self.get_reader()

    def get_reader(self):
        if self.stream_type == data_streams.JSON.value:
            return json_reader.json_reader(self.file_path, self.chunk_size)
        if self.stream_type == data_streams.PANDAS_CSV.value:
            return pandas_csv_reader(self.file_path, self.chunk_size)
    
    def read_chunk(self):
        return self.reader.read_chunk()

    def stream_data(self):
        # Generator that yields entries from each chunk
        while True:
            chunk = self.read_chunk()
            if not chunk:
                break
            for entry in chunk:
                yield entry