from collections import deque
import pandas as pd
from .kdb_interface import kdb_link as kdb
from .indicators import FUNCTION_ARR_DICT as functions  # TODO bad, but ok for now
from .constants import DATA_WINDOW_LENGTH

params = {
            "script_path": "/home/mica/finProject/finStuff/databases/db_handler_alpha_fac.q", 
            "database_path": "/home/mica/finProject/finStuff/databases/db", 
            "start_date": "2021.01.01", 
            "end_date": "2021.12.31", 
            "ticker": "JPM",
            "timeframe": "1d"
         }

def preprocess_indicators(params=params, functions=functions, output_path="", ):

    data_window = deque(maxlen=DATA_WINDOW_LENGTH)

    jpm = kdb(params=params, chunk_size=100)
    
    start_date = pd.to_datetime(params["start_date"], format="%Y.%m.%d")

    dates = pd.date_range(start=start_date, periods=1, freq="D")
    data = pd.DataFrame(data={'price': 0, **{functions[key]["name"]: 0 for key in functions}}, index=dates)

    timestamp_candidates = ["Date", "Datetime", "date", "time", "timestamp"]

    i = 0
    while True:
        i += 1
        df = jpm.read_chunk()

        if df is None:
            print(f"done after {i} chunks")
            break

        ts_col = next((col for col in timestamp_candidates if col in df.columns), None)

        for j in range(len(df)):
            data_window.append(df.iloc[j])

            if ts_col is not None:
                ts_val = pd.to_datetime(df.iloc[j][ts_col], errors="coerce")
                row_index = ts_val if pd.notna(ts_val) else df.index[j]
            else:
                row_index = df.index[j]

            data = pd.concat([data, pd.DataFrame({
                "price": df.iloc[j]["Close"],
                **{functions[key]["name"]: functions[key]["function"](data_window) for key in functions}
            }, index=[row_index])], ignore_index=False)

            for key in functions:
                func = functions[key]["function"]
                result = func(data_window)
                print(f"{func.__name__}: {result}")

    # Keep chronology stable and eliminate duplicate index rows produced by chunk-local indexing.
    data = data.sort_index()
    data = data[~data.index.duplicated(keep="last")]

    if output_path != "":
        data.to_csv(output_path)
    else:
        data.to_csv("preprocessed_indicators.csv")
    
