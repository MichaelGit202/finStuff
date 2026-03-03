import pandas as pd
import json



def SD5Y_to_json(company, chunk_size=100):
    #converting one company from this dataset to json to use in the sim
    
    df = pd.read_csv('./data/stock_details_5_years.csv', chunksize=chunk_size)
    records = []
    count = 0
    for chunk in df:
        #print(chunk)
        filtered_df = chunk.loc[chunk['Company'] == company]
        #print(filtered_df)
        for row in filtered_df.to_dict(orient='records'):
            records.append({
                'time': row["Date"],
                'open': row["Open"],
                'high': row["High"],
                'low': row["Low"],
                'close': row["Close"],
                'volume': row["Volume"],
                'dividends' : row["Dividends"],
                'stock_splits' : row["Stock Splits"]
            })
            count += 1

    print(records)
        
    print(f"Records extracted: {count}")
    with open(f'./data/stock_details_5_years_{company}.json', 'w') as f:
       json.dump(records, f, indent=4)