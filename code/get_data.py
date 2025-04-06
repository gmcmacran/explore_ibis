import os

import polars as pl

os.getcwd()

# download
df = pl.read_csv("hf://datasets/AYUSHKHAIRE/real-time-stocks-data/stocks.csv")
df.head()
df.shape


df = df.with_columns(
    pl.col("timestamp").str.strptime(pl.Datetime).alias("timestamp")
).select([pl.col("stockname"), pl.col("timestamp"), pl.col("open")])

path = os.path.join(os.getcwd(), "data", "stock_data.parquet")
df.write_parquet(file=path)
