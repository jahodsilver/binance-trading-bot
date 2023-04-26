import numpy as np
import pandas as pd
from datetime import datetime
import vectorbt as vbt

# reads in a CSV file containing Bitcoin price data and extracts the timestamp and close columns
btc_closing_price = pd.read_csv("btcusd.csv")[["timestamp","close"]]

# converts the timestamp values to datetime objects (tells pandas that the values in the timestamp column represent Unix timestamps,) and sets the date column as the DataFrame index
btc_closing_price["date"] = pd.to_datetime(btc_closing_price["timestamp"], unit = "s")

# sets the date column as the index of the DataFrame, selects only the close column of the resulting DataFrame
btc_closing_price = btc_closing_price.set_index("date")["close"]

sma_15 = vbt.MA.run(btc_closing_price, window=15, short_name="sma_15")
sma_50 = vbt.MA.run(btc_closing_price, window=50, short_name="sma_50")

entry = sma_15.ma_crossed_above(sma_50)
exit = sma_15.ma_crossed_below(sma_50)

pf = vbt.Portfolio.from_signals(btc_closing_price, entry, exit)

print(pf.stats())
