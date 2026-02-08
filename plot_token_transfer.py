from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser


dm = DatasetManager()
dm.add_dataset(r"./datasets/ERC20-stablecoins.zip")

# Retrieve dataframes
tokens = dm.get_df("token_transfers_V3")

print("Data extracted.")

# Clean specific features
tokens["amount"] = tokens["value"]
tokens["Date"] = dm.unix_to_datetime(tokens["time_stamp"])
tokens.sort_values("Date").reset_index(drop=True)

# Focusing on specific period for analysis
tokens = tokens[(tokens["Date"] >= dm.string_to_datetime("2022-04-20")) 
                         & (tokens["Date"] <= dm.string_to_datetime("2022-05-30"))]

# Contract filtering if needed
USDT_CONTRACT = "0xa47c8bf37f92abed4a126bda807a7b7498661acd"

if "contract_address" in tokens.columns:
    if tokens["contract_address"].nunique() > 1:
        print("Filtering to USDT only...")
        tokens = tokens[tokens["contract_address"].str.lower() == USDT_CONTRACT.lower()].copy()

print("Data cleaned.")

# Rolling window indicators
df = tokens.set_index("Date").sort_index()
df.index = dm.unix_to_datetime(df.index)

roller = df["amount"].rolling(window="24h", min_periods=1)

df["Volume_24h"] = roller.sum()
df["TxCount_24h"] = roller.count()
df["AvgTxSize_24h"] = roller.mean()
df["MedianTxSize_24h"] = roller.median()
df["TxVolatility_24h"] = roller.std()

LARGE_TX_PERCENTILE = 95
threshold = df["amount"].quantile(LARGE_TX_PERCENTILE / 100)
df["is_large_tx"] = (df["amount"] >= threshold).astype(int)
df["LargeTxCount_24h"] = df["is_large_tx"].rolling(
    window="24h", min_periods=1
).sum()

tokens = df.reset_index()

print("Rolling window complete.")

# Hourly aggregates 
tokens["Hour"] = tokens["Date"].dt.floor("h")
hourly = tokens.groupby("Hour").agg({
    "amount": ["sum", "mean", "median", "std", "count"],
    "from_address": "nunique",
    "to_address": "nunique",
    "is_large_tx": "sum"
})

hourly.columns = ["Total_Volume", "Avg_Tx", "Median_Tx", "Tx_Std", "Tx_Count", "Unique_Senders", "Unique_Receivers", "Large_Tx_Count"]
hourly = hourly.reset_index()

STRESS_VOLUME_PERCENTILE = 90
volume_threshold = hourly["Total_Volume"].quantile(STRESS_VOLUME_PERCENTILE / 100)
count_threshold = hourly["Tx_Count"].quantile(STRESS_VOLUME_PERCENTILE / 100)

hourly["stress_period"] = (hourly["Total_Volume"] >= volume_threshold) & (hourly["Tx_Count"] >= count_threshold)

print("Hourly aggregates completed.")

# Daily aggregates
tokens["Day"] = tokens["Date"].dt.date
daily = tokens.groupby("Day").agg(
    Day_Volume=("amount", "sum"),
    Unique_Senders=("from_address", "nunique"),
    Unique_Receivers=("to_address", "nunique"),
    Day_Tx_Count=("amount", "count")
).reset_index()

# HHI Data
sender_daily_vols = tokens.groupby(["Day", "from_address"])["amount"].sum().reset_index()
sender_daily_vols["Share_Sq"] = (sender_daily_vols["amount"] / 
                                    sender_daily_vols.groupby("Day")["amount"].transform("sum"))**2

hhi_df = sender_daily_vols.groupby("Day")["Share_Sq"].sum().reset_index(name="HHI_Senders")

daily = daily.merge(hhi_df, on="Day", how="left")
daily["Date"] = dm.unix_to_datetime(daily["Day"])
daily["Day_Volume_M"] = daily["Day_Volume"] / 100000000
daily["Day_Tx_Count_K"] = daily["Day_Tx_Count"] / 1000

print("Daily aggregates completed.")

# Create graphs
graphs = [
    {
        "Title": "Crisis Onset: Volume and Transaction Surge",
        "Traces": [
            {
                "Name": "Total Volume of Tokens / 100M",
                "x": "Date",
                "y": "Day_Volume_M",
                "Color": "crimson"
            },
            {
                "Name": "Transaction Count / Thousands",
                "x": "Date",
                "y": "Day_Tx_Count_K",
                "Color": "steelblue"
            }            
        ]
    }
]


# Focus the daily aggregate dataframe then plot the graph
vis = Visualiser(daily)
vis.focus("2022-05-03", "2022-05-20")
vis.plot_indicators(title="Terra-Luna Crisis: Confidence Breakdown Analysis", graphs=graphs)