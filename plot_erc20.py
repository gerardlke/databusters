from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser


dm = DatasetManager()
dm.add_dataset(r"./datasets/ERC20-stablecoins.zip")

# Retrieve dataframes
dai = dm.get_df("dai_price_data")
pax = dm.get_df("pax_price_data")
usdc = dm.get_df("usdc_price_data")
usdt = dm.get_df("usdt_price_data")
ustc = dm.get_df("ustc_price_data")
wluna = dm.get_df("wluna_price_data")

# Build indicators
for coin, rename in [(dai, "dai"), (pax, "pax"), (usdc, "usdc"), (usdt, "usdt"), (ustc, "ustc"), (wluna, "wluna")]:
    # Build indicators for each
    coin["peg_deviation"] = abs(coin["close"] - 1)
    coin["volatility"] = (coin["high"] - coin["low"]) / coin["close"]
    
    # Clean the data for each coin
    coin = dm.clean_price(coin, rename)

# Peg deviation indicator for ustc
pre_crisis_data = ustc[(ustc["Date"] >= dm.string_to_datetime("2022-04-23"))     # 2 weeks before crisis
                        & (ustc["Date"] <= dm.string_to_datetime("2022-05-06"))]  # 1 day before crisis

peg_threshold = pre_crisis_data["ustc_peg_deviation"].mean() + (3 * pre_crisis_data["ustc_peg_deviation"].std())  # Peg threshold = mean + 3 x std
ustc["peg_threshold"] = peg_threshold

peg_deviations = ustc[(ustc["Date"] >= dm.string_to_datetime("2022-05-06"))  # 1 day before crisis 
                            & (ustc["ustc_peg_deviation"] > peg_threshold)].index
if len(peg_deviations) > 0:
    first_deviation_time = ustc.loc[peg_deviations[0], "Date"]
    print(f"\nFirst meaningful deviation: {first_deviation_time}")
else:
    first_deviation_time = None
    print("No significant deviation detected")

# Peak crisis data
min_price_idx = ustc["ustc_close"].idxmin()
peak_crisis_time = ustc.loc[min_price_idx, "Date"]
min_price = ustc.loc[min_price_idx, "ustc_close"]

print(f"\nPeak crisis (min price): {peak_crisis_time}")
print(f"Minimum price: ${min_price:.6f}")

# Create graphs (focused on USTC)
graphs = [
    {
        "Title": "USTC Peg Deviation",
        "Traces": [
            {
                "Name": "Peg Deviation",
                "x": "Date",
                "y": "ustc_peg_deviation",
                "Color": "red"
            },
            {
                "Name": "Peg Deviation Threshold",
                "x": "Date",
                "y": "peg_threshold",
                "Color": "white"
            }
        ]
    },
    {
        "Title": "USTC Volatility",
        "Traces": [
            {
                "Name": "Volatility",
                "x": "Date",
                "y": "ustc_volatility",
                "Color": "orange"
            }
        ]
    }
]

vertical_lines = [
    {
        "Label": "Meaningful Peg Deviation",
        "x": dm.string_to_unix(first_deviation_time)
    }
]

# Focus the dataframe then plot the graph
vis = Visualiser(ustc)
vis.focus("2022-05-02", "2022-05-25")
vis.plot_indicators(title="Terra USTC Crisis Analysis", graphs=graphs, v_lines=vertical_lines, graph_height=450, vert_spacing=0.15)