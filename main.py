from datetime import timedelta
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pymongo
import mplfinance as mpf

#connect to mongodb
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.BNBUSDT
collection = db.BNBUSDT_60T

#convert collection to dataframe
df = pd.DataFrame(list(collection.find()))


df.rename(columns={'timestamp':'Date', 'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'], unit='s')
df.set_index('Date', inplace=True)
#diffrence beetwenn high and low
df['candle_size'] = df['High'] - df['Low']
#calculate the mean of moving avarge of candle size for 24 hours
df['candle_size_ma'] = df['candle_size'].rolling(24, min_periods = 1).mean()
#calcutate trend direction
df['direction'] = np.where(df['Close'] > df['Open'], 'bull', 'bear')


#has to be 3 x times larger than the moving average df['candle_size_ma'] 
candle_size_mult = 3
candle_idx = []

x = []
for i in range(0, len(df)):
    #find big candles bigger in size than the moving average by candle size_mult
    if df['candle_size'][i] >= df['candle_size_ma'][i] * candle_size_mult:
        #find candle body that is bigger than 50% of total size of the candle
        if (abs(df['Open'][i] - df['Close'][i]) / df['candle_size'][i]) * 100 >= 50:
            #check only for green candle
            if df['Open'][i] <= df['Close'][i]:
                #check the next 24 candles that they high is bigger than the current candle open
                if (all(df['High'][i+1 :i+24] > df['Open'][i])):
                    #append candles
                    candle_idx.append(df.index[i])
                    #
                    x = max(df[i-48: i][df[i-48: i]['direction'] != df['direction'][i]].index) + timedelta(hours = 1) \
                                                if df['direction'][i] == df['direction'][i-1] else df.index[i]
print(len(candle_idx))
        
mpf.plot(df,
         vlines = dict(vlines = candle_idx, alpha = 0.3), figsize = (13, 5), style = 'yahoo', warn_too_much_data = len(df) + 1, type = 'candle')



def daily_range(df):
    daily_range = []
    for i in range(len(df)):
        if df.index.day[i] != df.index.day[i-1]:
            try:
                daily_range.append(max(df[df.index[i]: df.index[i+24]]['High']) - min(df[df.index[i]: df.index[i+24]]['Low']))
            except:
                daily_range.append(max(df[df.index[i]: df.index.max()]['High']) - min(df[df.index[i]: df.index.max()]['Low']))
    return np.mean(daily_range[-10:])

print(daily_range(df))