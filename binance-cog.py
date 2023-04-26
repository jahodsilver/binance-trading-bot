from decouple import config
from binance.client import Client
import pandas as pd
import pandas_ta as ta
import json
import os
import time
import datetime
import csv
from pdfreader import SimplePDFViewer
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader


# to trade live, remove the testnet=True, and add api key, also you need tld="us"
client = Client(config("API_KEY"), config("SECRET_KEY"), testnet=True, tld="us")
asset = "BTCUSDT"
candle_holder = []

# account balance in demo account
account_balance = client.get_asset_balance(asset="BTC")


def get_candlestick_data(asset):

    # getting candlestick data for 1H interval from Binance
    candlestick_data = client.get_historical_klines(asset, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")

    # grabs first (open time) and fifth (converted to float because it's a string) element for every element in candlestick_data
    for i in candlestick_data:

        candle_holder.append([i[0], float(i[4])])

        candlestick_data = candle_holder

    candlestick_data = pd.DataFrame(candlestick_data, columns = ["open_time", "close"])

    # converting time column to yyyy-mm-dd
    candlestick_data["open_time"] = pd.to_datetime(candlestick_data["open_time"], unit = "ms")

    # each list represents a candlestick
    return candlestick_data

def get_sma_15(asset):

    candlestick_data = get_candlestick_data(asset)
    candlestick_data["sma_15"] = ta.sma(close = candlestick_data["close"], length = 15)

    # return the the most updated (which is the last element) 50 SMA value
    return candlestick_data["sma_15"].iloc[-1]

def get_sma_50(asset):
    candlestick_data = get_candlestick_data(asset)

    # adds column holding 50 SMA values into candlestick_data
    candlestick_data["sma_50"] = ta.sma(close = candlestick_data["close"], length = 50)

    # return the the most updated (which is the last element) 200 SMA value
    return candlestick_data["sma_50"].iloc[-1]

# logging what's going on
def make_account():


    pdf = canvas.Canvas("account_status.pdf")
    pdf.drawString(100, 750, f"Buying {asset}.")
    pdf.save()

    account_status = dict(buying=True, asset=f"{asset}")
    print(account_status)

    with open("account_status.json", "w") as f:
        f.write(json.dumps(account_status))


def enter_trade(account, client, asset, side, quantity) :

    if side == "buy":

        order = client.order_market_buy(
            symbol = asset,
            quantity = quantity
        )
        account["buying"] = False

    else:

        order = client.order_market_sell(
            symbol = asset,
            quantity = quantity
        )
        account["buying"] = True

    order_id = order["orderId"]

    # while order status doesn't equal "FILLED", check if orders are filled
    while order["status"] != "FILLED":

        order = client.get_order(
            symbol = asset,
            orderId = order_id)
        time.sleep(1) # for not spamming binance's api

    print(order)

    with open("account_status.json", "w") as f:
        f.write(json.dumps(account))

sma_15 = get_sma_15(asset)
sma_50 = get_sma_50(asset)



while 1:

    try:

        # does the account file exist?
        if not (os.path.exists("account_status.pdf") and os.path.exists("account_status.json")):
            make_account()

        with open("account_status.json") as f:
            account = json.load(f)

        print (account, account_balance)

        reader = PdfReader("account_status.pdf")
        text= ""

        # open the PDF file in read-binary mode
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()


        if account["buying"]:

            if sma_15 > sma_50:
                enter_trade(account, client, asset, "buy", 0.01)

        else:

            if sma_15 < sma_50:
                enter_trade(account, client, asset, "sell", 0.01)

            time.sleep(15)

    # what exception is called
    except Exception as e:
        print("error" + str(e))
