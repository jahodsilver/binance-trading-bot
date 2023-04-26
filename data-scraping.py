import json
import requests
import pandas as pd
import datetime

currency_pair = "btcusd"
url = f"https://www.bitstamp.net/api/v2/ohlc/{currency_pair}/"


# creates a list of hourly timestamps between a start and end date using pandas date_range() function.
time_range = pd.date_range(start="2021-11-01", end="2021-12-30", freq = "1H")

# converts the timestamps to Unix time format and places them in a list.
time_range_unix = (time_range.astype('int64') // 10**9).tolist()


"""
iterates through a pair of hourly timestamps and makes a GET request to the Binance API for each time
period using the requests.get() function. The parameters for each request are defined in the params dictionary.
The returned data is stored in data and is then converted to a JSON object using .json().
the ohlc key of the JSON object corresponds to the financialdata for the time period, which is then added to container using the += operator.
"""

# initializes an empty list to store the downloaded financial data
ohlc_final = []

for open, close, in zip(time_range_unix, time_range_unix[1:]): # time_range_unix[1:] is a list containing all the elements of dates starting from the second element

    params = {
        "step":60, # every 60 seconds
        "limit":1000, # up to the last 1000 data points
        "start":open,
        "end": close,

    }

    ohlc_binance = requests.get(url, params = params)
    ohlc_binance = ohlc_binance.json()["data"]["ohlc"]
    ohlc_final.append(ohlc_binance) # or ohlc += ohlc_binance


# creates a pandas DataFrame from
df = pd.DataFrame(ohlc_final)

# removes any duplicate rows from the DataFrame
df = df.drop_duplicates()

# converts the timestamp column to integers
df["timestamp"] = df["timestamp"].astype(int)

# sorts the DataFrame by timestamp
df = df.sort_values(by="timestamp")

# filter the DataFrame to only include rows that fall within the start and end dates
df = df[df ["timestamp"] >= time_range_unix[0]]
df = df[df ["timestamp"] < time_range_unix[-1]]


# saves the filtered DataFrame as a CSV file named "tutorial.csv" without the index column.
df.to_csv("ohlc.csv", index=False)
