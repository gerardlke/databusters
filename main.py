from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser

if __name__ == "__main__":
    dm = DatasetManager()
    dm.add_dataset(r"./datasets/ERC20-stablecoins.zip")
    dm.add_dataset(r"./datasets/gfc.zip")

    # Retrieve dataframes
    vix = dm.clean_yahoo(dm.get_df("VIX.csv"))
    ted = dm.clean_fred(dm.get_df("TEDRATE.csv"), "TEDRATE")
    t3m = dm.clean_fred(dm.get_df("WGS3MO.csv"), "WGS3MO")

    # Build indicators
    vix["Vix_volatility"] = (vix["High"] - vix["Low"]) / vix["Close"]
    vix["Vix_intraday_vol"] = (vix["High"] - vix["Low"]) / vix["Close"]
    vix["Vix_volume"] = (vix["High"] - vix["Low"]) / vix["Close"]

    # Merge to a common date index for aligned plotting
    combined_df = (vix[["Date", "Close", "Vix_intraday_vol", "Vix_volume"]]
          .merge(ted, on="Date", how="outer")
          .merge(t3m, on="Date", how="outer")
          .sort_values("Date")
    )


    vis = Visualiser(combined_df)
    
    # Focus on a specific window
    print(vis.focus("2008-01-01", "2009-01-01"))
    print(vis.focus())

    graphs = [
        {
            "Title": "Market Volatility (VIX)",
            "Traces": [{
                "Name": "VIX Close",
                "x": "Date",
                "y": "Close",
                "Color": "red"
            }]
        },
        {
            "Title": "Systemic Stress (TED Spread & T-Bills)",
            "Traces": [{
                "Name": "TED Spread",
                "x": "Date",
                "y": "TEDRATE",
                "Color": "orange"
            },
            {
                "Name": "3M T-Bill Yield",
                "x": "Date",
                "y": "WGS3MO",
                "Color": "blue"
            }]
        }
    ]
    vis.plot_indicators(title="Financial Crisis Stress Propagation", graphs=graphs)