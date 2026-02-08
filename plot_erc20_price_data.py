from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser


dm = DatasetManager()
dm.add_dataset(r"./datasets/ERC20-stablecoins.zip")

# # Retrieve dataframes
dai = dm.get_df("dai_price_data")
pax = dm.get_df("pax_price_data")
usdc = dm.get_df("usdc_price_data")
usdt = dm.get_df("usdt_price_data")
ustc = dm.get_df("ustc_price_data")
wluna = dm.get_df("wluna_price_data")

# Clean data and build indicators
for coin, rename in [(dai, "dai"), (pax, "pax"), (usdc, "usdc"), (usdt, "usdt"), (ustc, "ustc"), (wluna, "wluna")]:
    coin["volatility"] = (coin["high"] - coin["low"]) / coin["close"]
    coin = dm.clean_price(coin, rename)

# Combine dataframes
combined_price_df = dm.combine_dfs(
    [dai, pax, usdc, usdt, ustc, wluna],
    on="Date",
    how="outer"
).sort_values("Date")

graphs = [
    {
        "Title": "Overall Prices",
        "Traces": [
            {
                "Name": "DAI",
                "x": "Date",
                "y": "dai_close",
                "Color": "blue"
            },
            {
                "Name": "PAX",
                "x": "Date",
                "y": "pax_close",
                "Color": "orange"
            },
            {
                "Name": "USDC",
                "x": "Date",
                "y": "usdc_close",
                "Color": "red"
            },
            {
                "Name": "USDT",
                "x": "Date",
                "y": "usdt_close",
                "Color": "yellow"
            },
            {
                "Name": "USTC",
                "x": "Date",
                "y": "ustc_close",
                "Color": "green"
            },
            {
                "Name": "WLUNA",
                "x": "Date",
                "y": "wluna_close",
                "Color": "white"
            }
        ]
    },
    {
        "Title": "Overall Price Volatility",
        "Traces": [
            {
                "Name": "DAI",
                "x": "Date",
                "y": "dai_volatility",
                "Color": "blue"
            },
            {
                "Name": "PAX",
                "x": "Date",
                "y": "pax_volatility",
                "Color": "orange"
            },
            {
                "Name": "USDC",
                "x": "Date",
                "y": "usdc_volatility",
                "Color": "red"
            },
            {
                "Name": "USDT",
                "x": "Date",
                "y": "usdt_volatility",
                "Color": "yellow"
            },
            {
                "Name": "USTC",
                "x": "Date",
                "y": "ustc_volatility",
                "Color": "green"
            },
            {
                "Name": "WLUNA",
                "x": "Date",
                "y": "wluna_volatility",
                "Color": "white"
            }
        ]
    }
]
vis = Visualiser(combined_price_df)
vis.plot_indicators(title="Stable Coins Price Fluctuations", graphs=graphs)